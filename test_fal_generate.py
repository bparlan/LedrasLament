#!/usr/bin/env python3
"""
Test script for validating the consolidated fal_generate.py module.
Tests that the new module can replace all duplicate scripts.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the current directory to the path so we can import fal_generate
sys.path.insert(0, str(Path(__file__).parent))

import fal_generate


def test_config_validation():
    """Test that config validation works correctly."""
    print("🔍 Testing config validation...")
    
    # Create a valid config
    valid_config = {
        "fal_model": "fal-ai/z-image/turbo/controlnet",
        "fal_control_strength": 0.7,
        "size": "1280x720",
        "output_dir": "assets/generated",
        "guideline_image": "stage/stage_clean_v3_1280x720x64dpi.jpg",
        "style_seed": "Test style",
        "negative_prompt": "blurry, deformed text"
    }
    
    # Create temporary directory and config file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "imagine-config.json"
        
        with open(config_file, 'w') as f:
            json.dump(valid_config, f)
        
        # Test loading with proper project root
        cfg = fal_generate.load_config(temp_path)
        
        # Verify all required keys are present
        required_keys = ["fal_model", "fal_control_strength", "size", "output_dir"]
        for key in required_keys:
            assert key in cfg, f"Missing required key: {key}"
        
        print("✅ Config validation test passed")
        return True


def test_missing_config_keys():
    """Test that missing config keys raise clear errors."""
    print("🔍 Testing missing config keys validation...")
    
    # Create config with missing keys
    incomplete_config = {
        "fal_model": "fal-ai/z-image/turbo/controlnet",
        # Missing: fal_control_strength, size, output_dir, guideline_image
    }
    
    # Create temporary directory and config file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "imagine-config.json"
        
        with open(config_file, 'w') as f:
            json.dump(incomplete_config, f)
        
        try:
            cfg = fal_generate.load_config(temp_path)
            print("❌ Missing config keys test failed - should have raised ValueError")
            return False
            
        except ValueError as e:
            if "Missing required config keys" in str(e):
                print("✅ Missing config keys validation test passed")
                return True
            else:
                print(f"❌ Wrong error message: {e}")
                return False
        except Exception as e:
            print(f"❌ Missing config keys test failed with unexpected error: {e}")
            return False


def test_request_building():
    """Test that request building works correctly."""
    print("🔍 Testing request building...")
    
    # Mock the SyncClient upload_file method
    mock_client = MagicMock()
    mock_client.upload_file.return_value = "https://fal.ai/test-image.jpg"
    
    with patch('fal_generate.SyncClient', return_value=mock_client):
        config = {
            "fal_model": "fal-ai/z-image/turbo/controlnet",
            "fal_control_strength": 0.7,
            "size": "1280x720",
            "style_seed": "Cypro-Phoenician / Levantine Bronze Age ruin style",
            "negative_prompt": "blurry, deformed text, extra objects, watermark"
        }
        
        scene_data = {
            "id": 1,
            "prompt": "Test scene prompt",
            "style": "Test style",
            "negative_prompt": "blurry, deformed text",
            "control_strength": 0.7
        }
        
        control_image_path = "/tmp/test-lineout.png"
        
        try:
            request = fal_generate.build_request(scene_data, config, control_image_path)
            
            # Verify request structure
            assert "prompt" in request
            assert "control_image" in request  # z-image uses control_image field
            assert "strength" in request
            assert "width" in request
            assert "height" in request
            assert "num_images" in request
            
            # Verify content
            assert "exact composition, text zones and proportions of line‑out template" in request["prompt"]
            assert request["width"] == 1280
            assert request["height"] == 720
            assert request["strength"] == 0.7
            
            # Verify control_image field was set
            assert "https://fal.ai/test-image.jpg" in request["control_image"]
            
            print("✅ Request building test passed")
            return True
            
        except Exception as e:
            print(f"❌ Request building test failed: {e}")
            return False


def test_cost_estimation():
    """Test cost estimation for different models."""
    print("🔍 Testing cost estimation...")
    
    test_cases = [
        # (width, height, model, expected_cost)
        (1280, 720, "fal-ai/z-image/turbo/controlnet", 0.0060),  # 1280×720×0.0065 = 0.0060
        (1280, 720, "fal-ai/sd15-depth-controlnet", 0.0444),   # 35.5s × 0.00125
    ]
    
    for width, height, model, expected_cost in test_cases:
        try:
            cost = fal_generate.estimate_cost(width, height, model)
            
            # Allow small floating point tolerance
            if abs(cost - expected_cost) < 0.0001:
                print(f"✅ Cost estimation test passed for {model}: ${cost:.4f}")
            else:
                print(f"❌ Cost estimation test failed for {model}: expected ${expected_cost:.4f}, got ${cost:.4f}")
                return False
                
        except Exception as e:
            print(f"❌ Cost estimation test failed for {model}: {e}")
            return False
    
    return True


def test_cli_parsing():
    """Test CLI argument parsing."""
    print("🔍 Testing CLI parsing...")
    
    # We can't easily test the full CLI without running the module,
    # but we can test that the main function exists and is callable
    assert hasattr(fal_generate, 'main')
    assert callable(fal_generate.main)
    
    print("✅ CLI parsing test passed")
    return True


def main():
    """Run all tests."""
    print("🧪 Running tests for consolidated fal_generate.py module\n")
    
    tests = [
        test_config_validation,
        test_missing_config_keys,
        test_request_building,
        test_cost_estimation,
        test_cli_parsing,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("❌ Some tests failed!")
        return 1
    else:
        print("✅ All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())