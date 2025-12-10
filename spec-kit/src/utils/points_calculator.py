"""
Points calculator for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module calculates points based on implemented features and requirements.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json


class PointsCalculator:
    """Calculates points based on implemented features."""

    def __init__(self, project_root: str = None):
        """
        Initialize the points calculator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.feature_points = {
            # Core features (P1 - Required)
            "textbook_import": {"base_points": 20, "completed": False},
            "docusaurus_config": {"base_points": 15, "completed": False},
            "rag_chatbot_backend": {"base_points": 25, "completed": False},
            "frontend_chatbot": {"base_points": 15, "completed": False},
            "authentication_system": {"base_points": 20, "completed": False},
            "user_questionnaire": {"base_points": 10, "completed": False},
            "deployment_github_pages": {"base_points": 15, "completed": False},

            # Bonus features (P2-P3)
            "chapter_personalization": {"base_points": 0, "bonus_points": 20, "completed": False},  # Bonus
            "urdu_translation": {"base_points": 0, "bonus_points": 25, "completed": False},  # Bonus
            "advanced_rag_features": {"base_points": 0, "bonus_points": 15, "completed": False},  # Bonus
            "enhanced_ui_ux": {"base_points": 0, "bonus_points": 10, "completed": False},  # Bonus
            "performance_optimization": {"base_points": 0, "bonus_points": 15, "completed": False},  # Bonus
            "comprehensive_testing": {"base_points": 0, "bonus_points": 20, "completed": False},  # Bonus
        }

    def check_file_exists(self, relative_path: str) -> bool:
        """Check if a file exists at the given relative path from project root."""
        file_path = self.project_root / relative_path
        return file_path.exists()

    def check_file_contains(self, relative_path: str, content_patterns: List[str]) -> bool:
        """Check if a file exists and contains specified content patterns."""
        file_path = self.project_root / relative_path
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            return any(pattern.lower() in content for pattern in content_patterns)
        except:
            return False

    def calculate_textbook_import_points(self) -> Tuple[bool, int]:
        """Calculate points for textbook import feature."""
        # Check for required files and functionality
        required_files = [
            "src/services/chapter_service.py",
            "src/api/v1/chapters.py",
            "src/utils/textbook_importer.py",
            "src/utils/frontmatter_validator.py"
        ]

        has_required_files = all(self.check_file_exists(f) for f in required_files)

        # Check for import functionality in API
        has_import_endpoint = self.check_file_contains(
            "src/api/v1/chapters.py",
            ["import", "upload", "create_multiple", "bulk"]
        )

        completed = has_required_files and has_import_endpoint
        points = self.feature_points["textbook_import"]["base_points"] if completed else 0

        return completed, points

    def calculate_docusaurus_config_points(self) -> Tuple[bool, int]:
        """Calculate points for Docusaurus configuration."""
        # Check for Docusaurus files
        required_files = [
            "my-website/docusaurus.config.js",
            "my-website/package.json",
            "my-website/src/pages",
            "my-website/docs"
        ]

        has_required_files = all(self.check_file_exists(f) for f in required_files)

        # Check for proper configuration
        has_proper_config = self.check_file_contains(
            "my-website/docusaurus.config.js",
            ["title", "tagline", "url", "baseUrl", "organizationName", "projectName"]
        )

        completed = has_required_files and has_proper_config
        points = self.feature_points["docusaurus_config"]["base_points"] if completed else 0

        return completed, points

    def calculate_rag_backend_points(self) -> Tuple[bool, int]:
        """Calculate points for RAG chatbot backend."""
        # Check for RAG backend components
        required_files = [
            "src/services/embedding_service.py",
            "src/services/openai_service.py",
            "src/api/v1/chat.py",
            "src/models/chat_session.py"
        ]

        has_required_files = all(self.check_file_exists(f) for f in required_files)

        # Check for RAG functionality in API
        has_rag_functionality = self.check_file_contains(
            "src/api/v1/chat.py",
            ["rag", "query", "context", "response", "similarity"]
        )

        completed = has_required_files and has_rag_functionality
        points = self.feature_points["rag_chatbot_backend"]["base_points"] if completed else 0

        return completed, points

    def calculate_frontend_chatbot_points(self) -> Tuple[bool, int]:
        """Calculate points for frontend chatbot integration."""
        # Check for frontend chatbot components
        required_files = [
            "my-website/src/components/ChatWidget",
            "my-website/src/components/ChatWidget/index.js",
            "my-website/src/css/chat.css"
        ]

        has_required_files = any(self.check_file_exists(f) for f in required_files)

        # Check for chat functionality in components
        has_chat_component = any(self.check_file_contains(f, ["chat", "message", "response", "input"])
                                for f in required_files if self.check_file_exists(f))

        completed = has_required_files and has_chat_component
        points = self.feature_points["frontend_chatbot"]["base_points"] if completed else 0

        return completed, points

    def calculate_authentication_points(self) -> Tuple[bool, int]:
        """Calculate points for authentication system."""
        # Check for auth components
        required_files = [
            "src/services/auth_service.py",
            "src/api/v1/auth.py",
            "src/models/user.py",
            "src/utils/auth.py"
        ]

        has_required_files = all(self.check_file_exists(f) for f in required_files)

        # Check for auth functionality
        has_auth_functionality = (self.check_file_contains("src/api/v1/auth.py", ["login", "register", "profile"]) and
                                  self.check_file_contains("src/services/auth_service.py", ["authenticate", "create_user", "verify"]))

        completed = has_required_files and has_auth_functionality
        points = self.feature_points["authentication_system"]["base_points"] if completed else 0

        return completed, points

    def calculate_questionnaire_points(self) -> Tuple[bool, int]:
        """Calculate points for user questionnaire."""
        # Check for questionnaire components
        has_questionnaire = (self.check_file_exists("src/api/v1/users.py") and
                           self.check_file_contains("src/api/v1/users.py", ["questionnaire", "background", "profile"]))

        points = self.feature_points["user_questionnaire"]["base_points"] if has_questionnaire else 0
        return has_questionnaire, points

    def calculate_deployment_points(self) -> Tuple[bool, int]:
        """Calculate points for GitHub Pages deployment."""
        # Check for deployment configuration
        required_files = [
            ".github/workflows/ci-cd.yml",
            "DEPLOYMENT.md",
            "backend/docker-compose.yml"
        ]

        has_deployment_config = all(self.check_file_exists(f) for f in required_files)

        # Check for deployment scripts
        has_deploy_script = self.check_file_contains("frontend/package.json", ["deploy", "gh-pages"])

        completed = has_deployment_config or has_deploy_script
        points = self.feature_points["deployment_github_pages"]["base_points"] if completed else 0

        return completed, points

    def calculate_personalization_points(self) -> Tuple[bool, int]:
        """Calculate bonus points for chapter personalization."""
        # Check for personalization components
        required_files = [
            "src/services/personalization_service.py",
            "src/api/v1/personalization.py",
            "src/models/personalization_profile.py"
        ]

        has_required_files = all(self.check_file_exists(f) for f in required_files)

        # Check for personalization functionality
        has_personalization = (has_required_files and
                              self.check_file_contains("src/services/personalization_service.py", ["personalize", "preference", "adjust"]))

        points = self.feature_points["chapter_personalization"]["bonus_points"] if has_personalization else 0
        return has_personalization, points

    def calculate_translation_points(self) -> Tuple[bool, int]:
        """Calculate bonus points for Urdu translation."""
        # Check for translation components
        required_files = [
            "src/services/translation_service.py",
            "src/api/v1/translation.py",
            "src/models/translation_cache.py",
            "my-website/src/components/Translation"
        ]

        has_required_files = all(self.check_file_exists(f) for f in required_files)

        # Check for translation functionality
        has_translation = (has_required_files and
                          self.check_file_contains("src/services/translation_service.py", ["translate", "urdu", "language"]) and
                          self.check_file_contains("my-website/src/components/Translation/index.js", ["translate", "button"]))

        points = self.feature_points["urdu_translation"]["bonus_points"] if has_translation else 0
        return has_translation, points

    def calculate_advanced_rag_points(self) -> Tuple[bool, int]:
        """Calculate bonus points for advanced RAG features."""
        # Check for advanced RAG components
        has_advanced_rag = (self.check_file_exists("src/services/embedding_service.py") and
                           self.check_file_contains("src/services/embedding_service.py", ["similarity", "retrieval", "context"]))

        points = self.feature_points["advanced_rag_features"]["bonus_points"] if has_advanced_rag else 0
        return has_advanced_rag, points

    def calculate_enhanced_ux_points(self) -> Tuple[bool, int]:
        """Calculate bonus points for enhanced UI/UX."""
        # Check for enhanced UI components
        has_enhanced_ux = (self.check_file_exists("my-website/src/css/custom.css") and
                          self.check_file_contains("my-website/src/css/custom.css", ["responsive", "theme", "design"]))

        points = self.feature_points["enhanced_ui_ux"]["bonus_points"] if has_enhanced_ux else 0
        return has_enhanced_ux, points

    def calculate_performance_points(self) -> Tuple[bool, int]:
        """Calculate bonus points for performance optimization."""
        # Check for performance optimization
        has_performance = (self.check_file_exists("tests/test_rag_performance.py") and
                          self.check_file_contains("tests/test_rag_performance.py", ["performance", "benchmark", "response_time"]))

        points = self.feature_points["performance_optimization"]["bonus_points"] if has_performance else 0
        return has_performance, points

    def calculate_testing_points(self) -> Tuple[bool, int]:
        """Calculate bonus points for comprehensive testing."""
        # Count test files
        test_dir = self.project_root / "tests"
        if test_dir.exists():
            test_files = list(test_dir.rglob("test_*.py"))
            has_comprehensive_testing = len(test_files) >= 5  # At least 5 test files
        else:
            has_comprehensive_testing = False

        points = self.feature_points["comprehensive_testing"]["bonus_points"] if has_comprehensive_testing else 0
        return has_comprehensive_testing, points

    def calculate_all_points(self) -> Dict[str, Any]:
        """Calculate points for all features."""
        results = {}

        # Core features
        results["textbook_import"] = self.calculate_textbook_import_points()
        results["docusaurus_config"] = self.calculate_docusaurus_config_points()
        results["rag_chatbot_backend"] = self.calculate_rag_backend_points()
        results["frontend_chatbot"] = self.calculate_frontend_chatbot_points()
        results["authentication_system"] = self.calculate_authentication_points()
        results["user_questionnaire"] = self.calculate_questionnaire_points()
        results["deployment_github_pages"] = self.calculate_deployment_points()

        # Bonus features
        results["chapter_personalization"] = self.calculate_personalization_points()
        results["urdu_translation"] = self.calculate_translation_points()
        results["advanced_rag_features"] = self.calculate_advanced_rag_points()
        results["enhanced_ui_ux"] = self.calculate_enhanced_ux_points()
        results["performance_optimization"] = self.calculate_performance_points()
        results["comprehensive_testing"] = self.calculate_testing_points()

        return results

    def generate_points_report(self) -> Dict[str, Any]:
        """Generate a comprehensive points report."""
        results = self.calculate_all_points()

        core_points = 0
        bonus_points = 0
        total_possible_core = 0
        total_possible_bonus = 0
        completed_features = 0
        total_features = len(results)

        feature_details = {}

        for feature, (completed, points) in results.items():
            feature_info = self.feature_points[feature]
            is_bonus = "bonus_points" in feature_info

            if is_bonus:
                total_possible_bonus += feature_info["bonus_points"]
                if completed:
                    bonus_points += points
            else:
                total_possible_core += feature_info["base_points"]
                if completed:
                    core_points += points

            if completed:
                completed_features += 1

            feature_details[feature] = {
                "completed": completed,
                "points_earned": points,
                "possible_points": feature_info.get("bonus_points", feature_info["base_points"]),
                "is_bonus": is_bonus,
                "category": "Bonus" if is_bonus else "Core"
            }

        total_points = core_points + bonus_points
        total_possible = total_possible_core + total_possible_bonus
        completion_percentage = (completed_features / total_features) * 100 if total_features > 0 else 0
        points_percentage = (total_points / total_possible) * 100 if total_possible > 0 else 0

        report = {
            "summary": {
                "core_points_earned": core_points,
                "core_points_possible": total_possible_core,
                "bonus_points_earned": bonus_points,
                "bonus_points_possible": total_possible_bonus,
                "total_points_earned": total_points,
                "total_points_possible": total_possible,
                "completed_features": completed_features,
                "total_features": total_features,
                "completion_percentage": round(completion_percentage, 2),
                "points_percentage": round(points_percentage, 2)
            },
            "features": feature_details,
            "grading": self._determine_grade(points_percentage)
        }

        return report

    def _determine_grade(self, points_percentage: float) -> str:
        """Determine letter grade based on points percentage."""
        if points_percentage >= 95:
            return "A+"
        elif points_percentage >= 90:
            return "A"
        elif points_percentage >= 85:
            return "A-"
        elif points_percentage >= 80:
            return "B+"
        elif points_percentage >= 75:
            return "B"
        elif points_percentage >= 70:
            return "B-"
        elif points_percentage >= 65:
            return "C+"
        elif points_percentage >= 60:
            return "C"
        elif points_percentage >= 50:
            return "C-"
        else:
            return "F"

    def print_points_report(self):
        """Print a formatted points report to console."""
        report = self.generate_points_report()

        print("=" * 100)
        print("POINTS CALCULATION REPORT - UNIFIED PHYSICAL AI & HUMANOID ROBOTICS LEARNING BOOK")
        print("=" * 100)
        print(f"Completion: {report['summary']['completed_features']}/{report['summary']['total_features']} features")
        print(f"Completion Rate: {report['summary']['completion_percentage']}%")
        print(f"Points Earned: {report['summary']['total_points_earned']}/{report['summary']['total_points_possible']}")
        print(f"Points Percentage: {report['summary']['points_percentage']}%")
        print(f"Grade: {report['grading']}")
        print()
        print("CORE FEATURES (Required):")
        print("-" * 50)
        core_features = {k: v for k, v in report['features'].items() if not v['is_bonus']}
        for feature, details in core_features.items():
            status = "✅" if details['completed'] else "❌"
            print(f"{status} {feature.replace('_', ' ').title()}: {details['points_earned']}/{details['possible_points']} points")

        print(f"\nCore Points Earned: {report['summary']['core_points_earned']}/{report['summary']['core_points_possible']}")
        print()
        print("BONUS FEATURES:")
        print("-" * 50)
        bonus_features = {k: v for k, v in report['features'].items() if v['is_bonus']}
        for feature, details in bonus_features.items():
            status = "✅" if details['completed'] else "❌"
            print(f"{status} {feature.replace('_', ' ').title()}: {details['points_earned']}/{details['possible_points']} points")

        print(f"\nBonus Points Earned: {report['summary']['bonus_points_earned']}/{report['summary']['bonus_points_possible']}")
        print()
        print("=" * 100)

        return report

    def save_points_report(self, output_path: str = "points_report.json"):
        """Save the points report to a file."""
        report = self.generate_points_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"Points report saved to: {output_path}")
        return output_path


def main():
    """Main function to calculate and print points report."""
    import argparse

    parser = argparse.ArgumentParser(description="Calculate points for project features")
    parser.add_argument("--project-root", "-p", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output file for points report (JSON)")
    parser.add_argument("--format", "-f", choices=["console", "json", "both"], default="console",
                       help="Output format")

    args = parser.parse_args()

    calculator = PointsCalculator(project_root=args.project_root)

    if args.format in ["console", "both"]:
        report = calculator.print_points_report()
    else:
        report = calculator.generate_points_report()

    if args.output or args.format == "json":
        output_path = args.output or "points_report.json"
        calculator.save_points_report(output_path)

    # Exit with success
    print(f"\n✓ Points calculation completed!")
    sys.exit(0)


if __name__ == "__main__":
    main()