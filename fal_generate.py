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

import json
import os
import random
import requests
import sys
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from fal_client import SyncClient, upload_file

from utils import get_resolution, estimate_cost


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

    def setup_fal_client(self):
        """Setup fal client with environment-based authentication"""
        self.api_key = os.environ.get('FAL_API_KEY')

        if not self.api_key:
            print("⚠️  WARNING: FAL_API_KEY not set. Image generation may fail.")
            print("   Set it using: export FAL_API_KEY='your-api-key'")
            self.client = SyncClient()
        else:
            print("✅ FAL_API_KEY configured successfully")
            self.client = SyncClient(key=self.api_key)

        if hasattr(self, 'api_key') and self.api_key and ':' in self.api_key:
            uuid_part, suffix_part = self.api_key.split(':', 1)
            print(f"   Key format: UUID ({len(uuid_part)} chars) + suffix ({len(suffix_part)} chars)")

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

    def generate_prompt(self, scene_id: int, role: str = "loop") -> str:
        """Generate prompt for specific scene and role."""
        try:
            with open(self.config.scenes_file, 'r') as f:
                scenes_data = json.load(f)
            scene = next(
                (s for s in scenes_data.get('scenes', []) if s.get('id') == scene_id),
                None,
            )
            if scene is None:
                print(f"⚠️  Scene {scene_id} not found")
                return ""
            return self._build_prompt(scene, role)
        except Exception as e:
            print(f"❌ Error generating prompt for scene {scene_id}: {e}")
            return ""

    def generate_all_prompts(self) -> Dict[int, Dict[str, str]]:
        """Generate prompts for all scenes and roles."""
        try:
            with open(self.config.scenes_file, 'r') as f:
                scenes_data = json.load(f)
            prompts = {}
            for scene in scenes_data.get('scenes', []):
                scene_id = scene.get('id')
                if not scene_id:
                    continue
                prompts[scene_id] = {
                    'intro': self._build_prompt(scene, 'intro'),
                    'loop': self._build_prompt(scene, 'loop'),
                }
            return prompts
        except Exception as e:
            print(f"❌ Error generating all prompts: {e}")
            return {}

    def generate_image(self, prompt: str, scene_id: int, role: str, *,
                       sub_label: str = "") -> Optional[Dict[str, Any]]:
        """Generate a single image using fal.ai API with SyncClient"""
        request_seed = random.randint(1, 2**31 - 1)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            print(f"🎨 Generating image: Scene {scene_id}, Role: {role}")
            print(f"   Prompt preview: {prompt[:100]}..." if len(prompt) > 100 else f"   Prompt: {prompt}")

            # Upload local control image to fal.ai storage
            control_image_path = self.config.control_image_path
            if not control_image_path:
                print("❌ ERROR: control_image_path not configured")
                return None
            import os
            if not os.path.exists(control_image_path):
                print(f"❌ ERROR: Control image not found at {control_image_path}")
                return None
            print(f"📤 Uploading control image: {control_image_path}")
            control_lora_image_url = upload_file(control_image_path)
            print(f"✅ Control image uploaded: {control_lora_image_url}")

            # Prepare fal.ai API parameters — validated against fal-ai/flux-control-lora-canny input schema
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
                "control_lora_strength": self.config.control_lora_strength,
            }

            print(f"🤖 Calling SyncClient.run() API with model: {self.config.fal_model}")

            # Use the SyncClient to call the API
            result = self.client.run(
                application=self.config.fal_model,
                arguments=fal_params
            )

            if result:
                # Handle both dict-style (fal SDK) and attribute-style responses
                images = (result.get("images", []) if isinstance(result, dict)
                          else (result.images if hasattr(result, 'images') else []))
                if images:
                    image_data = images[0]
                    print(f"✅ Image generation successful for scene {scene_id}!")

                    # Build deterministic file name and save image
                    image_seed = request_seed
                    sub_part = f"_{sub_label}" if sub_label else ""
                    filename = f"scene-{scene_id:02d}{sub_part}_v{image_seed:03d}_{timestamp}.png"
                    output_path = os.path.join(self.config.output_dir, filename)
                    file_path = None

                    # Handle both dict and attribute-style image_data
                    image_url = (image_data.get("url") if isinstance(image_data, dict)
                                 else (image_data.url if hasattr(image_data, 'url') else None))
                    if image_url:
                        # Log URL before download — recoverable if download fails
                        log_path = os.path.join(self.config.output_dir, "generation_log.jsonl")
                        log_entry = {
                            "scene_id": scene_id, "seed": image_seed,
                            "sub_label": sub_label, "role": role,
                            "image_url": image_url, "timestamp": timestamp,
                            "filename": filename,
                        }
                        try:
                            os.makedirs(self.config.output_dir, exist_ok=True)
                            with open(log_path, 'a') as f:
                                f.write(json.dumps(log_entry) + "\n")
                        except Exception as e:
                            print(f"⚠️  Failed to write generation log: {e}")

                        # Download with bounded exponential backoff retry
                        for attempt in range(3):
                            try:
                                response = requests.get(image_url, timeout=30)
                                response.raise_for_status()
                                break
                            except Exception as e:
                                if attempt == 2:  # Last attempt
                                    print(f"⚠️  Failed to download image after {3} attempts: {e}")
                                    raise  # Propagate the error
                                
                                # Calculate exponential backoff delay
                                delay = min(0.5 * (2 ** attempt), 5.0)  # Max 5 second delay
                                print(f"⚠️  Download failed (attempt {attempt + 1}), retrying in {delay:.1f}s: {e}")
                                time.sleep(delay)

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
            else:
                print(f"⚠️  No images returned from API for scene {scene_id}")
                return None

        except Exception as e:
            print(f"❌ Image generation failed for scene {scene_id}: {str(e)}")
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
                generated[scene_id] = image_info
                print(f"✅ Scene {scene_id} generated successfully")
            else:
                print(f"❌ Failed to generate scene {scene_id}")

            print()

        return generated

    def generate_subscene_images(self, scene_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Generate images for all subscenes of given scenes."""
        try:
            with open(self.config.scenes_file, 'r') as f:
                scenes_data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading scenes: {e}")
            return {}

        total_subs = 0
        for scene_id in scene_ids:
            scene = next((s for s in scenes_data.get('scenes', [])
                          if s.get('id') == scene_id), None)
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
            scene = next((s for s in scenes_data.get('scenes', [])
                          if s.get('id') == scene_id), None)
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
                    if scene_id not in results:
                        results[scene_id] = {}
                    results[scene_id][sub_name] = info
                    print(f"  ✅ Subscene {sub_id} generated")
                else:
                    print(f"  ❌ Subscene {sub_id} failed")

            print()

        print(f"✅ Generated {sum(len(v) for v in results.values())} subscene images")
        return results

    def run_complete_pipeline(self, target_scenes: List[int], target_role: str = "intro"):
        """Run the complete pipeline for target scenes"""
        print("=" * 60)
        print("🚀 STARTING LEDRAS LAMENT PIPELINE")
        print("=" * 60)
        print(f"📽️  Target Scenes: {target_scenes}")
        print(f"🎭 Target Role: {target_role}")
        print()

        print("🎨 Generating images...")
        generated = self.generate_specific_images(target_scenes, target_role)

        print()
        print("✅ Pipeline completed!")
        print(f"📊 Generated: {len(generated)}/{len(target_scenes)} scenes")

        print()
        print("=" * 60)
        print("🎉 PIPELINE SUMMARY")
        print("=" * 60)
        print(f"✅ Total scenes generated: {len(generated)}")
        print(f"✅ Model used: {self.config.fal_model}")
        print(f"✅ Control strength: {self.config.control_lora_strength}")
        print(f"✅ Cultural authenticity: {self.config.cultural_authenticity_level}")
        print("=" * 60)

        return generated

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
        
        # Report every 5 seconds, or if force=True
        if self.verbose or force or (current_time - self.last_report) >= 5:
            timestamp = current_time - self.start_time
            
            # Simple progress indicator
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
    
    def finish(self, success_count, total):
        """Print final progress summary"""
        elapsed = time.time() - self.start_time
        rate = success_count / elapsed if elapsed > 0 else 0
        efficiency = (success_count / total * 100) if total > 0 else 0
        
        print(f"
{'='*70}")
        print(f"🎉 PIPELINE COMPLETED")
        print(f"{'='*70}")
        print(f"⏱️  Total runtime: {elapsed:8.1f} seconds")
        print(f"📊 Generation rate: {rate:8.2f} images/second")
        print(f"✅ Success: {success_count:3d}/{total} ({efficiency:5.1f}%)")
        if self.errors_count > 0:
            print(f"❌ Errors: {self.errors_count}")
        print(f"{'='*70}")
        """Run the complete pipeline for target scenes"""
        print("=" * 60)
        print("🚀 STARTING LEDRAS LAMENT PIPELINE")
        print("=" * 60)
        print(f"📽️  Target Scenes: {target_scenes}")
        print(f"🎭 Target Role: {target_role}")
        print()

        print("🎨 Generating images...")
        generated = self.generate_specific_images(target_scenes, target_role)

        print()
        print("✅ Pipeline completed!")
        print(f"📊 Generated: {len(generated)}/{len(target_scenes)} scenes")

        print()
        print("=" * 60)
        print("🎉 PIPELINE SUMMARY")
        print("=" * 60)
        print(f"✅ Total scenes generated: {len(generated)}")
        print(f"✅ Model used: {self.config.fal_model}")
        print(f"✅ Control strength: {self.config.control_lora_strength}")
        print(f"✅ Cultural authenticity: {self.config.cultural_authenticity_level}")
        print("=" * 60)

        return generated


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

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)