#!/usr/bin/env python3
"""
Generate image for a specific scene using Fal.ai ControlNet.
Uses ledras_scenes_v4.json for scene description (includes base amphitheater structure).
"""

import argparse
import os
import sys
import json
import base64
import urllib.request
from pathlib import Path

from PIL import Image, ImageFilter
import numpy as np

# Fal.ai client (sync)
from fal_client import SyncClient

def load_config(project_root: Path) -> dict:
    """Load imagination config from `imagine-config.json`."""
    cfg_path = project_root / "imagine-config.json"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_scenes(project_root: Path) -> list:
    """Load scenes from ledras_scenes_v4.json."""
    scenes_path = project_root / "ledras_scenes_v4.json"
    with open(scenes_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["scenes"]

def ensure_line_out(config: dict, project_root: Path) -> str:
    """Extract (or reuse) the line‑out template.
    The line‑out is a black‑white edge image derived from the guideline.
    """
    guideline = project_root / config["guideline_image"]
    line_out = project_root / config.get(
        "line_out_path", config["guideline_image"].replace(".", "_lineout.")
    )
    if not line_out.exists():
        print(f"🔧 Extracting line‑out to {line_out}")
        img = Image.open(guideline).convert("L")
        edges = img.filter(ImageFilter.FIND_EDGES)
        line_out_img = Image.fromarray(255 - np.array(edges))
        line_out_img.save(line_out)
    else:
        print(f"✅ Line‑out already present: {line_out}")
    return str(line_out)

def find_next_available_id(out_dir: Path, scene_id: int) -> str:
    """Find the next available ID for a given scene ID to avoid overwriting existing images."""
    import re
    
    pattern = re.compile(rf"stage-{scene_id:02d}-(\d{{3}})\.png$")
    existing_ids = []
    
    if out_dir.exists():
        for file in out_dir.iterdir():
            if file.is_file():
                match = pattern.match(file.name)
                if match:
                    existing_ids.append(int(match.group(1)))
    
    if not existing_ids:
        return f"stage-{scene_id:02d}-001.png"
    
    next_id = max(existing_ids) + 1
    return f"stage-{scene_id:02d}-{next_id:03d}.png"

def generate_stage_fal(
    client: SyncClient,
    config: dict,
    project_root: Path,
    scene: dict,
    line_out_path: str,
    control_strength: float,
) -> str:
    """Generate a single stage using Fal.ai (ControlNet img2img)."""
    scene_desc = scene["description"]
    style = config.get("style_seed", "")
    negative = config.get(
        "negative_prompt",
        "blurry, deformed text, extra objects, watermark",
    )
    # Ultra‑short prompt as required by imagegen‑grok
    prompt = (
        f"exact composition, text zones and proportions of line‑out template. {scene_desc}. {style}. --no {negative}"
    )
    width, height = map(int, config["size"].split("x"))

    # Upload line-out image to Fal.ai storage to get a URL
    print(f"📤 Uploading line-out image to Fal.ai storage...")
    image_url = client.upload_file(line_out_path)

    # Override model to sd15-depth-controlnet as requested
    config["fal_model"] = "fal-ai/sd15-depth-controlnet"
    model_name = config["fal_model"]

    arguments = {
        "prompt": prompt,
        "control_image_url": image_url,
        "strength": control_strength,
        "width": width,
        "height": height,
        "num_images": 1,
    }
    
    # DEBUG: Log exact model and control_image_url parameter before API call
    print(f"🔍 DEBUG: Model = {model_name}")
    print(f"🔍 DEBUG: Control image URL = {image_url}")
    print(f"🔍 DEBUG: Arguments keys = {list(arguments.keys())}")
    
    resp = client.run(model_name, arguments)
    images = resp.get("images") if isinstance(resp, dict) else None
    if not images:
        raise RuntimeError(f"Fal.ai did not return an image for scene {scene['id']}")
    img_info = images[0]
    out_dir = project_root / config["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / find_next_available_id(out_dir, scene["id"])

    # FIXED: Proper response parsing for both URL and base64
    if isinstance(img_info, dict) and 'url' in img_info:
        # Download from URL
        print(f"📥 Downloading image from URL: {img_info['url']}")
        with urllib.request.urlopen(img_info['url']) as response:
            image_data = response.read()
            out_path.write_bytes(image_data)
        print(f"✅ Scene {scene['id']} generated → {out_path} (URL)")
    elif isinstance(img_info, str):
        # Handle base64 if present
        try:
            out_path.write_bytes(base64.b64decode(img_info))
            print(f"✅ Scene {scene['id']} generated → {out_path} (base64)")
        except (base64.binascii.Error, TypeError):
            # Fallback to URL string
            print(f"📥 Downloading image from URL string")
            with urllib.request.urlopen(img_info) as response:
                image_data = response.read()
                out_path.write_bytes(image_data)
            print(f"✅ Scene {scene['id']} generated → {out_path} (URL)")
    else:
        raise RuntimeError(f"Unrecognized image format: {type(img_info)}. Response: {img_info}")

    return str(out_path)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate image for a specific scene using Fal.ai ControlNet"
    )
    parser.add_argument(
        "--scene-id",
        type=int,
        required=True,
        help="Scene ID to generate (from ledras_scenes_v4.json)",
    )
    parser.add_argument(
        "--control-strength",
        type=float,
        default=0.7,
        help="ControlNet strength (0.3‑0.9). Higher values keep the line‑out more faithfully.",
    )
    args = parser.parse_args()
    if not (0.3 <= args.control_strength <= 0.9):
        print("❌ control-strength must be between 0.3 and 0.9")
        sys.exit(1)
    fal_key = os.getenv("FAL_API_KEY")
    if not fal_key:
        print("❌ FAL_API_KEY not set in environment")
        sys.exit(1)
    client = SyncClient(key=fal_key)
    project_root = Path.cwd()
    config = load_config(project_root)
    scenes = load_scenes(project_root)
    # Find scene
    scene = None
    for s in scenes:
        if s["id"] == args.scene_id:
            scene = s
            break
    if not scene:
        print(f"❌ Scene ID {args.scene_id} not found in ledras_scenes_v4.json")
        sys.exit(1)
    line_out_path = ensure_line_out(config, project_root)
    generate_stage_fal(
        client,
        config,
        project_root,
        scene,
        line_out_path,
        args.control_strength,
    )
    print("🎉 Done – single image generated.")

if __name__ == "__main__":
    main()
