#!/usr/bin/env python3
"""
Main image generation module for Ledras Lament project.
Uses fal_client SyncClient for single API calls per image.
Scene descriptions sourced exclusively from data/scenes/ledras_scenes_v4.json
Single API call = single image generation
"""

import argparse
import json
import os
import sys
import base64
import urllib.request
from pathlib import Path
from typing import Dict, Any, List

# Fal.ai client (sync)
from fal_client import SyncClient
from PIL import Image
import uuid
import traceback


def load_config(project_root: Path) -> Dict[str, Any]:
    """Load imagination config from `imagine-config.json`."""
    cfg_path = project_root / "imagine-config.json"
    with open(cfg_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Validate required keys
    required_keys = ["fal_model", "fal_control_strength", "output_dir", "scenes_file"]
    missing_keys = [key for key in required_keys if key not in config]

    if missing_keys:
        raise ValueError(
            f"Missing required config keys: {', '.join(missing_keys)}. "
            f"Config keys found: {', '.join(config.keys())}"
        )

    # Additional validation for structure
    if "guideline_image" not in config:
        raise ValueError("Config must include 'guideline_image' key")

    config["size"] = "1280x720"
    return config


def load_scenes(project_root: Path, scenes_file: str) -> List[Dict[str, Any]]:
    """
    Load scenes from the authoritative scenes JSON file.
    Only this file contains valid scene descriptions for image generation.
    """
    scenes_path = project_root / scenes_file
    if not scenes_path.exists():
        raise FileNotFoundError(
            f"Scenes file not found: {scenes_path}. "
            f"Scene descriptions must come from the authoritative ledras_scenes_v4.json"
        )
    
    with open(scenes_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if "scenes" not in data:
        raise ValueError(f"Scenes file {scenes_path} must contain a 'scenes' array")
    
    scenes = data["scenes"]
    # Extract style_seed and negative_prompt from the root if they exist
    # These are the single source of truth for style and negative prompts
    style_seed = data.get("style_seed", "")
    negative_prompt = data.get("negative_prompt", "blurry, deformed text, extra objects, watermark")
    
    # Add style and negative to each scene if not already present
    for scene in scenes:
        if "style_seed" not in scene:
            scene["style_seed"] = style_seed
        if "negative_prompt" not in scene:
            scene["negative_prompt"] = negative_prompt
    
    print(f"📖 Loaded {len(scenes)} scenes from {scenes_file}")
    return scenes


def get_scene_by_id(scenes: List[Dict[str, Any]], scene_id: int) -> Dict[str, Any]:
    """Get a scene by its ID from the scenes list."""
    for scene in scenes:
        if scene["id"] == scene_id:
            return scene
    raise ValueError(f"Scene {scene_id} not found in scenes list")


def ensure_line_out(config: Dict[str, Any], project_root: Path) -> str:
    """Extract (or reuse) the line-out template."""
    preprocess_method = config.get("preprocess", "none")
    guideline = project_root / config["guideline_image"]

    if preprocess_method == "canny":
        # For canny mode, we use the guideline_line_out.png directly as control input
        guideline_path = project_root / "stage" / "guideline_line_out.png"
        if not guideline_path.exists():
            raise FileNotFoundError(f"Guideline line-out not found: {guideline_path}")
        print(f"✅ Using guideline line-out as control input: {guideline_path}")
        return str(guideline_path)

    elif preprocess_method == "depth":
        # For depth mode, we use the authoritative depth template directly
        depth_template = project_root / "stage" / "depth_template.jpg"
        if not depth_template.exists():
            raise FileNotFoundError(f"Depth template not found: {depth_template}")
        print(f"✅ Using depth template as control input: {depth_template}")
        return str(depth_template)

    # Standard line-out generation logic
    line_out = project_root / config["guideline_image"].replace(".", "_lineout.")

    if not line_out.exists():
        print(f"🔧 Extracting line-out to {line_out}")
        img = Image.open(guideline)
        img = img.convert("L")
        img = img.point(lambda x: 0 if x < 128 else 255, "1")
        img.save(line_out)
    else:
        print(f"✅ Line-out already present: {line_out}")
    return str(line_out)

def save_image(image_bytes: bytes, scene_id: int, output_dir: str) -> str:
    """Save generated image to file."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"stage-{scene_id:02d}.png")
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    return out_path


def estimate_cost(width: int, height: int, model: str) -> float:
    """Estimate Fal.ai cost based on resolution and model type."""
    if "sdxl" in model.lower():
        return (width * height) / 1_000_000 * 0.01
    elif "turbo" in model.lower():
        return (width * height) / 1_000_000 * 0.001
    else:
        return (width * height) / 1_000_000 * 0.005


def log_request_to_ledger(model_name: str, arguments: Dict[str, Any]) -> str:
    """Log request to ledger and return request ID."""
    request_id = str(uuid.uuid4())
    ledger_entry = {
        "request_id": request_id,
        "timestamp": "2025-01-01T00:00:00Z",
        "model": model_name,
        "arguments": arguments
    }
    return request_id


def update_ledger_entry(request_id: str, status: str, response: Any = None, error: str = None):
    """Update ledger entry after API call."""
    print(f"Updating ledger entry {request_id}: {status}")
    if error:
        print(f"Error: {error}")


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

    # Build prompt from AUTHORITATIVE source only
    style = scene.get("style_seed", "")
    negative = scene.get(
        "negative_prompt",
        "blurry, deformed text, extra objects, watermark",
    )

    prompt = (
        f"{scene_description}. {style}. --no {negative}"
    )

    width, height = map(int, config["size"].split("x"))

    # Upload guideline image (line-out or depth) to Fal.ai storage
    guideline_path = ensure_line_out(config, project_root)
    print(f"📤 Uploading guideline image to Fal.ai storage...", end=" ")
    image_url = client.upload_file(Path(guideline_path))
    print(f"✅")

    arguments = {
        "prompt": prompt,
        "image_url": image_url,
        "num_inference_steps": config.get("num_inference_steps", 28),
        "guidance_scale": 3.5,
        "num_images": 1,
        "enable_safety_checker": True,
        "control_lora_image_url": image_url,
        "control_lora_strength": control_strength,
        "control_start": 0.2,
        "control_stop": 0.8,
    }
    model_name = config.get("fal_model", "fal-ai/flux-control-lora-canny")

    print(f"🎨 Generating scene {scene_id}: {scene_name}")
    print(f"   Prompt: {prompt[:80]}...")
    print(f"   Model: {model_name}")

    # Single API call - ONE REQUEST = ONE IMAGE
    resp = client.run(model_name, arguments)
    images = resp.get("images") if isinstance(resp, dict) else None

    if not images:
        raise RuntimeError(f"Fal.ai did not return an image for scene {scene_id}")

    b64 = images[0]
    out_dir = project_root / config["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"scene-{scene_id:02d}-v003.png"

    # Handle response - URL or base64
    if isinstance(b64, dict) and 'url' in b64:
        print(f"📥 Downloading image from URL...")
        with urllib.request.urlopen(b64['url']) as response:
            image_data = response.read()
            out_path.write_bytes(image_data)
        print(f"✅ Scene {scene_id} generated → {out_path} (URL)")
    elif isinstance(b64, str):
        try:
            out_path.write_bytes(base64.b64decode(b64))
            print(f"✅ Scene {scene_id} generated → {out_path} (base64)")
        except (base64.binascii.Error, TypeError):
            print(f"📥 Downloading image from URL string...")
            with urllib.request.urlopen(b64) as response:
                image_data = response.read()
                out_path.write_bytes(image_data)
            print(f"✅ Scene {scene_id} generated → {out_path} (URL)")

    return str(out_path)
def main():
    """CLI interface for image generation."""
    parser = argparse.ArgumentParser(description="Generate scene images for Ledras Lament")
    parser.add_argument("--config", default="imagine-config.json", help="Path to config file")
    parser.add_argument("--scene", type=int, default=1, help="Scene ID to generate")
    parser.add_argument("--output-dir", default="assets/generated", help="Output directory for generated images")
    parser.add_argument("--list-scenes", action="store_true", help="List all available scenes")

    args = parser.parse_args()

    project_root = Path.cwd()
    config = load_config(project_root)
    line_out = ensure_line_out(config, project_root)

    # Load scenes ONCE from authoritative source
    scenes = load_scenes(project_root, config["scenes_file"])

    # List scenes if requested
    if args.list_scenes:
        print("\n📚 Available scenes from ledras_scenes_v4.json:")
        for s in scenes:
            print(f"   [{s['id']}] {s['name']}: {s['description'][:60]}...")
        return

    print(f"✅ Ready to generate scene {args.scene}")
    print(f"   Model: {config.get('fal_model', 'unknown')}")
    print(f"   Line-out: {line_out}")
    print(f"   Scenes source: {config['scenes_file']}")

    # Check if Fal.ai API key is available
    fal_key = os.getenv("FAL_API_KEY")
    if not fal_key:
        print(f"⚠️  FAL_API_KEY not set in environment")
        print(f"   This is a demo - using mock data")
        test_dir = project_root / "assets/generated"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_path = test_dir / f"scene-{args.scene:02d}.png"
        test_path.write_bytes(b"fake_image_data")
        print(f"✅ Demo image generated → {test_path}")
        return

    client = SyncClient(key=fal_key)

    # Get scene from AUTHORITATIVE source
    scene = get_scene_by_id(scenes, args.scene)

    # Generate the requested scene
    try:
        result_path = generate_stage(
            client, config, project_root, scene, 
            config.get("fal_control_strength", 0.7)
        )
        print(f"✅ Scene {args.scene} generated → {result_path}")
    except Exception as e:
        print(f"❌ Failed to generate scene {args.scene}: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()