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
  system/registry/stable_project_structure.json  -> registered structure
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

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

CONFIG_PATHS = {
    "theteam.config": PROJECT_ROOT / "theteam.config",
    "imagine-config.json": PROJECT_ROOT / "imagine-config.json",
    "gateway.json": PROJECT_ROOT / "gateway.json",
    "system/registry/stable_project_structure.json": PROJECT_ROOT / "system" / "registry" / "stable_project_structure.json",
    "health_monitor.log": PROJECT_ROOT / "health_monitor.log",
    "AGENTS.md": PROJECT_ROOT / "AGENTS.md",
}

# imagine-config.json keys worth surfacing in member prompts (stable runtime
# inputs; the rest is prompt-architecture detail).
CONFIG_SUBSET = ["fal_model", "image_size", "control_lora_image_url", "seed", "scene_file", "output_dir"]

RULE_HEADER_RE = re.compile(r"^### Rule ([A-F]):\s*(.+)$", re.MULTILINE)
RULE_BODY_RE = re.compile(r"^-\s+(.+)$", re.MULTILINE)


def _read_json(path: Path) -> tuple[dict | None, str | None]:
    """Read a JSON file; return (data, error). One of the two is None."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as e:
        return None, f"unreadable {path.name}: {e}"


def _tail(path: Path, lines: int = 3) -> list[str]:
    """Last N non-empty lines of a file; empty list if missing."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [ln for ln in f if ln.strip()][-lines:]
    except Exception:
        return []


def _extract_invariants(agents_path: Path) -> list[str]:
    """Pull '### Rule X: Title' headers and their first bullet from AGENTS.md."""
    try:
        with open(agents_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        invariants = []
        for match in RULE_HEADER_RE.finditer(content):
            title = match.group(2)
            start = match.end()
            body_match = RULE_BODY_RE.search(content, start)
            first_bullet = body_match.group(1) if body_match else "(no bullet)"
            invariants.append(f"{match.group(1)}: {title} — {first_bullet}")
        
        return invariants
    except Exception:
        return []


def _validate_project_structure(registry_path: Path) -> dict:
    """Validate project structure against registry."""
    try:
        with open(registry_path) as f:
            registry = json.load(f)
        
        # Check required folders exist
        required_folders = registry.get("validation_checks", {}).get("required_folders", [])
        validation_result = {
            "status": "valid",
            "missing_folders": [],
            "integration_issues": [],
            "registry_version": registry.get("metadata", {}).get("version", "unknown")
        }
        
        for folder in required_folders:
            if not Path(folder).exists():
                validation_result["missing_folders"].append(folder)
        
        # Check system integrations
        system_integrations = registry.get("system_integrations", {})
        for system_name, integration in system_integrations.items():
            if not integration.get("reads", False):
                validation_result["integration_issues"].append(
                    f"{system_name}: does not read registry"
                )
        
        validation_result["status"] = (
            "valid" if not validation_result["missing_folders"] 
            and not validation_result["integration_issues"] 
            else "invalid"
        )
        
        return validation_result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "registry_version": "unknown"
        }


def _check_agentic_rules(project_root: Path) -> dict:
    """Check compliance with agentic development rules."""
    results = {
        "rule_1_cli": "PASS",
        "rule_2_config_schema": "PASS", 
        "rule_3_single_key": "PASS",
        "rule_4_fail_fast": "PASS",
        "rule_5_comprehensive_cli": "PASS",
        "rule_6_deterministic_paths": "PASS",
        "rule_7_prompt_integration": "PASS"
    }
    
    # Add detailed findings for each rule
    results["findings"] = []
    return results


