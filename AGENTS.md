# AGENTS.md - Ledras Lament Engineering Rules

## 🔒 PRODUCTION STABILITY RULES

### 1. Validation Before Execution
- **MANDATORY**: Always validate user requests before starting any work.
- **REQUIRED**: Provide clear problem statement, proposed solution, and expected outcome.
- **QUESTION**: Ask for clarification when requirements are ambiguous or contradictory.

### 2. Code Modification Policy
- **ONLY EDIT** to fix identified bugs or issues in EXISTING CODE.
- **NEVER MODIFY** working code for feature additions without explicit user approval.
- **ASK VERIFICATION** before any non-bugfix changes.
- **DOCUMENT** all changes with clear reasoning.

### 3. File Editing Constraints
- **READ FIRST**: Always read existing files completely before editing.
- **BACKUP REQUIRED**: Create backup before significant modifications.
- **MINIMAL CHANGE**: Make the smallest change necessary to fix the issue.
- **TEST AFTER EDIT**: Verify changes work correctly.
- **TOKEN EFFICIENCY**: Utilize surgical edits; touch only touched lines. Never re-write entire files when surgical updates suffice.

### 4. Image Generation Policy
- **NEVER GENERATE** images for verification purposes.
- **ONLY GENERATE** when explicitly requested with clear intent.
- **ASK CONFIRMATION** before any image creation.
- **RESPECT "NO"**: Never suggest visual verification as alternative.

## 🏛️ LEDRAS LAMENT PROJECT AWARENESS CONTEXT

### Project Architecture & Identity
- **Repository**: `Ledras Lament` (`/Users/bparlan/devcode/ledraslament`)
- **Domain**: Automated scene visual generation pipeline using fal.ai AI infrastructure for the Ledras Lament artistic/narrative production.
- **Active Model Pipeline**: FLUX.1 [dev] Control LoRA Canny (`fal-ai/flux-control-lora-canny`).
- **Control Input Strategy**: Guideline line-out (`stage/guideline_line_out.png`) via Canny edge detection. Control strength set to `1.5` for strict structural adherence.

### Core Component Map

```
/Users/bparlan/devcode/ledraslament/
├── imagine-config.json               # Primary generation pipeline configuration
│   ├── fal_model: "fal-ai/flux-control-lora-canny"
│   ├── fal_control_strength: 1.5
│   ├── preprocess: "canny"
│   └── guideline_image: "stage/guideline_line_out.png"
├── data/scenes/
│   └── ledras_scenes_v4.json         # Authoritative 9-scene database with visual/narrative prompts
├── src/
│   └── fal_generate.py               # Main CLI & fal_client driver
│       ├── load_config()             # Project config validator
│       ├── load_scenes()             # JSON scene parser
│       ├── ensure_line_out()         # Control input router (canny / depth modes)
│       ├── generate_stage()          # Single-request fal.ai SyncClient engine
│       └── main()                    # CLI argument parser (--scene N, --list-scenes)
├── stage/                            # Structural guideline & depth assets
│   ├── guideline_line_out.png        # Canny edge control template
│   └── depth_template.jpg            # Depth map control template
├── assets/generated/                 # Production output directory
│   ├── scene-01-v002.png             # Active versioned outputs
│   └── scene-05-v002.png
├── session_context_logs/             # Session audit & context reports
│   └── session_report_*.md           # Historical execution logs for agent continuity
└── README.md                         # Command & usage documentation
```

### Production Data Invariants
1. **Single Request = Single Image**: `generate_stage` MUST invoke `client.run` exactly ONCE per scene execution.
2. **Authoritative Scene Source**: All prompts, style seeds, and negative prompts derive strictly from `data/scenes/ledras_scenes_v4.json`.
3. **Output Naming Standard**: Output files MUST be named with explicit scene ID and versioning: `assets/generated/scene-{scene_id:02d}-v{version}.png`.

## 🛡️ CURRENT PRODUCTION STATUS

**Status**: ACTIVE PRODUCTION
**Generation Method**: FLUX Control LoRA Canny (`fal-ai/flux-control-lora-canny`)
**Preprocessing Mode**: Canny (`stage/guideline_line_out.png`)
**Control Strength**: 1.5 (High structural fidelity)
**Output Naming Pattern**: `assets/generated/scene-XX-v002.png`

## ✅ VALIDATION CHECKLIST

Before each task:
1. [ ] Is this a BUG FIX or NEW FEATURE?
2. [ ] If NEW FEATURE: Did I ask for verification?
3. [ ] Am I only fixing EXISTING broken code?
4. [ ] Have I read ALL related files?
5. [ ] Do I understand the current state?
6. [ ] Will my changes affect existing outputs?
7. [ ] Am I using the minimal token-efficient edit?

---
**Last Updated**: 2026-09-05
**Production Status**: ACTIVE - Minimal changes only

## 🆘 PRODUCTION SAVETY RULES

### 4. Data Integrity Protection
- **NEVER REMOVE**: Previous generation versions or historical outputs
- **MANDATORY**: Preserve all existing generated files (scene-*-v*.png, stage-*-*.png)
- **VERSIONING**: Always increment version numbers for new generations
- **BACKUP REQUIRED**: Never overwrite existing production files without explicit approval
- **AUDIT TRAIL**: Keep all generated outputs for reproducibility and rollback

**Rationale**: Generated images contain artistic and narrative content that may be referenced by users or used in subsequent workflows. Removing historical versions breaks reproducibility and user workflows.
