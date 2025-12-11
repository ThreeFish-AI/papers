#!/usr/bin/env python3
"""Test runner script for the agentic-ai-papers project."""

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


def main():
    """Main test runner."""
    project_root = Path(__file__).parent

    print(f"Project root: {project_root}")

    # Check if tests directory exists
    tests_dir = project_root / "tests" / "agents"
    if not tests_dir.exists():
        print(f"Error: Tests directory not found at {tests_dir}")
        return 1

    # Run unit tests
    success = run_command(
        [sys.executable, "-m", "pytest", "tests/agents/unit", "-v", "--tb=short"],
        "Unit Tests",
    )

    if not success:
        print("\n❌ Unit tests failed!")
        return 1

    # Run integration tests
    success = run_command(
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

    if not success:
        print("\n❌ Integration tests failed!")
        return 1

    # Generate coverage report
    success = run_command(
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

    if not success:
        print("\n⚠️ Coverage generation failed (but tests passed)")

    print("\n✅ All tests passed successfully!")
    print("\n📊 Coverage report generated in htmlcov/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
