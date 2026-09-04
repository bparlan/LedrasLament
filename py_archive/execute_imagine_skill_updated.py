#!/usr/bin/env python3
"""
Imagine skill for the Ledras Lament project.
Now generates **only one image** per execution (default is the first stage in the config,
or a specific stage via `--stage-id`).
Uses Fal.ai (image‑to‑image) with ControlNet, feeding the extracted
`guideline_line_out.png` as the conditioning image so its composition
strongly guides the result.
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
    resp = client.run(model_name, arguments)
    images = resp.get("images") if isinstance(resp, dict) else None
    if not images:
        raise RuntimeError(f"Fal.ai did not return an image for stage {stage['id']}")
    b64 = images[0]
    out_dir = project_root / config["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / find_next_available_id(out_dir, stage["id"])

    # Handle Fal.ai response structure - it can be either a URL or base64 string
    if isinstance(b64, dict) and 'url' in b64:
        # Download from URL
        print(f"📥 Downloading image from URL...")
        with urllib.request.urlopen(b64['url']) as response:
            image_data = response.read()
            out_path.write_bytes(image_data)
        print(f"✅ Stage {stage['id']} generated → {out_path} (URL)")
    elif isinstance(b64, str):
        # Try to decode as base64, if it fails, it might be a URL
        try:
            out_path.write_bytes(base64.b64decode(b64))
            print(f"✅ Stage {stage['id']} generated → {out_path} (base64)")
        except (base64.binascii.Error, TypeError):
            # If base64 decode fails, try to download from URL
            print(f"📥 Downloading image from URL string...")
            with urllib.request.urlopen(b64) as response:
                image_data = response.read()
                out_path.write_bytes(image_data)
            print(f"✅ Stage {stage['id']} generated → {out_path} (URL)")
    else:
        raise RuntimeError(f"Fal.ai returned an unrecognized image format: {type(b64)}. Response: {b64}")

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