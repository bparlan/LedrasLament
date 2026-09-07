# Ledras Lament Engineering Rules

## Production Stability

### Validation
- Always validate before starting work
- Clear problem statement, solution, expected outcome
- Ask clarification when requirements are ambiguous

### Code Changes
- ONLY fix bugs in existing code
- NEVER modify working code for new features without approval
- Verify non-bugfix changes before proceeding
- Document all changes with reasoning

### File Handling
- READ files completely before editing
- Create backups before modifications
- Make minimal changes only
- Test all changes before completion
- Use surgical edits when possible

### Image Generation
- NEVER generate images for verification
- ONLY generate when explicitly requested
- ASK before any image creation
- Respect "NO" decisions immediately

## Current Configuration

### Guideline Image
- `stage/stage_v6_alphasky.png`

### Prompt Source
- `data/scenes/ledras_scenes_v7.json`

## Critical Rules

### Rule A: Model-Preprocessing Pair
- FLUX Control LoRA Canny MUST use Canny preprocessing only
- Mixing Canny with depth preprocessing creates structural noise
- Assert before generation → abort with explicit configuration error
- Rationale: Canny requires Canny preprocessing; depth requires depth preprocessing. Mixing creates structural noise

### Rule B: Canvas Geometry Conformance
- Output canvas dimensions MUST exactly match projection guide dimensions
- No post-processing warping allowed
- Action: `(width, height) = guide_dimensions; abort on mismatch`
- Rationale: Projected content must align with physical projection geometry. No post-processing warping

### Rule C: Structural-Only Conditioning
- NO `image_url` when no initial artwork exists
- Use prompt + `control_lora_image_url` ONLY
- Action: Verify `image_url` field is omitted in text-to-image endpoint requests
- Rationale: Prevents guide domination; enforces artistic reinterpretation of structure

### Rule D: Control Strength Limits
- Full control window (0.0–1.0) → `control_strength ≤ 0.7`, or use partial window (0.2–0.8)
- Action: Validate before generation; warn or auto-adjust parameters
- Rationale: High control window + high strength = output repetition of guide instead of reinterpretation

### Rule E: Guide Image Selection Hierarchy
- `guide_line_out.jpg` > `guideline_line_out.png` > `depth_template.jpg`
- Action: Primary selector; depth ONLY for depth-aware models (not Canny)
- Rationale: `guide_line_out.jpg` is architectural line guide; depth is spatial depth. Wrong model → wrong guide

### Rule F: Issue/Problem Reporting Protocol
- When any issue or blocker arises during execution, never silence it
- Action: 
  1. Immediately document the exact problem and root cause
  2. Surface the issue with clear, non-technical explanation
  3. Propose specific, actionable infrastructure-level fixes
  4. Never proceed without resolution unless explicitly instructed
- Rationale: Silent failures lead to wasted effort and degraded trust. Transparent issue reporting enables rapid troubleshooting and prevents downstream cascade failures

## Validation Checklist

Before each task:
1. [ ] Is this a BUG FIX or NEW FEATURE?
2. [ ] If NEW FEATURE: Did I ask for verification?
3. [ ] Am I only fixing EXISTING broken code?
4. [ ] Have I read ALL related files?
5. [ ] Do I understand the current state?
6. [ ] Will my changes affect existing outputs?
7. [ ] Am I using the minimal token-efficient edit?

---

## Production Safety

### Data Integrity Protection
- NEVER REMOVE: Previous generation versions or historical outputs
- MANDATORY: Preserve all existing generated files (scene-_-v_.png, stage-_-_.png)
- VERSIONING: Always increment version numbers for new generations
- BACKUP REQUIRED: Never overwrite existing production files without explicit approval
- AUDIT TRAIL: Keep all generated outputs for reproducibility and rollback

**Rationale**: Generated images contain artistic and narrative content that may be referenced by users or used in subsequent workflows. Removing historical versions breaks reproducibility and user workflows.

---

## Secrets and Environment Files — STRICT

Secret values are outside the agent's working context.

### NEVER read or inspect secret files

Agents MUST NOT read, display, search, grep, parse, copy, modify, or otherwise inspect:

- `.env`
- `.env.*`
- files containing API keys, tokens, passwords, credentials, or private keys

This prohibition applies even when debugging authentication or configuration problems.

Forbidden examples include:

```bash
cat .env
less .env
head .env
tail .env
grep ...
rg ...
find ... -exec cat
printenv
env
```

## SECRET BOUNDARY — NON-NEGOTIABLE

The agent must treat secrets as opaque runtime dependencies.

The user may provide environment variable NAMES, but secret VALUES are never required for development, debugging, or implementation.

### Known secret interface

Use only the environment variable names explicitly provided by the user.

Example:

```text
FAL_API_KEY
```