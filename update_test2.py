# Update the test cases with correct expected costs
import json

# Read the test file
with open('test_fal_generate.py', 'r') as f:
    content = f.read()

# Update the test cases with correct expected costs
old_test_cases = '''    test_cases = [
        # (width, height, model, expected_cost)
        (1280, 720, "fal-ai/z-image/turbo/controlnet", 0.0060),  # 1280×720×0.0065 = 0.0060
        (1280, 720, "fal-ai/sd15-depth-controlnet", 0.0375),   # 30s × 0.00125 (estimated)
    ]'''

new_test_cases = '''    test_cases = [
        # (width, height, model, expected_cost)
        (1280, 720, "fal-ai/z-image/turbo/controlnet", 0.0060),  # 1280×720×0.0065 = 0.0060
        (1280, 720, "fal-ai/sd15-depth-controlnet", 0.0444),   # 35.5s × 0.00125
    ]'''

content = content.replace(old_test_cases, new_test_cases)

# Write back to file
with open('test_fal_generate.py', 'w') as f:
    f.write(content)

print("Test expectations updated with correct SD15 cost")
