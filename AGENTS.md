# AGENTS.md - Ledras Lament Engineering Rules

## 🔒 PRODUCTION STABILITY RULES

### 1. Validation Before Execution
- **MANDATORY**: Always validate user requests before starting any work
- **REQUIRED**: Provide clear problem statement, proposed solution, and expected outcome
- **QUESTION**: Ask for clarification when requirements are ambiguous or contradictory

### 2. Code Modification Policy
- **ONLY EDIT** to fix identified bugs or issues in EXISTING CODE
- **NEVER MODIFY** working code for feature additions without explicit user approval
- **ASK VERIFICATION** before any non-bugfix changes
- **DOCUMENT** all changes with clear reasoning

### 3. File Editing Constraints
- **READ FIRST**: Always read existing files completely before editing
- **BACKUP REQUIRED**: Create backup before significant modifications
- **MINIMAL CHANGE**: Make the smallest change necessary to fix the issue
- **TEST AFTER EDIT**: Verify changes work correctly

### 4. Image Generation Policy
- **NEVER GENERATE** images for verification purposes
- **ONLY GENERATE** when explicitly requested with clear intent
- **ASK CONFIRMATION** before any image creation
- **RESPECT "NO"**: Never suggest visual verification as alternative

## 📊 PROJECT AWARENESS - File Index

### Configuration Files (DO NOT EDIT without approval)
```
imagine-config.json          # Model configuration and preprocessing settings
├── fal_model: fal-ai/flux-control-lora-canny
├── fal_control_strength: 1.5
├── preprocess: canny
└── guideline_image: stage/guideline_line_out.png

data/scenes/ledras_scenes_v4.json
└── 9 scenes with structured prompts and styles
```

### Core Implementation (READ BEFORE EDITING)
```
src/fal_generate.py
├── load_config()           # Configuration loading and validation
├── load_scenes()           # Scene data from JSON
├── ensure_line_out()       # Preprocessing (canny/depth modes)
├── generate_stage()        # Image generation API call
└── main()                  # CLI interface
```

### Output Structure
```
assets/generated/
├── scene-01-v002.png       # Generated images (versioned)
├── scene-05-v002.png       # Latest generation
└── stage-09-*.png          # Existing workflow outputs
```

## 🛡️ CURRENT PRODUCTION STATUS

**Status**: ACTIVE PRODUCTION
**Generation Method**: FLUX Control LoRA Canny
**Preprocesing**: Canny edge detection
**Control Input**: stage/guideline_line_out.png
**Control Strength**: 1.5 (high - strict structural control)
**Output Naming**: scene-XXX-v002.png

## ✅ VALIDATION CHECKLIST

Before each task:
1. [ ] Is this a BUG FIX or NEW FEATURE?
2. [ ] If NEW FEATURE: Did I ask for verification?
3. [ ] Am I only fixing EXISTING broken code?
4. [ ] Have I read ALL related files?
5. [ ] Do I understand the current state?
6. [ ] Will my changes affect existing outputs?

## 📋 ACTIVE CHANGES LOG

| Date | Change | Reason | Status |
|------|--------|--------|--------|
| 2026-09-04 | JSON syntax fix | Missing comma in scenes file | ✅ VERIFIED |
| 2026-09-04 | Model config update | Switch to flux-control-lora-canny | ✅ ACTIVE |
| 2026-09-04 | Control strength 1.5 | Increased for guidance control | ✅ ACTIVE |

## ❓ CLARIFICATION POINTS

Before proceeding with ANY work:

1. **Is the current infrastructure stable?**
   - Yes: No breaking changes allowed
   - No: Fix only, don't refactor

2. **Are new features or bug fixes?**
   - Bug fix: Edit allowed with testing
   - New feature: Requires explicit approval

3. **Do I have full context?**
   - Read all related files
   - Understand the workflow
   - Check existing outputs

## 🤔 ASK FOR CLARIFICATION

When in doubt:
1. Stop and analyze
2. Ask specific questions
3. Wait for explicit instructions
4. Don't proceed with assumptions

---
**Last Updated**: 2026-09-04
**Production Status**: ACTIVE - Minimal changes only
