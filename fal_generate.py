#!/usr/bin/env python3
"""
Ledras Lament Scene Generator - Fixed
This script generates images for Ledras Lament scenes using fal.ai API.
FIXED VERSION with proper imports and API calls.
"""

import json
import os
import hashlib
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Fal client imports - FIXED
try:
    from fal_client import run as fal_run, __version__ as fal_version
    print(f"✅ fal_client version {fal_version} imported successfully")
except ImportError:
    print("❌ ERROR: fal_client not installed. Please install with: pip install fal-client")
    exit(1)

# --- Configuration ---

class LedrasConfig:
    def __init__(self):
        self.guideline_image = "stage/stage_v5_alphasky.png"
        self.output_dir = "assets/generated"
        self.scenes_file = "data/scenes/ledras_scenes_v6.json"
        
        # Initialize from imagine-config.json
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
        defaults = {
            "guideline_image": "stage/stage_v5_alphasky.png",
            "preprocess": "canny",
            "fal_model": "fal-ai/flux-control-lora-canny",
            "control_start": 0.0,
            "control_stop": 1.0,
            "fal_control_strength": 0.7,
            "num_inference_steps": 28,
            "output_dir": "assets/generated",
            "image_size": "1280x720",
            "seed": 42,
            "weathered_stone_texture": True,
            "subscene_variation_count": 2,
            "cultural_authenticity_level": "cypro_phoenician",
            "ornamentation_allowed": False,
            "scenes_file": "data/scenes/ledras_scenes_v6.json"
        }
        
        for key, value in defaults.items():
            setattr(self, key, value)
            
        print("✅ Default configuration applied")

# --- Scene Generator ---

