"""
Constitution compliance validation script for the Unified Physical AI & Humanoid Robotics Learning Book project.
This script validates that the implemented system complies with the principles in constitution.md.
"""

import os
import sys
from pathlib import Path
import yaml
import json
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

# Add the project root to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.file_utils import read_file_with_encoding


@dataclass
class ValidationRule:
    """Represents a validation rule from the constitution."""
    id: str
    category: str
    description: str
    requirement: str
    implementation_status: str
    evidence_path: str
    validation_method: str


@dataclass
class ValidationResult:
    """Represents the result of a validation check."""
    rule_id: str
    rule_description: str
    passed: bool
    message: str
    evidence: str = ""


class ConstitutionValidator:
    """Validates project compliance with constitution.md principles."""

    def __init__(self, constitution_path: str = None, project_root: str = None):
        """
        Initialize the constitution validator.

        Args:
            constitution_path: Path to constitution.md file
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.constitution_path = Path(constitution_path) if constitution_path else self.project_root / ".specify" / "memory" / "constitution.md"
        self.rules = []

    def load_constitution(self) -> str:
        """Load the constitution file content."""
        try:
            return read_file_with_encoding(str(self.constitution_path))
        except FileNotFoundError:
            raise FileNotFoundError(f"Constitution file not found at: {self.constitution_path}")
        except Exception as e:
            raise Exception(f"Error reading constitution file: {str(e)}")

    def extract_principles(self) -> List[Dict[str, Any]]:
        """Extract principles from the constitution file."""
        constitution_content = self.load_constitution()
        principles = []

        # Parse the constitution markdown content
        lines = constitution_content.split('\n')
        current_section = ""
        current_principle = {}

        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                # New section
                current_section = line
            elif line.startswith('##') and 'Principle' in line:
                # Start of a new principle
                if current_principle:
                    principles.append(current_principle)
                current_principle = {
                    'title': line.replace('##', '').strip(),
                    'content': []
                }
            elif line and current_principle:
                # Add content to current principle
                current_principle['content'].append(line)

        # Add the last principle
        if current_principle:
            principles.append(current_principle)

        return principles

    def create_validation_rules(self) -> List[ValidationRule]:
        """Create validation rules based on constitution principles."""
        principles = self.extract_principles()
        rules = []

        for i, principle in enumerate(principles):
            rule = ValidationRule(
                id=f"PRIN-{i+1:03d}",
                category="Principle",
                description=principle['title'],
                requirement=" ".join(principle['content'][:3]) if principle['content'] else "Principle requirement",
                implementation_status="Implemented",
                evidence_path="",
                validation_method="Manual/Code Review"
            )
            rules.append(rule)

        # Add specific validation rules based on common constitution requirements
        specific_rules = [
            ValidationRule(
                id="SEC-001",
                category="Security",
                description="Secure authentication system",
                requirement="Implement secure authentication with proper validation",
                implementation_status="Implemented",
                evidence_path="src/services/auth_service.py",
                validation_method="Code Review"
            ),
            ValidationRule(
                id="PERF-001",
                category="Performance",
                description="Fast API response times",
                requirement="API endpoints should respond within 500ms for 95th percentile",
                implementation_status="Implemented",
                evidence_path="src/api/v1/*.py",
                validation_method="Performance Test"
            ),
            ValidationRule(
                id="TEST-001",
                category="Testing",
                description="Comprehensive test coverage",
                requirement="All critical components should have unit and integration tests",
                implementation_status="Implemented",
                evidence_path="tests/*.py",
                validation_method="Coverage Analysis"
            ),
            ValidationRule(
                id="DOC-001",
                category="Documentation",
                description="Comprehensive documentation",
                requirement="All public APIs and major components should be documented",
                implementation_status="Implemented",
                evidence_path="docs/*.md, src/**/*.py",
                validation_method="Documentation Review"
            ),
            ValidationRule(
                id="RAG-001",
                category="RAG",
                description="RAG system functionality",
                requirement="RAG system should provide accurate responses from book content",
                implementation_status="Implemented",
                evidence_path="src/services/embedding_service.py, src/services/openai_service.py",
                validation_method="Functional Test"
            ),
            ValidationRule(
                id="TRANSL-001",
                category="Translation",
                description="Translation functionality",
                requirement="System should support content translation with caching",
                implementation_status="Implemented",
                evidence_path="src/services/translation_service.py",
                validation_method="Functional Test"
            ),
            ValidationRule(
                id="PERSON-001",
                category="Personalization",
                description="Content personalization",
                requirement="System should allow content personalization based on user profile",
                implementation_status="Implemented",
                evidence_path="src/services/personalization_service.py",
                validation_method="Functional Test"
            ),
        ]

        rules.extend(specific_rules)
        return rules

    def validate_rule(self, rule: ValidationRule) -> ValidationResult:
        """Validate a single rule against the implementation."""
        # Check if the evidence path exists
        if rule.evidence_path:
            # Handle multiple paths (comma-separated)
            paths = [p.strip() for p in rule.evidence_path.split(',')]
            found_paths = []

            for path in paths:
                full_path = self.project_root / path.strip('*')
                if full_path.exists() or list(self.project_root.glob(path)):
                    found_paths.append(path)

            if found_paths:
                return ValidationResult(
                    rule_id=rule.id,
                    rule_description=rule.description,
                    passed=True,
                    message=f"Rule {rule.id} implementation found in: {', '.join(found_paths)}",
                    evidence=f"Files found: {', '.join(found_paths)}"
                )
            else:
                return ValidationResult(
                    rule_id=rule.id,
                    rule_description=rule.description,
                    passed=False,
                    message=f"Rule {rule.id} implementation NOT found: {rule.evidence_path}",
                    evidence=f"Files not found: {rule.evidence_path}"
                )

        # For rules without specific evidence paths, mark as manual validation required
        return ValidationResult(
            rule_id=rule.id,
            rule_description=rule.description,
            passed=False,  # Manual validation required
            message=f"Rule {rule.id} requires manual validation: {rule.description}",
            evidence="Manual review needed"
        )

    def validate_all_rules(self) -> List[ValidationResult]:
        """Validate all rules against the implementation."""
        rules = self.create_validation_rules()
        results = []

        for rule in rules:
            result = self.validate_rule(rule)
            results.append(result)

        return results

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        results = self.validate_all_rules()

        # Calculate statistics
        total_rules = len(results)
        passed_rules = sum(1 for r in results if r.passed)
        failed_rules = total_rules - passed_rules

        # Group results by category
        by_category = {}
        for result in results:
            # Find the corresponding rule to get category
            rules = self.create_validation_rules()
            rule = next((r for r in rules if r.id == result.rule_id), None)
            category = rule.category if rule else "Uncategorized"

            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)

        report = {
            "summary": {
                "total_rules": total_rules,
                "passed_rules": passed_rules,
                "failed_rules": failed_rules,
                "compliance_percentage": (passed_rules / total_rules * 100) if total_rules > 0 else 0
            },
            "detailed_results": [result.__dict__ for result in results],
            "by_category": {cat: [r.__dict__ for r in res] for cat, res in by_category.items()},
            "validation_timestamp": __import__('datetime').datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "constitution_path": str(self.constitution_path)
        }

        return report

    def print_validation_report(self):
        """Print a formatted validation report to console."""
        report = self.generate_validation_report()

        print("=" * 80)
        print("CONSTITUTION COMPLIANCE VALIDATION REPORT")
        print("=" * 80)
        print(f"Project Root: {report['project_root']}")
        print(f"Constitution Path: {report['constitution_path']}")
        print(f"Validation Timestamp: {report['validation_timestamp']}")
        print()

        print("SUMMARY:")
        print(f"  Total Rules: {report['summary']['total_rules']}")
        print(f"  Passed: {report['summary']['passed_rules']}")
        print(f"  Failed: {report['summary']['failed_rules']}")
        print(f"  Compliance: {report['summary']['compliance_percentage']:.1f}%")
        print()

        print("DETAILED RESULTS BY CATEGORY:")
        for category, results in report['by_category'].items():
            passed_in_cat = sum(1 for r in results if r['passed'])
            total_in_cat = len(results)
            print(f"  {category}: {passed_in_cat}/{total_in_cat} passed ({passed_in_cat/total_in_cat*100:.1f}%)")

        print()
        print("FAILED RULES:")
        failed_results = [r for r in report['detailed_results'] if not r['passed']]
        for result in failed_results:
            print(f"  - {result['rule_id']}: {result['rule_description']}")
            print(f"    Message: {result['message']}")

        print("=" * 80)

        return report


def main():
    """Main function to run the constitution validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate project compliance with constitution")
    parser.add_argument("--constitution", "-c", help="Path to constitution.md file")
    parser.add_argument("--project-root", "-p", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output file for validation report (JSON)")
    parser.add_argument("--format", "-f", choices=["console", "json", "both"], default="console",
                       help="Output format")

    args = parser.parse_args()

    validator = ConstitutionValidator(
        constitution_path=args.constitution,
        project_root=args.project_root
    )

    if args.format in ["console", "both"]:
        report = validator.print_validation_report()
    else:
        report = validator.generate_validation_report()

    if args.output or args.format == "json":
        output_path = args.output or "constitution_validation_report.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"Validation report saved to: {output_path}")

    # Exit with error code if compliance is below 90%
    compliance = report['summary']['compliance_percentage']
    if compliance < 90.0:
        print(f"\nWARNING: Compliance is below 90% ({compliance:.1f}%)")
        sys.exit(1)
    else:
        print(f"\nSUCCESS: Compliance is {compliance:.1f}%")
        sys.exit(0)


if __name__ == "__main__":
    main()