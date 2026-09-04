import re

# Read the fal_generate.py file
with open('fal_generate.py', 'r') as f:
    content = f.read()

# Fix the SD15 cost calculation to use 35.5 seconds (based on observed data)
# Change: estimated_compute_seconds = 30.0
# To: estimated_compute_seconds = 35.5

content = content.replace(
    'estimated_compute_seconds = 30.0  # rough estimate for 1024x576',
    'estimated_compute_seconds = 35.5  # based on observed 35.5s compute time'
)

# Write back to file
with open('fal_generate.py', 'w') as f:
    f.write(content)

print("SD15 cost calculation fixed to match observed data")
