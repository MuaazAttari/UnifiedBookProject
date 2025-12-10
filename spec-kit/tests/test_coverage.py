"""
Test coverage analysis for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module provides functionality to analyze and report test coverage.
"""

import pytest
import sys
import os
import subprocess
from pathlib import Path
import coverage
import json
from typing import Dict, List, Any


def analyze_test_coverage() -> Dict[str, Any]:
    """
    Analyze test coverage for the project using the coverage.py library.

    Returns:
        Dictionary containing coverage statistics and file-by-file breakdown
    """
    # Initialize coverage object
    cov = coverage.Coverage(
        source=['src/'],
        omit=[
            '*/venv/*',
            '*/env/*',
            '*/__pycache__/*',
            '*test*',
            '*tests/*',
            '*/migrations/*',
            '*/config/*',
            '*/settings/*'
        ]
    )

    # Start coverage measurement
    cov.start()

    try:
        # Run the existing tests to gather coverage data
        # This would normally run the actual test suite
        pytest.main([
            'tests/',
            '-v',
            '--tb=short',
            '--disable-warnings'
        ])
    except SystemExit:
        # pytest.main() calls sys.exit(), which we need to catch
        pass
    finally:
        # Stop coverage measurement
        cov.stop()
        cov.save()

    # Get coverage data
    analysis = cov.analysis()

    # Generate detailed coverage report
    report = {
        "summary": {
            "total_statements": 0,
            "total_executed": 0,
            "total_missing": 0,
            "total_excluded": 0,
            "overall_coverage": 0.0
        },
        "files": [],
        "missing_lines": {},
        "coverage_percentage": 0.0
    }

    # Analyze each file
    for file_path, statements, excluded, missing, _ in cov.analysis():
        executed = len(statements) - len(missing)
        coverage_pct = (executed / len(statements)) * 100 if statements else 0

        file_report = {
            "file": file_path,
            "statements": len(statements),
            "executed": executed,
            "missing": len(missing),
            "excluded": len(excluded),
            "coverage": round(coverage_pct, 2)
        }

        report["files"].append(file_report)
        report["missing_lines"][file_path] = missing

        # Update summary
        report["summary"]["total_statements"] += len(statements)
        report["summary"]["total_executed"] += executed
        report["summary"]["total_missing"] += len(missing)
        report["summary"]["total_excluded"] += len(excluded)

    # Calculate overall coverage
    if report["summary"]["total_statements"] > 0:
        report["summary"]["overall_coverage"] = round(
            (report["summary"]["total_executed"] / report["summary"]["total_statements"]) * 100, 2
        )
        report["coverage_percentage"] = report["summary"]["overall_coverage"]

    return report


