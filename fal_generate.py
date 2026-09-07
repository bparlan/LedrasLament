#!/usr/bin/env python3
"""
Ledras Lament Scene Generator - Deterministic Modular Edition

This script generates images for Ledras Lament scenes using fal.ai API.
Designed for deterministic, token-efficient generation of any scene/subscene.

User-Requested Parameters:
- guidance_scale: 3.5
- enable_safety_checker: True
- control_lora_strength: 0.6
- control_start: 0.0
- control_stop: 1.0
- image_size: 1280x720
- num_inference_steps: 28
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from fal_client import SyncClient
from src.gateway import Gateway
from enum import Enum
from dataclasses import dataclass
from contextlib import contextmanager
class GenerationRole(Enum):
    """Enumeration of valid generation roles"""
    INTRO = "intro"
    LOOP = "loop"
    OUTRO = "outro"
@dataclass
class SceneConfig:
    """Configuration for a specific scene"""
    scene_id: int
    name: str
    description: str
    seed: int
    subscenes: List[Dict[str, Any]] = None
@dataclass
class GenerationRequest:
    """Request for image generation"""
    scene_id: int
    role: str = "intro"
    subscene_id: Optional[int] = None
@dataclass
class GenerationResult:
    """Result of image generation"""
    success: bool
    scene_id: int
    role: str
    subscene_id: Optional[int]
    prompt: str
    image_data: Any = None
    error_message: Optional[str] = None
    timestamp: str = ""
    model_used: str = ""
    seed: int = 42
class LedrasConfig:
    """Configuration for Ledras Lament generation"""

    def __init__(self):
        # Core configuration parameters
        self.guideline_image = "stage/stage_v6_alphasky.png"
        self.output_dir = "assets/generated"
        self.scenes_file = "data/sources/ledras_scenes_v7.json"

        # FALAI API parameters - ALL USER-REQUESTED VALUES
        self.preprocess = "canny"
        self.fal_model = "fal-ai/flux-control-lora-canny"
        self.control_start = 0.0
        self.control_stop = 1.0
        self.fal_control_strength = 0.7
        self.num_inference_steps = 28
        self.image_size = "1280x720"
        self.seed = 42
        self.weathered_stone_texture = True
        self.subscene_variation_count = 2
        self.cultural_authenticity_level = "cypro_phoenician"
        self.ornamentation_allowed = False

        # Additional user-requested parameters
        self.guidance_scale = 3.5
        self.enable_safety_checker = True
        self.control_lora_strength = 0.6

    def load_imagine_config(self):
        """Load configuration from imagine-config.json"""
        config_path = "imagine-config.json"
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)

            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            print(f"✅ Configuration loaded from {config_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not load {config_path}: {e}")
class GatewayManager:
    """Manage gateway token allocation"""

    def __init__(self, initial_rights: int = 1):
        self.gateway = Gateway()

    def has_rights(self, n: int = 1) -> bool:
        """Check if we have rights for n generations"""
        return self.gateway.has_rights(n)

    def deduct(self, n: int = 1) -> int:
        """Deduct n rights and return remaining"""
        return self.gateway.deduct(n)

    def get_status(self) -> Dict[str, Any]:
        """Get current gateway status"""
        return self.gateway.get_status()
class SceneLoader:
    """Load scene configurations from JSON"""

    def __init__(self, config: LedrasConfig):
        self.config = config
        self.scenes: Dict[int, SceneConfig] = {}
        self._load_scenes()

    def _load_scenes(self):
        """Load scenes from JSON file"""
        try:
            with open(self.config.scenes_file, 'r') as f:
                scenes_data = json.load(f)

            scenes_data = scenes_data.get('scenes', [])
            print(f"✅ Loaded {len(scenes_data)} scenes from {self.config.scenes_file}")

            for scene_data in scenes_data:
                scene_id = scene_data.get('id')
                if scene_id:
                    scene = SceneConfig(
                        scene_id=scene_id,
                        name=scene_data.get('name', f"Scene {scene_id}"),
                        description=scene_data.get('description', ''),
                        seed=scene_data.get('seed', self.config.seed),
                        subscenes=scene_data.get('subscenes', [])
                    )
                    self.scenes[scene_id] = scene

        except Exception as e:
            print(f"❌ Error loading scenes from {self.config.scenes_file}: {e}")

    def get_scene(self, scene_id: int) -> Optional[SceneConfig]:
        """Get scene configuration by ID"""
        return self.scenes.get(scene_id)

    def get_all_scene_ids(self) -> List[int]:
        """Get all scene IDs"""
        return list(self.scenes.keys())

    def get_all_subscenes(self, scene_id: int) -> List[Dict[str, Any]]:
        """Get all subsences for a scene"""
        scene = self.scenes.get(scene_id)
        if scene:
            return scene.subscenes
        return []
class PromptGenerator:
    """Generate prompts for scenes and subsences"""

    def __init__(self, config: LedrasConfig):
        self.config = config

    def generate_prompt(self, scene_id: int, role: str = "intro", subscene_id: Optional[int] = None) -> str:
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

                    metadata = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}]"
                    if subscene_id:
                        metadata += f" [subscene:{subscene_id}]"
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

                # Generate loop prompt
                loop_metadata = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}] [loop]"
                scene_prompts['loop'] = f"{description} {loop_metadata}"

                # Generate outro prompt
                outro_metadata = f"[seed:{scene.get('seed', self.config.seed)}] [team:{self.config.cultural_authenticity_level}] [outro]"
                scene_prompts['outro'] = f"{description} {outro_metadata}"

                prompts[scene_id] = scene_prompts

            return prompts

        except Exception as e:
            print(f"❌ Error generating all prompts: {e}")
            return {}
class LedrasSceneGenerator:
    """Main scene generator class"""

    def __init__(self):
        self.config = LedrasConfig()
        self.gateway_manager = GatewayManager()
        self.scene_loader = SceneLoader(self.config)
        self.prompt_generator = PromptGenerator(self.config)
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
            # CORRECT: Create client with API key when available
            self.client = SyncClient(key=self.api_key)

        if hasattr(self, 'api_key') and self.api_key and ':' in self.api_key:
            uuid_part, suffix_part = self.api_key.split(':', 1)
            print(f"   Key format: UUID ({len(uuid_part)} chars) + suffix ({len(suffix_part)} chars)")

    def generate_prompt(self, scene_id: int, role: str = "intro", subscene_id: Optional[int] = None) -> str:
        """Generate prompt for specific scene and role"""
        return self.prompt_generator.generate_prompt(scene_id, role, subscene_id)

    def generate_image(self, prompt: str, scene_id: int, role: str, subscene_id: Optional[int] = None) -> Optional[GenerationResult]:
        """Generate a single image using fal.ai API with SyncClient"""
        try:
            print(f"🎨 Generating image: Scene {scene_id}, Role: {role}, Subscene: {subscene_id}")
            print(f"   Prompt preview: {prompt[:100]}..." if len(prompt) > 100 else f"   Prompt: {prompt}")

            # Prepare fal.ai API parameters with ALL user-requested values
            fal_params = {
                "image_size": self.config.image_size,
                "seed": self.config.seed,
                "num_inference_steps": self.config.num_inference_steps,
                "control_strength": self.config.fal_control_strength,
                "preprocess": self.config.preprocess,
                "control_lora_image_url": self.config.guideline_image,  # FIXED: use correct parameter name
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
                return GenerationResult(
                    success=True,
                    scene_id=scene_id,
                    role=role,
                    subscene_id=subscene_id,
                    prompt=prompt,
                    image_data=image_data,
                    timestamp=datetime.now().isoformat(),
                    model_used=self.config.fal_model,
                    seed=self.config.seed
                )
            else:
                print(f"⚠️  No images returned from API for scene {scene_id}")
                return GenerationResult(
                    success=False,
                    scene_id=scene_id,
                    role=role,
                    subscene_id=subscene_id,
                    prompt=prompt,
                    error_message="No images returned from API",
                    timestamp=datetime.now().isoformat(),
                    model_used=self.config.fal_model,
                    seed=self.config.seed
                )

        except Exception as e:
            print(f"❌ Image generation failed for scene {scene_id}: {str(e)}")
            return GenerationResult(
                success=False,
                scene_id=scene_id,
                role=role,
                subscene_id=subscene_id,
                prompt=prompt,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
                model_used=self.config.fal_model,
                seed=self.config.seed
            )

    def generate_specific_images(self, requests: List[GenerationRequest]) -> List[GenerationResult]:
        """Generate images for specific scene and role requests"""
        results = []

        print(f"🎨 Starting image generation for {len(requests)} requests")
        print(f"📁 Output directory: {self.config.output_dir}")
        print(f"🤖 Using model: {self.config.fal_model}")
        print(f"🎯 Control strength: {self.config.fal_control_strength}")
        print(f"🌱 Cultural authenticity: {self.config.cultural_authenticity_level}")
        print()

        for request in requests:
            print(f"📸 Processing Scene {request.scene_id} ({request.role}) Subscene: {request.subscene_id}")

            # Check if we have rights
            if not self.gateway_manager.has_rights(1):
                print(f"⚠️  No gateway rights available for scene {request.scene_id}")
                results.append(GenerationResult(
                    success=False,
                    scene_id=request.scene_id,
                    role=request.role,
                    subscene_id=request.subscene_id,
                    prompt="",
                    error_message="No gateway rights available",
                    timestamp=datetime.now().isoformat(),
                    model_used=self.config.fal_model,
                    seed=self.config.seed
                ))
                continue

            prompt = self.generate_prompt(request.scene_id, request.role, request.subscene_id)

            if not prompt:
                print(f"⚠️  No prompt available for scene {request.scene_id}")
                results.append(GenerationResult(
                    success=False,
                    scene_id=request.scene_id,
                    role=request.role,
                    subscene_id=request.subscene_id,
                    prompt="",
                    error_message="No prompt available",
                    timestamp=datetime.now().isoformat(),
                    model_used=self.config.fal_model,
                    seed=self.config.seed
                ))
                continue

            # Deduct rights before generation
            self.gateway_manager.deduct(1)

            image_info = self.generate_image(prompt, request.scene_id, request.role, request.subscene_id)

            if image_info:
                results.append(image_info)
                print(f"✅ Scene {request.scene_id} generated successfully")
            else:
                results.append(GenerationResult(
                    success=False,
                    scene_id=request.scene_id,
                    role=request.role,
                    subscene_id=request.subscene_id,
                    prompt=prompt,
                    error_message="Generation returned None",
                    timestamp=datetime.now().isoformat(),
                    model_used=self.config.fal_model,
                    seed=self.config.seed
                ))
                print(f"❌ Failed to generate scene {request.scene_id}")

            print()

        return results

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

    def generate_all_scenes(self, target_roles: List[str] = None) -> List[GenerationResult]:
        """Generate all scenes and subsences deterministically"""
        if target_roles is None:
            target_roles = ["intro", "loop", "outro"]

        requests = []

        # Generate all scenes and subsences
        for scene_id in self.scene_loader.get_all_scene_ids():
            for role in target_roles:
                request = GenerationRequest(scene_id=scene_id, role=role)
                requests.append(request)

                # Add subscenes if they exist
                subscenes = self.scene_loader.get_all_subscenes(scene_id)
                for subscene in subscenes:
                    subscene_request = GenerationRequest(
                        scene_id=scene_id,
                        role=role,
                        subscene_id=subscene.get('id')
                    )
                    requests.append(subscene_request)

        print(f"📊 Total generation requests prepared: {len(requests)}")
        return self.generate_specific_images(requests)

    def run_complete_pipeline(self, target_scenes: List[int], target_roles: List[str] = None):
        """Run the complete pipeline for target scenes and roles"""
        if target_roles is None:
            target_roles = ["intro"]

        requests = []

        # Prepare requests
        for scene_id in target_scenes:
            for role in target_roles:
                requests.append(GenerationRequest(scene_id=scene_id, role=role))

                # Add subsences if they exist
                subscenes = self.scene_loader.get_all_subscenes(scene_id)
                for subscene in subscenes:
                    requests.append(GenerationRequest(
                        scene_id=scene_id,
                        role=role,
                        subscene_id=subscene.get('id')
                    ))

        print("=" * 60)
        print("🚀 STARTING LEDRAS LAMENT DETERMINISTIC PIPELINE")
        print("=" * 60)
        print(f"📽️  Target Scenes: {target_scenes}")
        print(f"🎭 Target Roles: {target_roles}")
        print(f"📊 Total Requests: {len(requests)}")
        print()

        # Check gateway status
        print(f"🔑 Gateway Status: {self.gateway_manager.get_status()}")
        print()

        # Generate images
        print("🎨 Step 1: Generating images...")
        generated = self.generate_specific_images(requests)

        print()
        print("✅ Step 2: Pipeline completed!")
        print(f"📊 Generated: {len([r for r in generated if r.success])}/{len(requests)} requests")
        print(f"❌ Failed: {len([r for r in generated if not r.success])}/{len(requests)}")

        # Validate prompts
        print()
        print("🔍 Step 3: Validating prompts...")
        validation = self.validate_generated_prompts()

        print()
        print("=" * 60)
        print("🎉 DETERMINISTIC PIPELINE SUMMARY")
        print("=" * 60)
        print(f"✅ Total scenes generated: {len([r for r in generated if r.success])}")
        print(f"✅ Validation pass rate: {validation['validation_pass_rate']:.2f}%")
        print(f"✅ Model used: {self.config.fal_model}")
        print(f"✅ Control strength: {self.config.fal_control_strength}")
        print(f"✅ Cultural authenticity: {self.config.cultural_authenticity_level}")
        print(f"✅ Deterministic seed: {self.config.seed}")
        print(f"✅ Gateway rights used: {self.gateway_manager.get_status()['used']}")
        print("=" * 60)

        return generated

    def __call__(self, target_scenes: List[int] = None, target_roles: List[str] = None):
        """Allow instance to be called as a function - Fixed to generate only scene 5 by default"""
        if target_scenes is None:
            target_scenes = [5]  # Default to scene 5 only

        return self.run_complete_pipeline(target_scenes, target_roles)
@contextmanager
def resource_manager():
    """Context manager for resource cleanup"""
    try:
        yield
    except Exception as e:
        print(f"⚠️  Resource manager caught exception: {e}")
        raise
    finally:
        print("🧹 Resource cleanup completed")
def parse_command_line_args():
    """Parse command-line arguments for flexible scene selection"""
    parser = argparse.ArgumentParser(
        description="Ledras Lament Scene Generator - Deterministic Edition",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--scene",
        type=int,
        nargs="+",
        default=[5],
        help="Scene IDs to generate (e.g., --scene 5 or --scene 1 3 5 8)"
    )

    parser.add_argument(
        "--roles",
        type=str,
        nargs="+",
        default=["intro", "loop", "outro"],
        help="Roles to generate for each scene (e.g., --roles intro loop outro)"
    )

    parser.add_argument(
        "--subscene-only",
        action="store_true",
        help="Only generate subscenes, not main scenes"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Ledras Lament Scene Generator 1.0.0"
    )

    return parser.parse_args()
def main():
    """Main execution function"""
    print("=== Ledras Lament Scene Generation Pipeline - Deterministic Edition ===")
    print()

    try:
        # Parse command-line arguments for flexible scene selection
        args = parse_command_line_args()

        # Setup Gateway for rate limiting
        generator = LedrasSceneGenerator()

        # Prepare requests based on arguments
        requests = []

        if not args.subscene_only:
            for scene_id in args.scene:
                for role in args.roles:
                    requests.append(GenerationRequest(scene_id=scene_id, role=role))

        # Add subsences for each specified scene
        for scene_id in args.scene:
            subscenes = generator.scene_loader.get_all_subscenes(scene_id)
            for subscene in subscenes:
                subscene_request = GenerationRequest(
                    scene_id=scene_id,
                    role=args.roles[0] if args.roles else "intro",
                    subscene_id=subscene.get('id')
                )
                requests.append(subscene_request)

        print(f"🎨 Starting generation for Scenes {args.scene}")
        print(f"🎭 Roles: {args.roles}")
        print(f"📊 Total requests: {len(requests)}")

        # Generate images
        print()
        print("📸 Step 1: Generating images...")
        generated = generator.generate_specific_images(requests)

        print()
        print("✅ Step 2: Generation complete!")
        print(f"📊 Generated: {len([r for r in generated if r.success])}/{len(requests)} requests")
        print(f"❌ Failed: {len([r for r in generated if not r.success])}/{len(requests)}")

        # Summary by scene
        scenes_by_id = {}
        for result in generated:
            if result.scene_id not in scenes_by_id:
                scenes_by_id[result.scene_id] = []
            scenes_by_id[result.scene_id].append(result)

        print()
        print("📊 Generation Summary:")
        for scene_id in sorted(scenes_by_id.keys()):
            scene_results = scenes_by_id[scene_id]
            success_count = len([r for r in scene_results if r.success])
            total_count = len(scene_results)
            print(f"  Scene {scene_id}: {success_count}/{total_count} successful")

        return generated

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
if __name__ == "__main__":
    main()