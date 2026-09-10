#!/usr/bin/env python3
"""
Ledras Lament Scene Generation Pipeline - Comprehensive CLI

This script replaces multiple one-off scripts with comprehensive CLI parameterization,
implementing Rule 1 (CLI Parameterization) from Agentic System Awareness.

Usage:
  python3 fal_generate_improved.py [scene_ids] [--subscenes] [--model <model>]
                      [--strength <0.0-1.0>] [--seed <int>] [--resolution <widthxheight>]
                      [--help]

Features:
- All CLI flags from original fal_generate.py plus new comprehensive options
- No more one-off scripts needed for parameter variations
- Full backward compatibility with existing workflows
- Proper config schema validation
"""

import json
import os
import argparse
import sys
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from fal_client import SyncClient
from utils import get_resolution, estimate_cost

# Load .env BEFORE any SDK import
_script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_script_dir, '.env'), override=True)

# Constants for deterministic behavior
DEFAULT_SEED = 502
DEFAULT_STRENGTH = 0.75
DEFAULT_WINDOW = [0.2, 0.8]


def setup_argument_parser():
    """Setup comprehensive argument parser for CLI parameterization."""
    parser = argparse.ArgumentParser(
        description="Ledras Lament Scene Generation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single scene with custom parameters
  python3 fal_generate_improved.py 1 --model fal-ai/flux-control-lora-canny 
                    --strength 0.8 --seed 123 --resolution "1920x1080"
  
  # Generate all subscenes with custom settings
  python3 fal_generate_improved.py 1-3 --subscenes --model fal-ai/flux-control-lora-canny 
                    --strength 0.6 --seed 456 --resolution "1280x720"
  
  # Generate scenes with predefined config
  python3 fal_generate_improved.py 1 --model fal-ai/flux-control-lora-canny 
                    --strength 0.75 --seed 502
        """
    )
    
    # Positional argument: scene IDs
    parser.add_argument(
        'scene_ids',
        nargs='+',
        help='Scene ID(s) to generate (e.g., 1 2 3 or 1-5)'
    )
    
    # Common generation options
    parser.add_argument(
        '--subscenes',
        action='store_true',
        help='Generate all subscenes for each specified scene'
    )
    
    parser.add_argument(
        '--model',
        default='fal-ai/flux-control-lora-canny',
        help='Model name for generation (default: fal-ai/flux-control-lora-canny)'
    )
    
    parser.add_argument(
        '--strength',
        type=float,
        default=DEFAULT_STRENGTH,
        help=f'Control strength (0.0-1.0, default: {DEFAULT_STRENGTH})'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=DEFAULT_SEED,
        help=f'Seed for deterministic generation (default: {DEFAULT_SEED})'
    )
    
    parser.add_argument(
        '--resolution',
        default='1920x1080',
        help='Image resolution in format WIDTHxHEIGHT (default: 1920x1080)'
    )
    
    # Configuration file option
    parser.add_argument(
        '--config',
        help='Path to imagine-config.json file (overrides defaults)'
    )
    
    # Output directory option
    parser.add_argument(
        '--output-dir',
        default='assets/generated/ledras-premier/set_06',
        help='Output directory for generated images (default: assets/generated/ledras-premier/set_06)'
    )
    
    return parser


class LedrasConfig:
    """Structured configuration class with validation."""
    
    def __init__(self, config_data: dict = None):
        self.validate_and_normalize(config_data)
    
    def validate_and_normalize(self, config_data: dict = None):
        """Validate and normalize configuration with explicit schema."""
        # Load default config if not provided
        if config_data is None:
            with open('imagine-config.json', 'r') as f:
                config_data = json.load(f)
        
        # Initialize all attributes with defaults
        self.fal_model = config_data.get("fal_model", "fal-ai/flux-control-lora-canny")
        self.image_size = self._normalize_image_size(config_data.get("image_size"))
        self.control_lora_image_url = config_data.get("control_lora_image_url")
        self.seed = config_data.get("seed", DEFAULT_SEED)
        self.control_lora_strength = config_data.get("control_lora_strength", DEFAULT_STRENGTH)
        self.control_lora_window = config_data.get("control_lora_window", DEFAULT_WINDOW)
        self.guideline_image = config_data.get("guideline_image")
        self.scenes_file = config_data.get("scenes_file")
        self.num_inference_steps = config_data.get("num_inference_steps", 28)
        self.guidance_scale = config_data.get("guidance_scale", 3.5)
        self.enable_safety_checker = config_data.get("enable_safety_checker", True)
        self.output_dir = config_data.get("output_dir", "assets/generated/ledras-premier/set_06")
        self.log_file = config_data.get("log_file", "generation.log")
        self.cultural_authenticity_level = config_data.get("cultural_authenticity_level", "cypro_phoenician")
        
        # Validate critical fields
        self._validate_config()
    
    def _normalize_image_size(self, size: str) -> dict:
        """Normalize image size string to dict format."""
        if isinstance(size, dict):
            return size
        
        if size and 'x' in size:
            width, height = size.split('x', 1)
            return {"width": int(width), "height": int(height)}
        
        # Default landscape
        return {"width": 1920, "height": 1080}
    
    def _validate_config(self):
        """Validate configuration schema."""
        # Validate model name
        if not self.fal_model.startswith('fal-ai/'):
            raise ValueError(f"Invalid model name: {self.fal_model}")
        
        # Validate strength range
        if not 0.0 <= self.control_lora_strength <= 1.0:
            raise ValueError(f"Control strength must be between 0.0 and 1.0, got: {self.control_lora_strength}")
        
        # Validate strength within window
        if not self.control_lora_window[0] <= self.control_lora_strength <= self.control_lora_window[1]:
            raise ValueError(f"Control strength {self.control_lora_strength} outside window {self.control_lora_window}")
        
        # Validate image size
        if not isinstance(self.image_size, dict) or 'width' not in self.image_size or 'height' not in self.image_size:
            raise ValueError(f"Invalid image size: {self.image_size}")
        
        # Validate seed
        if not isinstance(self.seed, int) or self.seed < 0:
            raise ValueError(f"Invalid seed: {self.seed}")
        
        # Ensure no deprecated aliases are present
        if hasattr(self, 'prompt_architecture') and isinstance(self.prompt_architecture, dict):
            if any(key in self.prompt_architecture for key in ['control_image_path', 'control_image_url_path']):
                import warnings
                warnings.warn("Deprecated control image keys found. Use control_lora_image_url only.", DeprecationWarning)


def create_deterministic_filename(scene_id: int, subscene_id: int = None, seed: int = None) -> str:
    """Create deterministic filename without random timestamps."""
    seed = seed or DEFAULT_SEED
    if subscene_id:
        return f"scene-{scene_id:02d}_subscene-{subscene_id:02d}_v{seed:03d}.png"
    return f"scene-{scene_id:02d}_v{seed:03d}.png"


def safe_download_image(client: SyncClient, image_url: str, output_path: str, seed: int, scene_id: int) -> bool:
    """Download image with deterministic naming."""
    try:
        # Use deterministic seed for API calls
        response = client.run(
            input={
                "image": image_url,
                "prompt": f"Generate scene {scene_id}",
                "seed": seed,
                "guidance_scale": 3.5,
                "num_inference_steps": 28
            }
        )
        
        # Save with deterministic filename
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return True
        
    except Exception as e:
        print(f"❌ Download failed for scene {scene_id}: {e}")
        return False


def process_scenes(scene_ids, subscene_mode, config):
    """Process scenes with deterministic behavior."""
    print(f"🎨 Processing scenes {scene_ids}")
    print(f"   Model: {config.fal_model}")
    print(f"   Strength: {config.control_lora_strength}")
    print(f"   Seed: {config.seed}")
    print(f"   Resolution: {config.image_size['width']}x{config.image_size['height']}")
    print(f"   Subscenes mode: {'enabled' if subscene_mode else 'disabled'}")
    
    # Load scenes data
    with open(config.scenes_file, 'r') as f:
        scenes_data = json.load(f)
    
    results = []
    
    for scene_id_str in scene_ids:
        # Parse scene ID (handle ranges like "1-5")
        if '-' in scene_id_str:
            start, end = map(int, scene_id_str.split('-'))
            scene_ids_range = range(start, end + 1)
        else:
            scene_ids_range = [int(scene_id_str)]
        
        for current_scene_id in scene_ids_range:
            scene = next((s for s in scenes_data if s['scene_id'] == current_scene_id), None)
            
            if not scene:
                print(f"⚠️  Scene {current_scene_id} not found, skipping")
                continue
            
            # Process subscenes if enabled
            if subscene_mode and 'subscenes' in scene:
                for subscene_id, subscene_data in enumerate(scene['subscenes'], 1):
                    result = process_scene_generation(
                        current_scene_id, subscene_id, subscene_data, config
                    )
                    results.extend(result)
            else:
                # Process main scene only
                result = process_scene_generation(
                    current_scene_id, None, None, config
                )
                results.extend(result)
    
    return results


def process_scene_generation(scene_id, subscene_id, subscene_data, config):
    """Process single scene generation with deterministic naming."""
    print(f"🌅 Generating scene {scene_id}")
    
    # Create deterministic filename
    filename = create_deterministic_filename(scene_id, subscene_id, config.seed)
    output_path = os.path.join(config.output_dir, filename)
    
    # Ensure output directory exists
    os.makedirs(config.output_dir, exist_ok=True)
    
    # Download and save image
    success = safe_download_image(
        SyncClient(api_key=os.getenv('FAL_KEY')),
        config.control_lora_image_url,
        output_path,
        config.seed,
        scene_id
    )
    
    result = {
        "scene_id": scene_id,
        "subscene_id": subscene_id,
        "filename": filename,
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    if success:
        print(f"   ✅ Generated: {filename}")
    else:
        print(f"   ❌ Failed: {filename}")
    
    return [result]


def generate_help_text():
    """Generate help text showing available options."""
    help_text = """
=== Ledras Lament Scene Generation Pipeline ===

Available CLI Options:
  scene_ids        Space-separated list of scene IDs (e.g., "1 2 3" or "1-5")

  --subscenes      Generate all subscenes for each specified scene
  --model MODEL    Model name (default: fal-ai/flux-control-lora-canny)
  --strength VAL   Control strength (0.0-1.0, default: 0.75)
  --seed VAL       Random seed for deterministic generation (default: 502)
  --resolution WXH Image resolution (default: 1920x1080)
  --config FILE    Path to imagine-config.json (overrides defaults)
  --output-dir DIR Output directory (default: assets/generated/ledras-premier/set_06)

All script variations are now covered by CLI flags - no need for one-off scripts!
"""
    return help_text


def main():
    """Main entry point with comprehensive CLI."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Show help if no arguments provided
    if len(sys.argv) == 1:
        print(generate_help_text())
        return 0
    
    try:
        # Parse scene IDs
        scene_ids = []
        for item in args.scene_ids:
            if '-' in item:
                start, end = map(int, item.split('-'))
                scene_ids.extend(range(start, end + 1))
            else:
                scene_ids.append(int(item))
        
        # Load configuration from file if specified
        config_data = None
        if args.config:
            with open(args.config, 'r') as f:
                config_data = json.load(f)
        
        # Create config with validation
        config = LedrasConfig(config_data)
        
        # Override config with CLI arguments if provided
        if args.model:
            config.fal_model = args.model
        if args.strength:
            config.control_lora_strength = args.strength
        if args.seed:
            config.seed = args.seed
        if args.resolution:
            config.image_size = get_resolution(args.resolution)
        if args.output_dir:
            config.output_dir = args.output_dir
        
        # Process scenes
        results = process_scenes(scene_ids, args.subscenes, config)
        
        # Print summary
        successful = sum(1 for r in results if r['success'])
        print(f"\n📊 Generation Summary:")
        print(f"   Scenes processed: {len(set(r['scene_id'] for r in results))}")
        print(f"   Total attempts: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {len(results) - successful}")
        
        # Save results to log file
        log_path = os.path.join(config.output_dir, config.log_file)
        with open(log_path, 'a') as f:
            f.write(json.dumps({
                'timestamp': datetime.now().isoformat(),
                'command': ' '.join(sys.argv),
                'results': results,
                'summary': {
                    'scenes_processed': len(set(r['scene_id'] for r in results)),
                    'total_attempts': len(results),
                    'successful': successful,
                    'failed': len(results) - successful
                }
            }) + '\n')
        
        return 0 if successful > 0 else 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())