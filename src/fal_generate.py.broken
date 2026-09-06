#!/usr/bin/env python3
"""
Fixed version of fal_generate.py that prevents overwriting issues.

Key fixes:
1. Version tracking to ensure unique file names
2. Deterministic naming for generated assets
3. No overwriting of existing generated images
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import datetime

# Fal.ai client (sync)
from fal_client import SyncClient

# Gateway for rate limiting
from gateway import Gateway

def load_config(project_root: Path) -> Dict[str, Any]:
    """Load imagination config from `imagine-config.json`."""
    config_path = project_root / "imagine-config.json"
    with open(config_path, "r") as f:
        return json.load(f)

def load_scenes(project_root: Path, scenes_file: str) -> List[Dict[str, Any]]:
    """Load scenes from ledras_scenes_v4.json (AUTHORITATIVE source)."""
    scenes_path = project_root / scenes_file
    with open(scenes_path, "r") as f:
        data = json.load(f)
    return data.get("scenes", [])

def get_scene_by_id(scenes: List[Dict[str, Any]], scene_id: int) -> Dict[str, Any]:
    """Get a scene by its ID from the scenes list."""
    for scene in scenes:
        if scene.get("id") == scene_id:
            return scene
    raise ValueError(f"Scene {scene_id} not found in scenes list")

def ensure_line_out(config: Dict[str, Any], project_root: Path) -> str:
    """Extract (or reuse) the line-out structural template."""
    guideline_image = config.get("guideline_image")
    if guideline_image:
        line_out_path = project_root / guideline_image
        if line_out_path.exists():
            return str(line_out_path)

    # Prefer guide_line_out.jpg (projection guide)
    for candidate in ["stage/guide_line_out.jpg", "stage/guideline_line_out.png"]:
        cand_path = project_root / candidate
        if cand_path.exists():
            return str(cand_path)

    raise FileNotFoundError("No structural guideline image (guide_line_out.jpg / guideline_line_out.png) found.")

def get_next_version_number(output_dir: Path, scene_id: int) -> int:
    """
    Get the next version number for a scene to ensure unique filenames.
    
    This function ensures that each generated image for a given scene gets a unique
    filename, preventing overwrites of previously generated assets.
    
    Args:
        output_dir: Directory where images are stored
        scene_id: ID of the scene
        
    Returns:
        Next available version number (e.g., 2, 3, 4...)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Pattern: scene-01-v[version].png
    version_pattern = f"scene-{scene_id:02d}-v*.png"
    
    max_version = 0
    for file_path in output_dir.glob(version_pattern):
        # Extract version number from filename
        try:
            # Extract version from pattern like "scene-01-v002.png"
            version_str = file_path.stem.split('-')[-1][1:]  # Remove 'v' prefix
            version = int(version_str)
            max_version = max(max_version, version)
        except (ValueError, IndexError):
            continue
    
    return max_version + 1

def save_image(image_bytes: bytes, scene_id: int, output_dir: str) -> str:
    """
    Save generated image to file with version tracking to prevent overwrites.
    
    Key fix: Each save operation gets a unique version number to prevent
    overwriting existing assets. The function tracks existing files for the
    given scene and increments the version number accordingly.
    """
    output_path = Path(output_dir)
    
    # Get next available version number
    version = get_next_version_number(output_path, scene_id)
    
    # Create filename with version number: scene-01-v002.png
    out_path = output_path / f"scene-{scene_id:02d}-v{version:03d}.png"
    
    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save the image
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    
    print(f"📸 Saved scene {scene_id} as {out_path.name} (version {version})")
    return str(out_path)

def estimate_cost(width: int, height: int, model: str) -> float:
    """Estimate Fal.ai cost based on resolution and model type."""
    if model == "fal-ai/flux-control-lora-canny":
        return (width * height) / 1_000_000 * 0.005
    return (width * height) / 1_000_000 * 0.01

def get_resolution(config: Dict[str, Any]) -> tuple[int, int]:
    """Convert image_size config to width x height tuple."""
    size_map = {
        "landscape_16_9": (1280, 720),
        "landscape_4_3": (1280, 960),
        "portrait_9_16": (720, 1280),
    }
    size_str = config.get("image_size", "landscape_16_9")
    if size_str not in size_map:
        print(f"⚠️  Unknown image_size '{size_str}', using default landscape_16_9")
        size_str = "landscape_16_9"
    return size_map[size_str]

