#!/usr/bin/env python3
"""
Ledras Lament Scene Generator - CONSOLIDATED

This script generates images for Ledras Lament scenes using fal.ai API.
Combines ALL required parameters with multi-scene support.

User-Requested Parameters:
- guidance_scale: 3.5
- enable_safety_checker: True
- control_lora_strength: 0.6
- control_start: 0.0
- control_stop: 1.0
- control_lora_image_url
- num_inference_steps: 28
- image_size: 1280x720
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Fal client imports
from fal_client import SyncClient

# Import shared utilities
from utils import get_resolution, estimate_cost
# Re-export utilities for test compatibility
__all__ = ["get_resolution", "estimate_cost"]

# ====================================================
# CONFIGURATION CLASS (from src/fal_generate_fixed.py)
# ====================================================

class LedrasConfig:
    def __init__(self):
        # Core configuration parameters (defaults – overridden by imagine-config.json)
        self.guideline_image = "stage/stage_v6_alphasky.png"
        self.output_dir = "assets/generated"
        self.scenes_file = "data/scenes/ledras_scenes_v7.json"

        # API defaults – may be overridden by config file
        self.preprocess = "canny"
        self.fal_model = "fal-ai/flux-control-lora-canny"
        self.control_start = 0.0
        self.control_stop = 1.0
        self.fal_control_strength = 0.6
        self.num_inference_steps = 28
        self.image_size = "1280x720"
        self.seed = 42
        self.weathered_stone_texture = True
        self.subscene_variation_count = 2
        self.cultural_authenticity_level = "cypro_phoenician"
        self.ornamentation_allowed = False

        # Load overrides from imagine-config.json if present
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
        """Apply built‑in defaults when imagine-config.json is missing.
        Mirrors the constructor defaults defined above.
        """
        # All defaults already set in __init__; just inform the user.
        print("✅ Default configuration applied (imagine-config.json not found)")

# ====================================================
# SCENE GENERATOR CLASS (from src/fal_generate_fixed.py)
# ====================================================

class LedrasSceneGenerator:
    def __init__(self):
        self.config = LedrasConfig()
        self.setup_fal_client()
        self._scenes_cache = None  # cache for scene data

    def setup_fal_client(self):
        """Setup fal client with environment-based authentication"""
        self.api_key = os.environ.get('FAL_API_KEY')

        if not self.api_key:
            raise RuntimeError("FAL_API_KEY environment variable is required for image generation.")
        print("✅ FAL_API_KEY configured successfully")
        self.client = SyncClient(key=self.api_key)

        if hasattr(self, 'api_key') and self.api_key and ':' in self.api_key:
            uuid_part, suffix_part = self.api_key.split(':', 1)
            print(f"   Key format: UUID ({len(uuid_part)} chars) + suffix ({len(suffix_part)} chars)")

    def generate_prompt(self, scene_id: int, role: str = "loop") -> str:
        """Generate prompt for a specific scene and role using cached scenes."""
        try:
            scenes = self._load_scenes()
            for scene in scenes:
                if scene.get('id') == scene_id:
                    roles = scene.get('roles', {})
                    if role in roles:
                        prompt = roles[role]
                    elif 'intro' in roles:
                        prompt = roles['intro']
                    else:
                        prompt = scene.get('description', '')
                    metadata = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}]"
                    return f"{prompt} {metadata}"
            print(f"⚠️  Scene {scene_id} not found")
            return ""
        except Exception as e:
            print(f"❌ Error generating prompt for scene {scene_id}: {e}")
            return ""

    def generate_all_prompts(self) -> Dict[int, Dict[str, str]]:
        """Generate prompts for all scenes and roles using cached data."""
        try:
            scenes = self._load_scenes()
            prompts = {}
            for scene in scenes:
                scene_id = scene.get('id')
                if not scene_id:
                    continue
                description = scene.get('description', '')
                meta_base = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}]"
                prompts[scene_id] = {
                    'intro': f"{description} {meta_base} [intro]",
                    'loop': f"{description} {meta_base} [loop]",
                }
            return prompts
        except Exception as e:
            print(f"❌ Error generating all prompts: {e}")
            return {}

    def generate_specific_images(self, scene_ids: List[int], role: str = "intro"):
        """Generate images for specific scenes and roles using precomputed prompts."""
        generated = {}

        print(f"🎨 Starting image generation for scenes {scene_ids}, role: {role}")
        print(f"📁 Output directory: {self.config.output_dir}")
        print(f"🤖 Using model: {self.config.fal_model}")
        print(f"🎯 Control strength: {self.config.fal_control_strength}")
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

    def generate_image(self, prompt: str, scene_id: int, role: str) -> Optional[Dict[str, Any]]:
        """Generate a single image using fal.ai API with SyncClient"""
        try:
            print(f"🎨 Generating image: Scene {scene_id}, Role: {role}")
            print(f"   Prompt preview: {prompt[:100]}..." if len(prompt) > 100 else f"   Prompt: {prompt}")

            # Prepare fal.ai API parameters with ALL user-requested values
            fal_params = {
                "image_size": self.config.image_size,
                "seed": self.config.seed,
                "num_inference_steps": self.config.num_inference_steps,
                "control_strength": self.config.fal_control_strength,
                "preprocess": self.config.preprocess,
                "guideline_image": self.config.guideline_image,
                "num_images": 1,
                "output_format": "png",
                "prompt": prompt,
                # User-requested parameters
                "guidance_scale": self.config.guidance_scale,
                "enable_safety_checker": self.config.enable_safety_checker,
                "control_lora_strength": self.config.control_lora_strength,
                "control_start": self.config.control_start,
                "control_stop": self.config.control_stop,
            }

            if self.config.weathered_stone_texture:
                fal_params["weathered_stone_texture"] = True

            print(f"🤖 Calling SyncClient.run() API with model: {self.config.fal_model}")

            # Use the SyncClient to call the API
            result = self.client.run(
                application=self.config.fal_model,
                arguments=fal_params
            )

            if result and hasattr(result, 'images') and result.images:
                image_data = result.images[0]
                print(f"✅ Image generation successful for scene {scene_id}!")
                return {
                    "scene_id": scene_id,
                    "role": role,
                    "prompt": prompt,
                    "image_data": image_data,
                    "generation_timestamp": datetime.now().isoformat(),
                    "model_used": self.config.fal_model,
                    "seed": self.config.seed
                }
            else:
                print(f"⚠️  No images returned from API for scene {scene_id}")
                return None

        except Exception as e:
            print(f"❌ Image generation failed for scene {scene_id}: {str(e)}")
            return None

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
        """Validate generated prompts"""
        try:
            prompts = self.generate_all_prompts()

            report = {
                'total_scenes': len(prompts),
                'scenes_with_prompts': 0,
                'validation_pass_rate': 0.0,
                'missing_prompts': [],
                'generated_scenes': list(prompts.keys())
            }

            for scene_id, roles in prompts.items():
                scene_valid = True

                for role, prompt in roles.items():
                    if not prompt or len(prompt.strip()) < 10:
                        scene_valid = False
                        report['missing_prompts'].append(f"Scene {scene_id}, Role {role}")

                if scene_valid:
                    report['scenes_with_prompts'] += 1

            if report['total_scenes'] > 0:
                report['validation_pass_rate'] = (report['scenes_with_prompts'] /
                                                 report['total_scenes']) * 100

            print(f"✅ Validation complete: {report['validation_pass_rate']:.2f}% pass rate")
            return report

        except Exception as e:
            print(f"❌ Error validating prompts: {e}")
            return {
                'validation_pass_rate': 0.0,
                'error': str(e)
            }

    def run_complete_pipeline(self, target_scenes: List[int], target_role: str = "intro"):
        """Run the complete pipeline for target scenes"""
        print("=" * 60)
        print("🚀 STARTING LEDRAS LAMENT PIPELINE")
        print("=" * 60)
        print(f"📽️  Target Scenes: {target_scenes}")
        print(f"🎭 Target Role: {target_role}")
        print()

        # Generate prompts first
        print("📝 Step 1: Generating prompts...")
        self.save_prompts()

        print()
        print("🎨 Step 2: Generating images...")
        generated = self.generate_specific_images(target_scenes, target_role)

        print()
        print("✅ Step 3: Pipeline completed!")
        print(f"📊 Generated: {len(generated)}/{len(target_scenes)} scenes")

        # Validate prompts
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
        print(f"✅ Control strength: {self.config.fal_control_strength}")
        print(f"✅ Cultural authenticity: {self.config.cultural_authenticity_level}")
        print("=" * 60)

        return generated

    def __call__(self):
        """Allow instance to be called as a function"""
        return self.run_complete_pipeline([5, 8], "intro")

# ====================================================
# MAIN EXECUTION
# ====================================================

if __name__ == "__main__":
    print("=== Ledras Lament Scene Generation Pipeline ===")

    try:
        generator = LedrasSceneGenerator()
        result = generator()

        if result:
            print(f"🎉 SUCCESS: Pipeline completed with {len(result)} scenes generated")
            exit(0)
        else:
            print("❌ FAILURE: Pipeline produced no results")
            exit(1)

    except Exception as e:
        print(f"❌ FATAL ERROR: {str(e)}")
        exit(1)