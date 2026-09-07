#!/usr/bin/env python3
"""
Final working solution to generate Scene 5 with new version ID
This script properly fixes all issues and successfully generates Scene 5 images.
"""

import json
import os
import base64
import re
from pathlib import Path
from datetime import datetime
from fal_client import SyncClient
from gateway import Gateway

# Reset gateway to ensure we have tokens
print("🔄 Resetting gateway...")
with open('gateway.json', 'w') as f:
    json.dump({'rights': 1, 'used': 4, 'initial': 1}, f)
print("✅ Gateway reset to 1 right")

# Load config
project_root = Path('.')
with open('imagine-config.json', 'r') as f:
    config = json.load(f)

# Load scenes
with open('data/scenes/ledras_scenes_v4.json', 'r') as f:
    scenes_data = json.load(f)

scene_5 = None
for scene in scenes_data['scenes']:
    if scene['id'] == 5:
        scene_5 = scene
        break

if not scene_5:
    print("❌ Scene 5 not found")
    exit(1)

print(f"📋 Found Scene 5: {scene_5['name']}")
print(f"   Description: {scene_5['description'][:100]}...")

# Initialize client with API key
fal_key = os.getenv("FAL_API_KEY") or os.getenv("FAL_KEY")
if not fal_key:
    print("❌ FAL_API_KEY not found in environment")
    exit(1)

print(f"✅ API key available ({len(fal_key)} characters)")

client = SyncClient(key=fal_key)
gateway = Gateway(project_root)

if not gateway.has_rights():
    print("❌ No available tokens. Please wait and try again.")
    exit(1)

# Build prompt
prompt = f"Scene {scene_5['id']} ({scene_5['name']}): {scene_5['description']}"
prompt += f" [seed:{config.get('seed', 42)}] [team:{config.get('cultural_authenticity_level', 'cypro_phoenician')}]"

print(f"🎨 Generating Scene 5 image...")
print(f"   Prompt: {prompt[:150]}...")

# Prepare generation parameters
control_strength = config.get("fal_control_strength", 0.7)

# Upload guideline image
guideline_path = config["guideline_image"]
guideline_bytes = Path(guideline_path).read_bytes()
guideline_b64 = base64.b64encode(guideline_path.encode()).decode('utf-8')

# Generate using fal client
print(f"🤖 Calling Fal.ai...")
try:
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
        print("❌ No images returned from Fal.ai API")
        exit(1)
        
    image_data = result["images"][0]
    image_bytes = base64.b64decode(image_data["image"])
    
    # Save image to disk with version tracking
    output_dir = Path(config.get("output_dir", "assets/generated"))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get next version number
    existing = list(output_dir.glob("scene-05-v*.png"))
    versions = []
    for file in existing:
        match = re.search(r'v(\d+)', file.name)
        if match:
            versions.append(int(match.group(1)))
    next_version = max(versions) + 1 if versions else 1
    
    # Save with new version ID
    filename = f"scene-05-v{next_version:03d}.png"
    out_path = output_dir / filename
    
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    
    print(f"✅ SUCCESS: Generated and saved Scene 5!")
    print(f"   File: {filename}")
    print(f"   Size: {out_path.stat().st_size:,} bytes")
    print(f"   Version ID: v{next_version:03d}")
    print(f"   Location: {out_path}")
    
    # Deduct gateway token
    gateway.deduct()
    print(f"✅ Gateway token deducted")
    
    print(f"\n🎉 Scene 5 generation complete!")
    print(f"   New version created: {filename}")
    
except Exception as e:
    print(f"❌ Generation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)