def generate_coverage_report(report_data: Dict[str, Any], output_path: str = "coverage_report.json"):
    """
    Generate a detailed coverage report in JSON format.

    Args:
        report_data: Coverage analysis data from analyze_test_coverage()
        output_path: Path where to save the report
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"Coverage report saved to: {output_path}")


def print_coverage_summary(report_data: Dict[str, Any]):
    """
    Print a summary of the coverage analysis to console.

    Args:
        report_data: Coverage analysis data from analyze_test_coverage()
    """
    summary = report_data["summary"]

    print("=" * 60)
    print("TEST COVERAGE ANALYSIS REPORT")
    print("=" * 60)
    print(f"Overall Coverage: {report_data['coverage_percentage']:.2f}%")
    print(f"Total Statements: {summary['total_statements']}")
    print(f"Executed Statements: {summary['total_executed']}")
    print(f"Missing Statements: {summary['total_missing']}")
    print(f"Excluded Statements: {summary['total_excluded']}")
    print()

    print("FILE-BY-FILE BREAKDOWN:")
    print("-" * 60)

    # Sort files by coverage percentage
    sorted_files = sorted(report_data["files"], key=lambda x: x["coverage"])

    for file_report in sorted_files:
        status = "✅" if file_report["coverage"] >= 80 else "⚠️" if file_report["coverage"] >= 50 else "❌"
        print(f"{status} {file_report['file']}")
        print(f"    Coverage: {file_report['coverage']:.2f}% "
              f"({file_report['executed']}/{file_report['statements']})")

        if file_report["missing"]:
            print(f"    Missing lines: {file_report['missing'][:10]}{'...' if len(file_report['missing']) > 10 else ''}")
        print()

    print("=" * 60)

    # Coverage goals
    goals_met = []
    goals_not_met = []

    if report_data['coverage_percentage'] >= 80:
        goals_met.append("✅ Overall coverage >= 80%")
    else:
        goals_not_met.append(f"❌ Overall coverage >= 80% (current: {report_data['coverage_percentage']:.2f}%)")

    if report_data['summary']['total_statements'] > 0:
        goals_met.append("✅ Code base has measurable coverage")
    else:
        goals_not_met.append("❌ No statements found for coverage analysis")

    print("COVERAGE GOALS:")
    for goal in goals_met:
        print(f"  {goal}")
    for goal in goals_not_met:
        print(f"  {goal}")

    print("=" * 60)


def run_coverage_analysis():
    """
    Run the complete coverage analysis workflow.
    """
    print("Running test coverage analysis...")

    try:
        report_data = analyze_test_coverage()
        generate_coverage_report(report_data, "test_coverage_report.json")
        print_coverage_summary(report_data)

        # Return success status based on coverage threshold
        return report_data['coverage_percentage'] >= 70  # 70% minimum acceptable coverage

    except Exception as e:
        print(f"Error during coverage analysis: {str(e)}")
        return False


def get_test_file_coverage_stats() -> Dict[str, Any]:
    """
    Get statistics about test files themselves.

    Returns:
        Dictionary containing test file statistics
    """
    test_dir = Path("tests")
    stats = {
        "total_test_files": 0,
        "total_test_functions": 0,
        "test_files": [],
        "coverage_by_module": {}
    }

    if test_dir.exists():
        for test_file in test_dir.rglob("test_*.py"):
            stats["total_test_files"] += 1

            # Read the test file to count test functions
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count test functions (functions starting with test_)
            import re
            test_functions = re.findall(r'def test_\w+', content)
            test_count = len(test_functions)

            stats["total_test_functions"] += test_count

            file_stats = {
                "file": str(test_file),
                "test_functions": test_count,
                "size": test_file.stat().st_size
            }
            stats["test_files"].append(file_stats)

            # Determine which module this test covers
            relative_path = str(test_file.relative_to(test_dir))
            if relative_path.startswith("test_"):
                covered_module = "general"
            else:
                # Extract module name from path
                parts = relative_path.split(os.sep)
                covered_module = parts[0] if parts else "general"

            if covered_module not in stats["coverage_by_module"]:
                stats["coverage_by_module"][covered_module] = 0
            stats["coverage_by_module"][covered_module] += test_count

    return stats


def print_test_stats():
    """
    Print statistics about the test suite.
    """
    stats = get_test_file_coverage_stats()

    print("\nTEST SUITE STATISTICS:")
    print("=" * 40)
    print(f"Total Test Files: {stats['total_test_files']}")
    print(f"Total Test Functions: {stats['total_test_functions']}")
    print()

    print("Tests by Module:")
    for module, count in stats["coverage_by_module"].items():
        print(f"  {module}: {count} tests")

    print()
    print("Individual Test Files:")
    for file_stat in stats["test_files"]:
        print(f"  {file_stat['file']}: {file_stat['test_functions']} tests ({file_stat['size']} bytes)")


def validate_test_quality():
    """
    Validate the quality of tests based on best practices.

    Returns:
        Dictionary with validation results
    """
    validation_results = {
        "total_files_analyzed": 0,
        "files_passing_quality_check": 0,
        "issues_found": [],
        "quality_score": 0
    }

    test_dir = Path("tests")

    if test_dir.exists():
        for test_file in test_dir.rglob("test_*.py"):
            validation_results["total_files_analyzed"] += 1

            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()

            issues = []

            # Check for common test quality issues
            if "import pdb" in content or "pdb.set_trace()" in content:
                issues.append("Debug breakpoint found")

            if "print(" in content and "print(" in content.split('\n')[:10]:
                # Check if print statements are in comments or actual code
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('print(') and '#' not in line:
                        issues.append("Print statement found in test code")
                        break

            if "assert 1 == 1" in content or "assert True" in content:
                issues.append("Trivial assertion found")

            if "time.sleep(" in content:
                issues.append("Hard-coded sleep found (use mocking instead)")

            # Check for proper test structure
            if "def test_" not in content:
                issues.append("No test functions found")

            if len(content.strip()) < 50 and "def test_" in content:
                issues.append("Test file is very short - may lack proper tests")

            if not issues:
                validation_results["files_passing_quality_check"] += 1
            else:
                validation_results["issues_found"].append({
                    "file": str(test_file),
                    "issues": issues
                })

    if validation_results["total_files_analyzed"] > 0:
        validation_results["quality_score"] = round(
            (validation_results["files_passing_quality_check"] /
             validation_results["total_files_analyzed"]) * 100, 2
        )

    return validation_results


def print_quality_validation(quality_results: Dict[str, Any]):
    """
    Print the quality validation results.

    Args:
        quality_results: Results from validate_test_quality()
    """
    print("\nTEST QUALITY VALIDATION:")
    print("=" * 40)
    print(f"Files Analyzed: {quality_results['total_files_analyzed']}")
    print(f"Files Passing Quality Check: {quality_results['files_passing_quality_check']}")
    print(f"Quality Score: {quality_results['quality_score']:.2f}%")

    if quality_results["issues_found"]:
        print("\nIssues Found:")
        for issue in quality_results["issues_found"]:
            print(f"  {issue['file']}:")
            for issue_desc in issue["issues"]:
                print(f"    - {issue_desc}")
    else:
        print("✅ No quality issues found!")


def generate_comprehensive_test_report():
    """
    Generate a comprehensive test report including coverage, statistics, and quality.
    """
    print("Generating Comprehensive Test Report...")
    print("=" * 60)

    # Run coverage analysis
    coverage_success = run_coverage_analysis()

    # Print test statistics
    print_test_stats()

    # Validate test quality
    quality_results = validate_test_quality()
    print_quality_validation(quality_results)

    # Overall assessment
    print("\nOVERALL ASSESSMENT:")
    print("=" * 40)

    assessments = []
    if coverage_success:
        assessments.append("✅ Test coverage meets minimum requirements (>=70%)")
    else:
        assessments.append("❌ Test coverage needs improvement (<70%)")

    if quality_results["quality_score"] >= 80:
        assessments.append("✅ Test quality is good")
    else:
        assessments.append("⚠️ Test quality could be improved")

    for assessment in assessments:
        print(f"  {assessment}")

    print("=" * 60)

    return coverage_success and quality_results["quality_score"] >= 60


if __name__ == "__main__":
    success = generate_comprehensive_test_report()

    if success:
        print("\n✓ Comprehensive test analysis completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ Some test quality metrics need attention!")
        sys.exit(1 if not success else 0)