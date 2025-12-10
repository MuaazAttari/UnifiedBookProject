"""
Quality assurance checks for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module performs comprehensive quality reviews of the codebase.
"""

import os
import sys
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json
import re
from collections import defaultdict


class QualityAssuranceChecker:
    """Performs comprehensive quality assurance checks on the codebase."""

    def __init__(self, project_root: str = None):
        """
        Initialize the quality assurance checker.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.issues = defaultdict(list)
        self.metrics = {}

    def check_code_quality_metrics(self) -> Dict[str, Any]:
        """Check various code quality metrics."""
        results = {
            "file_count": 0,
            "total_lines": 0,
            "python_files": 0,
            "test_files": 0,
            "average_file_size": 0,
            "complexity_metrics": {}
        }

        total_size = 0
        python_files = []
        test_files = []

        for file_path in self.project_root.rglob("*.py"):
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    file_size = len(lines)

                results["file_count"] += 1
                results["total_lines"] += file_size
                total_size += len(lines) * len("".join(lines))  # Approximate byte count
                python_files.append((file_path, file_size))

                if "test" in str(file_path).lower():
                    results["test_files"] += 1

            except Exception:
                continue

        results["python_files"] = len(python_files)
        results["average_file_size"] = results["total_lines"] / results["python_files"] if results["python_files"] > 0 else 0

        # Calculate complexity metrics for a sample of files
        complexity_files = python_files[:10]  # Check first 10 files for complexity
        complexity_results = []
        for file_path, _ in complexity_files:
            complexity = self._calculate_file_complexity(file_path)
            complexity_results.append(complexity)

        results["complexity_metrics"] = {
            "files_analyzed": len(complexity_results),
            "average_function_count": sum(c.get("function_count", 0) for c in complexity_results) / len(complexity_results) if complexity_results else 0,
            "average_class_count": sum(c.get("class_count", 0) for c in complexity_results) / len(complexity_results) if complexity_results else 0,
        }

        self.metrics["code_quality"] = results
        return results

    def _calculate_file_complexity(self, file_path: Path) -> Dict[str, int]:
        """Calculate complexity metrics for a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            function_count = 0
            class_count = 0
            complexity_score = 0  # Cyclomatic complexity approximation

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_count += 1
                    # Count control flow statements as complexity
                    complexity_score += sum(1 for child in ast.walk(node)
                                          if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)))

                elif isinstance(node, ast.ClassDef):
                    class_count += 1

            return {
                "function_count": function_count,
                "class_count": class_count,
                "complexity_score": complexity_score,
                "file_path": str(file_path)
            }
        except:
            return {"function_count": 0, "class_count": 0, "complexity_score": 0, "file_path": str(file_path)}

    def check_documentation_quality(self) -> Dict[str, Any]:
        """Check quality of documentation."""
        results = {
            "readme_exists": False,
            "docs_directory_exists": False,
            "doc_files_count": 0,
            "api_docs_exists": False,
            "has_contributing_guide": False,
            "has_license": False
        }

        # Check for README
        readme_files = ["README.md", "README.rst", "readme.md"]
        results["readme_exists"] = any((self.project_root / f).exists() for f in readme_files)

        # Check for docs directory
        docs_dir = self.project_root / "docs"
        results["docs_directory_exists"] = docs_dir.exists()

        # Count documentation files
        if docs_dir.exists():
            results["doc_files_count"] = len(list(docs_dir.rglob("*.md"))) + len(list(docs_dir.rglob("*.rst")))

        # Check for API documentation (Docusaurus config)
        docusaurus_config = self.project_root / "my-website" / "docusaurus.config.js"
        results["api_docs_exists"] = docusaurus_config.exists()

        # Check for contributing guide
        contributing_files = ["CONTRIBUTING.md", "CONTRIBUTING.rst", "contributing.md", "docs/contributing.md"]
        results["has_contributing_guide"] = any((self.project_root / f).exists() for f in contributing_files)

        # Check for license
        license_files = ["LICENSE", "LICENSE.md", "LICENSE.txt", "license"]
        results["has_license"] = any((self.project_root / f).exists() for f in license_files)

        self.metrics["documentation"] = results
        return results

    def check_security_issues(self) -> List[Dict[str, Any]]:
        """Check for potential security issues in the codebase."""
        issues = []
        security_keywords = [
            "password", "secret", "token", "key", "auth", "credential", "private", "api_key"
        ]

        for py_file in self.project_root.rglob("*.py"):
            if "test" in str(py_file).lower() or "venv" in str(py_file).lower():
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                for i, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    for keyword in security_keywords:
                        if keyword in line_lower and "=" in line and "os.getenv" not in line and ".env" not in line:
                            # Check if it's a hardcoded credential
                            if any(cred_word in line_lower for cred_word in ["=", ":"]):
                                issues.append({
                                    "file": str(py_file),
                                    "line_number": i,
                                    "line_content": line.strip(),
                                    "issue_type": "hardcoded_credential",
                                    "severity": "high"
                                })
            except:
                continue

        # Check for common security vulnerabilities
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for eval() usage
                if re.search(r'\beval\s*\(', content):
                    issues.append({
                        "file": str(py_file),
                        "line_number": self._find_line_number(content, "eval"),
                        "line_content": "eval() function usage detected",
                        "issue_type": "eval_usage",
                        "severity": "high"
                    })

                # Check for exec() usage
                if re.search(r'\bexec\s*\(', content):
                    issues.append({
                        "file": str(py_file),
                        "line_number": self._find_line_number(content, "exec"),
                        "line_content": "exec() function usage detected",
                        "issue_type": "exec_usage",
                        "severity": "high"
                    })

            except:
                continue

        self.issues["security"] = issues
        return issues

    def _find_line_number(self, content: str, search_term: str) -> int:
        """Find the line number of a search term in content."""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if search_term in line:
                return i
        return 0

    def check_performance_considerations(self) -> List[Dict[str, Any]]:
        """Check for performance-related issues."""
        issues = []
        performance_patterns = [
            (r'for.*in.*range\((\d+)\)', "large_range_loop", "medium"),
            (r'import\s+[*]', "wildcard_import", "low"),
            (r'while\s+True', "infinite_loop", "medium"),
            (r'list\(\)\.append', "inefficient_list_building", "medium")
        ]

        for py_file in self.project_root.rglob("*.py"):
            if "test" in str(py_file).lower() or "venv" in str(py_file).lower():
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for pattern, issue_type, severity in performance_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        issues.append({
                            "file": str(py_file),
                            "line_number": self._find_line_number(content, match.group(0)),
                            "line_content": match.group(0),
                            "issue_type": issue_type,
                            "severity": severity
                        })

                # Check for missing indexes in database queries (heuristic)
                if "filter" in content and "query" in content and ("db." in content or "session." in content):
                    # This is a heuristic - actual database query optimization would require more analysis
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if "filter" in line and "id" in line and "query" in content[:content.find(line)]:
                            issues.append({
                                "file": str(py_file),
                                "line_number": i,
                                "line_content": line.strip(),
                                "issue_type": "potential_missing_index",
                                "severity": "medium"
                            })

            except:
                continue

        self.issues["performance"] = issues
        return issues

    def check_test_coverage(self) -> Dict[str, Any]:
        """Check test coverage and quality."""
        results = {
            "test_files_count": 0,
            "test_directories": [],
            "coverage_estimate": 0,
            "test_quality_indicators": {
                "has_test_descriptions": 0,
                "has_assertions": 0,
                "has_fixtures": 0
            }
        }

        test_files = list(self.project_root.rglob("test_*.py")) + list(self.project_root.rglob("*_test.py"))
        results["test_files_count"] = len(test_files)

        # Check test directories
        test_dirs = set()
        for test_file in test_files:
            test_dirs.add(str(test_file.parent))
        results["test_directories"] = list(test_dirs)

        # Analyze test quality
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Count test descriptions (docstrings in test functions)
                test_functions = re.findall(r'def test_.*?:\s*(""".*?"""|\'.*?\')', content, re.DOTALL)
                results["test_quality_indicators"]["has_test_descriptions"] += len(test_functions)

                # Count assertions
                assertions = re.findall(r'assert', content, re.IGNORECASE)
                results["test_quality_indicators"]["has_assertions"] += len(assertions)

                # Count fixtures
                fixtures = re.findall(r'@pytest\.fixture', content, re.IGNORECASE)
                results["test_quality_indicators"]["has_fixtures"] += len(fixtures)

            except:
                continue

        # Estimate coverage based on ratio of test files to source files
        source_files = list(self.project_root.rglob("src/**/*.py"))
        if source_files:
            results["coverage_estimate"] = round((results["test_files_count"] / len(source_files)) * 100, 2)
        else:
            results["coverage_estimate"] = 0

        self.metrics["testing"] = results
        return results

    def check_code_style_compliance(self) -> List[Dict[str, Any]]:
        """Check for code style compliance using external tools if available."""
        issues = []

        # Check if flake8 is available and run it on a sample of files
        try:
            py_files = list(self.project_root.rglob("*.py"))[:5]  # Check first 5 Python files
            for py_file in py_files:
                if "test" not in str(py_file).lower():
                    try:
                        result = subprocess.run([
                            sys.executable, "-m", "flake8", str(py_file),
                            "--max-line-length=120",
                            "--ignore=E203,W503"  # Common ignores
                        ], capture_output=True, text=True, timeout=30)

                        if result.returncode != 0:
                            flake8_issues = result.stdout.strip().split('\n')
                            for issue in flake8_issues:
                                if issue and ':' in issue:
                                    parts = issue.split(':', 3)
                                    if len(parts) >= 3:
                                        issues.append({
                                            "file": parts[0],
                                            "line_number": parts[1],
                                            "column_number": parts[2],
                                            "line_content": parts[3] if len(parts) > 3 else "",
                                            "issue_type": "style_violation",
                                            "severity": "low"
                                        })
                    except subprocess.TimeoutExpired:
                        continue
                    except Exception:
                        # flake8 not available, skip this check
                        break
        except Exception:
            # If flake8 check fails, continue without it
            pass

        self.issues["style"] = issues
        return issues

    def run_all_quality_checks(self) -> Dict[str, Any]:
        """Run all quality assurance checks."""
        print("Running quality assurance checks...")

        # Run all checks
        code_quality = self.check_code_quality_metrics()
        documentation_quality = self.check_documentation_quality()
        security_issues = self.check_security_issues()
        performance_issues = self.check_performance_considerations()
        test_coverage = self.check_test_coverage()
        style_issues = self.check_code_style_compliance()

        # Calculate overall quality score
        quality_score = self._calculate_quality_score(
            code_quality, documentation_quality, security_issues,
            performance_issues, test_coverage, style_issues
        )

        report = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "metrics": {
                "code_quality": code_quality,
                "documentation": documentation_quality,
                "testing": test_coverage
            },
            "issues": {
                "security": security_issues,
                "performance": performance_issues,
                "style": style_issues
            },
            "quality_score": quality_score,
            "recommendations": self._generate_recommendations(security_issues, performance_issues, style_issues)
        }

        return report

    def _calculate_quality_score(self, code_quality, documentation, security_issues,
                               performance_issues, test_coverage, style_issues) -> float:
        """Calculate overall quality score based on various metrics."""
        # Base score calculations
        base_score = 50  # Start with 50%

        # Code quality factors
        if code_quality["python_files"] > 0:
            base_score += 10  # Points for having Python files
        if code_quality["test_files"] > 0:
            base_score += 15  # Points for having tests
        if code_quality["average_file_size"] < 200:  # Files not too large
            base_score += 5

        # Documentation factors
        if documentation["readme_exists"]:
            base_score += 5
        if documentation["docs_directory_exists"]:
            base_score += 5
        if documentation["api_docs_exists"]:
            base_score += 10

        # Penalty for issues
        issue_count = len(security_issues) + len(performance_issues) + len(style_issues)
        penalty = min(issue_count * 2, 30)  # Max 30% penalty
        base_score -= penalty

        # Bonus for good testing
        if test_coverage["test_files_count"] > 0:
            base_score += min(test_coverage["test_coverage"], 15)  # Max 15% bonus

        return max(0, min(100, base_score))  # Clamp between 0 and 100

    def _generate_recommendations(self, security_issues, performance_issues, style_issues) -> List[str]:
        """Generate recommendations based on identified issues."""
        recommendations = []

        if len(security_issues) > 0:
            recommendations.append(f"Security: Address {len(security_issues)} security issues, particularly hardcoded credentials")

        if len(performance_issues) > 0:
            recommendations.append(f"Performance: Review {len(performance_issues)} performance-related issues")

        if len(style_issues) > 0:
            recommendations.append(f"Code Style: Fix {len(style_issues)} style violations")

        if not any([security_issues, performance_issues, style_issues]):
            recommendations.append("Great job! No major quality issues detected.")

        return recommendations

    def print_quality_report(self):
        """Print a formatted quality report to console."""
        report = self.run_all_quality_checks()

        print("=" * 100)
        print("QUALITY ASSURANCE REPORT - UNIFIED PHYSICAL AI & HUMANOID ROBOTICS LEARNING BOOK")
        print("=" * 100)
        print(f"Generated at: {report['timestamp']}")
        print(f"Project root: {report['project_root']}")
        print()
        print(f"QUALITY SCORE: {report['quality_score']}/100")
        print(f"GRADE: {self._score_to_grade(report['quality_score'])}")
        print()
        print("METRICS:")
        print(f"  Python files: {report['metrics']['code_quality']['python_files']}")
        print(f"  Test files: {report['metrics']['code_quality']['test_files']}")
        print(f"  Total lines: {report['metrics']['code_quality']['total_lines']}")
        print(f"  Documentation files: {report['metrics']['documentation']['doc_files_count']}")
        print(f"  Estimated test coverage: {report['metrics']['testing']['coverage_estimate']}%")
        print()
        print("RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        print()
        print("DETAILED ISSUES:")
        print("-" * 100)

        issue_types = ["security", "performance", "style"]
        for issue_type in issue_types:
            issues = report['issues'][issue_type]
            if issues:
                print(f"\n{issue_type.upper()} ISSUES ({len(issues)} found):")
                for issue in issues[:10]:  # Show first 10 issues
                    print(f"  • {issue['file']}:{issue.get('line_number', 'N/A')} - {issue['line_content'][:100]}...")
                if len(issues) > 10:
                    print(f"    ... and {len(issues) - 10} more issues")

        print()
        print("=" * 100)

        return report

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "F"

    def save_quality_report(self, output_path: str = "quality_report.json"):
        """Save the quality report to a file."""
        report = self.run_all_quality_checks()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"Quality report saved to: {output_path}")
        return output_path


def main():
    """Main function to run quality assurance checks."""
    import argparse

    parser = argparse.ArgumentParser(description="Run quality assurance checks on the project")
    parser.add_argument("--project-root", "-p", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output file for quality report (JSON)")
    parser.add_argument("--format", "-f", choices=["console", "json", "both"], default="console",
                       help="Output format")

    args = parser.parse_args()

    checker = QualityAssuranceChecker(project_root=args.project_root)

    if args.format in ["console", "both"]:
        report = checker.print_quality_report()
    else:
        report = checker.run_all_quality_checks()

    if args.output or args.format == "json":
        output_path = args.output or "quality_report.json"
        checker.save_quality_report(output_path)

    # Exit with success
    print(f"\n✓ Quality assurance checks completed!")
    sys.exit(0)


if __name__ == "__main__":
    main()