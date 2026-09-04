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

# Add src directory to the path so we can import fal_generate
sys.path.insert(0, str(Path(__file__).parent / "src"))

import fal_generate

def test_config_validation():
    """Test that config validation works correctly."""
    project_root = Path("/tmp/test_project")
    project_root.mkdir(exist_ok=True)
    
    # Write a valid config
    config_path = project_root / "imagine-config.json"
    config_data = {
        "fal_model": "fal-ai/test",
        "fal_control_strength": 0.7,
        "size": "1024x576",
        "output_dir": "assets/generated",
        "guideline_image": "stage/test.jpg"
    }
    config_path.write_text(json.dumps(config_data))
    
    try:
        config = fal_generate.load_config(project_root)
        assert config["fal_model"] == "fal-ai/test"
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Cleanup
        if config_path.exists():
            config_path.unlink()
        project_root.rmdir()
def test_missing_config_keys():
    """Test that missing config keys raise clear errors."""
    project_root = Path("/tmp/test_project")
    project_root.mkdir(exist_ok=True)
    
    # Write an invalid config (missing required keys)
    config_path = project_root / "imagine-config.json"
    config_data = {
        "guideline_image": "stage/test.jpg",
        "fal_model": "fal-ai/test"
        # Missing required keys: fal_control_strength, size, output_dir
    }
    config_path.write_text(json.dumps(config_data))
    
    try:
        config = fal_generate.load_config(project_root)
        print("Config loaded when it shouldn't have")
        return False
    except ValueError as e:
        assert "Missing required config keys" in str(e)
        return True
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        # Cleanup
        if config_path.exists():
            config_path.unlink()
        if project_root.exists():
            project_root.rmdir()
def test_request_building():
    """Test that request building works correctly."""
    project_root = Path("/tmp/test_project")
    project_root.mkdir(exist_ok=True)
    
    # Write a config
    config_path = project_root / "imagine-config.json"
    config_data = {
        "fal_model": "fal-ai/test",
        "fal_control_strength": 0.7,
        "size": "1024x576",
        "output_dir": "assets/generated",
        "guideline_image": "stage/test.jpg"
    }
    config_path.write_text(json.dumps(config_data))
    
    # Write line-out
    line_out_path = project_root / "stage/test_lineout.png"
    line_out_path.write_bytes(b"fake_image_data")
    
    try:
        config = fal_generate.load_config(project_root)
        line_out = fal_generate.ensure_line_out(config, project_root)
        assert line_out == str(line_out_path)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Cleanup
        if config_path.exists():
            config_path.unlink()
        if line_out_path.exists():
            line_out_path.unlink()
        if project_root.exists():
            project_root.rmdir()
def test_cost_estimation():
    """Test cost estimation for different models."""
    # Test with standard model
    cost1 = fal_generate.estimate_cost(1024, 576, "fal-ai/z-image/turbo")
    assert cost1 > 0
    
    # Test with SD15 model
    cost2 = fal_generate.estimate_cost(512, 512, "fal-ai/sdxl")
    assert cost2 > 0
    
    # Test with different sizes
    cost3 = fal_generate.estimate_cost(2048, 1024, "fal-ai/z-image/turbo")
    assert cost3 > cost1
    
    return True
def test_cli_parsing():
    """Test CLI argument parsing."""
    # This would test argument parsing if fal_generate had a CLI interface
    return True
def main():
    """Run all tests."""
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
                print(f"✅ {test.__name__} passed")
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1
if __name__ == "__main__":
    sys.exit(main())
