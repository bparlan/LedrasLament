#!/usr/bin/env python3
"""
Manual FLUX 2.0 Image Generation Script
Generates ledras-premier scene 2 images using FLUX models
"""

import os
import json
import requests
import base64
from pathlib import Path

class LedrasPremierGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("FAL_API_KEY")
        self.base_url = "https://fal.ai"
        self.output_dir = Path("/Users/bparlan/devcode/ledraslament/assets/generated/ledras-premier/set_04")
        
    def generate_scene_2(self):
        """Generate ledras-premier scene 2 with FLUX 2.0"""
        print("=== Ledras-Premier Scene 2 Generation ===")
        
        # Scene 2 specifications from ledras-premier.json
        scene_data = {
            "scene_id": 2,
            "name": "Scene 2 - Deep Night",
            "seed": 502,
            "description": "Deep night settles over the amphitheater. The moon at the center of the frame casts long silver shadows across the six stone tiers. Fog and smoke interweave around the stage. The ancient space feels genuinely watchful and still.",
            "prompt": "Photorealistic deep night settles over the amphitheater. The moon at the center of the frame casts long silver shadows across the six stone tiers. Fog and smoke interweave around the stage. The ancient space feels genuinely watchful and still. Photorealistic visual composition with authentic texture details showing weathered limestone surfaces, fine desert sand textures, and star-filled sky. Professional architectural photography with strong vertical axis through frame opening and leading lines along tier boundaries converging toward rear wall. Camera at tier 3 elevation with balanced negative space and enhanced depth. Authentic atmospheric perspective creating foreground-to-background depth with realistic light interaction and material response. All visual elements positioned exclusively around side stair structures on left and right sides, with no central tier elements or lighting. Immersive cinematic presentation with genuine ancient ambiance and photorealistic environmental storytelling with enhanced side stair focus and starry night sky.",
            "control_image": "data/control_images/stage_rehersals.png",
            "control_strength": 0.8,
            "model": "FLUX.2",
            "generation_date": "2026-09-09"
        }
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate image using FLUX 2.0
        image_data = self._generate_with_flux(scene_data)
        
        if image_data:
            # Save generated image
            self._save_image(image_data, scene_data)
            
            # Update scene data with generation details
            self._update_scene_data(scene_data, image_data)
            
            return True
        else:
            print("❌ Failed to generate image")
            return False
    
    def _generate_with_flux(self, scene_data):
        """Generate image using FLUX 2.0 API"""
        print("1. Preparing FLUX 2.0 generation request...")
        
        # Try to access FLUX 2.0 through fal.ai
        flux_endpoints = [
            "https://fal.ai/api/v1/images/generate",
            "https://fal.ai/api/generate",
            "https://fal.ai/api/v1/text-to-image"
        ]
        
        payload = {
            "prompt": scene_data["prompt"],
            "model": "FLUX.2",
            "seed": scene_data["seed"],
            "num_images": 1,
            "image_format": "jpeg",
            "enhance_prompt": True,
            "guidance_scale": 7.5,
            "num_inference_steps": 50
        }
        
        # Add control image if available
        if scene_data.get("control_image"):
            payload["control_image"] = {
                "url": f"https://fal.ai/api/placeholder/{scene_data['control_image'].replace('/', '-')}"
            }
            payload["control_strength"] = scene_data.get("control_strength", 0.8)
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        for endpoint in flux_endpoints:
            print(f"   Trying endpoint: {endpoint}")
            try:
                response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Successfully generated image")
                    
                    # Extract image data
                    if "images" in result and result["images"]:
                        image_info = result["images"][0]
                        
                        # Handle different response formats
                        if "url" in image_info:
                            # Download the image
                            img_response = requests.get(image_info["url"], timeout=60)
                            if img_response.status_code == 200:
                                return {
                                    "data": img_response.content,
                                    "url": image_info["url"],
                                    "format": "jpeg"
                                }
                        elif "base64" in image_info:
                            # Handle base64 encoded images
                            return {
                                "data": base64.b64decode(image_info["base64"]),
                                "format": "jpeg"
                            }
                        
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    print(f"   Response: {response.text[:300]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("   ⚠️  All FLUX endpoints failed, will try alternative generation")
        return None
    
    def _save_image(self, image_data, scene_data):
        """Save generated image to disk"""
        filename = f"scene2_flux_seed{scene_data['seed']}_{scene_data['generation_date']}.png"
        filepath = self.output_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(image_data["data"])
        
        print(f"   📸 Image saved to: {filepath}")
        print(f"   📊 Image size: {len(image_data['data'])} bytes")
        
        # Create thumbnail metadata
        metadata = {
            "filename": filename,
            "scene_id": scene_data["scene_id"],
            "scene_name": scene_data["name"],
            "seed": scene_data["seed"],
            "model": scene_data["model"],
            "generation_date": scene_data["generation_date"],
            "control_image": scene_data.get("control_image"),
            "control_strength": scene_data.get("control_strength"),
            "prompt_length": len(scene_data["prompt"]),
            "generation_method": "FLUX.2 API"
        }
        
        # Save metadata
        metadata_path = self.output_dir / f"{filename.replace('.png', '.json')}"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   📋 Metadata saved to: {metadata_path}")
    
    def _update_scene_data(self, scene_data, image_data):
        """Update scene data with generation results"""
        scene_data.update({
            "generated_filename": f"scene2_flux_seed{scene_data['seed']}_{scene_data['generation_date']}.png",
            "generation_success": True,
            "generation_method": "FLUX.2 API via fal.ai",
            "generated_url": image_data.get("url", "")
        })
        
        # Save updated scene data
        scene_path = self.output_dir / "scene2.json"
        with open(scene_path, "w") as f:
            json.dump(scene_data, f, indent=2)
        
        print(f"   📝 Scene data updated: {scene_path}")

if __name__ == "__main__":
    generator = LedrasPremierGenerator()
    success = generator.generate_scene_2()
    
    if success:
        print("\n✅ Scene 2 generation completed successfully!")
    else:
        print("\n❌ Scene 2 generation failed")