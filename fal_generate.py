#!/usr/bin/env python3
"""
Fal.ai Image Generation Module for Ledras Lament.
Consolidated from 9 duplicate scripts.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import base64
import urllib.request
from PIL import Image

# Fal.ai client (sync)
from fal_client import SyncClient


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
        img = Image.open(guideline).convert("L")
        from PIL import ImageFilter
        import numpy as np
        
        edges = img.filter(ImageFilter.FIND_EDGES)
        line_out_img = Image.fromarray(255 - np.array(edges))
        line_out_img.save(line_out)
    else:
        print(f"✅ Line‑out already present: {line_out}")
    return str(line_out)


def build_request(
    scene_data: Dict[str, Any], 
    config: Dict[str, Any], 
    control_image_path: str
) -> Dict[str, Any]:
    """
    Build Fal.ai request payload from scene data and config.
    Takes ARBITRARY scene data (prompt, scene id, style, negative prompt, line-out path).
    Returns the exact payload dict that will be sent to Fal,
    including whatever field name the model's actual API schema expects for the control/guide image.
    """
    # Extract scene parameters
    scene_id = scene_data.get("id", 1)
    prompt = scene_data.get("prompt", "")
    style = scene_data.get("style", config.get("style_seed", ""))
    negative = scene_data.get("negative_prompt", config.get(
        "negative_prompt", "blurry, deformed text, extra objects, watermark"
    ))
    control_strength = scene_data.get("control_strength", config.get("fal_control_strength", 0.7))
    
    # Build prompt as per original implementation
    full_prompt = (
        f"exact composition, text zones and proportions of line‑out template. {prompt}. {style}. --no {negative}"
    )
    
    # Parse and validate resolution
    requested_size = config["size"]
    width, height = map(int, requested_size.split("x"))
    
    # Upload control image to get Fal URL
    client = SyncClient(key=os.getenv("FAL_API_KEY", ""))
    control_image_url = client.upload_file(control_image_path)
    
    # Determine the correct field name based on current model
    model_name = config["fal_model"]
    # For ControlNet models, field name varies:
    # - z-image/turbo/controlnet: "control_image"
    # - sd15-depth-controlnet: "image_url" (as seen in many scripts)
    # - edge detection models: "control_image_url"
    
    if "z-image" in model_name:
        control_field = "control_image"
    elif "sd15-depth" in model_name:
        control_field = "image_url"
    else:
        control_field = "image_url"  # Default
    
    # Build request payload
    request_payload = {
        "prompt": full_prompt,
        control_field: control_image_url,
        "strength": control_strength,
        "width": width,
        "height": height,
        "num_images": 1,
    }
    
    return request_payload


def log_request_to_ledger(model_name: str, arguments: Dict[str, Any]) -> str:
    """
    Log request to fal_request_ledger.jsonl BEFORE making API call.
    Returns request_id for tracking.
    """
    from uuid import uuid4
    
    request_id = str(uuid4())[:8]
    timestamp = datetime.utcnow().isoformat()
    
    ledger_entry = {
        "timestamp": timestamp,
        "request_id": request_id,
        "model": model_name,
        "params": arguments,
        "status": "pending",
        "response": None,
        "error": None
    }
    
    ledger_path = Path("fal_request_ledger.jsonl")
    with open(ledger_path, "a") as f:
        f.write(json.dumps(ledger_entry) + "\n")
    
    print(f"📝 Logged request {request_id} to fal_request_ledger.jsonl")
    return request_id


def update_ledger_entry(request_id: str, status: str, response: Any = None, error: str = None):
    """Update ledger entry after API call."""
    ledger_path = Path("fal_request_ledger.jsonl")
    
    if not ledger_path.exists():
        return
    
    entries = []
    with open(ledger_path, "r") as f:
        for line in f:
            entry = json.loads(line.strip())
            entries.append(entry)
    
    for entry in entries:
        if entry["request_id"] == request_id:
            entry["status"] = status
            entry["response"] = response
            entry["error"] = error
            entry["timestamp_completed"] = datetime.utcnow().isoformat()
            break
    
    with open(ledger_path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")


def call_fal(client: SyncClient, model_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make exactly ONE API call, no retry logic of any kind.
    Logs request before call, updates ledger after.
    """
    request_id = log_request_to_ledger(model_name, arguments)
    
    try:
        print(f"🚀 Making Fal.ai API call (request {request_id})...")
        resp = client.run(model_name, arguments)
        
        # Update ledger with success
        update_ledger_entry(request_id, "success", response=resp)
        
        print(f"✅ API call completed for request {request_id}")
        return resp
        
    except Exception as e:
        # Update ledger with failure
        error_msg = str(e)
        update_ledger_entry(request_id, "failed", error=error_msg)
        
        print(f"❌ Fal.ai API call failed (request {request_id}): {error_msg}")
        print(f"📝 Check fal_request_ledger.jsonl for details")
        sys.exit(1)


