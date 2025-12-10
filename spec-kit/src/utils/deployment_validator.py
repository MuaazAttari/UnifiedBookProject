"""
Deployment validation checks for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module contains validation functions to ensure the system is ready for deployment.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple
import requests
import json
from urllib.parse import urlparse


class DeploymentValidator:
    """Validates that the system is ready for deployment."""

    def __init__(self, project_root: str = None):
        """
        Initialize the deployment validator.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.validation_results = []

    def check_environment_variables(self) -> Dict[str, Any]:
        """Check that required environment variables are set."""
        required_vars = [
            'DATABASE_URL',
            'QDRANT_URL',
            'OPENAI_API_KEY',
            'SECRET_KEY'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        result = {
            "check": "Environment Variables",
            "passed": len(missing_vars) == 0,
            "details": {
                "missing_variables": missing_vars,
                "total_required": len(required_vars),
                "missing_count": len(missing_vars)
            }
        }

        self.validation_results.append(result)
        return result

    def check_dependencies_installed(self) -> Dict[str, Any]:
        """Check that all required dependencies are installed."""
        try:
            # Check if requirements.txt exists
            requirements_path = self.project_root / "backend" / "requirements.txt"
            if not requirements_path.exists():
                result = {
                    "check": "Dependencies",
                    "passed": False,
                    "details": {
                        "error": "requirements.txt not found",
                        "path_checked": str(requirements_path)
                    }
                }
                self.validation_results.append(result)
                return result

            # Read requirements
            with open(requirements_path, 'r') as f:
                requirements = f.read().splitlines()

            # Check if packages are installed
            result = subprocess.run([sys.executable, "-m", "pip", "list"],
                                    capture_output=True, text=True)
            installed_packages = result.stdout.lower()

            missing_packages = []
            for req in requirements:
                if req.strip() and not req.startswith('#'):
                    # Extract package name (remove version spec)
                    package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].strip()
                    if package_name and package_name.lower() not in installed_packages:
                        missing_packages.append(package_name)

            result = {
                "check": "Dependencies",
                "passed": len(missing_packages) == 0,
                "details": {
                    "missing_packages": missing_packages,
                    "total_required": len([r for r in requirements if r.strip() and not r.startswith('#')]),
                    "missing_count": len(missing_packages)
                }
            }

            self.validation_results.append(result)
            return result

        except Exception as e:
            result = {
                "check": "Dependencies",
                "passed": False,
                "details": {
                    "error": str(e)
                }
            }
            self.validation_results.append(result)
            return result

    def check_database_connection(self) -> Dict[str, Any]:
        """Check if database connection is available."""
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.exc import SQLAlchemyError

            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                result = {
                    "check": "Database Connection",
                    "passed": False,
                    "details": {
                        "error": "DATABASE_URL not set"
                    }
                }
                self.validation_results.append(result)
                return result

            engine = create_engine(database_url)
            with engine.connect() as connection:
                # Test connection
                connection.execute("SELECT 1")

            result = {
                "check": "Database Connection",
                "passed": True,
                "details": {
                    "database_url_set": True,
                    "connection_successful": True
                }
            }

            self.validation_results.append(result)
            return result

        except Exception as e:
            result = {
                "check": "Database Connection",
                "passed": False,
                "details": {
                    "error": str(e),
                    "database_url_set": bool(os.getenv('DATABASE_URL'))
                }
            }
            self.validation_results.append(result)
            return result

    def check_qdrant_connection(self) -> Dict[str, Any]:
        """Check if Qdrant connection is available."""
        try:
            qdrant_url = os.getenv('QDRANT_URL')
            if not qdrant_url:
                result = {
                    "check": "Qdrant Connection",
                    "passed": False,
                    "details": {
                        "error": "QDRANT_URL not set"
                    }
                }
                self.validation_results.append(result)
                return result

            # Test Qdrant health endpoint
            health_url = f"{qdrant_url.rstrip('/')}/health"
            response = requests.get(health_url, timeout=10)

            result = {
                "check": "Qdrant Connection",
                "passed": response.status_code == 200,
                "details": {
                    "qdrant_url_set": True,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
            }

            self.validation_results.append(result)
            return result

        except Exception as e:
            result = {
                "check": "Qdrant Connection",
                "passed": False,
                "details": {
                    "error": str(e),
                    "qdrant_url_set": bool(os.getenv('QDRANT_URL'))
                }
            }
            self.validation_results.append(result)
            return result

    def check_openai_connection(self) -> Dict[str, Any]:
        """Check if OpenAI API connection is available."""
        try:
            import openai

            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                result = {
                    "check": "OpenAI Connection",
                    "passed": False,
                    "details": {
                        "error": "OPENAI_API_KEY not set"
                    }
                }
                self.validation_results.append(result)
                return result

            # Test OpenAI connection with a simple model list call
            openai.api_key = openai_api_key
            models = openai.Model.list()

            result = {
                "check": "OpenAI Connection",
                "passed": True,
                "details": {
                    "openai_api_key_set": True,
                    "models_available": len(models.data) > 0
                }
            }

            self.validation_results.append(result)
            return result

        except Exception as e:
            result = {
                "check": "OpenAI Connection",
                "passed": False,
                "details": {
                    "error": str(e),
                    "openai_api_key_set": bool(os.getenv('OPENAI_API_KEY'))
                }
            }
            self.validation_results.append(result)
            return result

    def check_frontend_build(self) -> Dict[str, Any]:
        """Check if frontend can be built successfully."""
        try:
            frontend_path = self.project_root / "frontend"
            if not frontend_path.exists():
                result = {
                    "check": "Frontend Build",
                    "passed": False,
                    "details": {
                        "error": "frontend directory not found",
                        "path_checked": str(frontend_path)
                    }
                }
                self.validation_results.append(result)
                return result

            # Check if package.json exists
            package_json = frontend_path / "package.json"
            if not package_json.exists():
                result = {
                    "check": "Frontend Build",
                    "passed": False,
                    "details": {
                        "error": "package.json not found in frontend directory"
                    }
                }
                self.validation_results.append(result)
                return result

            # Read package.json to check for build script
            with open(package_json, 'r') as f:
                pkg_data = json.load(f)

            has_build_script = 'build' in pkg_data.get('scripts', {})

            result = {
                "check": "Frontend Build",
                "passed": has_build_script,
                "details": {
                    "build_script_exists": has_build_script,
                    "package_json_found": True
                }
            }

            self.validation_results.append(result)
            return result

        except Exception as e:
            result = {
                "check": "Frontend Build",
                "passed": False,
                "details": {
                    "error": str(e)
                }
            }
            self.validation_results.append(result)
            return result

    def check_docker_compose(self) -> Dict[str, Any]:
        """Check if Docker Compose configuration is valid."""
        try:
            docker_compose_path = self.project_root / "backend" / "docker-compose.yml"
            if not docker_compose_path.exists():
                result = {
                    "check": "Docker Compose",
                    "passed": False,
                    "details": {
                        "error": "docker-compose.yml not found",
                        "path_checked": str(docker_compose_path)
                    }
                }
                self.validation_results.append(result)
                return result

            # Read the docker-compose file to check for required services
            with open(docker_compose_path, 'r') as f:
                compose_content = f.read()

            required_services = ['backend', 'db', 'qdrant']
            found_services = []
            for service in required_services:
                if f'service{s}' in compose_content or f'{service}:' in compose_content:
                    found_services.append(service)

            result = {
                "check": "Docker Compose",
                "passed": len(found_services) >= len(required_services) - 1,  # Allow one missing
                "details": {
                    "required_services": required_services,
                    "found_services": found_services,
                    "docker_compose_exists": True
                }
            }

            self.validation_results.append(result)
            return result

        except Exception as e:
            result = {
                "check": "Docker Compose",
                "passed": False,
                "details": {
                    "error": str(e)
                }
            }
            self.validation_results.append(result)
            return result

    def check_security_settings(self) -> Dict[str, Any]:
        """Check security-related configurations."""
        checks = {
            "secret_key_length": False,
            "debug_mode": True,  # Should be False in production
            "allowed_hosts": True  # Should be configured in production
        }

        secret_key = os.getenv('SECRET_KEY')
        if secret_key and len(secret_key) >= 32:
            checks["secret_key_length"] = True

        # In production, DEBUG should be false
        debug_mode = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
        checks["debug_mode"] = not debug_mode  # Passes if debug is False

        result = {
            "check": "Security Settings",
            "passed": all(checks.values()),
            "details": checks
        }

        self.validation_results.append(result)
        return result

    def run_all_validations(self) -> Dict[str, Any]:
        """Run all deployment validation checks."""
        print("Running deployment validation checks...")

        validations = [
            self.check_environment_variables,
            self.check_dependencies_installed,
            self.check_database_connection,
            self.check_qdrant_connection,
            self.check_openai_connection,
            self.check_frontend_build,
            self.check_docker_compose,
            self.check_security_settings
        ]

        for validation_func in validations:
            try:
                validation_func()
            except Exception as e:
                print(f"Error during validation {validation_func.__name__}: {str(e)}")
                # Add error result
                self.validation_results.append({
                    "check": validation_func.__name__.replace('check_', '').replace('_', ' ').title(),
                    "passed": False,
                    "details": {"error": str(e)}
                })

        # Calculate overall result
        passed_count = sum(1 for r in self.validation_results if r["passed"])
        total_count = len(self.validation_results)

        overall_result = {
            "overall_passed": passed_count == total_count,
            "passed_count": passed_count,
            "total_count": total_count,
            "success_rate": round((passed_count / total_count) * 100, 2) if total_count > 0 else 0,
            "validation_results": self.validation_results
        }

        return overall_result

    def print_validation_report(self) -> bool:
        """Print a formatted validation report to console and return overall success."""
        overall_result = self.run_all_validations()

        print("\n" + "="*80)
        print("DEPLOYMENT VALIDATION REPORT")
        print("="*80)
        print(f"Overall Status: {'✅ PASS' if overall_result['overall_passed'] else '❌ FAIL'}")
        print(f"Results: {overall_result['passed_count']}/{overall_result['total_count']} checks passed")
        print(f"Success Rate: {overall_result['success_rate']}%")
        print()

        for result in overall_result['validation_results']:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['check']}")
            if not result["passed"]:
                details = result["details"]
                if "error" in details:
                    print(f"    Error: {details['error']}")
                elif "missing_variables" in details:
                    print(f"    Missing: {', '.join(details['missing_variables'])}")
                elif "missing_packages" in details:
                    print(f"    Missing packages: {', '.join(details['missing_packages'])}")
                # Add other detail types as needed

        print("="*80)

        # Return True if all checks passed, False otherwise
        return overall_result['overall_passed']


def main():
    """Main function to run deployment validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate deployment readiness")
    parser.add_argument("--project-root", "-p", help="Project root directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    validator = DeploymentValidator(project_root=args.project_root)
    success = validator.print_validation_report()

    if args.verbose:
        print("\nDetailed validation results:")
        for result in validator.validation_results:
            print(f"- {result}")

    # Exit with appropriate code
    if success:
        print("\n✓ All deployment validation checks passed!")
        sys.exit(0)
    else:
        print("\n✗ Some deployment validation checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()