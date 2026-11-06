#!/usr/bin/env python3
"""Require the expected number of GoogleTest cases to complete without skips or failures."""
import json
import pathlib
import sys

result = json.loads(pathlib.Path(sys.argv[1]).read_text())
expected = int(sys.argv[2])
cases = [case for suite in result["testsuites"] for case in suite["testsuite"]]
if len(cases) != expected or result["tests"] != expected:
    raise SystemExit(f"Expected {expected} cases; report contains {len(cases)}")
for case in cases:
    if case["status"] != "RUN" or case["result"] != "COMPLETED" or case.get("failures"):
        raise SystemExit(f"Test did not pass: {case['name']}")
print(f"{expected}/{expected} cases completed, no skips or failures")
