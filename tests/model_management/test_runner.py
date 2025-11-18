#!/usr/bin/env python3
"""
Test Runner for Model Management System

This script runs the comprehensive test suite and generates a detailed report.
It can be run standalone or via pytest.

Usage:
    python test_runner.py                  # Run all tests
    python test_runner.py --verbose        # Verbose output
    pytest test_model_api.py              # Run with pytest
"""

import asyncio
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from test_model_api import run_all_tests


async def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Run Model Management Tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("\n" + "="*80)
    print("MODEL MANAGEMENT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Server: http://localhost:8000")
    print(f"Ollama Server: http://localhost:11434")
    print("="*80 + "\n")

    try:
        await run_all_tests()

        print("\n" + "="*80)
        print("TEST SUITE COMPLETED SUCCESSFULLY")
        print("="*80)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✅ All tests passed! Model management system is working correctly.\n")

        return 0

    except Exception as e:
        print("\n" + "="*80)
        print("TEST SUITE FAILED")
        print("="*80)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n❌ Test failed with error: {e}\n")

        if args.verbose:
            import traceback
            traceback.print_exc()

        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
