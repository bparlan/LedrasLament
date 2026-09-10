#!/usr/bin/env python3
"""
Registry integration validator - ensures stable_project_structure.json
properly integrates with all system components.
"""

import json
import sys
from pathlib import Path

def validate_registry():
    """Validate project registry integration."""
    PROJECT_ROOT = Path.cwd()
    registry_path = PROJECT_ROOT / "system" / "registry" / "stable_project_structure.json"
    
    if not registry_path.exists():
        print(f"❌ Registry file missing: {registry_path}")
        return False
    
    try:
        with open(registry_path) as f:
            registry = json.load(f)
        
        # Check critical integrations
        required_integrations = ["health_scanner", "theteam_health_skill", "context_aggregator"]
        system_integrations = registry.get("system_integrations", {}).keys()
        
        missing_integrations = []
        for integration in required_integrations:
            if integration not in system_integrations:
                missing_integrations.append(integration)
        
        # Validate required folders exist
        required_folders = registry.get("validation_checks", {}).get("required_folders", [])
        missing_folders = []
        for folder in required_folders:
            if not Path(folder).exists():
                missing_folders.append(folder)
        
        # Validate agentic requirements exist
        agentic_requirements = registry.get("validation_checks", {}).get("agentic_requirements", [])
        missing_agentic = []
        for req in agentic_requirements:
            if not Path(req).exists():
                missing_agentic.append(req)
        
        if missing_integrations:
            print(f"❌ Missing system integrations: {missing_integrations}")
        if missing_folders:
            print(f"❌ Missing required folders: {missing_folders}")
        if missing_agentic:
            print(f"❌ Missing agentic requirements: {missing_agentic}")
        
        success = not (missing_integrations or missing_folders or missing_agentic)
        
        if success:
            print(f"✅ Registry integration is properly configured")
            print(f"   System integrations: {len(system_integrations)}/3")
            print(f"   Required folders: {len(required_folders)} validated")
            print(f"   Agentic requirements: {len(agentic_requirements)} present")
        
        return success
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in registry: {e}")
        return False

if __name__ == "__main__":
    success = validate_registry()
    sys.exit(0 if success else 1)
