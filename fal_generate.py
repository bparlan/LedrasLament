#!/usr/bin/env python3
"""
Ledras Lament Scene Generator - CONSOLIDATED

This script generates images for Ledras Lament scenes using fal.ai API.
Combines ALL required parameters with multi-scene support.

User-Requested Parameters:
- guidance_scale: 3.5
- enable_safety_checker: True
- control_lora_strength: 0.6
- control_lora_image_url
- num_inference_steps: 28
- image_size: {"width": 1280, "height": 704}
"""

from dotenv import load_dotenv
import json, os, random, requests, sys, time
from typing import Dict, List, Any, Optional
from datetime import datetime

# Load .env BEFORE any SDK import — this is the root FAL_KEY source
load_dotenv('.env')

from fal_client import SyncClient

from utils import get_resolution, estimate_cost

# Centralized error handling
def _safe_error_handler(error: Exception, context: str, default_return: Any = None) -> Any:
    """Centralized error handler with consistent logging."""
    print(f"❌ {context}: {error}")
    return default_return

# Centralized file loading
def _load_scenes_data(file_path: str) -> Any:
    """Load scenes data from JSON file with error handling."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        _safe_error_handler(e, f"Error loading scenes file: {file_path}")
        return None

# Centralized logging
def _log_generation_result(log_path: str, log_entry: Dict):
    """Log generation results to file."""
    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a") as f_log:
            f_log.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"⚠️  Failed to write generation log: {e}")

# Centralized download with retry
def _download_image_with_retry(image_url: str, output_path: str) -> bool:
    """Download image with exponential backoff retry."""
    for attempt in range(3):
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            with open(output_path, "wb") as f_out:
                f_out.write(response.content)
            print(f"✅ Image saved to {output_path}")
            return True
        except Exception as e:
            if attempt == 2:
                print(f"⚠️  Failed to download image after 3 attempts: {e}")
                raise
            delay = min(0.5 * (2 ** attempt), 5.0)
            print(f"⚠️  Download failed (attempt {attempt + 1}), retrying in {delay:.1f}s: {e}")
            time.sleep(delay)
    return False

class LedrasConfig:
    def __init__(self):
        self.load_imagine_config()

    def load_imagine_config(self):
        """Load configuration from imagine-config.json (sole source of truth)"""
        config_path = "imagine-config.json"
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)

            for key, value in config_data.items():
                setattr(self, key, value)

            print(f"✅ Configuration loaded from {config_path}")
        except Exception as e:
            print(f"❌ Fatal: Could not load {config_path}: {e}")
            sys.exit(1)

class LedrasSceneGenerator:
    def __init__(self):
        self.config = LedrasConfig()
        self.setup_fal_client()
        self.progress = ProgressReporter(verbose=False)
        self._control_urls = {}  # cache for scene-specific control URLs
        self._scenes_data = None  # cache for scenes data

    def setup_fal_client(self):
        """Setup fal client — reads FAL_KEY from env per fal.ai convention"""
        # SyncClient() auto-reads FAL_KEY env var.
        # Module-level upload_file/status/result also use FAL_KEY natively.
        self.client = SyncClient()
        print("✅ FAL client ready (SyncClient reads FAL_KEY from env)")

    def _build_prompt(self, scene: dict, role: str = "intro") -> str:
        """Build canonical prompt: description + elements + metadata."""
        description = scene.get('description', '')
        elements = scene.get('elements', [])
        parts = [description]
        if elements:
            parts.append("Key elements: " + ", ".join(elements))
        metadata = (
            f"[seed:{scene.get('seed', self.config.seed)}] "
            f"[team:{self.config.cultural_authenticity_level}] [{role}]"
        )
        return f"{' '.join(parts)} {metadata}".strip()

    def _build_subscene_prompt(self, scene: dict, subscene: dict) -> str:
        """Build prompt from subscene description + scene elements."""
        elements = scene.get('elements', [])
        parts = [subscene.get('description', '')]
        if elements:
            parts.append("Key elements: " + ", ".join(elements))
        metadata = (
            f"[seed:{subscene.get('seed', self.config.seed)}] "
            f"[team:{self.config.cultural_authenticity_level}] [{subscene.get('name', 'subscene')}]"
        )
        return f"{' '.join(parts)} {metadata}".strip()

    def _get_scenes_data(self):
        """Get scenes data with caching."""
        if self._scenes_data is None:
            self._scenes_data = _load_scenes_data(self.config.scenes_file)
        return self._scenes_data

    def _get_scene_by_id(self, scene_id: int) -> Optional[Dict]:
        """Find a scene by ID from the scenes data."""
        scenes_data = self._get_scenes_data()
        if not scenes_data:
            return None

        # Support both object with 'scenes' key and array
        if isinstance(scenes_data, dict):
            scenes = scenes_data.get('scenes', scenes_data)
        else:
            scenes = scenes_data

        return next((s for s in scenes if isinstance(s, dict) and s.get('id') == scene_id), None)

    def generate_prompt(self, scene_id: int, role: str = "loop") -> str:
        """Generate prompt for specific scene and role."""
        scene = self._get_scene_by_id(scene_id)
        if scene is None:
            print(f"⚠️  Scene {scene_id} not found")
            return ""

        return self._build_prompt(scene, role)

    def generate_all_prompts(self) -> Dict[int, Dict[str, str]]:
        """Generate prompts for all scenes and roles."""
        scenes_data = self._get_scenes_data()
        if not scenes_data:
            return {}

        # Support both object with 'scenes' key and array
        if isinstance(scenes_data, dict):
            scenes = scenes_data.get('scenes', scenes_data)
        else:
            scenes = scenes_data

        prompts = {}
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            scene_id = scene.get('id')
            if not scene_id:
                continue
            prompts[scene_id] = {
                'intro': self._build_prompt(scene, 'intro'),
                'loop': self._build_prompt(scene, 'loop'),
            }
        return prompts

    def _get_control_path_for_scene(self, scene_id: int = None) -> Optional[str]:
        """Get control image path, checking scene-specific image first, then config default."""
        # First try scene-specific control image if scene_id is provided
        if scene_id is not None:
            scene = self._get_scene_by_id(scene_id)
            if scene and scene.get('control_image'):
                image_path = scene['control_image']
                print(f"🎨 Scene {scene_id} has own control image: {image_path}")
                if os.path.exists(image_path):
                    return image_path
                else:
                    print(f"⚠️  Scene {scene_id} control image not found: {image_path}, falling back to default")

        # Fall back to global configuration
        return self.config.control_lora_image_url

    def _get_control_strength_for_scene(self, scene_id: int = None) -> float:
        """Get control strength, checking scene-specific value first, then config default."""
        if scene_id is not None:
            scene = self._get_scene_by_id(scene_id)
            if scene and scene.get('control_lora_strength') is not None:
                print(f"🎯 Scene {scene_id} using its own control strength: {scene['control_lora_strength']}")
                return scene['control_lora_strength']

        print(f"🎯 Using global control strength: {self.config.control_lora_strength}")
        return self.config.control_lora_strength

    def _get_control_url(self, scene_id: int = None) -> Optional[str]:
        """Upload control image once and cache the CDN URL."""
        cache_key = f"control_url_{scene_id or 'global'}"

        # Return cached URL if available
        if cache_key in self._control_urls:
            return self._control_urls[cache_key]

        # Get control image path (scene-specific or global)
        control_image_path = self._get_control_path_for_scene(scene_id)

        if not control_image_path:
            print("❌ ERROR: control_lora_image_url not configured")
            self._control_urls[cache_key] = None
            return None
        if not os.path.exists(control_image_path):
            print(f"❌ ERROR: Control image not found at {control_image_path}")
            self._control_urls[cache_key] = None
            return None

        print(f"📤 Uploading control image: {control_image_path}")
        uploaded_url = self.client.upload_file(control_image_path)
        print(f"✅ Control image uploaded: {uploaded_url}")

        # Cache the result
        self._control_urls[cache_key] = uploaded_url
        return uploaded_url

    def generate_image(self, prompt: str, scene_id: int, role: str, *,
                       sub_label: str = "") -> Optional[Dict[str, Any]]:
        """Generate a single image using fal.ai API with SyncClient"""
        request_seed = random.randint(1, 2**31 - 1)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"🎨 Generating image: Scene {scene_id}, Role: {role}")
        print(f"   Prompt preview: {prompt[:100]}..." if len(prompt) > 100 else f"   Prompt: {prompt}")

        try:
            # Get control URL (scene-specific or global)
            control_lora_image_url = self._get_control_url(scene_id)
            if not control_lora_image_url:
                print(f"❌ ERROR: No control image URL available for scene {scene_id}")
                return None

            # Prepare fal.ai API parameters
            fal_params = {
                "prompt": prompt,
                "control_lora_image_url": control_lora_image_url,
                "image_size": self.config.image_size,
                "seed": request_seed,
                "num_inference_steps": self.config.num_inference_steps,
                "num_images": 1,
                "output_format": "png",
                "guidance_scale": self.config.guidance_scale,
                "enable_safety_checker": self.config.enable_safety_checker,
                "control_lora_strength": self._get_control_strength_for_scene(scene_id),
            }

            print(f"🤖 Calling fal.ai API with model: {self.config.fal_model}")

            # Use the SyncClient to call the API
            result = self.client.run(
                application=self.config.fal_model,
                arguments=fal_params
            )

            if not result:
                print(f"⚠️  No result returned from API for scene {scene_id}")
                return None

            # Handle both dict-style (fal SDK) and attribute-style responses
            images = (result.get("images", []) if isinstance(result, dict)
                      else (result.images if hasattr(result, "images") else []))

            if not images:
                print(f"⚠️  No images returned from API for scene {scene_id}")
                return None

            image_data = images[0]
            print(f"✅ Image generation successful for scene {scene_id}!")

            # Build deterministic file name
            sub_part = f"_{sub_label}" if sub_label else ""
            filename = f"scene-{scene_id:02d}{sub_part}_v{request_seed:03d}_{timestamp}.png"
            output_path = os.path.join(self.config.output_dir, filename)
            file_path = None

            image_url = (image_data.get("url") if isinstance(image_data, dict)
                         else (image_data.url if hasattr(image_data, "url") else None))
            if image_url:
                # Log generation before download
                log_path = os.path.join(self.config.output_dir, "generation_log.jsonl")
                log_entry = {
                    "scene_id": scene_id, "seed": request_seed,
                    "sub_label": sub_label, "role": role,
                    "image_url": image_url, "timestamp": timestamp,
                    "filename": filename,
                }
                _log_generation_result(log_path, log_entry)

                # Download image
                if _download_image_with_retry(image_url, output_path):
                    file_path = output_path

            return {
                "scene_id": scene_id,
                "role": role,
                "prompt": prompt,
                "image_data": image_data,
                "generation_timestamp": datetime.now().isoformat(),
                "model_used": self.config.fal_model,
                "seed": request_seed,
                "file_path": file_path
            }

        except Exception as e:
            _safe_error_handler(e, f"❌ Image generation failed for scene {scene_id}")
            return None

    def generate_specific_images(self, scene_ids: List[int], role: str = "intro"):
        """Generate images for specific scenes and roles"""
        generated = {}

        self.progress.set_target(len(scene_ids))
        self.progress.report(f"🎨 Starting image generation for scenes {scene_ids}, role: {role}")
        print(f"📁 Output directory: {self.config.output_dir}")
        print(f"🤖 Using model: {self.config.fal_model}")
        print(f"🎯 Control strength: {self.config.control_lora_strength}")
        print(f"🌱 Cultural authenticity: {self.config.cultural_authenticity_level}")
        print()

        prompts = self.generate_all_prompts()

        for scene_id in scene_ids:
            print(f"📸 Processing Scene {scene_id} ({role}):")

            prompt = prompts.get(scene_id, {}).get(role, "")

            if not prompt:
                print(f"⚠️  No prompt available for scene {scene_id}")
                continue

            image_info = self.generate_image(prompt, scene_id, role)

            if image_info:
                self.progress.increment()
                self.progress.report(f"Scene {scene_id} generated successfully")
                generated[scene_id] = image_info
                print(f"✅ Scene {scene_id} generated successfully")
            else:
                self.progress.increment_error()
                self.progress.report(f"Failed to generate scene {scene_id}", force=True)
                print(f"❌ Failed to generate scene {scene_id}")

        return generated

    def generate_subscene_images(self, scene_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Generate images for all subscenes of given scenes."""
        scenes_data = self._get_scenes_data()
        if not scenes_data:
            return {}

        # Support both object with 'scenes' key and array
        if isinstance(scenes_data, dict):
            scenes = scenes_data.get('scenes', scenes_data)
        else:
            scenes = scenes_data

        total_subs = 0
        for scene_id in scene_ids:
            scene = next((s for s in scenes if isinstance(s, dict) and s.get('id') == scene_id), None)
            if scene is None:
                print(f"⚠️  Scene {scene_id} not found, skipping")
                continue
            total_subs += len(scene.get('subscenes', []))

        print(f"🎨 Generating {total_subs} subscene images for scenes {scene_ids}")
        print(f"📁 Output directory: {self.config.output_dir}")
        print(f"🤖 Using model: {self.config.fal_model}")
        print()

        results: Dict[int, Dict[str, Any]] = {}

        for scene_id in scene_ids:
            scene = next((s for s in scenes if isinstance(s, dict) and s.get('id') == scene_id), None)
            if scene is None:
                continue

            print(f"📸 Scene {scene_id}: {scene.get('name', '')}")
            for sub in scene.get('subscenes', []):
                sub_name = sub.get('name', 'unknown')
                sub_id = sub.get('id', 0)
                prompt = self._build_subscene_prompt(scene, sub)

                print(f"  → Subscene {sub_id}: {sub_name}")
                info = self.generate_image(
                    prompt, scene_id, sub_name,
                    sub_label=str(sub_id),
                )
                if info:
                    self.progress.increment()
                    self.progress.report(f"Subscene {sub_id} for scene {scene_id} generated")
                    if scene_id not in results:
                        results[scene_id] = {}
                    results[scene_id][sub_name] = info
                    print(f"  ✅ Subscene {sub_id} generated")

            print()

        print(f"✅ Generated {sum(len(v) for v in results.values())} subscene images")
        return results

