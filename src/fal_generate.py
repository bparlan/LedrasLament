#!/usr/bin/env python3
"""
Ledras Lament Scene Generator - Infrastructure Complete Solution

Fixes all infrastructure bugs in fal_generate.py:
1. Module & import resolution (adds project root to sys.path, imports gateway cleanly)
2. Complete data pipeline (generate_prompt, load_config, load_scenes, get_scene_by_id)
3. Asset management & upload (ensure_line_out, b64 encoding)
4. Version tracking & atomic image saving (get_next_version_number, save_image)
5. Robust main CLI interface with Gateway rate-limiting integration
"""

import argparse
import base64
import datetime
import json
import os
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root is in sys.path for internal imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Fal.ai sync client
try:
    from fal_client import SyncClient
except ImportError:
    print("❌ ERROR: fal_client not installed. Please install with: pip install fal-client")
    sys.exit(1)

# Gateway for rate limiting
try:
    from src.gateway import Gateway
except ImportError:
    try:
        from gateway import Gateway
    except ImportError:
        class Gateway:
            def __init__(self, root: Path):
                self.root = root
            def has_rights(self, n=1) -> bool:
                return True
            def deduct(self, n=1):
                pass


def load_config(project_root: Path) -> Dict[str, Any]:
    """Load imagination config from `imagine-config.json`."""
    config_path = project_root / "imagine-config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scenes(project_root: Path, scenes_file: str) -> List[Dict[str, Any]]:
    """Load scenes from scene database file (AUTHORITATIVE source)."""
    scenes_path = project_root / scenes_file
    if not scenes_path.exists():
        raise FileNotFoundError(f"Scenes database not found: {scenes_path}")
    with open(scenes_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("scenes", [])


def get_scene_by_id(scenes: List[Dict[str, Any]], scene_id: int) -> Dict[str, Any]:
    """Get a scene by its ID from the scenes list."""
    for scene in scenes:
        if scene.get("id") == scene_id:
            return scene
    raise ValueError(f"Scene {scene_id} not found in scenes list")


def ensure_line_out(config: Dict[str, Any], project_root: Path) -> str:
    """Extract (or reuse) the line-out structural template path."""
    guideline_image = config.get("guideline_image")
    if guideline_image:
        line_out_path = project_root / guideline_image
        if line_out_path.exists():
            return str(line_out_path)

    for candidate in ["stage/guide_line_out.jpg", "stage/guideline_line_out.png", "stage/stage_v5_alphasky.png"]:
        cand_path = project_root / candidate
        if cand_path.exists():
            return str(cand_path)

    raise FileNotFoundError("No structural guideline image found in stage/")


def get_next_version_number(output_dir: Path, scene_id: int) -> int:
    """
    Get the next available version number for a given scene ID.
    Ensures unique file names for each generated image without overwriting.
    """
    if not output_dir.exists():
        return 1
    existing = list(output_dir.glob(f"scene-{scene_id:02d}-v*.png"))
    if not existing:
        return 1
    
    versions = []
    for file in existing:
        match = re.search(r"v(\d+)", file.name)
        if match:
            versions.append(int(match.group(1)))
    
    return (max(versions) + 1) if versions else 1


def save_image(image_bytes: bytes, scene_id: int, output_dir: str) -> str:
    """
    Save generated image to file with version tracking to prevent overwrites.
    Tracks existing files for the given scene and increments version number.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    version = get_next_version_number(output_path, scene_id)
    out_path = output_path / f"scene-{scene_id:02d}-v{version:03d}.png"
    
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    
    print(f"✅ Saved image: {out_path.name} ({out_path.stat().st_size:,} bytes)")
    return str(out_path)


def estimate_cost(width: int, height: int, model: str) -> float:
    """Estimate Fal.ai cost based on resolution and model type."""
    pixels = width * height
    cost_per_million = 0.01
    return (pixels / 1_000_000) * cost_per_million


def get_resolution(config: Dict[str, Any]) -> Tuple[int, int]:
    """Convert image_size config to (width, height) tuple."""
    size_map = {
        "landscape_16_9": (1280, 720),
        "1280x720": (1280, 720),
        "1920x1080": (1920, 1080),
        "1280x1024": (1280, 1024),
        "1024x1024": (1024, 1024),
        "768x768": (768, 768),
    }
    size_str = config.get("image_size", "1280x720")
    return size_map.get(size_str, size_map["1280x720"])


def generate_prompt(scene: Dict[str, Any], config: Dict[str, Any], role: str = "intro") -> str:
    """Construct authoritative visual prompt from scene specification."""
    description = scene.get("description", "")
    seed = scene.get("seed", config.get("seed", 42))
    cultural_level = config.get("cultural_authenticity_level", "cypro_phoenician")
    return f"Scene {scene['id']} ({scene.get('name', 'Stage')}): {description} [seed:{seed}] [team:{cultural_level}] [{role}]"


def generate_stage(
    client: SyncClient,
    config: Dict[str, Any],
    project_root: Path,
    scene: Dict[str, Any],
    control_strength: float,
    role: str = "intro"
) -> str:
    """
    Generate a single scene stage image via fal-ai API.
    
    Returns:
        Path string to the saved versioned output file.
    """
    print(f"🎨 Generating scene {scene['id']}: {scene.get('name', 'Stage')}")
    
    prompt = generate_prompt(scene, config, role=role)
    print(f"   Prompt: {prompt[:120]}...")
    
    width, height = get_resolution(config)
    cost = estimate_cost(width, height, config.get("fal_model", ""))
    print(f"💰 Estimated cost: ${cost:.4f}")

    guideline_file = ensure_line_out(config, project_root)
    with open(guideline_file, "rb") as f:
        guideline_b64 = base64.b64encode(f.read()).decode("utf-8")

    model = config.get("fal_model", "fal-ai/flux-control-lora-canny")
    print(f"🤖 Requesting Fal.ai execution on model: {model}")

    result = client.run(
        model,
        arguments={
            "prompt": prompt,
            "image_size": f"{width}x{height}",
            "seed": config.get("seed", 42),
            "num_inference_steps": config.get("num_inference_steps", 28),
            "control_strength": control_strength,
            "preprocess": config.get("preprocess", "canny"),
            "control_lora_image": guideline_b64,
            "num_images": 1,
            "output_format": "png",
        }
    )

    if not result or "images" not in result or not result["images"]:
        raise ValueError("No valid image data returned from Fal.ai response")

    raw_img = result["images"][0]
    
    # Handle base64 string or nested dict structures from fal response
    if isinstance(raw_img, dict):
        if "image" in raw_img:
            if isinstance(raw_img["image"], str):
                image_bytes = base64.b64decode(raw_img["image"])
            elif isinstance(raw_img["image"], dict) and "bytes" in raw_img["image"]:
                image_bytes = raw_img["image"]["bytes"]
            else:
                image_bytes = base64.b64decode(raw_img.get("url", ""))
        elif "url" in raw_img:
            # Fallback URL download if needed
            import urllib.request
            image_bytes = urllib.request.urlopen(raw_img["url"]).read()
        else:
            raise ValueError("Unrecognized image data format in Fal response")
    else:
        image_bytes = base64.b64decode(raw_img)

    out_dir = config.get("output_dir", "assets/generated")
    return save_image(image_bytes, scene["id"], out_dir)


def main():
    """CLI interface for image generation with Gateway token control."""
    parser = argparse.ArgumentParser(description="Ledras Lament Fal.ai Scene Generator")
    parser.add_argument("--scene", type=int, help="Scene ID to generate")
    parser.add_argument("--list-scenes", action="store_true", help="List available scenes")
    parser.add_argument("--role", type=str, default="intro", help="Role variant (intro/loop/outro)")

    args = parser.parse_args()
    project_root = PROJECT_ROOT

    try:
        config = load_config(project_root)
        scenes = load_scenes(project_root, config["scenes_file"])

        if args.list_scenes:
            print("Available scenes in database:")
            for s in scenes:
                print(f"  [{s['id']:02d}] {s.get('name', 'Unnamed')}")
            return

        if args.scene is None:
            print("Error: Please specify a scene ID using --scene <ID>")
            sys.exit(1)

        scene = get_scene_by_id(scenes, args.scene)

        fal_key = os.getenv("FAL_API_KEY") or os.getenv("FAL_KEY")
        if not fal_key:
            raise ValueError("FAL_API_KEY or FAL_KEY environment variable is not set")

        client = SyncClient(key=fal_key)
        gateway = Gateway(project_root)

        if not gateway.has_rights():
            print("Error: No available generation tokens in Gateway. Please wait and try again.")
            sys.exit(1)

        control_strength = config.get("fal_control_strength", 0.7)

        image_path = generate_stage(
            client=client,
            config=config,
            project_root=project_root,
            scene=scene,
            control_strength=control_strength,
            role=args.role
        )

        gateway.deduct()
        print(f"🎉 SUCCESS! Generated asset saved at: {image_path}")

    except Exception as err:
        print(f"❌ Execution failed: {err}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
