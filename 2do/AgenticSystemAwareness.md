# Agentic System Awareness - Ledras Lament

## 🎯 Overview

This document defines the **Agentic Development Rules** that guide the Ledras Lament project toward a codebase that AI agents can work with efficiently. These rules prevent the common pattern where developers create new scripts for parameter variations instead of enhancing existing infrastructure.

## 📊 Current System State

### Compliance Score: 20/100

| Rule | Status | Issues Found | Score |
|------|--------|--------------|-------|
| Rule 1: CLI Parameterization | ❌ | 30+ one-off scripts | 20 |
| Rule 2: Config Schema | ❌ | setattr dump without validation | 30 |
| Rule 3: Single Key Per Concept | ⚠️ | Multiple control_image keys | 70 |
| Rule 4: Fail-Fast Init | ❌ | Silent None propagation | 25 |
| Rule 5: Comprehensive CLI | ❌ | Only --subscenes flag | 40 |
| Rule 6: Deterministic Paths | ⚠️ | Random seed + timestamp | 60 |
| Rule 7: Prompt Integration | ❌ | Per-scene config unused | 35 |
| Rule 8: System Integration | ❌ | Partial implementation | 30 |
| Rule 9: Continuous Improvement | ❌ | No compliance feedback | 20 |
| Rule 10: Knowledge Preservation | ⚠️ | Partial system awareness | 50 |

---

## 🔧 Quick Fix Guide

### Most Critical Violations

#### 🚨 Rule 1: CLI Parameterization (Score: 20)

**Problem:** 30+ one-off scripts in recyclebin indicate developers use new files for parameter variations.

**Evidence:**
```bash
ls recyclebin/*.py | wc -l  # ~30 files
```

**Fix:**
```bash
# Add comprehensive CLI flags to fal_generate.py
python3 scripts/agentic_compliance.py --fix Rule1

# Resulting CLI:
# python3 fal_generate.py [scene_ids] [--subscenes] [--model <model>]
#                     [--strength <0.0-1.0>] [--seed <int>] [--resolution <widthxheight>] [--help]
```

#### 🚨 Rule 2: Config Schema Validation (Score: 30)

**Problem:** Config uses `setattr(self, key, value)` pattern, silently dropping unknown keys.

**Evidence:**
```python
# In fal_generate.py LedrasConfig:
for key, value in config_data.items():
    setattr(self, key, value)  # No validation!
```

**Fix:**
```bash
# Replace with structured config class:
class LedrasConfig:
    def __init__(self):
        self.validate_and_normalize()

    def validate_and_normalize(self):
        # Explicit validation for each key
        self.fal_model = self._validate_model(self.config.get("fal_model"))
        self.image_size = self._normalize_image_size(self.config.get("image_size"))
        # ... other validations
```

#### ⚠️ Rule 3: Single Key Per Concept (Score: 70)

**Problem:** Multiple aliases for control image concept.

**Evidence:**
```json
{
  "control_lora_image_url": "data/...",
  "prompt_architecture": {
    "control_image_path": "data/...",
    "control_image_url_path": "data/..."
  },
  "guideline_image": "data/..."
}
```

**Fix:**
```bash
# Consolidate to single key:
# Keep: control_lora_image_url
# Deprecate: control_image_path, control_image_url_path, guideline_image
# Update references to use canonical key only
```

---

## 🛠️ Compliance Commands

### Quick Compliance Check
```bash
# Get current compliance status
python3 scripts/agentic_compliance.py --all --out reports/agentic-compliance-$(date +%Y%m%d).json

# Fix specific rule violations
python3 scripts/agentic_compliance.py --fix Rule1
python3 scripts/agentic_compliance.py --fix Rule2

# Get actionable guidance
python3 theteam/workflow/context_aggregator.py --enable-compliance
```

### System Integration
```bash
# Full health check with agentic compliance
python3 scripts/health_scanner.py --mode interactive

# Get team context with compliance findings
python3 theteam/workflow/context_aggregator.py --out /tmp/context.json --enable-compliance
```

---

## 📋 Task Dependencies

### System-Level Dependencies
```yaml
task_dependencies:
  - TSK-009: "Enhance CLI Parameterization"  # Depends on Rule 1 compliance
  - TSK-010: "Implement Config Validation"    # Depends on Rule 2 compliance
  - TSK-011: "Consolidate Config Keys"        # Depends on Rule 3 compliance
  - TSK-012: "Add Fail-Fast Init"             # Depends on Rule 4 compliance
```

