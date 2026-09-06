#!/usr/bin/env python3
"""
Minimal Scene Generator for Ledras Lament - based on original working version
"""

import json
import os
from fal_client import run as fal_run

def main():
    api_key = os.environ.get('FAL_API_KEY')
    if not api_key:
        print("❌ FAL_API_KEY not set")
        return

    # Original working parameters found in fal_generate.py.backup
    model = "fal-ai/flux-control-lora-canny"
    prompt = "Water enters the fixed ancient amphitheater in harmony with the existing architecture. Calm streams and narrow canals follow the natural horizontal and vertical stone geometry. [seed:42] [team:cypro_phoenician] [intro]"
    
    fal_params = {
        "image_size": "1280x720",
        "seed": 42,
        "num_inference_steps": 28,
        "control_strength": 0.7,
        "preprocess": "canny",
        "guideline_image": "stage/guideline_line_out.png",
        "num_images": 1,
        "output_format": "png",
        "prompt": prompt
    }

    print(f"🤖 Calling fal.run() API with model: {model}")
    try:
        result = fal_run(model, arguments=fal_params)
        if result and hasattr(result, 'images') and result.images:
            image_data = result.images[0]
            with open("scene-05-minimal-test.png", "wb") as f:
                f.write(image_data['image']['bytes'])
            print("✅ Image generated successfully!")
        else:
            print("❌ No images returned")
            print(f"Result structure: {type(result)}")
    except Exception as e:
        print(f"❌ Generation failed: {e}")

if __name__ == "__main__":
    main()