def generate_stage(
    client: SyncClient,
    config: Dict[str, Any],
    project_root: Path,
    scene: Dict[str, Any],
    control_strength: float,
) -> str:
    """
    Generate a single stage using Fal.ai FLUX Control LoRA Canny.

    Args:
        client: Fal.ai SyncClient instance
        config: Configuration dictionary
        project_root: Path to project root
        scene: Scene dict from ledras_scenes_v4.json (MUST come from this source)
        control_strength: Control LoRA strength value

    Returns:
        Path to generated image file
    """

    scene_id = scene["id"]
    scene_name = scene.get("name", "Unknown")
    scene_description = scene["description"]

    # Validate scene comes from authoritative source
    if "elements" not in scene or "subscenes" not in scene:
        raise ValueError(
            f"Scene {scene_id} missing required fields. "
            f"Ensure scene data comes from ledras_scenes_v4.json"
        )

    # Build enhanced prompt with visual directives for FLUX Control LoRA Canny
    style = scene.get("style_seed", "")
    style_text = style if style.strip() else ""

    negative = scene.get(
        "negative_prompt",
        "blurry, deformed text, extra objects, watermark",
    )

    # Extract key visual elements for enhanced prompting
    elements = scene.get("elements", [])

    # Build enhanced prompt with visual directives and composition guidance
    enhanced_prompt = (
        f"{scene_description}. "
        f"{style_text}with dramatic cinematic lighting emphasizing architectural geometry. "
        f"Compose wide shot showing {', '.join([str(e) for e in elements])} with depth of field. "
        f"Full moon casting dramatic shadows across stone structure and creating highlight reflections. "
        f"{style.lower()}texture details with weathered limestone surfaces and weathered stone patterns. "
        f"Professional architectural photography composition with strong leading lines. "
        f"Atmospheric depth with distant horizon elements creating spatial depth. "
        f"moody, contemplative, monumental atmosphere with timeless quality. "
        f"--no {negative}"
    )

    prompt = enhanced_prompt

    # Get resolution from image_size config
    width, height = get_resolution(config)

    # Upload guideline image (line-out or depth) to Fal.ai storage
    guideline_path = ensure_line_out(config, project_root)
    print(f"📤 Uploading structural guideline to Fal.ai storage...", end=" ")
    image_url = client.upload_file(guideline_path)
    print(f"✅")

    arguments = {
        "prompt": prompt,
        # "image_url": image_url,  # DO NOT populate image_url for structural-only generation
        "control_lora_image_url": image_url,  # Upload guide_line_out.jpg only as control_lora_image_url
        "num_inference_steps": config.get("num_inference_steps", 28),
        "guidance_scale": 3.5,
        "num_images": 1,
        "enable_safety_checker": True,
        "control_lora_strength": control_strength,
        "control_start": 0.0,
        "control_stop": 1.0,
    }

    model_name = config.get("fal_model", "fal-ai/flux-control-lora-canny")

    # Estimate cost for debugging/monitoring
    cost = estimate_cost(width, height, model_name)
    print(f"💰 Estimated cost: ${cost:.4f}")

    print(f"🎨 Generating scene {scene_id}: {scene_name}")
    print(f"   Prompt: {prompt[:80]}...")
    print(f"   Model: {model_name}")

    # Single API call - ONE REQUEST = ONE IMAGE
    import base64, urllib.request
    resp = client.run(model_name, arguments)
    images = resp.get("images") if isinstance(resp, dict) else None

    if not images:
        raise ValueError(f"API did not return an image for scene {scene_id}")

    b64 = images[0]
    out_dir = project_root / config["output_dir"]
    
    # FIXED: Use the improved save_image function that handles version tracking
    out_path = save_image(b64, scene_id, str(out_dir))

    # Handle response - URL or base64
    if isinstance(b64, dict) and 'url' in b64:
        print(f"📥 Downloading image from URL...")
        with urllib.request.urlopen(b64['url']) as response:
            image_data = response.read()
            # Save with version tracking
            with open(out_path, "wb") as f:
                f.write(image_data)
        print(f"✅ Scene {scene_id} generated → {out_path} (URL)")
    elif isinstance(b64, str):
        try:
            image_data = base64.b64decode(b64)
            with open(out_path, "wb") as f:
                f.write(image_data)
            print(f"✅ Scene {scene_id} generated → {out_path} (base64)")
        except Exception as e:
            raise ValueError(f"Failed to decode base64 image: {str(e)}")

    return str(out_path)

def main():
    """CLI interface for image generation with gateway rate limiting."""
    parser = argparse.ArgumentParser(description="Generate images using Fal.ai")
    parser.add_argument("--scene", type=int, help="Scene ID to generate")
    parser.add_argument("--list-scenes", action="store_true", help="List available scenes")

    args = parser.parse_args()
    project_root = Path(__file__).parent.parent

    try:
        config = load_config(project_root)
        scenes = load_scenes(project_root, config["scenes_file"])

        if args.list_scenes:
            print("Available scenes:")
            for scene in scenes:
                print(f"{scene['id']}: {scene['name']}")
            return

        if args.scene is None:
            print("Error: Please specify a scene ID with --scene")
            return

        scene = get_scene_by_id(scenes, args.scene)

        # Initialize client with API key from environment
        fal_key = os.getenv("FAL_API_KEY") or os.getenv("FAL_KEY")
        if not fal_key:
            raise ValueError("FAL_API_KEY or FAL_KEY not found in environment variables")

        client = SyncClient(key=fal_key)
        gateway = Gateway(project_root)

        if not gateway.has_rights():
            print("Error: No available tokens. Please wait and try again.")
            return

        # Use control strength from config
        control_strength = config.get("fal_control_strength", 0.8)

        # Generate the stage
        image_path = generate_stage(
            client,
            config,
            project_root,
            scene,
            control_strength,
        )

        print(f"✅ Generated image: {image_path}")
        gateway.deduct()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()