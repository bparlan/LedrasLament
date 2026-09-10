#!/usr/bin/env python3
"""
Ledras Lament Scene Generator - MINIMAL VERSION

This script generates images for Ledras Lament scenes using fal.ai API.
Supports prelude-intro-moments.json structure.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Fal client imports
from fal_client import SyncClient

# ====================================================
# CONFIGURATION CLASS
# ====================================================

class LedrasConfig:
    def __init__(self):
        # Core configuration parameters
        self.guideline_image = "stage_rehersals.png"
        self.output_dir = "assets/generated/ledras-premier/prelude-moments/"
        self.scenes_file = "data/scenes/prelude-intro-moments.json"
        
        # FALAI API parameters - ALL USER-REQUESTED VALUES
        self.preprocess = "canny"
        self.fal_model = "fal-ai/flux-control-lora-canny"
        self.control_start = 0.0
        self.control_stop = 1.0
        self.fal_control_strength = 0.6
        self.num_inference_steps = 28
        self.image_size = {"width": 1280, "height": 704}
        self.seed = 42
        self.weathered_stone_texture = True
        self.subscene_variation_count = 2
        self.cultural_authenticity_level = "cypro_phoenician"
        self.ornamentation_allowed = False

        # Additional user-requested parameters
        self.guidance_scale = 3.5
        self.enable_safety_checker = True
        self.control_lora_strength = 0.6
        self.control_lora_image_url = "assets/control_images/stage_rehersals.png"
        
        # Load from imagine-config.json if available
        self.load_imagine_config()

    def load_imagine_config(self):
        """Load configuration from imagine-config.json"""
        config_path = "imagine-config.json"
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)

            for key, value in config_data.items():
                if key in ['guideline_image', 'output_dir', 'scenes_file', 
                          'preprocess', 'fal_model', 'control_start', 'control_stop',
                          'fal_control_strength', 'num_inference_steps', 'image_size',
                          'seed', 'weathered_stone_texture', 'subscene_variation_count',
                          'cultural_authenticity_level', 'ornamentation_allowed',
                          'guidance_scale', 'enable_safety_checker', 'control_lora_strength',
                          'control_lora_image_url']:
                    setattr(self, key, value)

            print(f"✅ Configuration loaded from {config_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not load {config_path}: {e}")
            self.set_default_config()

    def set_default_config(self):
        """Set default configuration values"""
        print("✅ Default configuration applied")

# ====================================================
# SCENE GENERATOR CLASS
# ====================================================

class LedrasSceneGenerator:
    def __init__(self):
        self.config = LedrasConfig()
        self.setup_fal_client()

    def setup_fal_client(self):
        """Setup fal client with environment-based authentication"""
        self.api_key = os.environ.get('FAL_KEY')

        if not self.api_key:
            print("⚠️  WARNING: FAL_KEY not set. Image generation may fail.")
            print("   Set it using: export FAL_KEY='your-api-key'")
            self.client = SyncClient()
        else:
            print("✅ FAL_KEY configured successfully")
            self.client = SyncClient(key=self.api_key)

    def generate_prompt(self, scene_id: int, role: str = "loop") -> str:
        """Generate prompt for specific scene and role"""
        try:
            with open(self.config.scenes_file, 'r') as f:
                scenes_data = json.load(f)

            # Handle both structures: scenes as dict with 'scenes' key, or scenes list directly
            if isinstance(scenes_data, dict) and 'scenes' in scenes_data:
                scenes = scenes_data['scenes']
            elif isinstance(scenes_data, list):
                scenes = scenes_data
            else:
                print(f"❌ Unexpected scenes data structure")
                return ""

            for scene in scenes:
                if isinstance(scene, dict) and scene.get('id') == scene_id:
                    # For prelude-intro-moments.json, use the description field directly
                    prompt = scene.get('description', '')

                    metadata = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}]"
                    return f"{prompt} {metadata}"

            print(f"⚠️  Scene {scene_id} not found")
            return ""

        except Exception as e:
            print(f"❌ Error generating prompt for scene {scene_id}: {e}")
            return ""

    def generate_all_prompts(self) -> Dict[int, Dict[str, str]]:
        """Generate prompts for all scenes and roles"""
        try:
            with open(self.config.scenes_file, 'r') as f:
                scenes_data = json.load(f)

            # Handle both structures: scenes as dict with 'scenes' key, or scenes list directly
            if isinstance(scenes_data, dict) and 'scenes' in scenes_data:
                scenes = scenes_data['scenes']
            elif isinstance(scenes_data, list):
                scenes = scenes_data
            else:
                print(f"❌ Unexpected scenes data structure")
                return {}

            prompts = {}

            for scene in scenes:
                if not isinstance(scene, dict):
                    continue

                scene_id = scene.get('id')
                if not scene_id:
                    continue

                scene_prompts = {}
                description = scene.get('description', '')

                # Generate intro prompt
                intro_metadata = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}] [intro]"
                scene_prompts['intro'] = f"{description} {intro_metadata}"

                # Generate loop prompt
                loop_metadata = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}] [loop]"
                scene_prompts['loop'] = f"{description} {loop_metadata}"

                prompts[scene_id] = scene_prompts

            return prompts

        except Exception as e:
            print(f"❌ Error generating all prompts: {e}")
            return {}

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
                "control_lora_image_url": self.config.control_lora_image_url,
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

            return {
                "scene_id": scene_id,
                "role": role,
                "prompt": prompt,
                "image_data": image_data,
                "generation_timestamp": datetime.now().isoformat(),
                "model_used": self.config.fal_model,
                "seed": self.config.seed,
            }

        except Exception as e:
            print(f"❌ ERROR: Image generation failed for scene {scene_id}: {e}")
            import traceback
            traceback.print_exc()
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

        return generated

    def __call__(self):
        """Main entry point - generate all intro scenes"""
        print("=== Ledras Lament Scene Generation Pipeline ===")
        print()

        try:
            # Generate all scenes for prelude-intro-moments.json
            scene_ids = [1, 2, 3, 4, 5, 6, 7]  # All scenes from prelude-intro-moments.json
            
            print(f"🎨 Generating scenes {scene_ids}...")
            scenes = self.generate_specific_images(scene_ids, "intro")
            
            print(f"\n✅ SUCCESS: Scenes {scene_ids} generated successfully!")
            print(f"📊 Generated: {len(scenes)} scenes")
            
            return scenes

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            exit(1)

# ====================================================
# MAIN EXECUTION
# ====================================================

if __name__ == "__main__":
    generator = LedrasSceneGenerator()
    scenes = generator()
