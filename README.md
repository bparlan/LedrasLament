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
# Set API key (required)
export FAL_API_KEY="your-fal-api-key-here"

# Generate default scene 6
python3 fal_generate.py

# Generate specific scenes
python3 fal_generate.py 3 5 8

# Generate a single scene
python3 fal_generate.py 2
```

No `--flags`, no subcommands. Scene IDs as positional args; default `6` if none given.

## Testing

```bash
python3 tests/test_fal_generate.py
```

10 assertions covering resolution mapping, cost estimation, prompt building, and API parameter schema compliance.

## Architecture

```
imagine-config.json          ← sole config source
fal_generate.py              ← pipeline: LedrasConfig + LedrasSceneGenerator
utils.py                     ← get_resolution(), estimate_cost()
src/gateway.py               ← advisory token tracking (prints warning, never blocks)
data/sources/ledras_scenes_v8.json  ← scene definitions
tests/test_fal_generate.py   ← test suite
assets/generated/            ← output images
```

**No runtime dependencies beyond** `requests`, `fal_client` (SyncClient), and Python stdlib.

## Agent Quick Reference

- **Config change?** Edit `imagine-config.json` only.
- **Scene data change?** Edit `data/sources/ledras_scenes_v8.json` only.
- **Image size / control strength / model?** `imagine-config.json` → automatically picked up by `fal_generate.py` on next run.
- No need to touch `fal_generate.py`, `AGENTS.md`, or docs when config values change.