class ProgressReporter:
    """Concise progress reporting for image generation pipeline"""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.start_time = time.time()
        self.last_report = 0
        self.images_generated = 0
        self.total_target = 0
        self.errors_count = 0

    def set_target(self, total):
        """Set the total number of images to be generated"""
        self.total_target = total

    def report(self, message, force=False):
        """Report progress with timing and statistics"""
        current_time = time.time()
        elapsed = current_time - self.start_time

        if self.verbose or force or (current_time - self.last_report) >= 5:
            timestamp = current_time - self.start_time

            if self.total_target > 0:
                progress = (self.images_generated / self.total_target) * 100
                rate = self.images_generated / elapsed if elapsed > 0 else 0
                print(f"[{timestamp:6.1f}s] {message} ({progress:5.1f}% - {self.images_generated}/{self.total_target}, {rate:4.1f} img/s)")
            else:
                print(f"[{timestamp:6.1f}s] {message}")

            self.last_report = current_time

    def increment(self):
        """Increment the count of successfully generated images"""
        self.images_generated += 1

    def increment_error(self):
        """Increment the count of errors"""
        self.errors_count += 1

if __name__ == "__main__":
    print("=== Ledras Lament Scene Generation Pipeline ===")
    print()

    try:
        generator = LedrasSceneGenerator()

        # Parse CLI: `--subscenes` flag, remaining are scene IDs (default 1)
        subscene_mode = "--subscenes" in sys.argv
        args = [a for a in sys.argv[1:] if a != "--subscenes"]
        scene_ids = [int(a) for a in args] if args else [1]

        if subscene_mode:
            print(f"🎨 Generating ALL subscenes for scenes {scene_ids}...")
            scenes = generator.generate_subscene_images(scene_ids)
            total = sum(len(v) for v in scenes.values())
            print(f"\n✅ SUCCESS: {total} subscene images generated for scenes {scene_ids}")
        else:
            print(f"🎨 Generating scenes {scene_ids}...")
            scenes = generator.generate_specific_images(scene_ids, "intro")
            print(f"\n✅ SUCCESS: Scenes {scene_ids} generated successfully!")
            print(f"📊 Generated: {len(scenes)} scenes")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)