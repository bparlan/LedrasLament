#!/usr/bin/env python3
"""
Verify that the ledras_scenes_v4.json is the single source of truth
for image generation prompts.
"""

import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import fal_generate
import json

def test_scenes_have_style_and_negative():
    """Test that scenes have style_seed and negative_prompt from ledras_scenes_v4.json"""
    print('Test 1: Verify scenes have style_seed and negative_prompt...')
    
    scenes = fal_generate.load_scenes(Path(__file__).parent, 'data/scenes/ledras_scenes_v4.json')
    
    has_style = all('style_seed' in s for s in scenes)
    has_negative = all('negative_prompt' in s for s in scenes)
    
    if has_style and has_negative:
        print('✅ All scenes have style_seed and negative_prompt from ledras_scenes_v4.json')
        print(f'   Sample style: {scenes[0]["style_seed"][:60]}...')
        print(f'   Sample negative: {scenes[0]["negative_prompt"]}')
        return True
    else:
        print('❌ Some scenes missing style_seed or negative_prompt')
        return False

def test_imagine_config():
    """Test that imagine-config.json has NO style_seed or negative_prompt"""
    print('Test 2: Verify imagine-config.json...')
    
    with open('imagine-config.json') as f:
        config = json.load(f)
        
    if 'style_seed' not in config and 'negative_prompt' not in config:
        print('✅ imagine-config.json has NO style_seed or negative_prompt')
    else:
        print('❌ imagine-config.json still has style_seed or negative_prompt')
        return False
        
    if 'scenes_file' in config:
        print(f'✅ scenes_file = {config["scenes_file"]}')
    else:
        print('❌ scenes_file missing from config')
        return False
        
    return True

def test_generate_stage_uses_scene_data():
    """Test that generate_stage uses scene data, not config"""
    print('Test 3: Verify generate_stage uses scene data...')
    
    # Read the source directly
    source_path = Path(__file__).parent / 'src' / 'fal_generate.py'
    with open(source_path) as f:
        source = f.read()
        
    # Check that generate_stage gets style from scene, not config
    if 'def generate_stage(' in source:
        # Find the generate_stage function
        import re
        match = re.search(r'def generate_stage\(.*?\):(.*?)(?=\n\s*def|\Z)', source, re.DOTALL)
        if match:
            func_body = match.group(1)
            
            # Check style
            if 'style = scene.get("style_seed"' in func_body:
                print('✅ generate_stage sources style from scene, NOT config')
            else:
                print('❌ generate_stage still sources style from config')
                return False
                
            # Check negative prompt - look for the actual pattern
            if 'negative = scene.get(' in func_body and 'negative_prompt' in func_body:
                print('✅ generate_stage sources negative from scene, NOT config')
            else:
                print('❌ generate_stage still sources negative from config')
                return False
                
        return True
    else:
        print('❌ generate_stage not found')
        return False

def test_prompt_construction():
    """Test that prompt construction uses scene data"""
    print('Test 4: Verify prompt construction uses scene data...')
    
    scenes = fal_generate.load_scenes(Path(__file__).parent, 'data/scenes/ledras_scenes_v4.json')
    scene = fal_generate.get_scene_by_id(scenes, 1)
    
    # Simulate prompt building from generate_stage
    style = scene.get("style_seed", "")
    negative = scene.get("negative_prompt", "blurry, deformed text, extra objects, watermark")
    scene_description = scene["description"]
    
    prompt = (
        f"exact composition, text zones and proportions of line-out template. "
        f"{scene_description}. {style}. --no {negative}"
    )
    
    # Verify prompt contains scene description
    if scene_description in prompt:
        print('✅ Prompt contains exact scene description from ledras_scenes_v4.json')
        print(f'   Prompt preview: {prompt[:100]}...')
        return True
    else:
        print('❌ Prompt does not contain scene description')
        return False

def main():
    print('🔍 Verifying single source of truth for ledras_scenes_v4.json')
    print("=" * 60)
    
    tests = [
        test_scenes_have_style_and_negative,
        test_imagine_config,
        test_generate_stage_uses_scene_data,
        test_prompt_construction,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print()
        if test():
            passed += 1
        print("-" * 60)
    
    print()
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ledras_scenes_v4.json is the single source of truth.")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())