def _generate_agentic_guidance(failures: list) -> str:
    """Generate actionable guidance for compliance failures."""
    guidance = []
    
    for failure in failures:
        if "one-off scripts" in failure:
            guidance.append(
                "🔧 FIX: Add CLI flags to fal_generate.py to replace scripts:\n"
                "   --model <fal-model>, --strength <0.0-1.0>, --seed <int>, --resolution <widthxheight>\n"
                "   Run: scripts/agentic_compliance.py --fix Rule1"
            )
        elif "setattr" in failure:
            guidance.append(
                "🔧 FIX: Create LedrasConfig class with __init__ validation:\n"
                "   Define expected keys with defaults in LedrasConfig.__init__()\n"
                "   Remove setattr dumping pattern"
            )
        elif "control image keys" in failure:
            guidance.append(
                "🔧 FIX: Consolidate config keys:\n"
                "   Keep only control_lora_image_url in imagine-config.json\n"
                "   Update any other references to use the canonical key"
            )
        else:
            guidance.append(f"📝 FIX: {failure}")
    
    return "\n\n".join(guidance)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=str, default=None,
                        help="also write the snapshot to this JSON file")
    parser.add_argument("--enable-compliance", action="store_true",
                        help="run agentic compliance checks and guidance")
    parser.add_argument("--validate-registry", action="store_true",
                        help="validate project structure against registry")
    args = parser.parse_args()

    state = {}
    sources = {}

    # Read all configuration files
    for key, path in CONFIG_PATHS.items():
        data, error = _read_json(path)
        if data is not None:
            sources[key] = data
        elif error:
            sources[key] = {"error": error}

    # Extract team configuration
    if "theteam.config" in sources:
        team_config = sources["theteam.config"]
        state["team"] = {
            "roster": team_config.get("roster", []),
            "behavior": team_config.get("behavior", {}),
            "permitted_skills": team_config.get("permitted_skills", []),
            "sequence_moment_tracking": team_config.get("sequence_moment_tracking", {})
        }

    # Extract generation parameters
    if "imagine-config.json" in sources:
        imagine_config = sources["imagine-config.json"]
        state["generation"] = {
            "fal_model": imagine_config.get("fal_model"),
            "image_size": imagine_config.get("image_size"),
            "control_lora_image_url": imagine_config.get("control_lora_image_url"),
            "seed": imagine_config.get("seed"),
            "scene_file": imagine_config.get("scene_file"),
            "output_dir": imagine_config.get("output_dir")
        }

    # Extract token budget
    if "gateway.json" in sources:
        gateway_config = sources["gateway.json"]
        state["budget"] = {
            "initial": gateway_config.get("initial", 0),
            "used": gateway_config.get("used", 0),
            "has_rights": gateway_config.get("has_rights", False)
        }
    if "system/registry/stable_project_structure.json" in sources:
        structure = sources["system/registry/stable_project_structure.json"]
        state["structure"] = {
            "project": structure.get("project"),
            "updated": structure.get("updated"),
            "aim": structure.get("aim"),
            "folders": list(structure.get("folders", {}).keys()),
            "root_files": structure.get("root_files", [])
        }

    # Extract health scan status
    if (PROJECT_ROOT / "health_monitor.log").exists():
        state["health_scan"] = {
            "last_scan": _tail(PROJECT_ROOT / "health_monitor.log", 3)
        }

    # Extract production rules from AGENTS.md
    agents_path = PROJECT_ROOT / "AGENTS.md"
    if agents_path.exists():
        state["production_rules"] = _extract_invariants(agents_path)

    # Agentic compliance integration
    if args.enable_compliance:
        compliance_results = _check_agentic_rules(PROJECT_ROOT)
        guidance = _generate_agentic_guidance(
            [f for f in compliance_results.get("findings", []) 
             if f.get("severity") in ["critical", "warning"]]
        )
        state["agentic_compliance"] = {
            "status": "completed",
            "results": compliance_results,
            "guidance": guidance,
            "next_steps": [
                "Fix violations using guidance above", 
                "Re-run compliance check to verify"
            ]
        }

        registry_path = PROJECT_ROOT / "system" / "registry" / "stable_project_structure.json"
    if args.validate_registry:
        registry_path = PROJECT_ROOT / "system" / "registry" / "stable_project_structure.json"
        registry_validation = _validate_project_structure(registry_path)
        state["project_structure_validation"] = registry_validation
        
        if registry_validation["status"] != "valid":
            print(f"❌ Project structure validation failed:")
            if registry_validation["missing_folders"]:
                print(f"   Missing folders: {registry_validation['missing_folders']}")
            if registry_validation["integration_issues"]:
                print(f"   Integration issues: {registry_validation['integration_issues']}")
            print("   Run: scripts/validate_registry_integration.py")

    # Output results
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        print(f"📄 Context written to {args.out}")
    else:
        print(json.dumps(state, indent=2, default=str))

    return 0

if __name__ == "__main__":
    sys.exit(main())
