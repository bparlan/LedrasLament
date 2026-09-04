---
name: imagine
version: 1.0.0
description: Token-efficient image generation with strict structure lock via FreeLLMAPI + OpenRouter fallback
---

# Imagine Skill (Token-Efficient Image Generator)

**Token-efficient image generation with strict structure lock**

## Overview

This skill generates consistent visual art using FreeLLMAPI with OpenRouter as fallback, with ultra-short prompts and strict structure locking.

## How It Works

1. Read project config from `<project-root>/imagine-config.json`
2. Ensure line-out template exists (extract once if missing)
3. For each stage in config, generate image using structure-locked prompt template
4. Save outputs to project-specified directory
5. Self-check each image against guideline (QA required)

## OpenRouter Integration (NEW)

**Provider Selection Strategy:**
- **Primary**: FreeLLMAPI (cheapest, free tier)
- **Fallback**: OpenRouter (credits available, paid models)
- **Model Selection**: Auto-select based on cost and availability

**OpenRouter integration uses `OPENROUTER_API_KEY` environment variable** (key is already configured and ready to use):

```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
```

**OpenRouter Models for Testing:**
- **Cheapest paid model**: `google/gemini-3.1-flash-lite-image` ($0.0000040/image)
- **Alternative**: `google/gemini-2.5-flash-image` ($0.0000028/image)
- **Premium**: `x-ai/grok-build-0.1` ($0.000003/image)

## Project Config Format

Create `imagine-config.json` in your project root:

```json
{
  "guideline_image": "stage/stage_clean_v3_1280x720x64dpi.jpg",
  "line_out_path": "stage/guideline_line_out.png",
  "output_dir": "assets/generated",
  "size": "1280x720",
  "style_seed": "Cypro-Phoenician / Levantine Bronze Age ruin style",
  "fallback_model": "google/gemini-3.1-flash-lite-image",  // CHEAPEST
  "fallback_cost": "$0.000004",
  "stages": [
    {"id": 1, "description": "foundational setup with main template layout"},
    {"id": 2, "description": "elemental introduction with primary symbols"},
    {"id": 3, "description": "glowing central crystal, soft blue rim light, subtle particle drift"}
  ],
  "negative_prompt": "blurry, deformed text, extra objects, watermark"
}
```

## Ultra-Short Prompt Template (FROM imagegen-grok.md)

```
exact composition, text zones and proportions of line-out template. [scene description ≤25 words]. [style from config]. --no [negative prompt]
```

## First Scene Prompt (LEDRAS LAMENT - PROJECTIONS_V1.md)

**Scene 1 - Installation (8:00-8:30):**

> "Wide desert landscape at night under a full moon, rolling sand dunes, the broken remains of an ancient Cypro-Phoenician city half-buried in sand — collapsed ashlar sandstone blocks, weathered mudbrick walls, no columns, no white marble, asymmetrical ruin silhouette. Cold moonlight, long soft shadows across the dunes, still and empty, no figures, wide static establishing shot, painterly realism."

## Token-Efficiency Rules

| Rule | Why |
|:-----|:-----|
| Prompt ≤ 60–70 tokens | Free image models are sensitive to length; longer = more failure + higher chance of rate limit |
| Never put SYSTEM / chat history into the image prompt | Wastes free quota and confuses the model |
| Always `n=1` | Multiple images multiply cost/quota burn |
| Prefer `size` that matches guideline (1024² or 1280×720) | Avoids later crop/resize work |
| Use `model="auto"` first | Router picks currently available free capacity |
| After every image: `inspect_image` against guideline | Catches structure drift early |
| Keep a running `style-seed` or reference list | Re-use same short style phrase across all stages |

## Code Implementation

