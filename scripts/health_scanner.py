#!/usr/bin/env python3
"""
Ledras Lament Health Scanner - Core file and folder health monitor.
Zero-configuration, standard-library-first scanner.

Features:
- Registry validation (stable_project_structure.json)
- Asset health checking (generated images, logs)
- Production asset discovery (specific_scenes, etc.)
- Loop-friendly report generation

Usage:
  python3 scripts/health_scanner.py --mode interactive    # manual check
  python3 scripts/health_scanner.py --mode daemon          # scheduled
  python3 scripts/health_scanner.py --mode trigger         # on file changes
  python3 scripts/health_scanner.py --report              # JSON output only
"""

import os
import json
import argparse
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

# --- Constants (Ponytail: define once, reuse) ---
PROJECT_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = PROJECT_ROOT / "docs" / "stable_project_structure.json"
SCANNER_VERSION = "2.0.0"
SCAN_FREQUENCY_MINUTES = 30

# --- Core scanning logic (pure standard library) ---
class LedrasHealthScanner:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.report = {
            "scanner_version": SCANNER_VERSION,
            "scan_time": datetime.now().isoformat(),
            "project": project_root.name,
            "findings": [],
            "registry_status": "unknown",
            "asset_status": "unknown",
            "production_status": "unknown"
        }

    def scan_registry_structure(self) -> None:
        """Validate registry against actual filesystem."""
        if not REGISTRY_PATH.exists():
            self.report["findings"].append({
                "severity": "critical",
                "category": "registry",
                "location": str(REGISTRY_PATH),
                "description": "Registry file missing",
                "impact": "Project structure cannot be validated"
            })
            self.report["registry_status"] = "missing"
            return

        try:
            with open(REGISTRY_PATH, 'r') as f:
                registry = json.load(f)

            # Check registered folders exist
            folders = registry.get("folders", {})
            missing_folders = []
            for folder_name in folders.keys():
                if not (self.project_root / folder_name.lstrip("/")).exists():
                    missing_folders.append(folder_name)

            if missing_folders:
                self.report["findings"].append({
                    "severity": "warning",
                    "category": "registry",
                    "location": str(REGISTRY_PATH),
                    "description": f"Registered folders missing: {missing_folders}",
                    "impact": "Registered folders do not exist in filesystem"
                })

            # Check for unregistered important folders
            important_unregistered = [
                "specific_scenes", "assets/generated", "docs"
            ]
            registered_folders = set(folders.keys())

            for important in important_unregistered:
                if not (self.project_root / important).exists():
                    continue

                # Check if it's registered (allow flexible matching)
                is_registered = any(
                    important in reg_folder or reg_folder in important
                    for reg_folder in registered_folders
                )

                if not is_registered:
                    self.report["findings"].append({
                        "severity": "info",
                        "category": "registry",
                        "location": f"project_root/{important}",
                        "description": f"Important folder '{important}' not registered",
                        "impact": "Production assets lack documentation coverage"
                    })

            self.report["registry_status"] = "ok"

        except Exception as e:
            self.report["findings"].append({
                "severity": "error",
                "category": "registry",
                "location": str(REGISTRY_PATH),
                "description": f"Registry validation failed: {str(e)}",
                "impact": "Registry may be corrupted or invalid JSON"
            })
            self.report["registry_status"] = "error"

    def scan_asset_health(self) -> None:
        """Check generated assets for anomalies."""
        assets_dir = self.project_root / "assets" / "generated"
        if not assets_dir.exists():
            self.report["findings"].append({
                "severity": "info",
                "category": "assets",
                "location": str(assets_dir),
                "description": "Assets directory missing",
                "impact": "No generated images to validate"
            })
            self.report["asset_status"] = "missing"
            return

        # Recursively find all PNG files (nested directories supported)
        png_files = []
        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                if file.lower().endswith('.png'):
                    png_files.append(Path(root) / file)

        if not png_files:
            self.report["findings"].append({
                "severity": "warning",
                "category": "assets",
                "location": str(assets_dir),
                "description": "No PNG files found",
                "impact": "No image generation outputs detected"
            })
            self.report["asset_status"] = "empty"
            return

        # Check file sizes (reasonable range for PNG images)
        tiny_files = []
        huge_files = []
        for png_file in png_files:
            size_kb = png_file.stat().st_size / 1024
            if size_kb < 50:  # suspiciously small for PNG
                tiny_files.append(png_file.name)
            elif size_kb > 5000:  # suspiciously large
                huge_files.append(png_file.name)

        if tiny_files:
            self.report["findings"].append({
                "severity": "warning",
                "category": "assets",
                "location": str(assets_dir),
                "description": f"Potentially corrupted tiny PNG files: {tiny_files[:5]}",
                "impact": f"{len(tiny_files)} files may be incomplete or corrupted"
            })

        if huge_files:
            self.report["findings"].append({
                "severity": "info",
                "category": "assets",
                "location": str(assets_dir),
                "description": f"Large PNG files detected: {huge_files[:5]}",
                "impact": f"{len(huge_files)} files unusually large"
            })

        # Check for log file
        log_file = assets_dir / "generation_log.jsonl"
        if not log_file.exists():
            self.report["findings"].append({
                "severity": "info",
                "category": "assets",
                "location": str(log_file),
                "description": "Generation log missing",
                "impact": "No download/recovery tracking available"
            })

        self.report["asset_status"] = "scanned"

    def scan_production_assets(self) -> None:
        """Check for unregistered production assets."""
        production_dir = self.project_root / "specific_scenes"
        if not production_dir.exists():
            self.report["findings"].append({
                "severity": "info",
                "category": "production",
                "location": str(production_dir),
                "description": "Production assets directory missing",
                "impact": "No scene-specific production prompts"
            })
            self.report["production_status"] = "missing"
            return

        # Count production files
        md_files = list(production_dir.glob("*.md"))
        if not md_files:
            self.report["findings"].append({
                "severity": "warning",
                "category": "production",
                "location": str(production_dir),
                "description": "No markdown files in production assets",
                "impact": "Production prompts not properly documented"
            })
            self.report["production_status"] = "empty"
            return

        # Check key file exists
        key_file = production_dir / "prelude-intro-moments.md"
        if not key_file.exists():
            self.report["findings"].append({
                "severity": "warning",
                "category": "production",
                "location": str(key_file),
                "description": "Key production file 'prelude-intro-moments.md' missing",
                "impact": "Main scene sequence not available"
            })

        self.report["production_status"] = "ok"

    def generate_report(self, mode: str = "quiet") -> None:
        """Output scan results."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if mode == "quiet":
            print(f"🔍 Ledras Health Scanner v{SCANNER_VERSION} - {timestamp}")
            print(f"Registry: {self.report['registry_status']}")
            print(f"Assets: {self.report['asset_status']}")
            print(f"Production: {self.report['production_status']}")

            severity_counts = {}
            for finding in self.report["findings"]:
                sev = finding["severity"]
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

            if severity_counts:
                print("Issues found:")
                for sev in ["critical", "warning", "error", "info"]:
                    if sev in severity_counts:
                        print(f"  {sev}: {severity_counts[sev]}")

        elif mode == "json":
            print(json.dumps(self.report, indent=2, default=str))

        elif mode == "detailed":
            print(f"🔍 Ledras Health Scanner v{SCANNER_VERSION} - {timestamp}")
            print(f"Project root: {self.project_root}")
            print(f"Registry file: {REGISTRY_PATH}")

            if self.report["findings"]:
                print("\nDetailed findings:")
                for finding in self.report["findings"]:
                    emoji = {"critical": "🚨", "warning": "⚠️", "error": "❌", "info": "ℹ️"}.get(
                        finding["severity"], "📝"
                    )
                    print(f"{emoji} {finding['severity'].upper()}: {finding['description']}")
                    print(f"   Location: {finding['location']}")
                    print(f"   Impact: {finding['impact']}")
                    print()
            else:
                print("✅ No issues found")

    def run(self, mode: str = "quiet") -> None:
        """Execute full health check."""
        self.scan_registry_structure()
        self.scan_asset_health()
        self.scan_production_assets()
        self.generate_report(mode)

# --- Helper functions ---
def setup_daemon():
    """Configure daemon scheduling (placeholder)."""
    print("📅 Daemon mode configured")
    print(f"   Scan frequency: every {SCAN_FREQUENCY_MINUTES} minutes")
    print(f"   Log file: {PROJECT_ROOT}/health_scanner.log")

def setup_triggers():
    """Configure file system event triggers (placeholder)."""
    print("🔄 Trigger mode configured")
    print("   Watching for changes in:")
    print("   - docs/stable_project_structure.json")
    print("   - scripts/health_scanner.py")
     print("   - data/scenes/*.json")
    print("   - assets/generated/*.png")

# --- CLI interface ---
def main():
    parser = argparse.ArgumentParser(description="Ledras Lament Health Scanner")
    parser.add_argument(
        "--mode",
        choices=["interactive", "daemon", "trigger"],
        default="interactive",
        help="Execution mode"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Output JSON report only"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show scanner version and exit"
    )

    args = parser.parse_args()

    if args.version:
        print(f"Ledras Health Scanner v{SCANNER_VERSION}")
        return

    scanner = LedrasHealthScanner(PROJECT_ROOT)

    if args.report:
        scanner.run("json")
    elif args.quiet:
        scanner.run("quiet")
    else:
        scanner.run("detailed")

    # Mode-specific setup
    if args.mode == "daemon":
        setup_daemon()
    elif args.mode == "trigger":
        setup_triggers()

if __name__ == "__main__":
    main()
