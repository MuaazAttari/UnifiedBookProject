"""
Final validation report generator for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module generates the final comprehensive validation report with all metrics.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import subprocess
import importlib.util
from src.utils.validation_report_generator import ValidationReportGenerator
from src.utils.points_calculator import PointsCalculator
from src.utils.quality_assurance import QualityAssuranceChecker
from src.utils.deployment_validator import DeploymentValidator


class FinalValidationReport:
    """Generates the final comprehensive validation report."""

    def __init__(self, project_root: str = None):
        """
        Initialize the final validation report generator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate the comprehensive final validation report."""
        print("Generating comprehensive final validation report...")

        # Generate individual reports
        validation_generator = ValidationReportGenerator(self.project_root)
        points_calculator = PointsCalculator(self.project_root)
        qa_checker = QualityAssuranceChecker(self.project_root)
        deployment_validator = DeploymentValidator(self.project_root)

        # Get individual reports
        validation_report = validation_generator.generate_report()
        points_report = points_calculator.generate_points_report()
        quality_report = qa_checker.run_all_quality_checks()
        deployment_report = deployment_validator.run_all_validations()

        # Compile the final report
        final_report = {
            "executive_summary": self._generate_executive_summary(
                validation_report, points_report, quality_report, deployment_report
            ),
            "validation_results": validation_report,
            "points_calculation": points_report,
            "quality_assessment": quality_report,
            "deployment_readiness": deployment_report,
            "final_grade": self._determine_final_grade(
                validation_report, points_report, quality_report
            ),
            "certification": self._generate_certification(
                validation_report, points_report, quality_report
            ),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "generator_version": "1.0.0"
            }
        }

        return final_report

    def _generate_executive_summary(self, validation_report, points_report, quality_report, deployment_report) -> Dict[str, Any]:
        """Generate an executive summary of the validation."""
        validation_success_rate = (
            validation_report['report_metadata']['passed_validations'] /
            validation_report['report_metadata']['total_validations']
            if validation_report['report_metadata']['total_validations'] > 0 else 0
        ) * 100

        points_percentage = points_report['summary']['points_percentage']
        quality_score = quality_report['quality_score']

        # Determine overall status
        if (validation_success_rate >= 80 and
            points_percentage >= 70 and
            quality_score >= 70 and
            deployment_report['overall_passed']):
            overall_status = "PASS"
            status_description = "Project meets all requirements and is ready for deployment"
        elif (validation_success_rate >= 60 and
              points_percentage >= 50 and
              quality_score >= 50):
            overall_status = "CONDITIONAL_PASS"
            status_description = "Project meets basic requirements with some areas for improvement"
        else:
            overall_status = "FAIL"
            status_description = "Project has significant gaps that need to be addressed"

        return {
            "overall_status": overall_status,
            "status_description": status_description,
            "validation_success_rate": round(validation_success_rate, 2),
            "points_earned_percentage": round(points_percentage, 2),
            "quality_score": round(quality_score, 2),
            "deployment_ready": deployment_report['overall_passed'],
            "total_features_implemented": validation_report['report_metadata']['passed_validations'],
            "total_points_earned": points_report['summary']['total_points_earned'],
            "grade": self._determine_final_grade(validation_report, points_report, quality_report)
        }

    def _determine_final_grade(self, validation_report, points_report, quality_report) -> str:
        """Determine the final letter grade based on all metrics."""
        # Weighted average of different metrics
        validation_weight = 0.3  # 30% weight to validation success
        points_weight = 0.4      # 40% weight to points earned
        quality_weight = 0.3     # 30% weight to code quality

        validation_success_rate = (
            validation_report['report_metadata']['passed_validations'] /
            validation_report['report_metadata']['total_validations']
            if validation_report['report_metadata']['total_validations'] > 0 else 0
        ) * 100

        points_percentage = points_report['summary']['points_percentage']
        quality_score = quality_report['quality_score']

        weighted_average = (
            (validation_success_rate * validation_weight) +
            (points_percentage * points_weight) +
            (quality_score * quality_weight)
        )

        # Convert to letter grade
        if weighted_average >= 95:
            return "A+"
        elif weighted_average >= 90:
            return "A"
        elif weighted_average >= 85:
            return "A-"
        elif weighted_average >= 80:
            return "B+"
        elif weighted_average >= 75:
            return "B"
        elif weighted_average >= 70:
            return "B-"
        elif weighted_average >= 65:
            return "C+"
        elif weighted_average >= 60:
            return "C"
        elif weighted_average >= 50:
            return "C-"
        else:
            return "F"

    def _generate_certification(self, validation_report, points_report, quality_report) -> Dict[str, Any]:
        """Generate a certification based on the validation results."""
        validation_success_rate = (
            validation_report['report_metadata']['passed_validations'] /
            validation_report['report_metadata']['total_validations']
            if validation_report['report_metadata']['total_validations'] > 0 else 0
        ) * 100

        points_percentage = points_report['summary']['points_percentage']
        quality_score = quality_report['quality_score']

        # Determine certification level
        if validation_success_rate >= 95 and points_percentage >= 90 and quality_score >= 90:
            certification_level = "EXCELLENCE"
            certification_description = "The project demonstrates excellence in all areas and exceeds requirements"
        elif validation_success_rate >= 85 and points_percentage >= 80 and quality_score >= 80:
            certification_level = "DISTINCTION"
            certification_description = "The project demonstrates high quality and meets requirements with distinction"
        elif validation_success_rate >= 75 and points_percentage >= 70 and quality_score >= 70:
            certification_level = "SATISFACTORY"
            certification_description = "The project meets minimum requirements and is satisfactory"
        else:
            certification_level = "NEEDS_IMPROVEMENT"
            certification_description = "The project has significant areas that need improvement"

        return {
            "certification_level": certification_level,
            "certification_description": certification_description,
            "certified": certification_level in ["EXCELLENCE", "DISTINCTION", "SATISFACTORY"],
            "certification_date": datetime.now().isoformat(),
            "compliance_score": round((validation_success_rate + points_percentage + quality_score) / 3, 2)
        }

    def print_final_report(self):
        """Print the final validation report to console."""
        final_report = self.generate_comprehensive_report()

        print("=" * 120)
        print("FINAL VALIDATION REPORT - UNIFIED PHYSICAL AI & HUMANOID ROBOTICS LEARNING BOOK")
        print("=" * 120)
        print(f"Generated at: {final_report['metadata']['generated_at']}")
        print(f"Project root: {final_report['metadata']['project_root']}")
        print()
        print("EXECUTIVE SUMMARY:")
        print(f"  Overall Status: {final_report['executive_summary']['overall_status']}")
        print(f"  Status Description: {final_report['executive_summary']['status_description']}")
        print(f"  Validation Success Rate: {final_report['executive_summary']['validation_success_rate']}%")
        print(f"  Points Earned Percentage: {final_report['executive_summary']['points_earned_percentage']}%")
        print(f"  Quality Score: {final_report['executive_summary']['quality_score']}/100")
        print(f"  Deployment Ready: {final_report['executive_summary']['deployment_ready']}")
        print(f"  Total Features Implemented: {final_report['executive_summary']['total_features_implemented']}")
        print(f"  Total Points Earned: {final_report['executive_summary']['total_points_earned']}")
        print(f"  Final Grade: {final_report['executive_summary']['grade']}")
        print()
        print("CERTIFICATION:")
        print(f"  Level: {final_report['certification']['certification_level']}")
        print(f"  Description: {final_report['certification']['certification_description']}")
        print(f"  Certified: {final_report['certification']['certified']}")
        print(f"  Compliance Score: {final_report['certification']['compliance_score']}")
        print()
        print("DETAILED SECTIONS:")
        print("  1. Validation Results - Comprehensive feature validation")
        print("  2. Points Calculation - Points earned for implemented features")
        print("  3. Quality Assessment - Code quality and security review")
        print("  4. Deployment Readiness - Deployment validation checks")
        print()
        print("VALIDATION HIGHLIGHTS:")
        core_passed = sum(1 for r in final_report['validation_results']['validation_results']
                         if r['category'] in ['Core Features', 'Constitution'] and r['passed'])
        core_total = sum(1 for r in final_report['validation_results']['validation_results']
                        if r['category'] in ['Core Features', 'Constitution'])
        print(f"  Core Features Passed: {core_passed}/{core_total}")

        bonus_passed = sum(1 for r in final_report['validation_results']['validation_results']
                          if r['category'] == 'Bonus Features' and r['passed'])
        bonus_total = sum(1 for r in final_report['validation_results']['validation_results']
                         if r['category'] == 'Bonus Features')
        print(f"  Bonus Features Passed: {bonus_passed}/{bonus_total}")

        quality_issues = (len(final_report['quality_assessment']['issues']['security']) +
                         len(final_report['quality_assessment']['issues']['performance']) +
                         len(final_report['quality_assessment']['issues']['style']))
        print(f"  Quality Issues Found: {quality_issues}")

        deployment_issues = final_report['deployment_readiness']['total_count'] - final_report['deployment_readiness']['passed_count']
        print(f"  Deployment Issues: {deployment_issues}")
        print()
        print("=" * 120)

        return final_report

    def save_final_report(self, output_path: str = "final_validation_report.json"):
        """Save the final validation report to a file."""
        final_report = self.generate_comprehensive_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)

        print(f"Final validation report saved to: {output_path}")
        return output_path


def main():
    """Main function to generate and print the final validation report."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate final validation report for the project")
    parser.add_argument("--project-root", "-p", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output file for final validation report (JSON)")
    parser.add_argument("--format", "-f", choices=["console", "json", "both"], default="console",
                       help="Output format")

    args = parser.parse_args()

    reporter = FinalValidationReport(project_root=args.project_root)

    if args.format in ["console", "both"]:
        report = reporter.print_final_report()
    else:
        report = reporter.generate_comprehensive_report()

    if args.output or args.format == "json":
        output_path = args.output or "final_validation_report.json"
        reporter.save_final_report(output_path)

    # Determine exit code based on overall status
    overall_status = report['executive_summary']['overall_status']
    if overall_status == "PASS":
        print(f"\n✓ Final validation report generated successfully! Project status: {overall_status}")
        sys.exit(0)
    elif overall_status == "CONDITIONAL_PASS":
        print(f"\n⚠️  Final validation report generated. Project status: {overall_status} - Ready with conditions")
        sys.exit(0)
    else:
        print(f"\n✗ Final validation report generated. Project status: {overall_status} - Needs improvements")
        sys.exit(1)


if __name__ == "__main__":
    main()