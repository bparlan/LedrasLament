import os
import fal_client

key = os.getenv('FAL_API_KEY')
print(f"Key starts with: {key[:5]}")

# Use the environment variable, the library should pick it up if set correctly
os.environ["FAL_KEY"] = key

try:
    # Use the run function without key argument
    result = fal_client.run(
        "fal-ai/flux-control-lora-canny",
        arguments={"prompt": "test", "image_size": "square_hd"},
    )
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
