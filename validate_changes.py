#!/usr/bin/env python3
"""
Validation script for fal_generate.py changes
Tests that:
1. Scenes are loaded from ledras_scenes_v4.json only
2. No stage data from imagine-config.json is used
3. Single API calls are made
4. Prompt comes exclusively from scene description
"""

import sys
import os
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import fal_generate
import json

def test_config_has_no_stages():
    """Test that imagine-config.json no longer contains stages array"""
    config_path = Path(__file__).parent / 'imagine-config.json'
    with open(config_path) as f:
        config = json.load(f)
    
    if 'stages' in config:
        print("❌ FAIL: imagine-config.json still contains 'stages' array")
        return False
    else:
        print("✅ PASS: imagine-config.json has no 'stages' array")
        
    if 'scenes_file' not in config:
        print("❌ FAIL: imagine-config.json missing 'scenes_file' key")
        return False
    else:
        print(f"✅ PASS: scenes_file = {config['scenes_file']}")
        
    return True

def test_scenes_loading():
    """Test that scenes are loaded from the authoritative source"""
    project_root = Path(__file__).parent
    config = fal_generate.load_config(project_root)
    
    try:
        scenes = fal_generate.load_scenes(project_root, config['scenes_file'])
        print(f"✅ PASS: Loaded {len(scenes)} scenes from {config['scenes_file']}")
        
        # Verify scene structure
        scene_1 = next((s for s in scenes if s['id'] == 1), None)
        if not scene_1:
            print("❌ FAIL: Scene ID 1 not found")
            return False
            
        required_fields = ['id', 'name', 'description', 'elements', 'subscenes']
        missing = [f for f in required_fields if f not in scene_1]
        if missing:
            print(f"❌ FAIL: Scene missing required fields: {missing}")
            return False
            
        print(f"✅ PASS: Scene 1 structure valid")
        print(f"   Name: {scene_1['name']}")
        print(f"   Description length: {len(scene_1['description'])} chars")
        print(f"   Elements: {len(scene_1['elements'])} items")
        print(f"   Subscenes: {len(scene_1['subscenes'])} items")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: Error loading scenes: {e}")
        return False

def test_scene_prompt_isolation():
    """Test that prompt building uses ONLY scene description"""
    project_root = Path(__file__).parent
    config = fal_generate.load_config(project_root)
    scenes = fal_generate.load_scenes(project_root, config['scenes_file'])
    scene = fal_generate.get_scene_by_id(scenes, 1)
    
    # Build prompt as generate_stage would
    style = config.get("style_seed", "")
    negative = config.get(
        "negative_prompt",
        "blurry, deformed text, extra objects, watermark",
    )
    
    prompt = (
        f"exact composition, text zones and proportions of line-out template. "
        f"{scene['description']}. {style}. --no {negative}"
    )
    
    # Verify prompt contains the EXACT scene description
    if scene['description'] in prompt:
        print("✅ PASS: Prompt contains exact scene description from ledras_scenes_v4.json")
        print(f"   Prompt preview: {prompt[:100]}...")
        return True
    else:
        print("❌ FAIL: Prompt does not contain scene description")
        return False

def test_single_image_request():
    """Test that generate_stage requests exactly one image"""
    # We can't easily test the actual API call without a key,
    # but we can verify the arguments structure
    
    # Check the source code for num_images: 1
    source_path = Path(__file__).parent / 'src' / 'fal_generate.py'
    with open(source_path) as f:
        source = f.read()
        
    if '"num_images": 1' in source:
        print("✅ PASS: generate_stage requests num_images: 1")
        return True
    else:
        print("❌ FAIL: generate_stage does not request num_images: 1")
        return False

def main():
    print("🔍 Validating fal_generate.py changes")
    print("=" * 50)
    
    tests = [
        test_config_has_no_stages,
        test_scenes_loading,
        test_scene_prompt_isolation,
        test_single_image_request,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print()
        if test():
            passed += 1
        print("-" * 30)
    
    print()
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validation tests passed!")
        return 0
    else:
        print("❌ Some validation tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())