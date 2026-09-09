#!/usr/bin/env python3
"""
Ledras Lament — Team Context Aggregator

Deterministic, zero-dependency snapshot of project state for theteam
discussions. Reads every machine-readable state file the orchestrator and
its members need, and emits one JSON blob on stdout.

Reads:
  theteam.config                      -> roster, behavior, permitted_skills
  imagine-config.json                 -> runtime generation parameters
  gateway.json                        -> token budget (rights/used/initial)
  docs/stable_project_structure.json  -> registered structure
  health_monitor.log                  -> last health scan status (tail)
  AGENTS.md                           -> production invariants (Rule A-F)

Never invokes the LLM; never mutates project files. A missing or corrupt
source degrades to a null field plus a `sources.<key>.error` note, never a
crash — the orchestrator proceeds with whatever is readable and reports the
gap.

Usage:
  python3 theteam/workflow/context_aggregator.py [--out <path>]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

CONFIG_PATHS = {
    "team": "theteam.config",
    "imagine": "imagine-config.json",
    "gateway": "gateway.json",
    "structure": "docs/stable_project_structure.json",
    "health_log": "health_monitor.log",
    "agents": "AGENTS.md",
}

# imagine-config.json keys worth surfacing in member prompts (stable runtime
# inputs; the rest is prompt-architecture detail).
CONFIG_SUBSET = [
    "fal_model",
    "seed",
    "guidance_scale",
    "num_inference_steps",
    "image_size",
    "enable_safety_checker",
    "control_lora_strength",
    "control_lora_image_url",
    "guideline_image",
    "scenes_file",
    "output_dir",
    "cultural_authenticity_level",
]

RULE_HEADER_RE = re.compile(r"^### Rule ([A-F]):\s*(.+)$", re.MULTILINE)
RULE_BODY_RE = re.compile(r"^-\s+(.+)$", re.MULTILINE)


def _read_json(path: Path) -> tuple[dict | None, str | None]:
    """Read a JSON file; return (data, error). One of the two is None."""
    if not path.exists():
        return None, f"missing: {path.relative_to(PROJECT_ROOT)}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except (json.JSONDecodeError, OSError) as e:
        return None, f"unreadable {path.name}: {e}"


def _tail(path: Path, lines: int = 3) -> list[str]:
    """Last N non-empty lines of a file; empty list if missing."""
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = [ln.rstrip() for ln in f]
    except OSError:
        return []
    return [ln for ln in raw if ln.strip()][-lines:]


def _extract_invariants(agents_path: Path) -> list[str]:
    """Pull '### Rule X: Title' headers and their first bullet from AGENTS.md."""
    if not agents_path.exists():
        return []
    try:
        text = agents_path.read_text(encoding="utf-8")
    except OSError:
        return []
    invariants: list[str] = []
    for block in re.split(r"\n(?=### Rule )", text):
        m = RULE_HEADER_RE.search(block)
        if not m:
            continue
        body = RULE_BODY_RE.search(block.split("\n", 1)[1]) if "\n" in block else None
        summary = body.group(1).strip() if body else ""
        invariants.append(f"Rule {m.group(1)}: {m.group(2).strip()}"
                          + (f" — {summary}" if summary else ""))
    return invariants


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=str, default=None,
                        help="also write the snapshot to this JSON file")
    args = parser.parse_args()

    sources: dict[str, dict] = {}
    state: dict = {"generated_at": datetime.now().isoformat(timespec="seconds")}

    # Team config
    team_cfg, err = _read_json(PROJECT_ROOT / CONFIG_PATHS["team"])
    if team_cfg:
        state["team"] = {
            "project": team_cfg.get("project", {}).get("name", "unknown"),
            "members": [
                {"id": m.get("id"), "role": m.get("role"),
                 "enabled": m.get("enabled", True)}
                for m in team_cfg.get("team", [])
            ],
            "enabled_count": sum(1 for m in team_cfg.get("team", [])
                                 if m.get("enabled", True)),
            "permitted_skills": team_cfg.get("permitted_skills", []),
        }
    sources["team"] = {"error": err} if err else {"ok": True}

    # imagine-config runtime subset
    img_cfg, err = _read_json(PROJECT_ROOT / CONFIG_PATHS["imagine"])
    if img_cfg:
        state["config"] = {k: img_cfg.get(k) for k in CONFIG_SUBSET}
        proj = img_cfg.get("project") or {}
        state["project"] = {
            "name": proj.get("name", "unknown"),
            "stack": proj.get("stack", []),
        }
    sources["imagine"] = {"error": err} if err else {"ok": True}

    # Gateway token budget
    gw, err = _read_json(PROJECT_ROOT / CONFIG_PATHS["gateway"])
    state["gateway"] = gw if gw else {"error": err} if err else None
    sources["gateway"] = {"error": err} if err else {"ok": True}

    # Structure registry (folders + root files only — no doc strings)
    struct, err = _read_json(PROJECT_ROOT / CONFIG_PATHS["structure"])
    if struct:
        state["structure"] = {
            "folders": sorted(struct.get("folders", {}).keys()),
            "root_files": [rf.split(" — ")[0] for rf in struct.get("root_files", [])],
        }
    sources["structure"] = {"error": err} if err else {"ok": True}

    # Health log tail
    health_lines = _tail(PROJECT_ROOT / CONFIG_PATHS["health_log"])
    state["health"] = {"log_tail": health_lines} if health_lines else {"log_tail": [], "note": "no health_monitor.log"}
    sources["health_log"] = {"ok": True}

    # Production invariants from AGENTS.md
    invariants = _extract_invariants(PROJECT_ROOT / CONFIG_PATHS["agents"])
    state["invariants"] = invariants
    sources["agents"] = {"ok": True, "invariants_found": len(invariants)}

    state["sources"] = sources

    out = json.dumps(state, indent=2, ensure_ascii=False)
    sys.stdout.write(out + "\n")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())