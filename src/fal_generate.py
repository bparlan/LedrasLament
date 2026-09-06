#!/usr/bin/env python3
"""
CLI interface for image generation using Fal.ai FLUX Control LoRA Canny.
Implements gateway token system for rate limiting and approval.
"""

import argparse
import base64
import json
import os
import traceback
import urllib.request
from pathlib import Path
from typing import Dict, Any, List

# Fal.ai client (sync)
from fal_client import SyncClient

# Gateway for rate limiting
from src.gateway import Gateway
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
    """Extract (or reuse) the line-out template."""
    guideline_image = config.get("guideline_image", "stage/guideline_line_out.png")
    line_out_path = project_root / guideline_image
    
    if not line_out_path.exists():
        line_out_path = project_root / "stage/guideline_line_out.png"
    
    return str(line_out_path)
def save_image(image_bytes: bytes, scene_id: int, output_dir: str) -> str:
    """Save generated image to file."""
    out_path = Path(output_dir) / f"scene-{scene_id:02d}-v002.png"
    out_path.write_bytes(image_bytes)
    return str(out_path)
def estimate_cost(width: int, height: int, model: str) -> float:
    """Estimate Fal.ai cost based on resolution and model type."""
    if model == "fal-ai/flux-control-lora-canny":
        return (width * height) / 1_000_000 * 0.005
    return (width * height) / 1_000_000 * 0.01
def log_request_to_ledger(model_name: str, arguments: Dict[str, Any]) -> str:
    """Log request to ledger and return request ID."""
    request_id = f"{model_name}_{os.getpid()}_{os.getpid()}"
    print(f"📝 Logged request: {request_id}")
    return request_id
def update_ledger_entry(request_id: str, status: str, response: Any = None, error: str = None):
    """Update ledger entry after API call."""
    if error:
        print(f"❌ Ledger entry {request_id} failed: {error}")
    else:
        print(f"✅ Ledger entry {request_id} updated: {status}")
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
        f"Compose wide shot showing {', '.join(elements[:4])} with depth of field. "
        f"Full moon casting dramatic shadows across stone structure and creating highlight reflections. "
        f"{style.lower()}texture details with weathered limestone surfaces and weathered stone patterns. "
        f"Professional architectural photography composition with strong leading lines. "
        f"Atmospheric depth with distant horizon elements creating spatial depth. "
        f"moody, contemplative, monumental atmosphere with timeless quality. "
        f"--no {negative}"
    )

    prompt = enhanced_prompt

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
        "control_lora_strength": config.get("fal_control_strength", 0.7),
        "control_start": config.get("control_start", 0.4),
        "control_stop": config.get("control_stop", 0.6),
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
    out_path = out_dir / f"scene-{scene_id:02d}-v002.png"

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
    """CLI interface for image generation with gateway rate limiting."""
    parser = argparse.ArgumentParser(
        description="Generate scene images for Ledras Lament with gateway approval"
    )
    parser.add_argument("--config", default="imagine-config.json", 
                       help="Path to config file")
    parser.add_argument("--scene", type=int, default=1,
                       help="Scene ID to generate")
    parser.add_argument("--output-dir", default="assets/generated",
                       help="Output directory for generated images")
    parser.add_argument("--list-scenes", action="store_true",
                       help="List all available scenes")

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

    # Initialize gateway for rate limiting and approval
    g = Gateway()
    
    # Check if generation is allowed (gateway approval)
    if not g.has_rights(1):
        print("❌ Gateway blocked: No generation rights available")
        print(f"   Used: {g.used}, Remaining: {g.rights}")
        return

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
        
        # Deduct token after successful generation (gateway approval)
        try:
            remaining = g.deduct(1)
            print(f"✅ Token deducted: {remaining} rights remaining")
            print(f"   Gateway status: {g.get_status()}")
        except PermissionError as e:
            print(f"❌ Token deduction failed: {e}")
        
    except Exception as e:
        print(f"❌ Failed to generate scene {args.scene}: {e}")
        traceback.print_exc()
if __name__ == "__main__":
    main()
