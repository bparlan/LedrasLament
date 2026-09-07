import sys
sys.path.insert(0, '.')

# First let's check the current setup_fal_client method
from fal_generate import LedrasSceneGenerator

# Create an instance
generator = LedrasSceneGenerator()

# Check if client exists
print("Client attribute exists:", hasattr(generator, 'client'))
print("Api key attribute exists:", hasattr(generator, 'api_key'))

if hasattr(generator, 'api_key'):
    print(f"Api key: {generator.api_key[:20]}...")
