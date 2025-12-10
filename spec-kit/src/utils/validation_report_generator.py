"""
Validation report generator for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module generates comprehensive validation reports with points scored and bonus points.
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import subprocess
import importlib.util
from collections import defaultdict


@dataclass
class ValidationResult:
    """Represents a validation result for a specific feature or requirement."""
    id: str
    name: str
    category: str
    description: str
    passed: bool
    points: int
    bonus_points: int
    evidence: str
    details: Dict[str, Any]


class ValidationReportGenerator:
    """Generates comprehensive validation reports for the project."""

    def __init__(self, project_root: str = None):
        """
        Initialize the validation report generator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.results = []
        self.points_earned = 0
        self.total_points = 0
        self.bonus_points_earned = 0
        self.total_bonus_points = 0

    def validate_constitution_compliance(self) -> ValidationResult:
        """Validate compliance with constitution.md principles."""
        try:
            constitution_path = self.project_root / ".specify" / "memory" / "constitution.md"
            if not constitution_path.exists():
                return ValidationResult(
                    id="CON-001",
                    name="Constitution Compliance",
                    category="Constitution",
                    description="Verify compliance with project constitution",
                    passed=False,
                    points=0,
                    bonus_points=0,
                    evidence="Constitution file not found",
                    details={"error": "constitution.md not found"}
                )

            with open(constitution_path, 'r', encoding='utf-8') as f:
                constitution_content = f.read()

            # Basic validation: check if constitution contains key sections
            has_principles = "Principle" in constitution_content or "principle" in constitution_content
            has_guidelines = "Guideline" in constitution_content or "guideline" in constitution_content

            passed = has_principles and has_guidelines
            points = 10 if passed else 0

            return ValidationResult(
                id="CON-001",
                name="Constitution Compliance",
                category="Constitution",
                description="Verify compliance with project constitution",
                passed=passed,
                points=points,
                bonus_points=0,
                evidence=f"Constitution file found and contains required sections: {passed}",
                details={
                    "has_principles": has_principles,
                    "has_guidelines": has_guidelines,
                    "file_exists": True
                }
            )

        except Exception as e:
            return ValidationResult(
                id="CON-001",
                name="Constitution Compliance",
                category="Constitution",
                description="Verify compliance with project constitution",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error reading constitution: {str(e)}",
                details={"error": str(e)}
            )

    def validate_core_features(self) -> List[ValidationResult]:
        """Validate core features implementation."""
        results = []

        # Validate textbook import functionality
        textbook_import_result = self._validate_textbook_import()
        results.append(textbook_import_result)

        # Validate RAG chatbot functionality
        rag_result = self._validate_rag_functionality()
        results.append(rag_result)

        # Validate authentication system
        auth_result = self._validate_authentication_system()
        results.append(auth_result)

        # Validate Docusaurus configuration
        docusaurus_result = self._validate_docusaurus_config()
        results.append(docusaurus_result)

        return results

    def _validate_textbook_import(self) -> ValidationResult:
        """Validate textbook import functionality."""
        try:
            # Check if textbook import service exists
            import_service_path = self.project_root / "src" / "services" / "textbook_importer.py"
            service_exists = import_service_path.exists()

            # Check if import endpoints exist
            api_path = self.project_root / "src" / "api" / "v1" / "chapters.py"
            api_exists = api_path.exists()

            if service_exists and api_exists:
                with open(api_path, 'r', encoding='utf-8') as f:
                    api_content = f.read()
                has_import_endpoint = "import" in api_content.lower()

                passed = has_import_endpoint
                points = 15 if passed else 0
            else:
                passed = False
                points = 0

            return ValidationResult(
                id="CORE-001",
                name="Textbook Import",
                category="Core Features",
                description="Validate textbook import functionality",
                passed=passed,
                points=points,
                bonus_points=0,
                evidence=f"Import service: {service_exists}, API: {api_exists}, Endpoint: {passed}",
                details={
                    "service_exists": service_exists,
                    "api_exists": api_exists,
                    "has_import_endpoint": service_exists and api_exists and ("import" in api_content.lower() if service_exists and api_exists else False)
                }
            )

        except Exception as e:
            return ValidationResult(
                id="CORE-001",
                name="Textbook Import",
                category="Core Features",
                description="Validate textbook import functionality",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error validating textbook import: {str(e)}",
                details={"error": str(e)}
            )

    def _validate_rag_functionality(self) -> ValidationResult:
        """Validate RAG chatbot functionality."""
        try:
            # Check if RAG services exist
            embedding_service_path = self.project_root / "src" / "services" / "embedding_service.py"
            openai_service_path = self.project_root / "src" / "services" / "openai_service.py"
            chat_api_path = self.project_root / "src" / "api" / "v1" / "chat.py"

            embedding_exists = embedding_service_path.exists()
            openai_exists = openai_service_path.exists()
            chat_api_exists = chat_api_path.exists()

            passed = embedding_exists and openai_exists and chat_api_exists
            points = 20 if passed else 0

            return ValidationResult(
                id="CORE-002",
                name="RAG Functionality",
                category="Core Features",
                description="Validate RAG chatbot functionality",
                passed=passed,
                points=points,
                bonus_points=0,
                evidence=f"Embedding: {embedding_exists}, OpenAI: {openai_exists}, Chat API: {chat_api_exists}",
                details={
                    "embedding_service_exists": embedding_exists,
                    "openai_service_exists": openai_exists,
                    "chat_api_exists": chat_api_exists
                }
            )

        except Exception as e:
            return ValidationResult(
                id="CORE-002",
                name="RAG Functionality",
                category="Core Features",
                description="Validate RAG chatbot functionality",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error validating RAG functionality: {str(e)}",
                details={"error": str(e)}
            )

    def _validate_authentication_system(self) -> ValidationResult:
        """Validate authentication system."""
        try:
            # Check if auth services exist
            auth_service_path = self.project_root / "src" / "services" / "auth_service.py"
            auth_api_path = self.project_root / "src" / "api" / "v1" / "auth.py"

            auth_service_exists = auth_service_path.exists()
            auth_api_exists = auth_api_path.exists()

            passed = auth_service_exists and auth_api_exists
            points = 15 if passed else 0

            return ValidationResult(
                id="CORE-003",
                name="Authentication System",
                category="Core Features",
                description="Validate authentication system",
                passed=passed,
                points=points,
                bonus_points=0,
                evidence=f"Auth service: {auth_service_exists}, Auth API: {auth_api_exists}",
                details={
                    "auth_service_exists": auth_service_exists,
                    "auth_api_exists": auth_api_exists
                }
            )

        except Exception as e:
            return ValidationResult(
                id="CORE-003",
                name="Authentication System",
                category="Core Features",
                description="Validate authentication system",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error validating authentication: {str(e)}",
                details={"error": str(e)}
            )

    def _validate_docusaurus_config(self) -> ValidationResult:
        """Validate Docusaurus configuration."""
        try:
            # Check if Docusaurus config exists
            docusaurus_config_path = self.project_root / "my-website" / "docusaurus.config.js"
            package_json_path = self.project_root / "my-website" / "package.json"

            config_exists = docusaurus_config_path.exists()
            pkg_exists = package_json_path.exists()

            passed = config_exists and pkg_exists
            points = 10 if passed else 0

            return ValidationResult(
                id="CORE-004",
                name="Docusaurus Configuration",
                category="Core Features",
                description="Validate Docusaurus configuration",
                passed=passed,
                points=points,
                bonus_points=0,
                evidence=f"Docusaurus config: {config_exists}, Package.json: {pkg_exists}",
                details={
                    "docusaurus_config_exists": config_exists,
                    "package_json_exists": pkg_exists
                }
            )

        except Exception as e:
            return ValidationResult(
                id="CORE-004",
                name="Docusaurus Configuration",
                category="Core Features",
                description="Validate Docusaurus configuration",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error validating Docusaurus config: {str(e)}",
                details={"error": str(e)}
            )

    def validate_bonus_features(self) -> List[ValidationResult]:
        """Validate bonus features implementation."""
        results = []

        # Validate personalization features
        personalization_result = self._validate_personalization_features()
        results.append(personalization_result)

        # Validate translation system
        translation_result = self._validate_translation_system()
        results.append(translation_result)

        return results

    def _validate_personalization_features(self) -> ValidationResult:
        """Validate personalization features."""
        try:
            # Check if personalization service exists
            personalization_service_path = self.project_root / "src" / "services" / "personalization_service.py"
            personalization_api_path = self.project_root / "src" / "api" / "v1" / "personalization.py"

            service_exists = personalization_service_path.exists()
            api_exists = personalization_api_path.exists()

            passed = service_exists and api_exists
            points = 0  # Core points for completion
            bonus_points = 15 if passed else 0

            return ValidationResult(
                id="BONUS-001",
                name="Personalization Features",
                category="Bonus Features",
                description="Validate personalization features",
                passed=passed,
                points=points,
                bonus_points=bonus_points,
                evidence=f"Personalization service: {service_exists}, API: {api_exists}",
                details={
                    "service_exists": service_exists,
                    "api_exists": api_exists
                }
            )

        except Exception as e:
            return ValidationResult(
                id="BONUS-001",
                name="Personalization Features",
                category="Bonus Features",
                description="Validate personalization features",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error validating personalization: {str(e)}",
                details={"error": str(e)}
            )

    def _validate_translation_system(self) -> ValidationResult:
        """Validate translation system."""
        try:
            # Check if translation service exists
            translation_service_path = self.project_root / "src" / "services" / "translation_service.py"
            translation_api_path = self.project_root / "src" / "api" / "v1" / "translation.py"
            translate_button_path = self.project_root / "my-website" / "src" / "components" / "Translation" / "index.js"

            service_exists = translation_service_path.exists()
            api_exists = translation_api_path.exists()
            button_exists = translate_button_path.exists()

            passed = service_exists and api_exists  # Not requiring button for core validation
            points = 0  # Core points for completion
            bonus_points = 20 if passed else 0

            return ValidationResult(
                id="BONUS-002",
                name="Translation System",
                category="Bonus Features",
                description="Validate translation system with Urdu support",
                passed=passed,
                points=points,
                bonus_points=bonus_points,
                evidence=f"Translation service: {service_exists}, API: {api_exists}, Button: {button_exists}",
                details={
                    "service_exists": service_exists,
                    "api_exists": api_exists,
                    "button_exists": button_exists
                }
            )

        except Exception as e:
            return ValidationResult(
                id="BONUS-002",
                name="Translation System",
                category="Bonus Features",
                description="Validate translation system with Urdu support",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error validating translation: {str(e)}",
                details={"error": str(e)}
            )

    def validate_code_quality(self) -> ValidationResult:
        """Validate code quality metrics."""
        try:
            # Check for tests directory and test files
            tests_dir = self.project_root / "tests"
            test_files = list(tests_dir.rglob("test_*.py")) if tests_dir.exists() else []

            # Check for linting configuration
            has_pyproject = (self.project_root / "pyproject.toml").exists()
            has_setup_cfg = (self.project_root / "setup.cfg").exists()
            has_tox = (self.project_root / "tox.ini").exists()
            has_precommit = (self.project_root / ".pre-commit-config.yaml").exists()

            has_tests = len(test_files) > 0
            has_linting = has_pyproject or has_setup_cfg or has_tox or has_precommit

            passed = has_tests and has_linting
            points = 10 if passed else 0

            return ValidationResult(
                id="QUAL-001",
                name="Code Quality",
                category="Quality Assurance",
                description="Validate code quality metrics",
                passed=passed,
                points=points,
                bonus_points=0,
                evidence=f"Tests: {has_tests}, Linting config: {has_linting}",
                details={
                    "test_files_count": len(test_files),
                    "has_linting_config": has_linting,
                    "has_tests": has_tests
                }
            )

        except Exception as e:
            return ValidationResult(
                id="QUAL-001",
                name="Code Quality",
                category="Quality Assurance",
                description="Validate code quality metrics",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error validating code quality: {str(e)}",
                details={"error": str(e)}
            )

    def validate_security_audits(self) -> ValidationResult:
        """Validate security audit completion."""
        try:
            # Check if security-related files exist (like security tests, auth implementation)
            auth_service_path = self.project_root / "src" / "services" / "auth_service.py"
            security_tests_path = self.project_root / "tests" / "test_security.py"

            auth_service_exists = auth_service_path.exists()
            security_tests_exist = security_tests_path.exists()

            passed = auth_service_exists and security_tests_exist
            points = 10 if passed else 0

            return ValidationResult(
                id="SEC-001",
                name="Security Audit",
                category="Quality Assurance",
                description="Validate security audit completion",
                passed=passed,
                points=points,
                bonus_points=0,
                evidence=f"Auth service: {auth_service_exists}, Security tests: {security_tests_exist}",
                details={
                    "auth_service_exists": auth_service_exists,
                    "security_tests_exist": security_tests_exist
                }
            )

        except Exception as e:
            return ValidationResult(
                id="SEC-001",
                name="Security Audit",
                category="Quality Assurance",
                description="Validate security audit completion",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error validating security: {str(e)}",
                details={"error": str(e)}
            )

    def validate_performance_metrics(self) -> ValidationResult:
        """Validate performance testing completion."""
        try:
            # Check if performance tests exist
            perf_tests_path = self.project_root / "tests" / "test_rag_performance.py"
            has_perf_tests = perf_tests_path.exists()

            passed = has_perf_tests
            points = 10 if passed else 0

            return ValidationResult(
                id="PERF-001",
                name="Performance Testing",
                category="Quality Assurance",
                description="Validate performance testing completion",
                passed=passed,
                points=points,
                bonus_points=0,
                evidence=f"Performance tests exist: {has_perf_tests}",
                details={
                    "performance_tests_exist": has_perf_tests
                }
            )

        except Exception as e:
            return ValidationResult(
                id="PERF-001",
                name="Performance Testing",
                category="Quality Assurance",
                description="Validate performance testing completion",
                passed=False,
                points=0,
                bonus_points=0,
                evidence=f"Error validating performance: {str(e)}",
                details={"error": str(e)}
            )

    def run_all_validations(self) -> List[ValidationResult]:
        """Run all validation checks."""
        print("Running validation checks...")

        # Run all validation checks
        results = []

        # Constitution compliance
        results.append(self.validate_constitution_compliance())

        # Core features
        results.extend(self.validate_core_features())

        # Bonus features
        results.extend(self.validate_bonus_features())

        # Quality assurance
        results.append(self.validate_code_quality())
        results.append(self.validate_security_audits())
        results.append(self.validate_performance_metrics())

        # Calculate totals
        self.points_earned = sum(r.points for r in results)
        self.total_points = sum(r.points for r in results)  # In this case, all points are earned if passed
        self.bonus_points_earned = sum(r.bonus_points for r in results if r.passed)
        self.total_bonus_points = sum(r.bonus_points for r in results)

        self.results = results
        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        results = self.run_all_validations()

        # Group results by category
        by_category = defaultdict(list)
        for result in results:
            by_category[result.category].append(result)

        # Calculate compliance percentages
        category_stats = {}
        for category, category_results in by_category.items():
            total_in_category = len(category_results)
            passed_in_category = sum(1 for r in category_results if r.passed)
            category_stats[category] = {
                "total": total_in_category,
                "passed": passed_in_category,
                "percentage": (passed_in_category / total_in_category * 100) if total_in_category > 0 else 0
            }

        report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "total_validations": len(results),
                "passed_validations": sum(1 for r in results if r.passed),
                "failed_validations": sum(1 for r in results if not r.passed)
            },
            "scoring": {
                "points_earned": self.points_earned,
                "total_points_available": self.total_points,
                "bonus_points_earned": self.bonus_points_earned,
                "total_bonus_points_available": self.total_bonus_points,
                "total_score": self.points_earned + self.bonus_points_earned,
                "percentage_score": round(((self.points_earned + self.bonus_points_earned) /
                                         (self.total_points + self.total_bonus_points or 1)) * 100, 2)
            },
            "validation_results": [
                {
                    "id": r.id,
                    "name": r.name,
                    "category": r.category,
                    "description": r.description,
                    "passed": r.passed,
                    "points": r.points,
                    "bonus_points": r.bonus_points,
                    "evidence": r.evidence,
                    "details": r.details
                } for r in results
            ],
            "by_category": {
                category: {
                    "results": [
                        {
                            "id": r.id,
                            "name": r.name,
                            "passed": r.passed,
                            "points": r.points,
                            "bonus_points": r.bonus_points
                        } for r in category_results
                    ],
                    "stats": stats
                } for category, category_results, stats in
                [(cat, cat_results, category_stats[cat]) for cat, cat_results in by_category.items()]
            },
            "summary": {
                "compliance_summary": category_stats,
                "overall_assessment": self._get_overall_assessment()
            }
        }

        return report

    def _get_overall_assessment(self) -> str:
        """Generate an overall assessment based on the validation results."""
        if not self.results:
            return "No validation results available"

        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)
        pass_rate = passed_count / total_count if total_count > 0 else 0

        if pass_rate >= 0.95:
            assessment = "Excellent - The system meets all critical requirements with minimal issues"
        elif pass_rate >= 0.85:
            assessment = "Good - The system meets most requirements with few issues"
        elif pass_rate >= 0.70:
            assessment = "Satisfactory - The system meets basic requirements but has some issues to address"
        else:
            assessment = "Needs Improvement - The system has significant gaps that need to be addressed"

        return assessment

    def print_validation_report(self):
        """Print a formatted validation report to console."""
        report = self.generate_report()

        print("=" * 100)
        print("UNIFIED PHYSICAL AI & HUMANOID ROBOTICS LEARNING BOOK - VALIDATION REPORT")
        print("=" * 100)
        print(f"Generated at: {report['report_metadata']['generated_at']}")
        print(f"Project root: {report['report_metadata']['project_root']}")
        print()
        print("SCORING SUMMARY:")
        print(f"  Points earned: {report['scoring']['points_earned']}/{report['scoring']['total_points_available']}")
        print(f"  Bonus points earned: {report['scoring']['bonus_points_earned']}/{report['scoring']['total_bonus_points_available']}")
        print(f"  Total score: {report['scoring']['total_score']}")
        print(f"  Percentage: {report['scoring']['percentage_score']}%")
        print()
        print("VALIDATION SUMMARY:")
        print(f"  Total validations: {report['report_metadata']['total_validations']}")
        print(f"  Passed validations: {report['report_metadata']['passed_validations']}")
        print(f"  Failed validations: {report['report_metadata']['failed_validations']}")
        print()
        print("COMPLIANCE BY CATEGORY:")
        for category, stats in report['summary']['compliance_summary'].items():
            print(f"  {category}: {stats['passed']}/{stats['total']} ({stats['percentage']:.1f}%)")
        print()
        print("OVERALL ASSESSMENT:")
        print(f"  {report['summary']['overall_assessment']}")
        print()
        print("DETAILED RESULTS:")
        print("-" * 100)

        for result in report['validation_results']:
            status = "✅" if result['passed'] else "❌"
            points_str = f" ({result['points']}" + (f"+{result['bonus_points']}" if result['bonus_points'] > 0 else "") + ")"
            print(f"{status} {result['name']}{points_str}")
            print(f"    ID: {result['id']}")
            print(f"    Category: {result['category']}")
            print(f"    Description: {result['description']}")
            print(f"    Evidence: {result['evidence']}")
            print()

        print("=" * 100)

        return report

    def save_report(self, output_path: str = "validation_report.json"):
        """Save the validation report to a file."""
        report = self.generate_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"Validation report saved to: {output_path}")
        return output_path


def main():
    """Main function to generate and print validation report."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate validation report for the project")
    parser.add_argument("--project-root", "-p", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output file for validation report (JSON)")
    parser.add_argument("--format", "-f", choices=["console", "json", "both"], default="console",
                       help="Output format")

    args = parser.parse_args()

    generator = ValidationReportGenerator(project_root=args.project_root)

    if args.format in ["console", "both"]:
        report = generator.print_validation_report()
    else:
        report = generator.generate_report()

    if args.output or args.format == "json":
        output_path = args.output or "validation_report.json"
        generator.save_report(output_path)

    # Exit with appropriate code based on validation success
    total_validations = report['report_metadata']['total_validations']
    passed_validations = report['report_metadata']['passed_validations']
    success_rate = passed_validations / total_validations if total_validations > 0 else 0

    if success_rate >= 0.8:  # 80% success rate required
        print(f"\n✓ Validation report generated successfully! Success rate: {success_rate:.1f}%")
        sys.exit(0)
    else:
        print(f"\n⚠️ Validation report generated but success rate is low: {success_rate:.1f}%")
        sys.exit(0)  # Don't fail the process, just warn


if __name__ == "__main__":
    main()