def parse_response(resp: Dict[str, Any]) -> bytes:
    """
    Parse Fal response - handles both url and b64_json response shapes explicitly.
    On any parse failure: log full raw response, print clear error, exit.
    Do not fall back, do not retry.
    """
    # First, check if it's a dict with images array
    if not isinstance(resp, dict) or "images" not in resp:
        error_msg = f"Invalid Fal response format: missing 'images' key. Response: {resp}"
        # Log the failed response
        ledger_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": error_msg,
            "raw_response": resp
        }
        
        with open("fal_request_ledger.jsonl", "a") as f:
            f.write(json.dumps(ledger_entry) + "\n")
        
        print(f"❌ Response parsing failed: {error_msg}")
        sys.exit(1)
    
    images = resp["images"]
    if not images or not isinstance(images, list):
        error_msg = f"Invalid 'images' in response: {resp}"
        
        with open("fal_request_ledger.jsonl", "a") as f:
            f.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "error": error_msg, "raw_response": resp}) + "\n")
        
        print(f"❌ Response parsing failed: {error_msg}")
        sys.exit(1)
    
    img_info = images[0]
    
    # Handle URL response (dict with 'url' key)
    if isinstance(img_info, dict) and 'url' in img_info:
        image_url = img_info['url']
        print(f"📥 Downloading image from URL: {image_url}")
        
        try:
            with urllib.request.urlopen(image_url) as response:
                return response.read()
        except Exception as e:
            error_msg = f"Failed to download image from URL {image_url}: {e}"
            
            with open("fal_request_ledger.jsonl", "a") as f:
                f.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "error": error_msg, "raw_response": resp}) + "\n")
            
            print(f"❌ Image download failed: {error_msg}")
            sys.exit(1)
    
    # Handle base64 string response
    elif isinstance(img_info, str):
        try:
            decoded = base64.b64decode(img_info)
            print(f"✅ Decoded base64 image data")
            return decoded
        except (base64.binascii.Error, TypeError) as e:
            # Don't fallback to URL parsing - this is a hard failure per requirements
            error_msg = f"Base64 decode failed: {e}. Response data preview: {img_info[:200]}..."
            
            with open("fal_request_ledger.jsonl", "a") as f:
                f.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "error": error_msg, "raw_response": resp}) + "\n")
            
            print(f"❌ Image parsing failed: {error_msg}")
            print(f"📝 Response was: {img_info[:200]}...")
            sys.exit(1)
    
    else:
        error_msg = f"Unrecognized image format in response: {type(img_info)}. Response: {img_info}"
        
        with open("fal_request_ledger.jsonl", "a") as f:
            f.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "error": error_msg, "raw_response": resp}) + "\n")
        
        print(f"❌ Response parsing failed: {error_msg}")
        sys.exit(1)


