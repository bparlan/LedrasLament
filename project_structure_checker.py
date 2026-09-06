#!/usr/bin/env python3
"""
Project Structure Maintenance Checker

Usage: python3 project_structure_checker.py [options]

This script helps team members identify structural issues in the Ledras Lament project
that may warrant maintenance intervention according to the evidence-first criteria.

Phase 1: Comprehensive Project Structure Inspection

The script performs 8 comprehensive phases of analysis:
1. Source Code Analysis
2. Configuration Analysis
3. Asset & Generated Output Analysis
4. Test & Documentation Analysis
5. Dependency Analysis
6. Git Status Analysis
7. Path Dependency Analysis
8. Agent Infrastructure Analysis

Each issue is documented with specific evidence to support the diagnosis.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import subprocess

class ProjectStructureChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.issues = []
        self.evidence_map = {}
        
    def run_complete_inspection(self) -> Dict[str, Any]:
        """Run all 8 phases of inspection"""
        print("🔍 Phase 1: Source Code Analysis")
        self.analyze_source_code()
        
        print("🔍 Phase 2: Configuration Analysis")
        self.analyze_configurations()
        
        print("🔍 Phase 3: Asset & Generated Output Analysis")
        self.analyze_assets_and_generated()
        
        print("🔍 Phase 4: Test & Documentation Analysis")
        self.analyze_tests_and_docs()
        
        print("🔍 Phase 5: Dependency Analysis")
        self.analyze_dependencies()
        
        print("🔍 Phase 6: Git Status Analysis")
        self.analyze_git_status()
        
        print("🔍 Phase 7: Path Dependency Analysis")
        self.analyze_path_dependencies()
        
        print("🔍 Phase 8: Agent Infrastructure Analysis")
        self.analyze_agent_infrastructure()
        
        return self.generate_report()
    
    def analyze_source_code(self):
        """Analyze source code structure and organization"""
        source_patterns = {
            'python_files': r'\.py$',
            'executable_scripts': r'\.py$'  # Based on Ledras Lament patterns
        }
        
        for pattern_name, pattern in source_patterns.items():
            files = list(self.project_root.glob(f"**/*{pattern}"))
            
            # Check for executable scripts
            if pattern_name == 'executable_scripts':
                for file_path in files:
                    if file_path.is_file() and os.access(file_path, os.X_OK):
                        # Check if script references paths that might break
                        try:
                            content = file_path.read_text()
                            if 'os.path.join' not in content and 'Path(' not in content:
                                self.add_issue(
                                    "Path fragility detected",
                                    f"Executable script {file_path} may use relative paths",
                                    f"Script {file_path.name} lacks explicit path handling",
                                    "medium",
                                    {"file": str(file_path), "pattern": "relative_paths"}
                                )
                        except:
                            pass
        
        # Check for mixing test and production code
        test_files = list(self.project_root.glob("**/test_*.py"))
        src_files = list(self.project_root.glob("**/src/*.py"))
        
        if test_files and src_files:
            # Check if test files are in src directory
            src_test_files = [f for f in test_files if 'src' in str(f)]
            if src_test_files:
                self.add_issue(
                    "Test/production mixing detected",
                    f"Test files found in src directory: {[str(f) for f in src_test_files]}",
                    "Tests should be separated from production code for clarity",
                    "medium",
                    {"files": [str(f) for f in src_test_files]}
                )
    
    def analyze_configurations(self):
        """Analyze configuration files and duplication"""
        config_files = [
            'imagine-config.json',
            'quality_assurance.json',
            'gateway.json',
            'team_config.json'
        ]
        
        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path) as f:
                        config_data = json.load(f)
                    
                    # Check for common config keys that might be duplicated
                    common_keys = ['model', 'api_key', 'endpoint', 'version', 'path']
                    found_keys = []
                    for key in common_keys:
                        if key in str(config_data):
                            found_keys.append(key)
                    
                    if found_keys:
                        self.add_issue(
                            "Configuration scattering detected",
                            f"Config {config_file} contains keys: {found_keys}",
                            "Multiple configs with overlapping keys unclear about authority",
                            "low",
                            {"file": str(config_path), "keys": found_keys}
                        )
                except:
                    pass
    
    def analyze_assets_and_generated(self):
        """Analyze assets and generated outputs for pollution"""
        # Check assets directory
        assets_dir = self.project_root / "assets"
        if assets_dir.exists():
            generated_files = list(assets_dir.glob("**/*scene-*.png"))
            source_files = list(assets_dir.glob("**/*.jpg"))
            
            # Check for generated files in unexpected locations
            for generated in generated_files:
                if 'src' in str(generated) or 'config' in str(generated):
                    self.add_issue(
                        "Generated outputs polluting source directories",
                        f"Generated file {generated} appears in source directory",
                        "Generated outputs should be isolated from source code",
                        "high",
                        {"file": str(generated), "type": "generated"}
                    )
        
        # Check stage directory
        stage_dir = self.project_root / "stage"
        if stage_dir.exists():
            stage_files = list(stage_dir.glob("*.*"))
            
            # Check for depth_template.jpg vs guideline_line_out.png
            depth_template = stage_dir / "depth_template.jpg"
            guideline_line_out = stage_dir / "guideline_line_out.png"
            
            if depth_template.exists():
                # Check if depth_template.jpg is referenced as input
                self.check_file_references(depth_template, "stage depth template")
            
            if guideline_line_out.exists():
                self.check_file_references(guideline_line_out, "stage guideline")
        
        # Check for .gitignore issues
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            gitignore_content = gitignore_path.read_text()
            
            # Check for generated assets that should be ignored
            if '*.png' not in gitignore_content and 'scene-*.png' not in gitignore_content:
                self.add_issue(
                    "Generated assets may be committed",
                    "No .gitignore rule for PNG files found",
                    "Generated images should be ignored by Git",
                    "high",
                    {"gitignore": str(gitignore_path)}
                )
    
    def analyze_tests_and_docs(self):
        """Analyze test files and documentation organization"""
        # Check for test files in production directories
        test_in_src = list(self.project_root.glob("**/src/*test*.py"))
        if test_in_src:
            self.add_issue(
                "Tests in production directory",
                f"Test files found in production code: {[str(f) for f in test_in_src]}",
                "Tests should be in dedicated test directories, not mixed with production",
                "medium",
                {"files": [str(f) for f in test_in_src]}
            )
        
        # Check for documentation organization
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            # Check if README is properly organized
            readme_path = self.project_root / "README.md"
            if readme_path.exists():
                content = readme_path.read_text()
                # Check for table of contents or organization
                if '##' not in content or len(content.split('##')) < 4:
                    self.add_issue(
                        "Documentation organization may be lacking",
                        "README.md lacks clear section organization",
                        "Documentation should be well-organized with clear sections",
                        "low",
                        {"file": str(readme_path)}
                    )
    
    def analyze_dependencies(self):
        """Analyze dependency artifacts and virtual environments"""
        # Check for .venv directory
        venv_dir = self.project_root / ".venv"
        if venv_dir.exists():
            size = self.get_directory_size(venv_dir)
            self.add_issue(
                "Virtual environment in project",
                f".venv directory found ({size} bytes)",
                "Virtual environments should be excluded from version control",
                "high",
                {"path": str(venv_dir), "size": size}
            )
        
        # Check for __pycache__ directories
        pycache_dirs = list(self.project_root.glob("**/__pycache__/"))
        for pycache in pycache_dirs:
            self.add_issue(
                "Python cache in source tree",
                f"__pycache__ directory at {pycache}",
                "Python cache should be excluded by .gitignore",
                "medium",
                {"path": str(pycache)}
            )
        
        # Check for node_modules (if JS project)
        node_modules = self.project_root / "node_modules"
        if node_modules.exists():
            size = self.get_directory_size(node_modules)
            self.add_issue(
                "Node modules in project",
                f"node_modules directory found ({size} bytes)",
                "Node modules should be excluded from version control",
                "high",
                {"path": str(node_modules), "size": size}
            )
    
    def analyze_git_status(self):
        """Analyze Git status and untracked files"""
        try:
            # Get git status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        status = line[0]
                        file_path = line[3:]
                        
                        if status == '??':  # Untracked file
                            self.check_untracked_file(file_path, line)
        except:
            pass
    
    def analyze_path_dependencies(self):
        """Analyze relative path usage and dependencies"""
        # Check for common path patterns
        path_patterns = [
            (r'os\.path\.join\([^)]*\)', "os.path.join usage"),
            (r'[\"\'][^\"\']*\.[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+[^\"\']*[\"\']', "hardcoded file paths")
        ]
        
        for pattern, description in path_patterns:
            for file_path in self.project_root.glob("**/*.py"):
                try:
                    content = file_path.read_text()
                    if re.search(pattern, content):
                        # Check if path is relative and might break
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if '/' in match and not match.startswith('.'):
                                self.add_issue(
                                    "Potentially fragile path dependency",
                                    f"File {file_path.name} contains path pattern: {match}",
                                    "Path may break if working directory changes",
                                    "low",
                                    {"file": str(file_path), "path": match}
                                )
                except:
                    pass
    
    def analyze_agent_infrastructure(self):
        """Analyze agent infrastructure and configurations"""
        # Check for .omp directory structure
        omp_dir = self.project_root / ".omp"
        if omp_dir.exists():
            # Check for theteam config
            theteam_config = omp_dir / "theteam" / "config"
            if theteam_config.exists():
                self.add_issue(
                    "Agent config in .omp directory",
                    "Agent configuration should be in project root",
                    ".omp directory contains agent infrastructure",
                    "low",
                    {"path": str(theteam_config)}
                )
        
        # Check for AGENTS.md (project-specific) vs agent/AGENTS.md (system)
        project_agents = self.project_root / "AGENTS.md"
        if project_agents.exists():
            system_agents = Path.home() / ".omp" / "agent" / "AGENTS.md"
            if system_agents.exists():
                self.add_issue(
                    "Project-specific AGENTS.md present",
                    "Both project AGENTS.md and system AGENTS.md exist",
                    "Unclear which AGENTS.md should be used by agents",
                    "low",
                    {"project": str(project_agents), "system": str(system_agents)}
                )
    
    def check_file_references(self, file_path: Path, description: str):
        """Check if a file is referenced as input data"""
        for py_file in self.project_root.glob("**/*.py"):
            try:
                content = py_file.read_text()
                if str(file_path) in content or file_path.name in content:
                    self.add_issue(
                        "Generated file referenced as input",
                        f"{file_path.name} ({description}) is referenced in {py_file.name}",
                        "If generated, should not be referenced as input; clarify role",
                        "medium",
                        {"referenced_file": str(file_path), "referencing_file": str(py_file)}
                    )
            except:
                pass
    
    def check_untracked_file(self, file_path: str, git_line: str):
        """Check if an untracked file indicates a structural issue"""
        path = Path(file_path)
        
        # Check for backup files
        if any(ext in str(path).lower() for ext in ['.bak', '_old', 'backup', 'temp']):
            self.add_issue(
                "Backup file in working directory",
                f"Backup file {file_path} found in workspace",
                "Backup files should be in .gitignore or version control",
                "low",
                {"file": file_path, "status": git_line}
            )
        
        # Check for generated content
        if any(ext in str(path).lower() for ext in ['.pyc', '.pyo', '.pyd']):
            self.add_issue(
                "Python artifact in working directory",
                f"Python artifact {file_path} found in workspace",
                "Python artifacts should be excluded by .gitignore",
                "medium",
                {"file": file_path, "status": git_line}
            )
    
    def add_issue(self, problem: str, evidence: str, improvement: str, severity: str, metadata: Dict):
        """Add an issue to the issues list"""
        issue = {
            "problem": problem,
            "evidence": evidence,
            "improvement": improvement,
            "severity": severity,
            "metadata": metadata,
            "phase": None  # Will be filled during analysis
        }
        self.issues.append(issue)
        self.evidence_map[problem] = evidence
    
    def get_directory_size(self, path: Path) -> int:
        """Get approximate size of a directory"""
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
        return total
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report"""
        # Categorize issues by severity and type
        high_severity = [i for i in self.issues if i["severity"] == "high"]
        medium_severity = [i for i in self.issues if i["severity"] == "medium"]
        low_severity = [i for i in self.issues if i["severity"] == "low"]
        
        # Group by phase/area
        issues_by_category = {}
        for issue in self.issues:
            # Determine category based on problem description
            if "path fragility" in issue["problem"].lower():
                category = "Path Dependencies"
            elif "generated" in issue["problem"].lower():
                category = "Generated Outputs"
            elif "test" in issue["problem"].lower():
                category = "Tests & Documentation"
            elif "config" in issue["problem"].lower():
                category = "Configuration"
            elif "dependency" in issue["problem"].lower():
                category = "Dependencies"
            elif "git" in issue["problem"].lower():
                category = "Git Status"
            elif "agent" in issue["problem"].lower():
                category = "Agent Infrastructure"
            else:
                category = "General Structure"
            
            if category not in issues_by_category:
                issues_by_category[category] = []
            issues_by_category[category].append(issue)
        
        return {
            "project_root": str(self.project_root),
            "timestamp": self.get_timestamp(),
            "summary": {
                "total_issues": len(self.issues),
                "high_severity": len(high_severity),
                "medium_severity": len(medium_severity),
                "low_severity": len(low_severity),
                "categories": list(issues_by_category.keys())
            },
            "issues_by_category": issues_by_category,
            "all_issues": self.issues,
            "proposals": self.generate_proposals(high_severity, medium_severity, low_severity)
        }
    
    def generate_proposals(self, high: List, medium: List, low: List) -> List[Dict]:
        """Generate structured proposals for maintenance"""
        proposals = []
        
        for issue in high + medium + low:
            proposal = {
                "problem": issue["problem"],
                "evidence": issue["evidence"],
                "improvement": issue["improvement"],
                "severity": issue["severity"],
                "minimum_viable_change": self.suggest_minimum_viable_change(issue),
                "affected_infrastructure": self.identify_affected_infrastructure(issue),
                "risk_level": self.assess_risk(issue)
            }
            proposals.append(proposal)
        
        return proposals
    
    def suggest_minimum_viable_change(self, issue: Dict) -> str:
        """Suggest the minimum change needed"""
        problem = issue["problem"].lower()
        
        if "path fragility" in problem:
            return "Add explicit path handling with os.path.join or Path()"
        elif "generated" in problem:
            return "Add to .gitignore or move to appropriate directory"
        elif "config" in problem:
            return "Consolidate config into single authoritative file"
        elif "test" in problem:
            return "Move tests to dedicated test directory"
        elif "dependency" in problem:
            return "Remove from version control and update .gitignore"
        elif "git" in problem:
            return "Add to .gitignore or version control"
        elif "agent" in problem:
            return "Move agent config to project root and update references"
        else:
            return "Investigate and apply appropriate fix"
    
    def identify_affected_infrastructure(self, issue: Dict) -> List[str]:
        """Identify infrastructure that could be affected"""
        metadata = issue.get("metadata", {})
        affected = []
        
        if "file" in metadata:
            affected.append(f"File: {metadata['file']}")
        if "path" in metadata:
            affected.append(f"Path pattern: {metadata['path']}")
        
        # Add inferred infrastructure based on issue type
        if issue["problem"].lower().find("path") != -1:
            affected.extend(["scripts", "imports", "configuration references"])
        elif issue["problem"].lower().find("generated") != -1:
            affected.extend(["Git tracking", "agents referencing these files"])
        
        return affected
    
    def assess_risk(self, issue: Dict) -> str:
        """Assess risk level of the issue"""
        if issue["severity"] == "high":
            return "High"
        elif issue["severity"] == "medium":
            return "Medium"
        else:
            return "Low"
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    print("🔍 Ledras Lament Project Structure Maintenance Checker")
    print("=" * 60)
    
    checker = ProjectStructureChecker()
    report = checker.run_complete_inspection()
    
    # Display summary
    print("\n📊 ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total issues found: {report['summary']['total_issues']}")
    print(f"High severity: {report['summary']['high_severity']}")
    print(f"Medium severity: {report['summary']['medium_severity']}")
    print(f"Low severity: {report['summary']['low_severity']}")
    
    print(f"\n📋 Categories with issues:")
    for category in report['summary']['categories']:
        count = len(report['issues_by_category'][category])
        print(f"  - {category}: {count} issues")
    
    # Display top 5 issues with evidence
    print(f"\n⚠️  TOP ISSUES (with evidence):")
    for i, issue in enumerate(report['all_issues'][:5]):
        print(f"\n{i+1}. {issue['problem']}")
        print(f"   Evidence: {issue['evidence']}")
        print(f"   Severity: {issue['severity']}")
    
    # Save report
    report_path = Path(".omp/theteam/reports/project-structure-analysis.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: {report_path}")
    
    # Generate actionable proposal format
    print(f"\n📝 PROPOSAL FORMAT FOR TEAM MEMBERS:")
    print("=" * 60)
    for proposal in report['proposals'][:3]:
        print(f"\n{proposal['problem']}")
        print(f"   Evidence: {proposal['evidence']}")
        print(f"   Minimum viable change: {proposal['minimum_viable_change']}")
        print(f"   Risk level: {proposal['risk_level']}")
    
    print(f"\n💡 Next steps:")
    print("1. Review issues with high severity first")
    print("2. Check affected infrastructure listed in proposals")
    print("3. Format proposal using the JSON template from the team subskill")
    
    # Return exit code based on high severity issues
    if report['summary']['high_severity'] > 0:
        print(f"\n🚨 HIGH SEVERITY ISSUES DETECTED - Action required!")
        return 1
    else:
        print(f"\n✅ No critical issues - optional maintenance")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