class LedrasSceneGenerator:
    def __init__(self):
        self.config = LedrasConfig()
        
        # Setup API client with environment-based authentication
        self.setup_fal_client()

    def setup_fal_client(self):
        """Setup fal client with environment-based authentication"""
        self.api_key = os.environ.get('FAL_API_KEY')
        
        if not self.api_key:
            print("⚠️  WARNING: FAL_API_KEY not set. Image generation may fail.")
            print("   Set it using: export FAL_API_KEY='your-api-key'")
            return
            
        print("✅ FAL_API_KEY configured successfully")
        
        # For debugging: show key format (safely)
        if ':' in self.api_key:
            uuid_part, suffix_part = self.api_key.split(':', 1)
            print(f"   Key format: UUID ({len(uuid_part)} chars) + suffix ({len(suffix_part)} chars)")

    def generate_prompt(self, scene_id: int, role: str = "loop") -> str:
        """Generate prompt for specific scene and role"""
        try:
            with open(self.config.scenes_file, 'r') as f:
                scenes_data = json.load(f)
                
            scenes = scenes_data.get('scenes', [])
            
            for scene in scenes:
                if scene.get('id') == scene_id:
                    roles = scene.get('roles', {})
                    if role in roles:
                        prompt = roles[role]
                    elif 'intro' in roles:
                        prompt = roles['intro']
                    else:
                        prompt = scene.get('description', '')
                    
                    # Add metadata to prompt
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
                
            scenes = scenes_data.get('scenes', [])
            prompts = {}
            
            for scene in scenes:
                scene_id = scene.get('id')
                if not scene_id:
                    continue
                    
                scene_prompts = {}
                description = scene.get('description', '')
                
                # Generate intro prompt
                intro_metadata = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}] [intro]"
                scene_prompts['intro'] = f"{description} {intro_metadata}"
                
                # Generate loop prompt (simplified version)
                loop_metadata = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}] [loop]"
                scene_prompts['loop'] = f"{description} {loop_metadata}"
                
                prompts[scene_id] = scene_prompts
                
            return prompts
            
        except Exception as e:
            print(f"❌ Error generating all prompts: {e}")
            return {}

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

    def generate_image(self, prompt: str, scene_id: int, role: str) -> Optional[Dict[str, Any]]:
        """Generate a single image using fal.ai API"""
        if not hasattr(self, 'api_key') or not self.api_key:
            print(f"❌ No API key available for scene {scene_id}")
            return None
            
        try:
            print(f"🎨 Generating image: Scene {scene_id}, Role: {role}")
            print(f"   Prompt preview: {prompt[:100]}..." if len(prompt) > 100 else f"   Prompt: {prompt}")

            # Prepare fal.ai API parameters
            fal_params = {
                "image_size": self.config.image_size,
                "seed": self.config.seed,
                "num_inference_steps": self.config.num_inference_steps,
                "control_strength": self.config.fal_control_strength,
                "preprocess": self.config.preprocess,
                "guideline_image": self.config.guideline_image,
                "num_images": 1,
                "output_format": "png",
                "prompt": prompt
            }

            if self.config.weathered_stone_texture:
                fal_params["weathered_stone_texture"] = True

            print(f"🤖 Calling fal.run() API with model: {self.config.fal_model}")
            
            # Call fal.ai API
            result = fal_run(
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

    def generate_specific_images(self, scene_ids: List[int], role: str = "intro"):
        """Generate images for specific scenes and roles"""
        generated = {}

        print(f"🎨 Starting image generation for scenes {scene_ids}, role: {role}")
        print(f"📁 Output directory: {self.config.output_dir}")
        print(f"🤖 Using model: {self.config.fal_model}")
        print(f"🎯 Control strength: {self.config.fal_control_strength}")
        print(f"🌱 Cultural authenticity: {self.config.cultural_authenticity_level}")
        print()

        for scene_id in scene_ids:
            print(f"📸 Processing Scene {scene_id} ({role}):")

            prompts = self.generate_all_prompts()
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

    def run_complete_pipeline(self, target_scenes: List[int], target_role: str = "intro"):
        """Run the complete image generation pipeline"""
        try:
            print(f"🚀 Starting Ledras Lament Scene Generation Pipeline")
            print(f"🎯 Target: Scenes {target_scenes}, Role: {target_role}")
            print(f"🌍 Cultural context: {self.config.cultural_authenticity_level}")
            print(f"🤖 Model: {self.config.fal_model}")
            print()

            # Step 1: Setup environment
            print("📋 Step 1: Setting up environment...")
            self.setup_environment()

            # Step 2: Generate and validate prompts
            print("📝 Step 2: Generating and validating prompts...")
            prompt_report = self.validate_generated_prompts()
            print(f"✅ Validation Pass Rate: {prompt_report['validation_summary']['validation_pass_rate']:.2f}%")

            # Step 3: Save prompts
            self.save_prompts()
            print("💾 Prompts saved to generated_prompts.json")

            # Step 4: Generate images for target scenes
            print(f"🎨 Step 4: Generating images for scenes {target_scenes}...")
            generated_images = self.generate_specific_images(target_scenes, target_role)

            # Step 5: Save metadata
            metadata = {
                "generation_timestamp": datetime.now().isoformat(),
                "scenes_generated": list(generated_images.keys()),
                "target_scenes": target_scenes,
                "target_role": target_role,
                "total_images": len(generated_images),
                "config_used": {
                    "model": self.config.fal_model,
                    "control_strength": self.config.fal_control_strength,
                    "preprocess": self.config.preprocess,
                    "seed": self.config.seed,
                    "cultural_authenticity": self.config.cultural_authenticity_level,
                    "weathered_stone_texture": self.config.weathered_stone_texture
                },
                "validation_report": prompt_report
            }

            metadata_path = os.path.join(self.config.output_dir, "generation_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            print(f"📊 Generation metadata saved: {metadata_path}")
            print()
            print("🎉 SUCCESS: Ledras Lament Scene Generation Complete!")
            print(f"✅ Generated {len(generated_images)} scenes: {list(generated_images.keys())}")
            print(f"📁 Check {self.config.output_dir}/ for output files")

        except Exception as e:
            print(f"❌ FATAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            exit(1)

    def setup_environment(self):
        """Setup output directory and verify API key"""
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        self.api_key = os.environ.get('FAL_API_KEY')
        
        if not self.api_key:
            print("⚠️  WARNING: FAL_API_KEY not set. Image generation may fail.")
            print("   Set it using: export FAL_API_KEY='your-api-key'")
        else:
            print("✅ FAL_API_KEY configured successfully")

if __name__ == "__main__":
    # Create generator instance
    gen = LedrasSceneGenerator()
    
    # Run complete pipeline for scenes 5 and 8 intro
    gen.run_complete_pipeline([5, 8], "intro")
