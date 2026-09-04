#!/usr/bin/env python3
"""
Simple test to verify fal_generate.py works correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    import fal_generate
    print("✅ Successfully imported fal_generate")
    
    # Check that essential functions exist
    functions_to_check = [
        'load_config',
        'ensure_line_out', 
        'generate_stage',
        'estimate_cost',
        'save_image'
    ]
    
    for func_name in functions_to_check:
        if hasattr(fal_generate, func_name):
            print(f"✅ {func_name} function exists")
        else:
            print(f"❌ {func_name} function missing")
    
    # Test the functions work with a mock project
    class MockPath:
        def __init__(self, path):
            self.path = path
            
        def __truediv__(self, other):
            return MockPath(f"{self.path}/{other}")
            
        def exists(self):
            return False
            
        def write_text(self, text):
            pass
            
        def read_text(self):
            return '{"fal_model": "test", "fal_control_strength": 0.7, "size": "1024x576", "output_dir": "assets/generated", "guideline_image": "stage/test.jpg", "stages": [{"id": 1, "description": "test stage"}]}'
            
        def unlink(self):
            pass
            
        def rmdir(self):
            pass
            
        def mkdir(self, parents=False, exist_ok=False):
            pass
            
        def __str__(self):
            return self.path
            
        def __fspath__(self):
            return self.path
    
    # Test load_config
    result = fal_generate.load_config(MockPath("/test"))
    assert result["fal_model"] == "test", f"Expected test model, got {result.get('fal_model')}"
    print("✅ load_config works")
    
    # Test estimate_cost
    cost = fal_generate.estimate_cost(1024, 576, "fal-ai/z-image/turbo")
    assert isinstance(cost, (int, float)), f"Expected number, got {type(cost)}"
    print("✅ estimate_cost works")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
