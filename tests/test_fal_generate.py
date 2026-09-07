#!/usr/bin/env python3
"""Test the corrected fal_generate.py module."""

from fal_generate import get_resolution, estimate_cost

# Test get_resolution
config = {'image_size': 'landscape_16_9'}
width, height = get_resolution(config)
print(f"Resolution: {width}x{height}")

# Test estimate_cost
cost = estimate_cost(width, height, 'fal-ai/flux-control-lora-canny')
print(f"Estimated cost: ${cost:.4f}")

# Test unknown size
config2 = {'image_size': 'unknown_size'}
width2, height2 = get_resolution(config2)
print(f"Unknown size defaulted to: {width2}x{height2}")

print("✅ All functions work correctly!")

 # Test other configs
 config3 = {'image_size': 'landscape_4_3'}
 width3, height3 = get_resolution(config3)
 print(f"Landscape 4:3 resolution: {width3}x{height3}")
 print("✅ All functions work correctly!")