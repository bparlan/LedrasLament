# Ledras Lament — Scene Generation Pipeline

Generates cinematic scene images for a Cypro-Phoenician narrative using
fal.ai FLUX Control LoRA Canny, conditioned on a fixed amphitheater Canny edge map.

## Configuration Model — Single Source of Truth

All project-wide variables live in **one file**:

[`imagine-config.json`](imagine-config.json) — edit this, everything follows.

| Variable | Current Value | Purpose |
|---|---|---|
| `fal_model` | `fal-ai/flux-control-lora-canny` | API model |
| `num_inference_steps` | `28` | Generation quality |
| `scenes_file` | `data/sources/ledras_scenes_v8.json` | Scene definitions |
| `output_dir` | `assets/generated` | Output images |
| `image_size` | `{"width": 1280, "height": 704}` | Output canvas |
| `seed` | `42` | Base RNG seed |
| `subscene_variation_count` | `6` | Subscenes per scene |
| `cultural_authenticity_level` | `cypro_phoenician` | Prompt metadata tag |
| `ornamentation_allowed` | `false` | Style constraint |
| `guidance_scale` | `3.5` | Prompt adherence |
| `enable_safety_checker` | `true` | API safety filter |
| `control_lora_strength` | `0.6` | Canny edge influence |
| `control_lora_image_url` | *(stage guide URL)* | Canny edge map source |

**No hardcoded defaults.** `LedrasConfig` reads only `imagine-config.json`. If the file is missing, the script exits with an error rather than silently serving stale defaults.

### Scene Data

`data/sources/ledras_scenes_v8.json` — 9 scenes, 6 subscenes each (54 total).

Each scene has: `id`, `name`, `description`, `elements[]`, `seed`, `subscenes[]`.

Each subscene has: `id`, `name`, `description`, `seed`, `cultural_notes`.

Negative prompt and style seed are applied globally at the file root.

## Usage

```bash
# Set API key (required) — fal.ai convention
export FAL_KEY="your-fal-api-key-here"

# Generate default scene 6
python3 fal_generate.py

# Generate specific scenes
python3 fal_generate.py 3 5 8

# Generate a single scene
python3 fal_generate.py 2

# Generate all 6 subscenes (narrative arc) for a scene
python3 fal_generate.py --subscenes 1

# Generate subscenes for multiple scenes (12 images total)
python3 fal_generate.py --subscenes 1 3
```

Scene IDs as positional args; default `6` if none given. Use `--subscenes` flag for narrative arc generation — produces 6 images per scene with unique seeds and per-subscene descriptions.

### Output naming

- **Per-scene**: `scene-03_v042_20260907_124714.png`
- **Per-subscene**: `scene-01_100_v042_20260907_151706.png` (`100` = subscene ID)

## Testing

```bash
python3 tests/test_fal_generate.py
```

15 assertions covering resolution mapping, cost estimation, prompt building, API parameter schema compliance, subscene prompt building (6 roles), filename format, and generation log structure.

## Architecture

```
imagine-config.json          ← sole config source
fal_generate.py              ← pipeline: LedrasConfig + LedrasSceneGenerator
utils.py                     ← get_resolution(), estimate_cost()
src/gateway.py               ← advisory token tracking (prints warning, never blocks)
data/sources/ledras_scenes_v8.json  ← scene definitions (54 subscenes across 9 scenes)
tests/test_fal_generate.py   ← test suite (15 assertions)
assets/generated/            ← output images
```

**No runtime dependencies beyond** `requests`, `fal_client` (SyncClient), and Python stdlib.

## Agent Quick Reference

- **Config change?** Edit `imagine-config.json` only.
- **Scene data change?** Edit `data/sources/ledras_scenes_v8.json` only.
- **Image size / control strength / model?** `imagine-config.json` → automatically picked up by `fal_generate.py` on next run.
- `assets/generated/generation_log.jsonl` is append-only — preserves URL even if download fails. Recovery: re-download by replaying URLs from this log within fal's CDN window (~hours).
- Changing config values? `imagine-config.json` only — no need to touch `fal_generate.py`, `AGENTS.md`, or docs.
- Generating subscenes? Use `--subscenes` flag. Each subscene uses its own seed from `ledras_scenes_v8.json`.
- Download failed? Check `assets/generated/generation_log.jsonl` — URLs are logged before download, so a script can re-fetch missing images from fal's temporary CDN.