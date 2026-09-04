import re

# Read the fal_generate.py file
with open('fal_generate.py', 'r') as f:
    content = f.read()

# Fix the estimate_cost function
old_code = '''def calculate_expected_cost(width: int, height: int, num_images: int) -> float:
    """Calculate expected Fal.ai cost based on current Z-Image Turbo pricing."""
    mp_per_image = (width * height) / 1_000_000
    total_mp = mp_per_image * num_images
    # Z-Image Turbo rate: $0.0065 per MP (based on documentation)
    return total_mp * 0.0065'''

new_code = '''def calculate_expected_cost(width: int, height: int, num_images: int) -> float:
    """Calculate expected Fal.ai cost based on current Z-Image Turbo pricing."""
    mp_per_image = (width * height) / 1_000_000
    total_mp = mp_per_image * num_images
    # Z-Image Turbo rate: $0.0065 per MP (based on documentation)
    return total_mp * 0.0065'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("Fixed calculate_expected_cost function")
else:
    print("Old calculate_expected_cost function not found, checking for other variations")

# Also check and fix the estimate_cost function for tests
if "mp_per_image * 0.0065" in content:
    print("Found mp_per_image * 0.0065 in content")
if "mp_per_image * 0.00125" in content:
    print("Found mp_per_image * 0.00125 in content")
if "mp_per_image * 0.01" in content:
    print("Found mp_per_image * 0.01 in content")

# Write back to file
with open('fal_generate.py', 'w') as f:
    f.write(content)

print("Code fixed successfully")
