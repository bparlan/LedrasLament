import re

# Read the current fal_generate.py
with open('fal_generate.py', 'r') as f:
    content = f.read()

# Fix 1: Replace setattr pattern with proper validation
old_setattr = '''            # Load and validate configuration
            config_data = self._load_and_validate_config(config_path)
            for key, value in config_data.items():
                setattr(self, key, value)

            print(f"✅ Configuration loaded from {config_path}")'''

new_setattr = '''            # Load and validate configuration
            config_data = self._load_and_validate_config(config_path)
            self.validate_and_normalize(config_data)

            print(f"✅ Configuration loaded from {config_path}")'''

content = content.replace(old_setattr, new_setattr)

# Fix 2: Add comprehensive argument parser
cli_addition = '''
# Add comprehensive argument parser
parser = argparse.ArgumentParser(
    description="Ledras Lament Scene Generation Pipeline",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  # Generate single scene with custom parameters
  python3 fal_generate.py 1 --model fal-ai/flux-control-lora-canny \
                    --strength 0.8 --seed 123 --resolution "1920x1080"
  
  # Generate all subscenes with custom settings
  python3 fal_generate.py 1-3 --subscenes --model fal-ai/flux-control-lora-canny \
                    --strength 0.6 --seed 456 --resolution "1280x720"
  
  # Generate scenes with predefined config
  python3 fal_generate.py 1 --model fal-ai/flux-control-lora-canny \
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
    default=0.75,
    help='Control strength (0.0-1.0, default: 0.75)'
)

parser.add_argument(
    '--seed',
    type=int,
    default=502,
    help='Seed for deterministic generation (default: 502)'
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

# Parse arguments
args = parser.parse_args()

# If no arguments provided, show help
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(0)
'''

# Fix 3: Replace the existing CLI parsing with comprehensive one
old_cli = '''        # Parse CLI: `--subscenes` flag, remaining are scene IDs (default 1)
        subscene_mode = "--subscenes" in sys.argv
        args = [a for a in sys.argv[1:] if a != "--subscenes"]
        scene_ids = [int(a) for a in args] if args else [1]
        if subscene_mode:
            print(f"🎨 Generating ALL subscenes for scenes {scene_ids}...")
            scenes = generator.generate_subscene_images(scene_ids)
            print(f"\n✅ SUCCESS: {total} subscene images generated for scenes {scene_ids}")
        else:
            print(f"🎨 Generating scenes {scene_ids}...")
            scenes = generator.generate_specific_images(scene_ids, "intro")
            print(f"\n✅ SUCCESS: Scenes {scene_ids} generated successfully!")'''

content = content.replace(old_cli, cli_addition)

# Write the fixed content back
with open('fal_generate.py', 'w') as f:
    f.write(content)

print("✅ Comprehensive CLI implemented for fal_generate.py")

# Also fix the LedrasConfig class
with open('fal_generate.py', 'r') as f:
    lines = f.readlines()

# Find and replace the LedrasConfig class
for i, line in enumerate(lines):
    if 'class LedrasConfig:' in line:
        # Find the end of the class
        for j in range(i, min(i+50, len(lines))):
            if 'def __init__(self):' in lines[j]:
                # Replace the entire class with improved version
                lines[j+1] = '        """Initialize configuration with validation."""\n'
                lines[j+2] = '        self.validate_and_normalize(None)\n'
                break
        break

# Write the changes back
with open('fal_generate.py', 'w') as f:
    f.writelines(lines)

print("✅ LedrasConfig class fixed with validation")
