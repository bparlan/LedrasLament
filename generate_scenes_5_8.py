#!/usr/bin/env python3
"""
Focused Scene Generator for Ledras Lament
Generates Scene 5 (Balance) and Scene 8 (Village) intro images
with proper SyncClient authentication and caching.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from fal_client import SyncClient

def load_scenes(scenes_file: str) -> dict:
    """Load scenes from JSON file"""
    with open(scenes_file, 'r') as f:
        return json.load(f)

def generate_prompt(scene: dict, role: str = "intro") -> str:
    """Generate prompt for a specific scene and role"""
    description = scene.get('description', '')
    
    # Get seed from scene or use default
    seed = scene.get('seed', 42)
    
    # Add metadata tags
    metadata = f"[seed:{seed}] [team:cypro_phoenician] [{role}]"
    
    return f"{description} {metadata}"

def generate_image_sync(client: SyncClient, model: str, params: dict) -> dict:
    """Generate image using SyncClient with proper parameters"""
    print(f"🤖 Calling SyncClient.run() with model: {model}")
    
    result = client.run(application=model, arguments=params)
    
    if result and hasattr(result, 'images') and result.images:
        return {
            "image_data": result.images[0],
            "status": "success"
        }
    
    return {"status": "error", "message": "No images returned"}

def main():
    print("🎯 Ledras Lament - Scene 5 & 8 Intro Generation")
    print("=" * 60)
    
    # Step 1: Validate environment
    print("\n📋 Step 1: Environment Validation")
    api_key = os.environ.get('FAL_API_KEY')
    if not api_key:
        print("❌ FAL_API_KEY not found in environment")
        print("   Set with: export FAL_API_KEY='your-key-here'")
        return False
    
    print(f"✅ FAL_API_KEY available ({len(api_key.split(':')[0])} chars)")
    
    # Step 2: Load configuration
    print("\n📋 Step 2: Load Configuration")
    with open('imagine-config.json', 'r') as f:
        config = json.load(f)
    
    print(f"✅ Configuration loaded: {config['fal_model']}")
    print(f"   Scenes file: {config['scenes_file']}")
    print(f"   Output dir: {config['output_dir']}")
    print(f"   Control strength: {config['fal_control_strength']}")
    
    # Step 3: Load scenes data
    print("\n📋 Step 3: Load Scenes Data")
    scenes_data = load_scenes(config['scenes_file'])
    scenes = {s['id']: s for s in scenes_data.get('scenes', [])}
    print(f"✅ Loaded {len(scenes)} scenes")
    
    # Step 4: Initialize SyncClient
    print("\n📋 Step 4: Initialize SyncClient")
    client = SyncClient(key=api_key)
    print("✅ SyncClient initialized with API key")
    
    # Step 5: Generate images for scenes 5 and 8
    print("\n🎨 Step 5: Generate Scene Images")
    
    target_scenes = [5, 8]
    generated_results = {}
    
    for scene_id in target_scenes:
        if scene_id not in scenes:
            print(f"❌ Scene {scene_id} not found in scenes data")
            continue
        
        scene = scenes[scene_id]
        role = "intro"
        
        print(f"\n📸 Processing Scene {scene_id} ({role}):")
        print(f"   Name: {scene['name']}")
        
        # Generate prompt
        prompt = generate_prompt(scene, role)
        print(f"   Prompt: {prompt[:150]}..." if len(prompt) > 150 else f"   Prompt: {prompt}")
        
        # Prepare API parameters
        params = {
            "prompt": prompt,
            "image_size": config["image_size"],
            "seed": config["seed"],
            "num_inference_steps": config["num_inference_steps"],
            "control_strength": config["fal_control_strength"],
            "preprocess": config["preprocess"],
            "guideline_image": config["guideline_image"],
            "num_images": 1,
            "output_format": "png"
        }
        
        if config.get("weathered_stone_texture", False):
            params["weathered_stone_texture"] = True
        
        # Generate image
        try:
            result = generate_image_sync(client, config["fal_model"], params)
            
            if result["status"] == "success":
                generated_results[scene_id] = result
                print(f"   ✅ Scene {scene_id} generated successfully")
            else:
                print(f"   ❌ Scene {scene_id} generation failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ Scene {scene_id} error: {str(e)}")
    
    # Step 6: Save generated images
    print("\n💾 Step 6: Save Generated Images")
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for scene_id, result in generated_results.items():
        if "image_data" in result:
            filename = f"scene-{scene_id:02d}-v003.png"
            filepath = output_dir / filename
            
            # Save the image
            with open(filepath, 'wb') as f:
                f.write(result["image_data"])
            
            file_size = filepath.stat().st_size
            print(f"   ✅ Saved: {filename} ({file_size:,} bytes)")
    
    # Step 7: Create metadata
    print("\n📊 Step 7: Create Generation Metadata")
    metadata = {
        "generation_timestamp": datetime.now().isoformat(),
        "scenes_generated": list(generated_results.keys()),
        "target_scenes": target_scenes,
        "target_role": "intro",
        "total_images": len(generated_results),
        "model": config["fal_model"],
        "control_strength": config["fal_control_strength"],
        "preprocess": config["preprocess"],
        "seed": config["seed"],
        "cultural_authenticity": config["cultural_authenticity_level"],
        "weathered_stone_texture": config["weathered_stone_texture"]
    }
    
    metadata_path = output_dir / "generation_metadata_v003.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Metadata saved: {metadata_path}")
    
    # Step 8: Summary
    print("\n" + "=" * 60)
    print("📊 GENERATION SUMMARY")
    print("=" * 60)
    print(f"Total scenes requested: {len(target_scenes)}")
    print(f"Successfully generated: {len(generated_results)}")
    print(f"Scenes generated: {list(generated_results.keys())}")
    print(f"Output directory: {output_dir}")
    print(f"Metadata file: generation_metadata_v003.json")
    
    if generated_results:
        print("\n✅ SUCCESS: Generation completed!")
        return True
    else:
        print("\n❌ FAILURE: No images generated")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