### Evidence Requirements
```yaml
compliance_evidence:
  Rule1_CLI_Parameterization:
    - "fal_generate.py contains --model, --strength, --seed, --resolution flags"
    - "recyclebin contains ≤ 2 non-backup/test scripts"
    - "All script variations covered by CLI flags"

  Rule2_Config_Schema:
    - "No setattr(self, key, value) pattern in LedrasConfig"
    - "image_size config normalized to dict at load time"
    - "All required config keys have explicit validation"

  Rule3_Single_Key:
    - "Exactly one control image key in imagine-config.json"
    - "All references use canonical key"
    - "Deprecated aliases marked with comments"
```

---

## 🔄 Continuous Improvement

### Compliance Score Tracking
```json
{
  "compliance_tracking": {
    "baseline_score": 20,
    "target_score": 95,
    "last_check": "2026-09-10T15:54:00Z",
    "improvement_goal": "Add 1-2 points per week",
    "milestones": [
      "Week 1: CLI Parameterization (Target: 40)",
      "Week 2: Config Schema (Target: 60)",
      "Week 3: Production Integration (Target: 80)",
      "Week 4: Full System (Target: 95)"
    ]
  }
}
```

### Feedback Loop
```bash
# Weekly compliance check
python3 scripts/agentic_compliance.py --all --out reports/agentic-compliance-weekly.json

# Generate improvement report
python3 -c "
import json
report = json.load(open('reports/agentic-compliance-weekly.json'))
score = report['compliance_score']
improvement = score - 20  # baseline
print(f'Compliance improved by {improvement} points to {score}/100')
print('Next priority: Fix ' + [r for r in report['findings'] if r['severity'] == 'critical'][0]['rule'])
"
```

---

## 📚 References

### Related Documents
- `AGENTS.md` - Production stability rules (Rules A-F)
- `system/registry/stable_project_structure.json` - Project structure registry
- `imagine-config.json` - Runtime configuration
- `gateway.json` - Token budget management
- `theteam.config` - Team configuration
- `2do/TASK_CONFIG.md` - Task management configuration
- `2do/TASK_MANIFEST.md` - Task execution framework

### Tools & Scripts
- `fal_generate.py` - Main generation pipeline
- `scripts/health_scanner.py` - Health monitoring
- `theteam/workflow/context_aggregator.py` - Context aggregation
- `scripts/agentic_compliance.py` - **NEW** - Agentic compliance checker
- `theteam/workflow/health_monitor/theteam_health_skill.py` - Health monitoring skill

---

## 🚀 Getting Started

### For New Development
1. **Run compliance check first:**
   ```bash
   python3 scripts/agentic_compliance.py --all
   ```
2. **Address critical violations:**
   ```bash
   # Fix CLI parameterization
   python3 scripts/agentic_compliance.py --fix Rule1

   # Fix config schema
   python3 scripts/agentic_compliance.py --fix Rule2
   ```
3. **Verify fixes:**
   ```bash
   python3 scripts/agentic_compliance.py --all
   ```

### For Existing Development
1. **Check compliance before making changes:**
   ```bash
   # Get specific guidance for violations
   python3 theteam/workflow/context_aggregator.py --enable-compliance
   ```
2. **Follow the evidence-based task system:**
   - Review `2do/TASK_CONFIG.md` for task categories
   - Use `2do/TASK_MANIFEST.md` for execution framework
   - Submit evidence for task completion
   ```

---

## 🎯 Success Metrics

### Quantitative Goals
- **Compliance Score:** 95/100 by end of week 4
- **One-off Scripts:** ≤ 2 in recyclebin by week 2
- **CLI Coverage:** 100% of script variations covered by flags by week 3
- **Documentation:** All rules documented in AGENTS.md by week 1

### Qualitative Goals
- **Developer Experience:** No need to create new scripts for parameter variations
- **Agent Efficiency:** AI agents can work with codebase without extensive exploration
- **System Stability:** Clear, predictable error messages and guidance
- **Continuous Improvement:** Weekly compliance monitoring and improvement

---

*This system ensures that every new development task starts with awareness of agentic-friendly patterns, preventing the accumulation of technical debt and one-off scripts while providing clear guidance for compliance improvements.*