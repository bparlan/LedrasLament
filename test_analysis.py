import sys
import os
from pathlib import Path

# Add src directory to the path so we can import fal_generate
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import fal_generate

print("=== Checking fal_generate.py implementation ===")
print()

# Check if call_fal exists and is mocked
if hasattr(fal_generate, 'call_fal'):
    print("❌ call_fal function still exists - likely mocked")
    print(f"   call_fal: {fal_generate.call_fal}")
else:
    print("✅ call_fal function has been removed")

print()

# Check if parse_response exists and is mocked
if hasattr(fal_generate, 'parse_response'):
    print("❌ parse_response function still exists - likely mocked")
    print(f"   parse_response: {fal_generate.parse_response}")
else:
    print("✅ parse_response function has been removed")

print()

# Check if save_image is a real implementation
if hasattr(fal_generate, 'save_image'):
    print("save_image function exists")
    import inspect
    source = inspect.getsource(fal_generate.save_image)
    if "fake_image_data" in source:
        print("❌ save_image is still mocked with fake data")
    else:
        print("✅ save_image appears to be a real implementation")
        print(f"   Source snippet: {source[:200]}...")

print()

# Check if load_config is real
if hasattr(fal_generate, 'load_config'):
    print("✅ load_config exists")
    import inspect
    source = inspect.getsource(fal_generate.load_config)
    if "Missing required config keys" in source:
        print("✅ load_config has real validation logic")

print()

# Check if generate_stage is real
if hasattr(fal_generate, 'generate_stage'):
    print("generate_stage function exists")
    import inspect
    source = inspect.getsource(fal_generate.generate_stage)
    if "client.run(model_name, arguments)" in source:
        print("✅ generate_stage calls client.run() directly")
        if '"num_images": 1' in source:
            print("✅ generate_stage requests num_images: 1")
        else:
            print("❌ generate_stage does not request num_images: 1")
    else:
        print("❌ generate_stage does not call client.run() directly")

print()

# Check if estimate_cost is real
if hasattr(fal_generate, 'estimate_cost'):
    print("estimate_cost function exists")
    import inspect
    source = inspect.getsource(fal_generate.estimate_cost)
    if "sdxl" in source and "turbo" in source:
        print("✅ estimate_cost has real implementation")

print()

# Check if log_request_to_ledger is real
if hasattr(fal_generate, 'log_request_to_ledger'):
    print("✅ log_request_to_ledger exists")

print()

# Check if update_ledger_entry is real
if hasattr(fal_generate, 'update_ledger_entry'):
    print("✅ update_ledger_entry exists")

print()

# Check if main is real
if hasattr(fal_generate, 'main'):
    print("✅ main function exists")
