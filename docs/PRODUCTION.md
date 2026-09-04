**Research summary: Coding-agent infrastructure for solo art production (OhMyPi-focused)**

Coding agents like OhMyPi are already being used as production directors for image + video pipelines. The shift in 2026 is from “prompt writer” to “agent-as-director”: the agent plans scenes, locks structure, generates/expands prompts, drives generation (via API, ComfyUI, or local), self-checks, and manages continuity. Solo developers get the highest leverage because the entire pipeline lives in one terminal session + local files + skills.

### Core patterns that work for solo art production

1. **Agent as Creative Director / Producer**  
   The agent owns the full loop: brief → scene breakdown → structured prompts → generation → QA → iteration. Examples include Hermes Agent + Remotion pipelines, GenClaw (code-driven sketch → generative color), Open-AI-Design-Agent, Wireflow creative agents, and multiple skill libraries that turn coding agents into art directors.

2. **Skills over giant system prompts**  
   OhMyPi (and similar agents) support progressive disclosure via skills (`SKILL.md`). Load only what is needed for the current stage (prompt generation, video direction, style lock, QA). This keeps context lean and reusable.

3. **Structured data as the source of truth**  
   Timeline + scenes live in JSON/TOML/Markdown tables (not free-form chat). The agent reads/writes these files. This is the single highest-leverage practice for consistency across 10 stages + loops + transitions.

4. **Guideline image / structure lock**  
   Your scene-structure guideline image becomes a permanent reference (ControlNet / IP-Adapter / first-frame / multi-ref). The agent is instructed never to break it.

5. **Free-first → paid escalation**  
   Agent prioritizes open-weight / free-tier models (Flux Schnell, SDXL Turbo, Kling free daily, Hailuo, local ComfyUI) and only escalates when quality fails the self-check.

### Recommended context links & documents to feed OhMyPi

Feed these as files in the project (or via `@` / skills) so the agent can pull them on demand. Grouped by usefulness for your exact goals (prompt generation for image/video + timeline/scene categorization).

#### Highest-value skill libraries (install or clone into skills/)

- **Generative-Media-Skills** (calesthio) — 150+ research-backed skills across image, video, audio, direction, QA. Directly usable with coding agents.
- **Omni-Art-Skills** (waterblower) — Creative director skills: script-to-shot-table, video-prompt-director, image-art-direction, style-distill, character-reference-pipeline.
- **AI Game Art Pipeline Skill** (ybuild-ai) — Excellent for structured asset pipelines even if you’re not making games (sprites → loops → consistency).

#### Prompt engineering & timeline / multi-shot documents

- “AI Video Prompt Engineering: 4 Formats That Actually Work in 2026”
- AI Cinematic Pipeline (billpar/ai-cinematic-pipeline) — Full methodology: script breakdown → character/setting assets → shot-by-shot prompts → consistency techniques.
- Structured caption / shot-list formats from recent papers (SmartDirector, CREA, GenClaw).

#### Context-file & agent best practices (for OhMyPi SYSTEM.md / AGENTS.md / skills)

- Progressive disclosure patterns (keep root SYSTEM.md / AGENTS.md short; put domain knowledge in skills/ or foundational/ folders).
- AGENTS.md best practices 2026 (tooling, conventions, anti-patterns only — avoid bloating).
- Context engineering guides that emphasize scope + time (load scene files only when working on that stage).

#### OhMyPi-native capabilities to leverage

- Built-in `generate_image` and `inspect_image` tools.
- Skills system + MCP support (you can add Fal, Replicate, ComfyUI, or custom image/video tools).
- File-based memory: keep `scenes.json` / `timeline.toml` / `style-lock.md` as living documents the agent reads and updates.

### Practical structure for your project (solo OhMyPi)

```
project/
├── SYSTEM.md (or AGENTS.md)          ← short core rules (budget, guideline lock, workflow order)
├── skills/
│   ├── video-prompt-director/
│   ├── image-art-direction/
│   ├── style-consistency/
│   └── comfyui-driver/               ← if using local ComfyUI
├── foundational/
│   ├── guideline-image-rules.md
│   ├── style-bible.md
│   └── model-priority.md             ← free-first list
├── scenes/
│   ├── scenes.json                   ← master timeline + per-scene prompts + status
│   ├── stage-01.md … stage-10.md
│   └── transitions.md
├── assets/
│   ├── guideline.png
│   ├── style-refs/
│   └── generated/
└── prompts/                          ← agent writes expanded prompts here
```

**scenes.json example shape the agent should maintain:**

```json
{
  "global": {
    "aspect": "1:1 or 16:9",
    "resolution": "1024x1024 stills / 720p video",
    "style_lock": "guideline image + seed family",
    "budget_mode": "free-first"
  },
  "stages": [
    {
      "id": 1,
      "title": "...",
      "still_prompt": "...",
      "motion_prompt": "...",
      "duration": "25s loop",
      "status": "accepted | needs_revision",
      "refs": ["guideline.png", "style-ref-01.png"]
    }
  ],
  "transitions": [...]
}
```

### Immediate recommendations for you

1. Install 2–3 of the skill libraries above (especially Generative-Media-Skills + Omni-Art-Skills + ComfyUI-Agent-Kit if you have a GPU).
2. Put your previous efficient OMP context into `SYSTEM.md` and keep it short.
3. Create the `scenes/` structure and have the agent populate/expand the first few stages from your existing scene notes.
4. Add a skill or rule that forces the agent to always start image/video prompts with the guideline-image structure lock.
5. For free experiments: let the agent drive Kling daily credits / Hailuo / local Flux via ComfyUI first.

This turns OhMyPi from a coding assistant into a persistent, low-cost art production director that never loses the timeline, never forgets the structure lock, and systematically multiplies concepts into loops and transitions.
