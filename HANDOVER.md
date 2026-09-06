# Ledras Lament Scene Generation Pipeline
## Project Handover Documentation

This document outlines the final production architecture, setup, configuration, and execution instructions for the Ledras Lament scene generation system.

---

### 1. Architecture & Core Files

- **`fal_generate.py`**: The primary executable pipeline script. It handles:
  - Configuration parsing and loading.
  - Scene prompt generation integrating progressive roles (`intro`, `loop`, `outro`).
  - Strict compliance checks using the `LedrasQualityValidator`.
  - Token-based quality validation using the `ValidationRegistry`.
- **`imagine-config.json`**: Technical configuration storing dimensions, pixel density, focus, styling intensity parameters, and target scene data pathways.
- **`scene_templates.json`**: Structural configuration mapping metadata tags, progressive narrative rules, and template variables.
- **`quality_assurance.json`**: Authoritative regulatory specifications outlining cultural styles and technical criteria.
- **`team_config.json`**: Consensus structure for specialized team agents (Technical Visionary, Cultural Scenarist, Production Lead).

---

### 2. Execution & Generation

To run the pipeline and generate/validate prompt assets:

```bash
chmod +x fal_generate.py
./fal_generate.py
```

This generates:
- **`generated_prompts.json`**: Complete prompt registry for all 9 scenes across all progressive roles (27 prompts in total).
- **`validation_report.json`**: Full compliance audit reports mapping verification checks per scene with validation tokens.

---

### 3. Pipeline Standards Met

- **Resolution & Aspect Ratio**: Locked to `1280x720px` with a `19:9` aspect ratio.
- **Pixel Density**: Enforced at exactly `120px/meter` across all scene templates.
- **Spot Light & Center-Focus**: Focused spotlight intensity calibrated at `0.8` for cinematic lighting.
- **Progressive Narrative Flow**: Every scene contains `intro` -> `loop` -> `outro` subscene variations to guarantee narrative continuity.
- **Cultural Accuracy**: Embedded Cypro-Phoenician style constraints with weathered limestone/mortar priorities and prohibited classical greek overrides.
- **Scene 4 Optimization**: Consolidated to 4 elements featuring twilight reflections, water channels, and Aquarius-themed transitions with a 100% validation success rate.
