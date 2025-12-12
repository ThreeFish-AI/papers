#!/usr/bin/env python3
"""Test runner script for the agentic-ai-papers project."""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the result."""
    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("STDERR:", result.stderr, file=sys.stderr)

    return result.returncode == 0


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run tests for the agentic-ai-papers project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py              # Run all tests (default)
  python run_tests.py unit         # Run only unit tests
  python run_tests.py integration  # Run only integration tests
  python run_tests.py coverage     # Generate only coverage report
        """,
    )

    parser.add_argument(
        "test_type",
        nargs="?",
        choices=["unit", "integration", "coverage", "all"],
        default="all",
        help="Type of test to run (default: all)",
    )

    return parser.parse_args()


def run_unit_tests():
    """Run unit tests only."""
    return run_command(
        [sys.executable, "-m", "pytest", "tests/agents/unit", "-v", "--tb=short"],
        "Unit Tests",
    )


def run_integration_tests():
    """Run integration tests only."""
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/agents/integration",
            "-v",
            "--tb=short",
        ],
        "Integration Tests",
    )


def generate_coverage_report():
    """Generate coverage report only."""
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/agents",
            "--cov=agents",
            "--cov-report=term-missing",
            "--cov-report=html",
        ],
        "Coverage Report",
    )


def main():
    """Main test runner."""
    # Parse arguments
    args = parse_arguments()

    # Get script location and project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Store and change working directory
    original_cwd = os.getcwd()
    os.chdir(project_root)

    try:
        print(f"Project root: {project_root}")

        # Check if tests directory exists
        if not script_dir.exists():
            print(f"Error: Tests directory not found at {script_dir}")
            return 1

        success = True

        # Run tests based on argument
        if args.test_type in ["unit", "all"]:
            success = run_unit_tests()
            if not success:
                if args.test_type == "unit":
                    print("\n❌ Unit tests failed!")
                    return 1
                else:
                    print("\n❌ Unit tests failed!")
                    return 1

        if args.test_type in ["integration", "all"]:
            success = run_integration_tests()
            if not success:
                if args.test_type == "integration":
                    print("\n❌ Integration tests failed!")
                    return 1
                else:
                    print("\n❌ Integration tests failed!")
                    return 1

        if args.test_type in ["coverage", "all"]:
            success = generate_coverage_report()
            if not success:
                if args.test_type == "coverage":
                    print("\n⚠️ Coverage generation failed!")
                    return 1
                else:
                    # For "all" mode, coverage failure is not critical
                    print("\n⚠️ Coverage generation failed (but tests passed)")

        # Print success message based on test type
        if args.test_type == "all":
            print("\n✅ All tests passed successfully!")
            print("\n📊 Coverage report generated in htmlcov/index.html")
        else:
            print(f"\n✅ {args.test_type.title()} tests completed successfully!")
            if args.test_type == "coverage":
                print("\n📊 Coverage report generated in htmlcov/index.html")

        return 0

    finally:
        # Restore original directory
        os.chdir(original_cwd)


if __name__ == "__main__":
    sys.exit(main())
