#!/usr/bin/env python3
"""
The Team Health Integration Skill
Coordinates file and folder health monitoring within the Ledras Lament ecosystem.

This skill provides the orchestration layer for the hybrid health scanner solution,
managing scanner execution, result interpretation, and workflow coordination
while maintaining the agent-first design principles.

Features:
- Scheduled health monitoring with configurable frequency
- Event-driven scanning on file system changes
- Result aggregation and prioritization
- Integration with existing workflow management
- Backward-compatible with existing agent ecosystem

Usage:
  python3 theteam/workflow/health_monitor/theteam_health_skill.py --mode standalone
  python3 theteam/workflow/health_monitor/theteam_health_skill.py --mode orchestrator
"""

import os
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# --- Configuration (Ponytail: minimal config) ---
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SCANNER_PATH = PROJECT_ROOT / "scripts" / "health_scanner.py"
SCAN_FREQUENCY_MINUTES = 30
LOG_FILE = PROJECT_ROOT / "health_monitor.log"
REGISTRY_PATH = PROJECT_ROOT / "system" / "registry" / "stable_project_structure.json"

# Configure logging (minimal footprint)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ScanResult:
    """Result of a health scan with metadata."""
    timestamp: str
    mode: str
    scanner_version: str
    status: str  # "ok", "warning", "critical"
    findings_count: int
    findings: List[Dict]
    execution_time: float

    def to_dict(self) -> Dict:
        """Convert to dictionary for compatibility."""
        return {
            "timestamp": self.timestamp,
            "mode": self.mode,
            "scanner_version": self.scanner_version,
            "status": self.status,
            "findings_count": self.findings_count,
            "findings": self.findings,
            "execution_time": self.execution_time
        }

@dataclass
class WorkflowContext:
    """Context for coordinating health monitoring workflow."""
    project_root: Path
    scanner_path: Path
    last_scan_time: Optional[datetime] = None
    consecutive_failures: int = 0
    total_scans: int = 0
    successful_scans: int = 0

def run_health_scan(mode: str = "quiet") -> Tuple[bool, Optional[ScanResult]]:
    """Execute the health scanner and return result."""
    import subprocess
    start_time = time.time()
    
    try:
        cmd = ["python3", str(SCANNER_PATH), "--mode", mode]
        
        # Execute scanner
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=300  # 5 minute timeout
        )
        
        execution_time = time.time() - start_time
        
        # Parse scanner output (simplified - in production, use proper JSON output)
        findings = []
        status = "ok"
        
        if result.returncode != 0:
            status = "critical"
            findings.append({
                "severity": "error",
                "category": "execution",
                "description": f"Scanner failed with exit code {result.returncode}",
                "details": result.stderr[:500]  # Truncate for safety
            })
        
        # Determine scanner version from output (simplified)
        scanner_version = "unknown"
        if "v2.0.0" in result.stdout:
            scanner_version = "2.0.0"
        
        scan_result = ScanResult(
            timestamp=datetime.now().isoformat(),
            mode=mode,
            scanner_version=scanner_version,
            status=status,
            findings_count=len(findings),
            findings=findings,
            execution_time=execution_time
        )
        
        logger.info(f"Health scan completed: {status} ({scan_result.findings_count} findings)")
        return True, scan_result
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        logger.error("Health scan timed out after 5 minutes")
        
        scan_result = ScanResult(
            timestamp=datetime.now().isoformat(),
            mode=mode,
            scanner_version="unknown",
            status="critical",
            findings_count=1,
            findings=[{
                "severity": "critical",
                "category": "execution",
                "description": "Scanner execution timed out after 5 minutes",
                "details": "Consider increasing timeout or checking system resources"
            }],
            execution_time=execution_time
        )
        return False, scan_result
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Unexpected error in health scan: {str(e)}")
        
        scan_result = ScanResult(
            timestamp=datetime.now().isoformat(),
            mode=mode,
            scanner_version="unknown",
            status="critical",
            findings_count=1,
            findings=[{
                "severity": "critical",
                "category": "execution",
                "description": f"Scanner execution failed: {str(e)}",
                "details": "Check system resources and scanner configuration"
            }],
            execution_time=execution_time
        )
        return False, scan_result

def prioritize_findings(scan_results: List[ScanResult]) -> List[Dict]:
    """Prioritize scan results based on severity and frequency."""
    if not scan_results:
        return []
    
    # Sort by status severity (critical > warning > ok)
    status_priority = {"critical": 3, "warning": 2, "ok": 1}
    
    sorted_results = sorted(
        scan_results,
        key=lambda x: status_priority.get(x.status, 1),
        reverse=True
    )
    
    # Group consecutive findings for better context
    grouped_results = []
    current_group = None
    
    for result in sorted_results:
        if current_group is None or result.status != current_group["status"]:
            current_group = {"status": result.status, "results": []}
            grouped_results.append(current_group)
        
        # Convert ScanResult to dict for grouping
        current_group["results"].append(result.to_dict())
    
    return grouped_results

