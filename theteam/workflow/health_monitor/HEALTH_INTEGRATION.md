# Health Integration for Ledras Lament

This document describes the hybrid health monitoring system for the Ledras Lament project, providing file and folder health checks with automated scanning and workflow coordination.

## Overview

The health integration system provides a unified approach to monitoring project health, combining file system scanning with workflow orchestration to ensure the Ledras Lament pipeline remains stable and functional.

## Key Components

### 1. Core Scanner (`scripts/health_scanner.py`)

**Purpose**: Lightweight, standard-library-based scanner that checks:
- Registry structure vs actual filesystem
- Generated asset health (PNG files, logs)
- Production asset discovery (specific_scenes, etc.)

**Features**:
- Zero external dependencies (pure Python standard library)
- Recursive directory scanning support
- Configurable output modes (quiet, detailed, JSON)
- Cross-platform compatibility
- Performance-optimized for large directories

**Usage Examples**:
```bash
# Detailed scan with full output
python3 scripts/health_scanner.py

# JSON-only output for automation
python3 scripts/health_scanner.py --report

# Quiet output for logging
python3 scripts/health_scanner.py --quiet
```

### 2. Orchestrator Skill (`theteam/workflow/health_monitor/theteam_health_skill.py`)

**Purpose**: Provides orchestration layer for the hybrid health scanner solution, managing scanner execution, result interpretation, and workflow coordination while maintaining agent-first design principles.

**Key Features**:
- Scheduled health monitoring with configurable frequency
- Event-driven scanning on file system changes
- Result aggregation and prioritization
- Integration with existing workflow management
- Backward-compatible with existing agent ecosystem

**Execution Modes**:

#### Standalone Mode
Runs a single health scan with detailed output and generates comprehensive workflow reports.

```bash
python3 theteam/workflow/health_monitor/theteam_health_skill.py --mode standalone
```

#### Orchestrator Mode
Runs continuous health monitoring with periodic scans and automatic failure recovery.

```bash
python3 theteam/workflow/health_monitor/theteam_health_skill.py --mode orchestrator
```

## System Architecture

### Health Scan Flow
```
┌─────────────────────────────────────────────────────────────┐
│                    HealthScanner                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ Registry    │  │ Asset       │  │ Production   │           │
│  │ Validation  │  │ Health Check │  │ Asset Check  │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  TheTeam Health Skill                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ Orchestrator│  │ Event       │  │ Workflow    │           │
│  │ Manager     │  │ Handler     │  │ Coordinator │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Result Processor                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ Report      │  │ Priority   │  │ Scheduling  │           │
│  │ Generator   │  │ Engine     │  │ Engine      │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Integration Points

#### 1. CI/CD Pipeline
The health scanner can be integrated into existing CI/CD workflows:

```yaml
# Example GitHub Actions step
- name: Health Check
  run: |
    python3 scripts/health_scanner.py --quiet || echo "Health issues detected"
```

#### 2. Project Structure Registry
The scanner validates the `stable_project_structure.json` registry:

```json
{
  "project": "ledraslament",
  "updated": "2026-09-09",
  "folders": {
    "stage/": { ... },
    "2do/": { ... },
        "data/scenes/": { ... },
    "src/": { ... },
    "tests/": { ... },
    "assets/generated/": { ... },
    "recyclebin/": { ... },
    "docs/": { ... }
  },
  "root_files": [...]
}
```

#### 3. Asset Management
Automated validation of generated assets:
- PNG file size validation
- Log file presence verification
- Nested directory support

## Configuration

### Scanner Configuration (`scripts/health_scanner.py`)

```python
# Core constants
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
REGISTRY_PATH = PROJECT_ROOT / "docs" / "stable_project_structure.json"
SCAN_FREQUENCY_MINUTES = 30  # Default scan frequency
```

### Orchestrator Configuration (`theteam/workflow/health_monitor/theteam_health_skill.py`)

```python
# Execution mode and frequency
parser.add_argument(
    "--mode",
    choices=["standalone", "orchestrator"],
    default="standalone",
    help="Execution mode (standalone or orchestrator)"
)

parser.add_argument(
    "--frequency",
    type=int,
    default=SCAN_FREQUENCY_MINUTES,
    help=f"Scan frequency in minutes (default: {SCAN_FREQUENCY_MINUTES})"
)
```

## Monitoring and Alerting

### Log Files
- **Health Scanner Log**: `health_monitor.log` - Detailed execution logs
- **Asset Log**: `assets/generated/generation_log.jsonl` - Generation tracking

### Report Formats

#### JSON Report
Provides machine-readable output for automation:
```json
{
  "scanner_version": "2.0.0",
  "scan_time": "2026-09-09T11:37:20",
  "project": "ledraslament",
  "findings": [...],
  "registry_status": "ok",
  "asset_status": "scanned",
  "production_status": "ok"
}
```

#### Detailed Report
Human-readable output with emoji indicators and severity levels:
```
🔍 Ledras Health Scanner v2.0.0 - 2026-09-09 11:37:20
Project root: /Users/bparlan/devcode/ledraslament
Registry file: /Users/bparlan/devcode/ledraslament/docs/stable_project_structure.json

