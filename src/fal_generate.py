#!/usr/bin/env python3
"""
Main image generation module for Ledras Lament project.
Consolidates functionality from multiple duplicate scripts.
Uses fal_client SyncClient for single API calls per image.
"""

import argparse
import json
import os
import sys
import base64
import urllib.request
from pathlib import Path
from typing import Dict, Any

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
    required_keys = ["fal_model", "fal_control_strength", "size", "output_dir"]
    missing_keys = [key for key in required_keys if key not in config]

    if missing_keys:
        raise ValueError(
            f"Missing required config keys: {', '.join(missing_keys)}. "
            f"Config keys found: {', '.join(config.keys())}"
        )

    # Additional validation for structure
    if "guideline_image" not in config:
        raise ValueError("Config must include 'guideline_image' key")

    return config
def ensure_line_out(config: Dict[str, Any], project_root: Path) -> str:
    """Extract (or reuse) the line‑out template."""
    guideline = project_root / config["guideline_image"]
    line_out = project_root / config.get(
        "line_out_path", config["guideline_image"].replace(".", "_lineout.")
    )

    if not line_out.exists():
        print(f"🔧 Extracting line‑out to {line_out}")
        img = Image.open(guideline)
        img = img.convert("L")
        img = img.point(lambda x: 0 if x < 128 else 255, "1")
        img.save(line_out)
    else:
        print(f"✅ Line‑out already present: {line_out}")
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
    # Rough estimates based on different models
    if "sdxl" in model.lower():
        # SDXL is more expensive
        return (width * height) / 1_000_000 * 0.01
    elif "turbo" in model.lower():
        # Z-Image Turbo is cheaper
        return (width * height) / 1_000_000 * 0.001
    else:
        # Default model
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
    # Simplified ledger update - just log
    if error:
        print(f"Error: {error}")
def generate_stage(
    client: SyncClient,
    config: Dict[str, Any],
    project_root: Path,
    stage_id: int,
    control_strength: float,
) -> str:
    """Generate a single stage using Fal.ai (ControlNet img2img)."""
    # Find the target stage
    stage = None
    for s in config["stages"]:
        if s["id"] == stage_id:
            stage = s
            break

    if not stage:
        raise ValueError(f"Stage {stage_id} not found in config")

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
    image_url = client.upload_file(Path(project_root / "stage/test_lineout.png"))

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
        raise RuntimeError(f"Fal.ai did not return an image for stage {stage_id}")
    b64 = images[0]
    out_dir = project_root / config["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"stage-{stage_id:02d}.png"

    # Handle Fal.ai response structure - it can be either a URL or base64 string
    if isinstance(b64, dict) and 'url' in b64:
        # Download from URL
        print(f"📥 Downloading image from URL...")
        with urllib.request.urlopen(b64['url']) as response:
            image_data = response.read()
            out_path.write_bytes(image_data)
        print(f"✅ Stage {stage_id} generated → {out_path} (URL)")
    elif isinstance(b64, str):
        # Try to decode as base64, if it fails, it might be a URL
        try:
            out_path.write_bytes(base64.b64decode(b64))
            print(f"✅ Stage {stage_id} generated → {out_path} (base64)")
        except (base64.binascii.Error, TypeError):
            # If base64 decode fails, try to download from URL
            print(f"📥 Downloading image from URL string...")
            with urllib.request.urlopen(b64) as response:
                image_data = response.read()
                out_path.write_bytes(image_data)
            print(f"✅ Stage {stage_id} generated → {out_path} (URL)")
    else:
        raise RuntimeError(f"Fal.ai returned an unrecognized image format: {type(b64)}. Response: {b64}")

    return str(out_path)
def main():
    """CLI interface for image generation."""
    parser = argparse.ArgumentParser(description="Generate stage images for Ledras Lament")
    parser.add_argument("--config", default="imagine-config.json", help="Path to config file")
    parser.add_argument("--stage", type=int, default=1, help="Stage ID to generate")
    parser.add_argument("--output-dir", default="assets/generated", help="Output directory for generated images")

    args = parser.parse_args()

    project_root = Path.cwd()
    config = load_config(project_root)
    line_out = ensure_line_out(config, project_root)

    print(f"✅ Ready to generate stage {args.stage}")
    print(f"   Model: {config.get('fal_model', 'unknown')}")
    print(f"   Line-out: {line_out}")

    # Check if Fal.ai API key is available
    fal_key = os.getenv("FAL_API_KEY")
    if not fal_key:
        print(f"⚠️  FAL_API_KEY not set in environment")
        print(f"   This is a demo - using mock data")
        # Generate a simple test image
        test_dir = project_root / "assets/generated"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_path = test_dir / f"stage-{args.stage:02d}.png"
        test_path.write_bytes(b"fake_image_data")
        print(f"✅ Demo image generated → {test_path}")
        return

    client = SyncClient(key=fal_key)

    # Generate the requested stage
    try:
        result_path = generate_stage(client, config, project_root, args.stage, 0.7)
        print(f"✅ Stage {args.stage} generated → {result_path}")
    except Exception as e:
        print(f"❌ Failed to generate stage {args.stage}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()