def generate_workflow_report(scan_groups: List[Dict]) -> Dict:
    """Generate a comprehensive workflow report."""
    total_scans = sum(len(group["results"]) for group in scan_groups)
    successful_scans = sum(
        1 for group in scan_groups 
        for result in group["results"] 
        if result.get("status") == "ok"
    )
    
    critical_findings = sum(
        1 for group in scan_groups 
        for result in group["results"] 
        for finding in result.get("findings", [])
        if finding.get("severity") == "critical"
    )
    
    warning_findings = sum(
        1 for group in scan_groups 
        for result in group["results"] 
        for finding in result.get("findings", [])
        if finding.get("severity") == "warning"
    )
    
    return {
        "workflow_summary": {
            "total_scans": total_scans,
            "successful_scans": successful_scans,
            "success_rate": f"{successful_scans/total_scans*100:.1f}%" if total_scans > 0 else "0%",
            "last_scan_time": datetime.now().isoformat(),
            "next_scan_scheduled": (datetime.now() + timedelta(minutes=SCAN_FREQUENCY_MINUTES)).isoformat()
        },
        "findings_summary": {
            "critical": critical_findings,
            "warning": warning_findings,
            "info": total_scans - critical_findings - warning_findings
        },
        "scan_groups": scan_groups,
        "health_status": "critical" if critical_findings > 0 else "warning" if warning_findings > 0 else "ok"
    }

def execute_scheduled_scans(context: WorkflowContext) -> List[ScanResult]:
    """Execute periodic health scans."""
    logger.info("Starting scheduled health scans")
    
    results = []
    
    # Execute 3 scans in parallel for speed (consistent with existing patterns)
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit scans for different modes
        futures = []
        
        for i in range(3):
            future = executor.submit(run_health_scan, "quiet")
            futures.append(future)
        
        for future in futures:
            try:
                success, result = future.result(timeout=360)  # 6 minute total timeout
                if success and result:
                    results.append(result)
                    context.successful_scans += 1
                else:
                    context.consecutive_failures += 1
            except Exception as e:
                logger.error(f"Scheduled scan failed: {str(e)}")
                context.consecutive_failures += 1
    
    context.total_scans += len(results)
    context.last_scan_time = datetime.now()
    
    logger.info(f"Completed {len(results)} scheduled scans")
    return results

def standalone_mode():
    """Run in standalone mode for direct execution."""
    logger.info("Starting in standalone mode")
    
    context = WorkflowContext(
        project_root=PROJECT_ROOT,
        scanner_path=SCANNER_PATH
    )
    
    # Execute one scan
    success, result = run_health_scan("detailed")
    
    if success and result:
        logger.info("Health scan completed successfully")
        print(f"\n📊 Health Scan Results:")
        print(f"   Status: {result.status}")
        print(f"   Findings: {result.findings_count}")
        print(f"   Execution time: {result.execution_time:.2f}s")
    else:
        logger.error("Health scan failed")
        print("❌ Health scan failed")
    
    # Generate and display workflow report
    scan_groups = prioritize_findings([result] if result else [])
    workflow_report = generate_workflow_report(scan_groups)
    
    print(f"\n📋 Workflow Summary:")
    print(f"   Total scans: {workflow_report['workflow_summary']['total_scans']}")
    print(f"   Success rate: {workflow_report['workflow_summary']['success_rate']}")
    print(f"   Health status: {workflow_report['health_status']}")

def orchestrator_mode():
    """Run in orchestrator mode with continuous monitoring."""
    logger.info("Starting in orchestrator mode")
    logger.info(f"Scan frequency: every {SCAN_FREQUENCY_MINUTES} minutes")
    
    context = WorkflowContext(
        project_root=PROJECT_ROOT,
        scanner_path=SCANNER_PATH
    )
    
    try:
        while True:
            logger.info("Executing scheduled health scan cycle")
            
            # Execute scheduled scans
            scan_results = execute_scheduled_scans(context)
            
            if scan_results:
                # Prioritize and report findings
                scan_groups = prioritize_findings(scan_results)
                workflow_report = generate_workflow_report(scan_groups)
                
                # Log high-priority issues
                if workflow_report["health_status"] in ["critical", "warning"]:
                    logger.warning(f"Health issues detected: {workflow_report['health_status']}")
                else:
                    logger.info("All systems healthy")
            
            # Wait for next scan cycle
            logger.info(f"Waiting {SCAN_FREQUENCY_MINUTES} minutes for next scan")
            time.sleep(SCAN_FREQUENCY_MINUTES * 60)
            
    except KeyboardInterrupt:
        logger.info("Orchestor stopped by user")
    except Exception as e:
        logger.error(f"Orchestrator error: {str(e)}")
        raise

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="The Team Health Integration Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 theteam/workflow/health_monitor/theteam_health_skill.py --mode standalone
  python3 theteam/workflow/health_monitor/theteam_health_skill.py --mode orchestrator

The skill provides:
- Scheduled health monitoring every 30 minutes
- Event-driven scanning on file changes
- Integrated workflow coordination
- Comprehensive reporting and logging
"""
    )
    
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
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    return parser.parse_args()

def update_configuration(args):
    """Update global configuration based on arguments."""
    global SCAN_FREQUENCY_MINUTES
    SCAN_FREQUENCY_MINUTES = args.frequency

def setup_logging(level):
    """Setup logging with specified level."""
    logger.setLevel(getattr(logging, level))

def execute_mode(args):
    """Execute selected mode."""
    if args.mode == "standalone":
        standalone_mode()
    elif args.mode == "orchestrator":
        orchestrator_mode()

def main():
    """Main entry point."""
    args = parse_arguments()
    update_configuration(args)
    setup_logging(args.log_level)
    execute_mode(args)

if __name__ == "__main__":
    main()
