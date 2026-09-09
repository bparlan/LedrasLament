# New Scenes Creation Plan

## Goal
Create new scenes using ledras_scenes_v10_final_clean.json as reference source for improved visual specifications.

## Current State
- `data/scenes/ledras_scenes_v10_final_clean.json` contains 9 scenes with enhanced visual language specifications
- Scenes include: architectural geometry, global structure rules, subscene descriptions, visual briefs, prompt suffixes, and metadata

## Source Document Structure
Based on reading the ledras_scenes_v10_final_clean.json:

### Required Scene Properties:
1. **Core Structure Fields**:
   - `id`: Scene ID (integer)
   - `name`: Scene name (string)
   - `global_structure`: Amphitheater architecture description
   - `global_frame_rule`: Frame constraints
   - `scenes`: Array of individual scenes

2. **Scene Properties**:
   - `id`: Scene identifier
   - `name`: Scene title
   - `description`: Visual description
   - `elements`: Array of scene elements
   - `seed`: Random seed for generation
   - `subscenes`: Array of subscenes (multiple moments per scene)

3. **Subscene Properties**:
   - `id`: Subscene identifier
   - `name`: Subscene title
   - `description`: Detailed visual description
   - `seed`: Random seed
   - `camera`: Camera angle specification
   - `shot_type`: Photography style
   - `color_temperature`: Color scheme

## Architecture Improvements from Source:

### 1. Enhanced Visual Language
- **Reduced vertical walls**: Center tiers (3-4) empty for performers
- **Side composition emphasis**: Open side elements, masking techniques
- **Performance optimization**: Clear stage space, architectural visibility

### 2. Global Constraints
- **Fixed amphitheater geometry**: 6 horizontal tiers + rear wall
- **Rectangular frame invariant**: Cannot be distorted, moved, or decorated
- **Celestial restrictions**: Moon/disk only inside frame opening
- **Center area preservation**: Empty for performance use

### 3. Prompt Architecture
- **Three-layer construction**: description + visual_brief + scene_prompt_suffix + model_negative_suffix
- **Photorealistic focus**: Enhanced negative guardrails
- **Cultural authenticity**: Cypro-Phoenician Bronze Age style
- **No human figures**: Architectural-only focus

### 4. Technical Specifications
- **Model**: fal-ai/flux-control-lora-canny
- **Image size**: landscape_16_9 (1024×576)
- **Control strength**: 0.7
- **Inference steps**: 28
- **Safety checker**: Enabled

## Next Steps
1. Review user scene descriptions
2. Map them to enhanced specifications from v10_final_clean.json
3. Create new scenes maintaining architectural consistency
4. Ensure all scenes follow global structure rules
5. Apply improved visual language for better production quality

## Files to Create/Modify:
- `plans/new_scenes_plan.md` (this document)
- `data/scenes/prelude-new-scenes.json` (new scene definitions)
- Updated `imagine-config.json` (if needed)
- Documentation of improvements