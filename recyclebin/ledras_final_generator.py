#!/usr/bin/env python3
"""
Ledras Lament Scene Generator - Fixed version that works correctly
Generates Scene 5 with proper API key handling and image saving.
"""

import json
import os
import base64
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from fal_client import SyncClient

# Gateway for rate limiting
from gateway import Gateway

def load_config(project_root: Path) -> Dict[str, Any]:
    """Load imagination config from ."""
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
    """Get next version number for a scene to avoid overwriting"""
    existing = list(output_dir.glob(f"scene-{scene_id:02d}-v*.png"))
    if not existing:
        return 1
    versions = []
    for file in existing:
        import re
        match = re.search(r'v(\d+)', file.name)
        if match:
            versions.append(int(match.group(1)))
    return max(versions) + 1

def save_image(image_bytes: bytes, scene_id: int, output_dir: str) -> str:
    """Save generated image to file with version tracking to prevent overwrites."""
    output_path = Path(output_dir)
    version = get_next_version_number(output_path, scene_id)
    
    out_path = output_path / f"scene-{scene_id:02d}-v{version:03d}.png"
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    
    print(f"✅ Saved image: {out_path.name} ({out_path.stat().st_size:,} bytes)")
    return str(out_path)

def generate_prompt(scene: Dict[str, Any], config: Dict[str, Any]) -> str:
    """Generate prompt for a scene"""
    prompt = f"Scene {scene['id']} ({scene['name']}): {scene['description']}"
    prompt += f" [seed:{config.get('seed', 42)}] [team:{config.get('cultural_authenticity_level', 'cypro_phoenician')}]"
    return prompt

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

        # Build prompt
        prompt = generate_prompt(scene, config)
        print(f"🎨 Generating scene {scene['id']}: {scene['name']}")
        print(f"   Prompt: {prompt[:100]}...")

        # Upload guideline image
        guideline_path = ensure_line_out(config, project_root)
        guideline_bytes = Path(guideine_path).read_bytes()
        guideline_b64 = base64.b64encode(guideine_path).decode('utf-8')

        # Generate using fal client with control LoRA
        print(f"🤖 Calling Fal.ai with model: {config.get("fal_model", "fal-ai/flux-control-lora-canny")}")
        
        result = client.run(
            config.get("fal_model", "fal-ai/flux-control-lora-canny"),
            arguments={
                "prompt": prompt,
                "image_size": "1280x720",
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
            raise ValueError("No images returned from Fal.ai API")

        image_data = result["images"][0]
        image_bytes = base64.b64decode(image_data["image"])
        
        # Save image to file
        image_path = save_image(image_bytes, scene["id"], config.get("output_dir", "assets/generated"))
        
        print(f"✅ Generated image: {image_path}")
        gateway.deduct()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    import argparse
    main()
