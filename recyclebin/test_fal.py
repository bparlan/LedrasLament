
import os
import sys

print('Testing fal client...')
try:
    from fal import run as fal_run
    print('✅ fal.run import successful')
except ImportError as e:
    print(f'❌ ERROR: fal import failed: {e}')
    sys.exit(1)

print('Environment Check:')
print(f'  FAL_API_KEY: {"SET" if "FAL_API_KEY" in os.environ else "NOT SET"}')
