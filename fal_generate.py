#!/usr/bin/env python3
"""
Ledras Lament Scene Generator - CONSOLIDATED

This script generates images for Ledras Lament scenes using fal.ai API.
Combines ALL required parameters with multi-scene support.

User-Requested Parameters:
- guidance_scale: 3.5
- enable_safety_checker: True
- control_lora_strength: 0.7
- control_lora_image_url
- num_inference_steps: 28
- image_size: {"width": 1280, "height": 720}
"""

import json
import os
import requests
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

from fal_client import SyncClient
from utils import get_resolution, estimate_cost
from src.gateway import Gateway

__all__ = ["get_resolution", "estimate_cost"]


class LedrasConfig:
    def __init__(self):
        # Core configuration
        self.output_dir = "assets/generated"
        self.scenes_file = "data/sources/ledras_scenes_v7.json"

        # FALAI API parameters (validated against fal-ai/flux-control-lora-canny schema)
        self.fal_model = "fal-ai/flux-control-lora-canny"
        self.num_inference_steps = 28
        self.image_size = {"width": 1280, "height": 720}
        self.seed = 42
        self.subscene_variation_count = 2
        self.cultural_authenticity_level = "cypro_phoenician"
        self.ornamentation_allowed = False

        # Additional user-requested parameters
        self.guidance_scale = 3.5
        self.enable_safety_checker = True
        self.control_lora_strength = 0.7

        # Load from imagine-config.json if available
        self.load_imagine_config()

    def load_imagine_config(self):
        """Load configuration from imagine-config.json"""
        config_path = "imagine-config.json"
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)

            for key, value in config_data.items():
                setattr(self, key, value)

            print(f"✅ Configuration loaded from {config_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not load {config_path}: {e}")
            self.set_default_config()

    def set_default_config(self):
        """Set default configuration values"""
        print("✅ Default configuration applied")


class LedrasSceneGenerator:
    def __init__(self):
        self.config = LedrasConfig()
        self.setup_fal_client()

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

    def generate_image(self, prompt: str, scene_id: int, role: str) -> Optional[Dict[str, Any]]:
        """Generate a single image using fal.ai API with SyncClient"""
        try:
            print(f"🎨 Generating image: Scene {scene_id}, Role: {role}")
            print(f"   Prompt preview: {prompt[:100]}..." if len(prompt) > 100 else f"   Prompt: {prompt}")

            # Prepare fal.ai API parameters — validated against fal-ai/flux-control-lora-canny input schema
            fal_params = {
                "prompt": prompt,
                "control_lora_image_url": self.config.control_lora_image_url,
                "image_size": self.config.image_size,
                "seed": self.config.seed,
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

            if result and hasattr(result, 'images') and result.images:
                image_data = result.images[0]
                print(f"✅ Image generation successful for scene {scene_id}!")

                # Build deterministic file name and save image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scene-{scene_id:02d}_v{self.config.seed:03d}_{timestamp}.png"
                output_path = os.path.join(self.config.output_dir, filename)
                file_path = None

                if hasattr(image_data, 'url'):
                    try:
                        response = requests.get(image_data.url)
                        response.raise_for_status()
                        os.makedirs(self.config.output_dir, exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        print(f"✅ Image saved to: {output_path}")
                        file_path = output_path
                    except Exception as e:
                        print(f"⚠️  Failed to download image: {e}")

                return {
                    "scene_id": scene_id,
                    "role": role,
                    "prompt": prompt,
                    "image_data": image_data,
                    "generation_timestamp": datetime.now().isoformat(),
                    "model_used": self.config.fal_model,
                    "seed": self.config.seed,
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

        print(f"🎨 Starting image generation for scenes {scene_ids}, role: {role}")
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

    def save_prompts(self, output_path: str = "generated_prompts.json"):
        """Save generated prompts to JSON file"""
        try:
            prompts = self.generate_all_prompts()
            with open(output_path, 'w') as f:
                json.dump(prompts, f, indent=2)
            print(f"✅ Prompts saved to {output_path}")
        except Exception as e:
            print(f"❌ Error saving prompts: {e}")

    def validate_generated_prompts(self) -> Dict[str, Any]:
        """Check generated prompts have sufficient content"""
        try:
            prompts = self.generate_all_prompts()

            missing = []
            valid_count = 0

            for scene_id, roles in prompts.items():
                for role, prompt in roles.items():
                    if not prompt or len(prompt.strip()) < 10:
                        missing.append(f"Scene {scene_id}, Role {role}")
                    else:
                        valid_count += 1

            report = {
                'total_scenes': len(prompts),
                'scenes_with_prompts': valid_count,
                'validation_pass_rate': valid_count / max(len(prompts), 1) * 100 if prompts else 0,
                'missing_prompts': missing,
                'generated_scenes': list(prompts.keys())
            }

            print(f"✅ Validation complete: {report['validation_pass_rate']:.2f}% pass rate")
            return report

        except Exception as e:
            print(f"❌ Error validating prompts: {e}")
            return {'validation_pass_rate': 0.0, 'error': str(e)}

    def run_complete_pipeline(self, target_scenes: List[int], target_role: str = "intro"):
        """Run the complete pipeline for target scenes"""
        print("=" * 60)
        print("🚀 STARTING LEDRAS LAMENT PIPELINE")
        print("=" * 60)
        print(f"📽️  Target Scenes: {target_scenes}")
        print(f"🎭 Target Role: {target_role}")
        print()

        print("📝 Step 1: Generating prompts...")
        self.save_prompts()

        print()
        print("🎨 Step 2: Generating images...")
        generated = self.generate_specific_images(target_scenes, target_role)

        print()
        print("✅ Step 3: Pipeline completed!")
        print(f"📊 Generated: {len(generated)}/{len(target_scenes)} scenes")

        print()
        print("🔍 Step 4: Validating prompts...")
        validation = self.validate_generated_prompts()

        print()
        print("=" * 60)
        print("🎉 PIPELINE SUMMARY")
        print("=" * 60)
        print(f"✅ Total scenes generated: {len(generated)}")
        print(f"✅ Validation pass rate: {validation['validation_pass_rate']:.2f}%")
        print(f"✅ Model used: {self.config.fal_model}")
        print(f"✅ Control strength: {self.config.control_lora_strength}")
        print(f"✅ Cultural authenticity: {self.config.cultural_authenticity_level}")
        print("=" * 60)

        return generated

    def __call__(self):
        """Allow instance to be called as a function"""
        return self.run_complete_pipeline([5, 8], "intro")


if __name__ == "__main__":
    print("=== Ledras Lament Scene Generation Pipeline ===")
    print()

    try:
        gateway = Gateway()

        if not gateway.has_rights():
            print("❌ No available tokens. Please wait and try again.")
            exit(1)

        generator = LedrasSceneGenerator()

        # Accept scene IDs from CLI args (e.g. `python3 fal_generate.py 3 5`); default scene 6
        scene_ids = [int(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else [6]

        print(f"🎨 Generating scenes {scene_ids}...")
        scenes = generator.generate_specific_images(scene_ids, "intro")

        print()
        print(f"✅ SUCCESS: Scenes {scene_ids} generated successfully!")
        print(f"📊 Generated: {len(scenes)} scenes")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)