ℹ️  INFO: Important folder 'specific_scenes' not registered
   Location: project_root/specific_scenes
   Impact: Production assets lack documentation coverage

⚠️  WARNING: Potentially corrupted tiny PNG files: ['scene-06-v001.png']
   Location: /Users/bparlan/devcode/ledraslament/assets/generated
   Impact: 1 files may be incomplete or corrupted
```

## Usage Scenarios

### 1. Development Environment
```bash
# Quick health check during development
python3 scripts/health_scanner.py --quiet

# Detailed analysis of specific issues
python3 theteam/workflow/health_monitor/theteam_health_skill.py --mode standalone
```

### 2. Production Monitoring
```bash
# Continuous monitoring with scheduling
python3 theteam/workflow/health_monitor/theteam_health_skill.py --mode orchestrator
```

### 3. CI/CD Integration
```yaml
# Automated health checks in CI/CD
- name: Project Health
  run: |
    python3 scripts/health_scanner.py --quiet || exit 1
  timeout: 300

- name: Production Assets
  run: |
    python3 scripts/health_scanner.py --quiet | grep -E "CRITICAL|WARNING"
  continue-on-error: true
```

### 4. Manual Investigation
```bash
# Investigate specific registry issues
python3 scripts/health_scanner.py | grep -A 3 "registry"

# Check only production assets
python3 scripts/health_scanner.py 2>&1 | head -20
```

## Maintenance and Troubleshooting

### Common Issues and Solutions

#### Issue: Scanner fails to find PNG files
**Cause**: Assets directory not created or generated
**Solution**: Run image generation pipeline first
```bash
python3 fal_generate.py --subscenes 3
```

#### Issue: Registry validation fails
**Cause**: `stable_project_structure.json` corrupted or missing
**Solution**: Restore from git or recreate manually
```bash
git checkout HEAD -- docs/stable_project_structure.json
```

#### Issue: Orchestrator mode doesn't start
**Cause**: Permission issues or missing dependencies
**Solution**: Check execution permissions and dependencies
```bash
chmod +x scripts/health_scanner.py
theteam/workflow/health_monitor/theteam_health_skill.py --mode standalone
```

### Updating the System

#### Adding New Scanners
Add new scanning functionality by extending the `LedrasHealthScanner` class in `scripts/health_scanner.py`

#### Modifying Scan Frequency
Update `SCAN_FREQUENCY_MINUTES` in both scanner files

#### Extending Registry Validation
Update the `scan_registry_structure()` method to include new validation rules

## Best Practices

### For Developers
1. **Minimal Dependencies**: Use standard library exclusively
2. **Performance**: Recursive scanning with early exit on critical issues
3. **Error Handling**: Comprehensive exception handling with safe defaults
4. **Logging**: Structured logging for troubleshooting

### For Operations
1. **Scheduled Monitoring**: Use orchestrator mode for continuous monitoring
2. **Alerting**: Integrate with existing monitoring systems
3. **Versioning**: Maintain backward compatibility
4. **Testing**: Run comprehensive tests after changes

### For Security
1. **Path Validation**: Use `Path` objects for safe filesystem operations
2. **Input Sanitization**: Validate all command-line arguments
3. **Timeout Handling**: Implement appropriate timeouts for long-running operations
4. **Resource Limits**: Monitor and limit resource usage

## Migration Guide

### From Previous Versions
If migrating from an earlier health monitoring system:

1. **Replace old scripts**: Move existing health scripts to backup location
2. **Update references**: Update any scripts or documentation referencing old paths
3. **Configure new system**: Adjust scan frequency and notification preferences
4. **Test thoroughly**: Run full test suite to ensure compatibility

### Backward Compatibility
The new system maintains backward compatibility:
- Existing test suites continue to work
- No breaking changes to public APIs
- Graceful degradation on failures
- Configurable output formats

## Conclusion

The hybrid health monitoring system provides a robust, scalable solution for maintaining Ledras Lament project health. By combining lightweight scanning with sophisticated orchestration, teams can ensure continuous monitoring while maintaining simplicity and reliability.

The system is designed to be:
- **Easy to use**: Simple CLI interface
- **Powerful**: Comprehensive scanning capabilities
- **Flexible**: Configurable for various environments
- **Robust**: Handles failures gracefully
- **Maintainable**: Clean code and documentation

This health integration is now ready to use in production and will help maintain the stability and reliability of the Ledras Lament pipeline.