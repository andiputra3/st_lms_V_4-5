#!/usr/bin/env python3
"""
ST-LMS v4 — Comprehensive Test Runner
=====================================
Discovers and runs ALL test files. Reports results by category,
pass/fail counts, execution time, and memory usage.
Returns exit code 0 if all pass, 1 if any fail.
"""

import os
import sys
import time
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

TEST_DIR = os.path.join(REPO_ROOT, "stlms", "tests")

CATEGORY_NAMES = {
    "test_foundation": "Foundation Tests",
    "test_market_evolution": "Market Evolution Tests",
    "test_phase_03_12": "Phase 3-12 Tests",
    "test_phase_13_20": "Phase 13-20 Tests",
    "test_market": "Market Tests",
}


def discover_tests():
    """Discover all test modules in the test directory."""
    loader = unittest.TestLoader()
    suite = loader.discover(TEST_DIR, pattern="test_*.py")
    return suite


def categorize_results(suite):
    """Run tests and categorize results by test file."""
    runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w"))
    results = runner.run(suite)
    return results


def run_tests():
    """Run all tests with detailed reporting."""
    print()
    print("=" * 60)
    print("  ST-LMS v4 — Market Evolution Testing System")
    print("=" * 60)
    print()

    loader = unittest.TestLoader()
    suite = loader.discover(TEST_DIR, pattern="test_*.py")

    start_time = time.time()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    elapsed = time.time() - start_time

    print()
    print("=" * 60)
    print("  TEST RESULTS SUMMARY")
    print("=" * 60)
    print()

    all_passed = result.wasSuccessful()
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors
    skipped = len(result.skipped)

    print(f"  Total tests:    {total}")
    print(f"  Passed:         {passed}")
    print(f"  Failed:         {failures}")
    print(f"  Errors:         {errors}")
    print(f"  Skipped:        {skipped}")
    print(f"  Time:           {elapsed:.2f}s")
    print()

    if failures > 0:
        print(f"  FAILURES ({failures}):")
        print(f"  {'-' * 50}")
        for test, traceback in result.failures:
            test_id = str(test)
            print(f"  FAIL: {test_id}")
            lines = traceback.strip().split("\n")
            for line in lines[-3:]:
                print(f"    {line}")
            print()

    if errors > 0:
        print(f"  ERRORS ({errors}):")
        print(f"  {'-' * 50}")
        for test, traceback in result.errors:
            test_id = str(test)
            print(f"  ERROR: {test_id}")
            lines = traceback.strip().split("\n")
            for line in lines[-3:]:
                print(f"    {line}")
            print()

    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF)
        max_mb = usage.ru_maxrss / 1024
        print(f"  Peak memory:    {max_mb:.1f} MB")
    except Exception:
        pass

    print()
    print("=" * 60)
    if all_passed:
        print("  ST-LMS is healthy. All tests passed.")
    else:
        print("  ST-LMS needs attention. Some tests did not pass.")
    print("=" * 60)
    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_tests())
