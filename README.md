# Ledras Lament - Image Generation Commands

This repository contains the image generation pipeline for the Ledras Lament project. The main command-line interface is provided by `src/fal_generate.py`.

## Overview

The `fal_generate.py` script generates scene images for the Ledras Lament project using the fal.ai API (or a demo mode if no API key is provided). It uses scene descriptions from the authoritative `data/scenes/ledras_scenes_v4.json` file and supports advanced image generation features including controlnet models and various preprocessing options.

## Basic Usage

```bash
# Generate scene 1 using default settings
python3 src/fal_generate.py

# Generate specific scene by ID
python3 src/fal_generate.py --scene 5

# List all available scenes
python3 src/fal_generate.py --list-scenes
```

## CLI Arguments

### `--config`
- **Type**: String
- **Default**: `imagine-config.json`
- **Description**: Path to the configuration JSON file
- **Example**: `--config myconfig.json`

### `--scene`
- **Type**: Integer
- **Default**: `1`
- **Description**: Scene ID to generate (must exist in the scenes JSON file)
- **Example**: `--scene 3`

### `--output-dir`
- **Type**: String
- **Default**: `assets/generated`
- **Description**: Output directory for generated images
- **Example**: `--output-dir /path/to/output` or `--output-dir ./images`

### `--list-scenes`
- **Type**: Flag
- **Default**: False
- **Description**: List all available scenes with their IDs, names, and descriptions
- **Example**: `--list-scenes`

## Configuration File (`imagine-config.json`)

The script requires a configuration file with the following structure. The default file is located at the project root:

```json
{
  "guideline_image": "stage/guide_line_out.jpg",
  "scenes_file": "data/scenes/ledras_scenes_v4.json",
  "output_dir": "assets/generated",
  "image_size": "landscape_16_9",
  "fallback_model": "google/gemini-2.5-flash-image",
  "fallback_cost": "$0.0000028",
  "fal_model": "fal-ai/z-image/turbo/controlnet",
  "fal_control_strength": 0.9,
  "num_inference_steps": 8,
  "enable_prompt_expansion": false,
  "preprocess": "none"
}
```

### Required Configuration Fields

- **`guideline_image`**: Path to the guideline/reference image
- **`scenes_file`**: Path to the JSON file containing scene descriptions
- **`output_dir`**: Default output directory for generated images
- **`fal_model`**: The fal.ai model to use for generation
- **`fal_control_strength`**: Control strength for the generation model

### Optional Configuration Fields

- **`image_size`**: Image size preset (e.g., "landscape_16_9", "square", "portrait_16_9")
- **`fallback_model`**: Model to use if the primary model fails
- **`fallback_cost`**: Cost estimate for the fallback model
- **`num_inference_steps`**: Number of inference steps (default: 8)
- **`enable_prompt_expansion`**: Enable prompt expansion (default: false)
- **`preprocess`**: Preprocessing mode ("none", "blur", "crop", etc.)

## Scene Data File

Scenes are loaded from `data/scenes/ledras_scenes_v4.json`. This file must contain:

```json
{
  "scenes": [
    {
      "id": 1,
      "name": "Scene Name",
      "description": "Detailed description for image generation",
      "style_seed": "art_style_identifier",
      "negative_prompt": "negative_prompt_text"
    }
  ],
  "style_seed": "global_style_seed",
  "negative_prompt": "global_negative_prompt"
}
```

## API Key Setup

To use real image generation (instead of demo mode), set the `FAL_API_KEY` environment variable:

```bash
export FAL_API_KEY="your_fal_api_key_here"

# Or in your shell profile
echo 'export FAL_API_KEY="your_fal_api_key_here"' >> ~/.bashrc
```

## Image Generation Process

1. **Load Configuration**: Reads `imagine-config.json` from the project root
2. **Load Scenes**: Loads all scenes from the authoritative JSON file
3. **Validate**: Checks for required configuration keys
4. **Generate Prompt**: Creates a detailed prompt for the requested scene using:
   - Scene description from JSON
   - Guideline image for composition guidance
   - Style information and negative prompts
5. **API Call**: Makes a single API call per image using fal.ai
6. **Save Result**: Saves the generated image to the specified output directory

## Example Outputs

Generated images are saved with naming convention: `scene-{ID}.png`

```
assets/generated/
├── scene-01.png
├── scene-02.png
├── scene-03.png
└── ...
```

## Error Handling

The script handles several error conditions:

- **Missing Configuration**: Raises `ValueError` with details of missing keys
- **Missing Scenes File**: Raises `FileNotFoundError` if the scenes JSON is missing
- **Invalid Scene ID**: Raises `ValueError` if the requested scene doesn't exist
- **Missing API Key**: Falls back to demo mode (generates a fake image file)
- **API Errors**: Catches and displays exception information with stack trace

## Advanced Usage

### Custom Configuration

Create a custom config file for specific projects or different models:

```bash
cat > custom_config.json << 'EOF'
{
  "guideline_image": "stage/custom_guide.jpg",
  "scenes_file": "data/custom_scenes.json",
  "output_dir": "./my_generated_images",
  "image_size": "square",
  "fal_model": "fal-ai/some-model",
  "fal_control_strength": 0.8,
  "num_inference_steps": 12,
  "enable_prompt_expansion": true,
  "preprocess": "blur"
}
EOF

python3 src/fal_generate.py --config custom_config.json --scene 2
```

### Batch Generation

Generate multiple scenes by running the script multiple times:

```bash
for scene in 1 2 3 4 5; do
    python3 src/fal_generate.py --scene $scene
    echo "Generated scene $scene"
done
```

## Dependencies

Ensure you have the following Python packages installed:

```bash
pip install fal_client pillow
```

## Project Structure

```
ledras_lament/
├── src/
│   ├── fal_generate.py              # Main generation script
│   └── __pycache__/                 # Compiled Python files
├── data/
│   └── scenes/                      # Scene data files
│       └── ledras_scenes_v4.json    # Scene descriptions
├── assets/
│   ├── generated/                   # Generated images (output)
│   └── ...
├── stage/                           # Stage reference files
├── imagine-config.json              # Configuration file
├── README.md                        # This file
└── ...
```

## Troubleshooting

### "Missing required config keys"
- Ensure `imagine-config.json` exists in the project root
- Verify all required keys are present in the config file

### "Scenes file not found"
- Check that `data/scenes/ledras_scenes_v4.json` exists
- Ensure the `scenes_file` path in config matches the actual file location

### "FAL_API_KEY not set"
- Set the `FAL_API_KEY` environment variable
- Or run in demo mode by letting it use fake image data for testing

### "Scene X not found"
- Check that the scene ID exists in the scenes JSON file
- Use `--list-scenes` to view all available scenes

## License

See the project documentation for licensing information related to the Ledras Lament project.

## Support

For issues with image generation or script usage, refer to the project documentation in the `docs/` directory or contact the project maintainers.