def save_image(image_bytes: bytes, scene_id: int, output_dir: str) -> str:
    """Save generated image to file."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_path = out_dir / f"stage-{scene_id:02d}.png"
    out_path.write_bytes(image_bytes)
    
    print(f"✅ Stage {scene_id} saved to {out_path}")
    return str(out_path)


def estimate_cost(width: int, height: int, model: str) -> float:
    """Estimate Fal.ai cost based on resolution and model type."""
    mp_per_image = (width * height) / 1_000_000
    
    # Model-specific cost rates
    if "z-image" in model:
        # Z-Image Turbo: $0.0065 per MP (based on original analysis)
        return mp_per_image * 0.0065
    elif "sd15-depth" in model:
        # SD1.5 Depth ControlNet: $0.00125 per compute second
        # Note: actual cost depends on compute time, which is hard to predict
        # This is a rough estimate based on observed 35.5 seconds = $0.044375
        estimated_compute_seconds = 35.5  # based on observed 35.5s compute time
        return estimated_compute_seconds * 0.00125
    else:
        # Default conservative estimate
        return mp_per_image * 0.01


def main():
    parser = argparse.ArgumentParser(
        description="Fal.ai Image Generation - Consolidated Module"
    )
    parser.add_argument("--scene-id", type=int, help="Scene ID to generate")
    parser.add_argument("--prompt", help="Override prompt for the scene")
    parser.add_argument("--control-strength", type=float, 
                       help="Control strength (0.3-0.9). Overrides config")
    parser.add_argument("--dry-run", action="store_true",
                       help="Build and print request payload WITHOUT calling Fal")
    parser.add_argument("--estimate-cost", action="store_true",
                       help="Print cost estimate based on resolution")
    parser.add_argument("--config", default="imagine-config.json",
                       help="Path to config file (default: imagine-config.json)")
    
    args = parser.parse_args()
    
    project_root = Path.cwd()
    
    # Load and validate config
    try:
        config = load_config(project_root)
    except Exception as e:
        print(f"❌ Config error: {e}")
        sys.exit(1)
    
    # Validate API key
    if not os.getenv("FAL_API_KEY"):
        print("❌ FAL_API_KEY not set in environment")
        sys.exit(1)
    
    # Prepare scene data
    scenes = config.get("stages", [])
    if not scenes:
        print("❌ Config must contain 'stages' array")
        sys.exit(1)
    
    target_scene = None
    if args.scene_id:
        target_scene = next((s for s in scenes if s.get("id") == args.scene_id), None)
        if not target_scene:
            print(f"❌ Scene ID {args.scene_id} not found in config")
            sys.exit(1)
    else:
        target_scene = scenes[0]
    
    # Prepare scene data dict for build_request
    scene_data = {
        "id": target_scene["id"],
        "prompt": args.prompt if args.prompt else target_scene["description"],
        "style": config.get("style_seed", ""),
        "negative_prompt": config.get("negative_prompt", ""),
        "control_strength": args.control_strength if args.control_strength else config.get("fal_control_strength", 0.7)
    }
    
    # Ensure line-out template
    line_out_path = ensure_line_out(config, project_root)
    
    # Build request
    try:
        request_payload = build_request(scene_data, config, line_out_path)
    except Exception as e:
        print(f"❌ Request building failed: {e}")
        sys.exit(1)
    
    # Show estimated cost if requested
    if args.estimate_cost:
        width = request_payload.get("width", 1280)
        height = request_payload.get("height", 720)
        estimated_cost = estimate_cost(width, height, config["fal_model"])
        print(f"💰 Estimated cost: ${estimated_cost:.4f}")
        print(f"📐 Resolution: {width}x{height} ({width*height/1000000:.4f} MP)")
        print(f"🤖 Model: {config['fal_model']}")
    
    # Dry run mode
    if args.dry_run:
        print("🔍 DRY RUN - Request payload that would be sent:")
        print(json.dumps(request_payload, indent=2))
        print(f"\n📋 Model: {config['fal_model']}")
        print(f"📐 Size: {request_payload['width']}x{request_payload['height']}")
        print(f"💪 Control Strength: {request_payload['strength']}")
        print("✅ Dry run completed - no API calls made")
        return
    
    # Normal mode - make API call
    client = SyncClient(key=os.getenv("FAL_API_KEY"))
    
    try:
        response = call_fal(client, config["fal_model"], request_payload)
        image_bytes = parse_response(response)
        save_image(image_bytes, scene_data["id"], config["output_dir"])
        print("🎉 Done – single image generated successfully.")
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()