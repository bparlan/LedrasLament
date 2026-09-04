**Token-efficient image generation guide for OhMyPi + FreeLLMAPI**

FreeLLMAPI exposes a standard OpenAI-compatible endpoint:

```
POST http://localhost:3001/v1/images/generations
Authorization: Bearer freellmapi-YOUR-KEY
```

It routes across every free image model you have enabled (dashboard → **Models → Image**) plus any custom OpenAI-compatible image endpoints you added. Response is normally `b64_json` or a URL, depending on the upstream provider.

### 1. Minimal OMP skill / rule (copy into `skills/image-gen/SKILL.md` or SYSTEM.md)

```markdown
# FreeLLMAPI Image Generation (token-efficient)

## How generation works

- Endpoint: POST {FREELLMAPI_BASE}/v1/images/generations
- Auth: Bearer freellmapi-...
- Model: "auto" (router picks best free image model) or explicit id from Models → Image tab
- Body fields that matter: prompt (required), model, n (1), size ("1024x1024" | "1280x720" | "512x512"), response_format ("b64_json")
- Free capacity is quota-limited per provider. Prefer short prompts. Never send long system context into the image call.
- After generation: save b64 to file, then use inspect_image tool for QA against guideline image.

## Prompt rules (strict, token-saving)

1. Structure lock first: "exact composition and text zones of the provided guideline image"
2. One short positive description (≤ 40 words)
3. Style lock: "same style, lighting, color grade as previous accepted stages"
4. Negative (optional, short): "blurry, deformed text, extra objects, watermark"
5. Never include chat history, explanations, or role text inside the image prompt.
6. For loops later: keep still prompts motion-neutral.

## Call pattern

Use the OpenAI SDK or curl. Always set n=1. Prefer size matching guideline aspect. Log X-Routed-Via header.
If rate-limited, fall back to next model or wait. Never burn paid quota while free remains.
```

### 2. Ultra-short prompt template (use every time)

```
exact composition, text zones and proportions of guideline image. [scene description ≤25 words]. consistent style and lighting. --no blurry, deformed text, extra elements, watermark
```

Example for one of your stages:

```
exact composition, text zones and proportions of guideline image. stage 3: glowing central crystal, soft blue rim light, subtle particle drift. consistent style and lighting. --no blurry, deformed text, extra elements, watermark
```

This stays under ~60 tokens and still locks structure + style.

### 3. Ready-to-use OMP tool call pattern

Have OMP do this (or put it in a skill):

```python
# Pseudocode OMP will generate / execute
from openai import OpenAI
import base64, pathlib

client = OpenAI(
    base_url="http://localhost:3001/v1",
    api_key="freellmapi-YOUR-KEY"
)

resp = client.images.generate(
    model="auto",                    # or specific free image model id
    prompt=SHORT_PROMPT_ABOVE,
    n=1,
    size="1024x1024",                # match your guideline
    response_format="b64_json"
)

img_b64 = resp.data[0].b64_json
path = pathlib.Path(f"assets/generated/stage-{n}.png")
path.write_bytes(base64.b64decode(img_b64))
print("Routed via:", resp.headers.get("x-routed-via"))
# then: inspect_image(path, "Does this match guideline structure and previous style?")
```

### 4. Token-efficiency rules for OMP

| Rule                                                     | Why                                                                                            |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Prompt ≤ 60–70 tokens                                    | Free image models are sensitive to length; longer = more failure + higher chance of rate limit |
| Never put SYSTEM / chat history into the image prompt    | Wastes free quota and confuses the model                                                       |
| Always `n=1`                                             | Multiple images multiply cost/quota burn                                                       |
| Prefer `size` that matches guideline (1024² or 1280×720) | Avoids later crop/resize work                                                                  |
| Use `model="auto"` first                                 | Router picks currently available free capacity                                                 |
| After every image: `inspect_image` against guideline     | Catches structure drift early                                                                  |
| Keep a running `style-seed` or reference list            | Re-use same short style phrase across all 10 stages                                            |

### 5. One-line SYSTEM.md addition

```
Image generation: always use FreeLLMAPI /v1/images/generations with model=auto, n=1, short structure-locked prompts (≤60 tokens). Save b64, then inspect against guideline image. Never embed chat history in the image prompt.
```

### 6. Quick test command (run once to confirm)

```bash
curl http://localhost:3001/v1/images/generations \
  -H "Authorization: Bearer freellmapi-YOUR-KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "prompt": "exact composition of guideline image. simple test crystal on pedestal, soft light. --no blurry, text, watermark",
    "n": 1,
    "size": "1024x1024",
    "response_format": "b64_json"
  }' | jq -r '.data[0].b64_json' | base64 -d > test.png
```

Check the response header `X-Routed-Via` to see which free image model actually ran.
