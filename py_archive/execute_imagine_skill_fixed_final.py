#!/usr/bin/env python3
"""
Imagine skill for the Ledras Lament project.
Fixed Z-Image Turbo ControlNet implementation with resolution constraints.
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

def ensure_line_out(config: dict, project_root: Path) -> str:
    """Extract (or reuse) the line‑out template."""
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

def validate_resolution(width: int, height: int) -> tuple:
    """Validate and enforce 1.0 MP resolution constraint."""
    mp = (width * height) / 1_000_000
    original_width, original_height = width, height
    
    if mp > 1.0:
        # Normalize to 1.0 MP maintaining aspect ratio
        # For 16:9 aspect ratio, use 1280×720 = 0.9216 MP
        if abs(height / width - 9/16) < 0.1:  # ~16:9 aspect ratio
            width, height = 1280, 720
            print(f"⚠️  Resolution normalized: {original_width}x{original_height} -> {width}x{height} ({width*height/1000000:.4f} MP)")
        else:
            # For other aspect ratios, calculate max dimensions
            max_pixels = 1_000_000
            if width > height:
                width = int((max_pixels * width / height) ** 0.5)
                height = int(height * width / original_width)
            else:
                height = int((max_pixels * height / width) ** 0.5)
                width = int(width * height / original_height)
            print(f"⚠️  Resolution normalized: {original_width}x{original_height} -> {width}x{height} ({width*height/1000000:.4f} MP)")
    
    return width, height

def find_next_available_id(out_dir: Path, stage_id: int) -> str:
    """Find the next available ID for a given stage ID to avoid overwriting existing images."""
    import re
    
    pattern = re.compile(rf"stage-{stage_id:02d}-(\d{{3}})\.png$")
    existing_ids = []
    
    if out_dir.exists():
        for file in out_dir.iterdir():
            if file.is_file():
                match = pattern.match(file.name)
                if match:
                    existing_ids.append(int(match.group(1)))
    
    if not existing_ids:
        return f"stage-{stage_id:02d}-001.png"
    
    next_id = max(existing_ids) + 1
    return f"stage-{stage_id:02d}-{next_id:03d}.png"

def calculate_expected_cost(width: int, height: int, num_images: int) -> float:
    """Calculate expected Fal.ai cost based on current Z-Image Turbo pricing."""
    mp_per_image = (width * height) / 1_000_000
    total_mp = mp_per_image * num_images
    # Z-Image Turbo rate: $0.0065 per MP (based on documentation)
    return total_mp * 0.0065

def generate_stage_fal(
    client: SyncClient,
    config: dict,
    project_root: Path,
    stage: dict,
    line_out_path: str,
    control_strength: float,
) -> str:
    """Generate a single stage using Fal.ai (ControlNet img2img)."""
    scene = stage["description"]
    style = config.get("style_seed", "")
    negative = config.get(
        "negative_prompt",
        "blurry, deformed text, extra objects, watermark",
    )
    # Ultra‑short prompt as required by imagegen‑grok
    prompt = (
        f"exact composition, text zones and proportions of line‑out template. {scene}. {style}. --no {negative}"
    )
    width, height = map(int, config["size"].split("x"))
    
    # Validate and enforce 1.0 MP resolution constraint
    width, height = validate_resolution(width, height)
    
    # Upload line-out image to Fal.ai storage to get a URL
    print(f"📤 Uploading line-out image to Fal.ai storage...")
    image_url = client.upload_file(line_out_path)

    arguments = {
        "prompt": prompt,
        "image_url": image_url,
        "strength": control_strength,
        "width": width,
        "height": height,
        "num_images": 1,
    }
    model_name = config.get("fal_model", "fal-ai/z-image/turbo/controlnet")
    
    # DEBUG: Log exact model and parameters before API call
    print(f"🔍 DEBUG: Model = {model_name}")
    print(f"🔍 DEBUG: Image URL = {image_url}")
    print(f"🔍 DEBUG: Arguments = {arguments}")
    
    expected_cost = calculate_expected_cost(width, height, 1)
    print(f"🔍 DEBUG: Expected cost for this request: ${expected_cost:.4f}")
    
    resp = client.run(model_name, arguments)
    images = resp.get("images") if isinstance(resp, dict) else None
    if not images:
        raise RuntimeError(f"Fal.ai did not return an image for stage {stage['id']}")
    img_info = images[0]
    out_dir = project_root / config["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / find_next_available_id(out_dir, stage["id"])

    # FIXED: Proper response parsing for both URL and base64
    if isinstance(img_info, dict) and 'url' in img_info:
        # Download from URL
        print(f"📥 Downloading image from URL: {img_info['url']}")
        with urllib.request.urlopen(img_info['url']) as response:
            image_data = response.read()
            out_path.write_bytes(image_data)
        print(f"✅ Stage {stage['id']} generated → {out_path} (URL)")
    elif isinstance(img_info, str):
        # Handle base64 if present
        try:
            out_path.write_bytes(base64.b64decode(img_info))
            print(f"✅ Stage {stage['id']} generated → {out_path} (base64)")
        except (base64.binascii.Error, TypeError):
            # Fallback to URL string
            print(f"📥 Downloading image from URL string")
            with urllib.request.urlopen(img_info) as response:
                image_data = response.read()
                out_path.write_bytes(image_data)
            print(f"✅ Stage {stage['id']} generated → {out_path} (URL)")
    else:
        raise RuntimeError(f"Unrecognized image format: {type(img_info)}. Response: {img_info}")

    # Verify generated image dimensions
    try:
        with Image.open(out_path) as img:
            actual_width, actual_height = img.size
            actual_mp = (actual_width * actual_height) / 1_000_000
            print(f"✅ Generated image dimensions: {actual_width}x{actual_height} ({actual_mp:.4f} MP)")
            if actual_mp > 1.0:
                print(f"⚠️  WARNING: Generated image exceeds 1.0 MP limit!")
    except Exception as e:
        print(f"⚠️  WARNING: Could not verify image dimensions: {e}")

    return str(out_path)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Imagine skill – generate a single image via Fal.ai (ControlNet)"
    )
    parser.add_argument(
        "--stage-id",
        type=int,
        help="Stage ID to generate (default: first listed in config)",
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
    # Resolve which stage to generate
    if args.stage_id:
        stage = None
        for s in config["stages"]:
            if s["id"] == args.stage_id:
                stage = s
                break
        if not stage:
            print(f"❌ Stage ID {args.stage_id} not found in config")
            sys.exit(1)
    else:
        stage = config["stages"][0]  # default to first entry
    line_out_path = ensure_line_out(config, project_root)
    generate_stage_fal(
        client,
        config,
        project_root,
        stage,
        line_out_path,
        args.control_strength,
    )
    print("🎉 Done – single image generated.")
if __name__ == "__main__":
    main()
