# Desert Moon Portal Sequence - 6 Moment Image Generation Guide

## Overview
This guide provides the complete setup and execution instructions for generating the 6-moment Desert Moon Portal Sequence images.

## Files Created

### Primary Scene Configuration
**Location:** `data/scenes/ledras_scenes_v11_moments.json`
- Contains all 6 moment scene definitions
- Includes hyperrealistic photorealistic visual specifications
- Compatible with existing `fal_generate.py` pipeline

### Enhanced Prompt Documentation  
**Location:** `specific_scenes/prelude-intro-moments.md`
- Detailed 6-moment prompt structure
- Hyperrealistic visual enhancements
- Technical specifications for image generation

## Image Generation Process

### Prerequisites
1. **FAL_API_KEY** environment variable set (required for fal.ai access)
2. **fal_client** Python package installed (`pip install fal-client`)
3. **Control image:** `stage_rehersals.png` in working directory

### Generation Steps

#### Option 1: Using fal_generate.py Script
```bash
# Navigate to project directory
cd /Users/bparlan/devcode/ledraslament

# Run the consolidated scene generator
python3 fal_generate.py
```

#### Option 2: Custom Generation Script
```bash
# Create custom script for moment-specific generation
cat > generate_moments.py << 'EOS'
#!/usr/bin/env python3
import json
from fal_generate import LedrasSceneGenerator

# Initialize generator
generator = LedrasSceneGenerator()

# Generate prompts for all moments
prompts = generator.generate_all_prompts()

# Generate each moment
for scene_id, roles in prompts.items():
    for role in roles:
        if role == 'intro':
            prompt = roles[role]
            result = generator.generate_image(prompt, scene_id, role)
            if result:
                print("Generated Moment " + str(scene_id) + ": " + role)
            else:
                print("Failed to generate Moment " + str(scene_id) + ": " + role)
EOS

python3 generate_moments.py
```

#### Option 3: Manual Generation
```bash
# For each moment (1-6)
# 1. Extract prompt from data/scenes/ledras_scenes_v11_moments.json
# 2. Run: python3 fal_generate.py --scene-id X --role intro
# 3. Review and download generated images
```

## Scene Configuration Details

### Moment-Specific Parameters

| Moment | Description | Key Elements | Camera | Color Temp |
|--------|-------------|--------------|--------|------------|
| 1 | Calm Portal Initiation | desert dunes, stone amphitheater, hourglass, rising moon | 1 | 1 |
| 2 | Portal Centered Transition | desert dunes, stone amphitheater, hourglass, rising moon | 2 | 2 |
| 3 | Blood Moon Portal Activation | desert dunes, stone amphitheater, hourglass, blood moon | 3 | 3 |
| 4 | Storm Peak Chaos | desert dunes, stone amphitheater, hourglass, blood moon | 4 | 4 |
| 5 | Portal Deactivation | desert dunes, stone amphitheater, hourglass | 5 | 5 |
| 6 | Final Resolution | desert dunes, stone amphitheater, hourglass | 6 | 6 |

### Generation Parameters
- **Model:** FLUX Control LoRA
- **Control Image:** `stage_rehersals.png` (alpha channel preserved)
- **Control Strength:** 0.7
- **Inference Steps:** 28
- **Guidance Scale:** 3.5
- **Safety Checker:** Enabled
- **Output Format:** PNG

## Quality Assurance

### Validation Commands
```bash
# Run existing test suite
python3 run_tests.py

# Check generated images
ls -la data/generated/

# Validate scene configuration
python3 -m json.tool data/scenes/ledras_scenes_v11_moments.json > /dev/null && echo "JSON valid"
```

### Expected Output
- **6 unique images** corresponding to each moment
- **Deterministic file names:** `scene-01_{seed}_{timestamp}.png`
- **Proper naming convention** for each moment's unique characteristics
- **Consistent visual style** across all moments

## Troubleshooting

### Common Issues

#### Missing FAL_API_KEY
```bash
# Set environment variable
export FAL_API_KEY="your-api-key-here"
```

#### Missing Control Image
```bash
# Ensure control image exists
cp stage_rehersals.png data/control_images/
```

#### Generation Failures
```bash
# Check logs
ls -la output/

tail -f generation_log.jsonl
```

## Post-Generation Workflow

### 1. Image Review
```bash
# Open generated images in image viewer
display data/generated/scene-01_*.png
```

### 2. Quality Validation
```bash
# Run quality assessment
python3 quality_validator.py data/generated/ scene_results.json
```

### 3. Documentation
```bash
# Update generation documentation
cat > docs/usage/generation_report.md << EOF
Generated: $(date)
Scenes: 6 moments
Images: $(ls data/generated/*.png | wc -l)
Status: Complete
EOF
```

## Integration with Existing Systems

### Compatibility
- Existing Scripts: `fal_generate.py` supports scene generation
- Configuration: Compatible with `imagine-config.json`
- Quality Assurance: Integrates with `run_tests.py`
- Documentation: Follows established project documentation patterns

### File Structure
```
project_root/
├── data/
│   ├── scenes/                    # Scene configurations
│   │   └── ledras_scenes_v11_moments.json
│   └── control_images/            # Control images
├── specific_scenes/              # Detailed prompts
│   └── prelude-intro-moments.md
├── docs/                         # Documentation
│   └── usage/                    # Generation guides
├── fal_generate.py                # Image generation script
└── run_tests.py                  # Quality validation
```

## Usage Summary

**The 6-moment Desert Moon Portal Sequence is ready for production image generation.**

**Key Features:**
- Hyper-realistic photorealistic visual specifications
- Complete compatibility with existing generation pipeline
- Detailed technical documentation and troubleshooting
- Integration with project quality assurance systems
- Production-ready file structure and naming conventions

**Next Steps:**
1. Set up FAL_API_KEY environment variable
2. Ensure control image is available
3. Run image generation using provided scripts
4. Validate generated images with quality assurance tests
5. Update documentation with generation results

---

**Version:** 1.0
**Last Updated:** 2026-09-09
**Status:** Ready for Production
