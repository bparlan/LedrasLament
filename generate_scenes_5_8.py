#!/usr/bin/env python3
"""
Focused Scene Generator for Ledras Lament - Fixed Image Size and Asset Upload
Generates Scene 5 (Balance) and Scene 8 (Village) intro images
with proper SyncClient authentication and asset uploading.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from fal_client import SyncClient, upload_file

def load_scenes(scenes_file: str) -> dict:
    """Load scenes from JSON file"""
    with open(scenes_file, 'r') as f:
        return json.load(f)

def generate_prompt(scene: dict, role: str = "intro") -> str:
    """Generate prompt for a specific scene and role"""
    description = scene.get('description', '')
    seed = scene.get('seed', 42)
    metadata = f"[seed:{seed}] [team:cypro_phoenician] [{role}]"
    return f"{description} {metadata}"

def main():
    print("🎯 Ledras Lament - Scene 5 & 8 Intro Generation (Fixed)")
    print("=" * 60)
    
    # Step 1: Validate environment
    api_key = os.environ.get('FAL_API_KEY')
    if not api_key:
        print("❌ FAL_API_KEY not found in environment")
        return False
    print(f"✅ FAL_API_KEY available")
    
    # Step 2: Load configuration
    with open('imagine-config.json', 'r') as f:
        config = json.load(f)
    print(f"✅ Configuration loaded: {config['fal_model']}")
    
    # Step 3: Load scenes data
    scenes_data = load_scenes(config['scenes_file'])
    scenes = {s['id']: s for s in scenes_data.get('scenes', [])}
    print(f"✅ Loaded {len(scenes)} scenes")
    
    # Step 4: Initialize SyncClient
    client = SyncClient(key=api_key)
    print("✅ SyncClient initialized with API key")
    
    # Step 5: Upload guideline image to fal storage
    guideline_path = config["guideline_image"]
    if os.path.exists(guideline_path):
        print(f"📤 Uploading guideline image to fal storage: {guideline_path}")
        guideline_url = client.upload_file(guideline_path)
        print(f"✅ Guideline image uploaded successfully: {guideline_url}")
    else:
        print(f"❌ Guideline image not found at {guideline_path}")
        return False
    
    # Step 6: Generate images for scenes 5 and 8
    target_scenes = [5, 8]
    generated_results = {}
    
    for scene_id in target_scenes:
        if scene_id not in scenes:
            continue
        
        scene = scenes[scene_id]
        role = "intro"
        print(f"\n📸 Processing Scene {scene_id} ({role}): {scene['name']}")
        
        prompt = generate_prompt(scene, role)
        print(f"   Prompt: {prompt[:100]}...")
        
        # Prepare API parameters with correct image_size dictionary and uploaded control_lora_image_url
        params = {
            "prompt": prompt,
            "image_size": {
                "width": 1280,
                "height": 720
            },
            "seed": config["seed"],
            "num_inference_steps": config["num_inference_steps"],
            "control_strength": config["fal_control_strength"],
            "preprocess": config["preprocess"],
            "control_lora_image_url": guideline_url,
            "num_images": 1,
            "output_format": "png"
        }
        
        if config.get("weathered_stone_texture", False):
            params["weathered_stone_texture"] = True
        
        try:
            print(f"🤖 Calling SyncClient.run() with model: {config['fal_model']}")
            result = client.run(
                application=config["fal_model"],
                arguments=params
            )
            
            if result and hasattr(result, 'images') and result.images:
                generated_results[scene_id] = {
                    "image_data": result.images[0],
                    "status": "success"
                }
                print(f"   ✅ Scene {scene_id} generated successfully")
            else:
                print(f"   ❌ Scene {scene_id} generation failed: No images returned")
                
        except Exception as e:
            print(f"   ❌ Scene {scene_id} error: {str(e)}")
    
    # Step 7: Save generated images
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for scene_id, result in generated_results.items():
        if "image_data" in result and isinstance(result["image_data"], dict) and "url" in result["image_data"]:
            import urllib.request
            image_url = result["image_data"]["url"]
            filename = f"scene-{scene_id:02d}-v003.png"
            filepath = output_dir / filename
            
            print(f"📥 Downloading image from {image_url}")
            urllib.request.urlretrieve(image_url, filepath)
            
            file_size = filepath.stat().st_size
            print(f"   ✅ Saved: {filename} ({file_size:,} bytes)")
    
    # Step 8: Save metadata
    metadata = {
        "generation_timestamp": datetime.now().isoformat(),
        "scenes_generated": list(generated_results.keys()),
        "target_scenes": target_scenes,
        "target_role": "intro",
        "total_images": len(generated_results),
        "model": config["fal_model"]
    }
    
    metadata_path = output_dir / "generation_metadata_v003.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Generation complete! Generated {len(generated_results)} images.")
    return len(generated_results) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