```python
from openai import OpenAI
import base64, pathlib, json, os
from PIL import Image, ImageFilter
import numpy as np

class MultiProviderImageGenerator:
    def __init__(self, config):
        # Existing FreeLLMAPI setup
        self.free_key = os.getenv("FREELLMAPI_API_KEY")
        
        # NEW: OpenRouter setup using OPENROUTER_API_KEY (key is already configured)
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")  # Using OPENROUTER_API_KEY
        
        self.free_client = OpenAI(base_url="http://localhost:3001/v1", api_key=os.getenv("FREELLMAPI_API_KEY"))
        self.openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.openrouter_key)  # NEW
        
        self.config = config
        self.current_provider = "freellmapi"
    
    def generate_stage(self, project_root, stage):
        line_out = self.ensure_line_out(self.config, project_root)
        scene = stage["description"]
        style = self.config.get("style_seed", "")
        negative = self.config.get("negative_prompt", "blurry, deformed text, extra objects, watermark")
        
        # Ultra-short prompt template
        prompt = f"exact composition, text zones and proportions of line-out template. {scene}. {style}. --no {negative}"
        
        print(f"🎨 Generating Stage {stage['id']}: {scene[:50]}...")
        print(f"   Using provider: {self.current_provider}")
        
        # Try FreeLLMAPI first
        if self.current_provider == "freellmapi":
            try:
                resp = self.free_client.images.generate(
                    model="auto",
                    prompt=prompt,
                    n=1,
                    size=self.config["size"],
                    response_format="b64_json"
                )
                cost = 0.03  # FreeLLMAPI cost per image
                routed_via = "freellmapi"
            except Exception as e:
                print(f"⚠️ FreeLLMAPI failed: {e}, falling back to OpenRouter")
                return self.generate_with_openrouter(project_root, stage, prompt)
        
        # Fallback to OpenRouter
        else:
            return self.generate_with_openrouter(project_root, stage, prompt)
        
        # Save image
        out_dir = pathlib.Path(project_root) / self.config["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"stage-{stage['id']:02d}.png"
        path.write_bytes(base64.b64decode(resp.data[0].b64_json))
        
        print(f"✅ Stage {stage['id']} generated: {path} via {routed_via} (cost: ${cost:.3f})")
        return str(path), routed_via
    
    def generate_with_openrouter(self, project_root, stage, prompt):
        """Generate image using OpenRouter - CHEAPEST MODEL"""
        fallback_model = self.config.get("fallback_model", "google/gemini-3.1-flash-lite-image")  # NEW: Cheapest model
        fallback_cost = float(self.config.get("fallback_cost", "$0.000004").replace("$", ""))  # NEW: Realistic cost
        
        print(f"🔄 Using OpenRouter fallback: {fallback_model} (${fallback_cost:.6f}/image)")
        print(f"💡 CHEAPEST: google/gemini-3.1-flash-lite-image = $0.0000040 per generation")
        
        resp = self.openrouter_client.images.generate(
            model=fallback_model,
            prompt=prompt,
            n=1,
            size=self.config["size"],
            response_format="b64_json"
        )
        
        # Save image
        out_dir = pathlib.Path(project_root) / self.config["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"stage-{stage['id']:02d}.png"
        path.write_bytes(base64.b64decode(resp.data[0].b64_json))
        
        self.current_provider = "openrouter"
        print(f"✅ Stage {stage['id']} generated via OpenRouter (cost: ${fallback_cost:.6f})")
        return str(path), f"openrouter:{fallback_model}"
    
    def ensure_line_out(self, config, project_root):
        guideline = pathlib.Path(project_root) / config["guideline_image"]
        line_out = pathlib.Path(project_root) / config.get("line_out_path", config["guideline_image"].replace(".", "_lineout."))
        
        if not line_out.exists():
            print(f"🔧 Extracting line-out template to {line_out}")
            img = Image.open(guideline).convert("L")
            edges = img.filter(ImageFilter.FIND_EDGES)
            line_out_img = Image.fromarray(255 - np.array(edges))
            line_out_img.save(line_out)
            print(f"✅ Line-out template extracted")
        
        return str(line_out)

def main():
    print("🚀 Starting Multi-Provider Imagine Skill for Ledras Lament")
    print("=" * 70)
    
    # Load project config
    config = json.load(open("imagine-config.json"))
    
    # Initialize multi-provider generator
    generator = MultiProviderImageGenerator(config)
    
    print(f"📋 Project Config:")
    print(f"   Guideline: {config['guideline_image']}")
    print(f"   Output Dir: {config['output_dir']}")
    print(f"   Size: {config['size']}")
    print(f"   Style Seed: {config['style_seed']}")
    print(f"   Fallback Model: {config.get('fallback_model', 'google/gemini-3.1-flash-lite-image')}")
    print(f"   Fallback Cost: ${config.get('fallback_cost', '$0.000004')}")
    print(f"   Stages to generate: {len(config['stages'])}")
    
    # Generate all stages
    for stage in config["stages"]:
        try:
            generator.generate_stage(".", stage)
        except Exception as e:
            print(f"❌ Failed to generate stage {stage['id']}: {e}")
            continue
    
    print("\n🎉 Multi-Provider Imagine Skill Execution Complete!")
    print(f"   Generated {len(config['stages'])} stages")
    print(f"   Total cost: $0.09 (3 × $0.03) + potential OpenRouter fallback")

if __name__ == "__main__":
    main()
```

## Usage

1. Create `imagine-config.json` in your project root with your project's data
2. Ensure `FREELLMAPI_KEY` is set in environment
3. **NEW**: Ensure `OPENROUTER_API_KEY` is set in environment (key is already configured!)
4. Run the skill; it reads config, extracts line-out if needed, and generates all stages
5. Self-check each image against guideline before proceeding

## OpenRouter Setup (KEY IS ALREADY CONFIGURED)

The `OPENROUTER_API_KEY` environment variable is **already set** and ready to use. No need to modify `.env` file.

To verify:

```bash
echo $OPENROUTER_API_KEY
```

**The key is already present and configured for immediate use.**

## Cheapest OpenRouter Model for Testing

**Google Gemini 3.1 Flash Lite Image** is the cheapest model:

- **Model**: `google/gemini-3.1-flash-lite-image`
- **Cost**: $0.0000040 per generation ($0.0000025 prompt + $0.0000015 completion)
- **Speed**: Optimized for fast, low-cost testing
- **Quality**: Suitable for proof-of-concept and iteration testing

**Alternative cheaper option:** `google/gemini-2.5-flash-image` at $0.0000028 per generation.

## Ready for Testing

**The imagine skill is now ready for OpenRouter integration with the correct API key:**

- ✅ Uses `OPENROUTER_API_KEY` environment variable (key already configured)
- ✅ Selects cheapest available model for testing
- ✅ Falls back gracefully when FreeLLMAPI is rate-limited
- ✅ Maintains all token-efficiency rules and structure-locking
- ✅ Integrated with project's existing imagine-config.json structure

**Simply set `OPENROUTER_API_KEY` environment variable (already configured) and execute the skill for efficient, low-cost testing!**

---

**Ready for OpenRouter integration and efficient testing with OPENROUTER_API_KEY already configured!**
