"""Validate a focused contribution without adding tooling to its source branch."""

import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    source = Path(sys.argv[1]).resolve()
    platform, patch = sys.argv[2:4]
    automation = Path(__file__).resolve().parent
    results = source / "preflight-results"
    results.mkdir(exist_ok=True)
    cases = {
        "fix-sd-decoder-rows": (
            "TestDecoderSdTail.cc",
            "*DecoderSdTail*",
            72,
        ),
        "fix-bmi2-test-registration": (
            "TestPackUnpackHelpers.cc",
            "unpack_planes_to_lanes.*:pack_group_planes_pdep.*:pack_groups_masked_pdep.*",
            3,
        ),
        "fix-logging-test-cleanup": (
            "TestSvtLog.cc",
            "LogCallback.*:LogDefault.*",
            3,
        ),
        "test-four-component-decomposition": (
            "TestFourComponentAlpha.cc",
            "*FourComponentEncodeParam*",
            30,
        ),
    }
    test_file, test_filter, expected = cases[patch]
    if platform == "windows" and patch == "fix-logging-test-cleanup":
        # Upstream encloses this entire POSIX subprocess fixture in !_WIN32.
        # Still build and run the complete Windows suite, and explicitly verify
        # that the focused filter has zero applicable tests on that platform.
        expected = 0
        print("Windows: logging subprocess fixture has 0 applicable tests", flush=True)

    def run(args, name, cwd=source, env=None):
        print("+", subprocess.list2cmdline(list(map(str, args))), flush=True)
        with (results / f"{name}.log").open("w") as log:
            process = subprocess.Popen(
                list(map(str, args)),
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                errors="replace",
            )
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
            if process.wait():
                raise RuntimeError(
                    f"{name} failed with exit status {process.returncode}"
                )

    def check_result(name):
        data = json.loads((results / f"{name}.json").read_text())
        assert data["tests"] == expected, data
        assert data["failures"] == 0, data
        assert data["disabled"] == 0, data
        for suite in data["testsuites"]:
            for case in suite["testsuite"]:
                assert case["result"] == "COMPLETED", case

    run(["git", "rev-parse", "HEAD"], "source-revision")
    run(["cmake", "--version"], "cmake-version")
    env = os.environ.copy()
    suffix = ".exe" if platform == "windows" else ""
    if platform == "windows":
        run(
            ["cmd", "/c", "build.bat", "2022", "release", "test"],
            "build",
            cwd=source / "Build/windows",
        )
        # The batch script can return success after an MSBuild failure. Check
        # the build through CMake directly as well, so its exit code is binding.
        run(
            [
                "cmake",
                "--build",
                source / "Build/windows",
                "--config",
                "Release",
                "--parallel",
                "2",
            ],
            "verify-build",
        )
        binary = source / "Bin/Release/SvtJpegxsUnitTests.exe"
    else:
        env["CC"] = "clang" if platform == "clang" else "gcc"
        env["CXX"] = "clang++" if platform == "clang" else "g++"
        run([env["CC"], "--version"], "compiler-version")
        run(
            [
                "cmake",
                "-S",
                source,
                "-B",
                "preflight-build",
                "-G",
                "Ninja",
                "-DBUILD_TESTING=ON",
                "-DCMAKE_BUILD_TYPE=Release",
                "-DCMAKE_C_FLAGS=-Wall -Wextra -Werror",
                "-DCMAKE_CXX_FLAGS=-Wall -Wextra -Werror",
            ],
            "configure",
            env=env,
        )
        run(
            ["cmake", "--build", "preflight-build", "--parallel", "2"], "build", env=env
        )
        binary = source / "Bin/Release/SvtJpegxsUnitTests"
    run([binary, f"--gtest_output=json:{results / 'full.json'}"], "full-tests")
    run(
        [
            binary,
            f"--gtest_filter={test_filter}",
            f"--gtest_output=json:{results / 'focused.json'}",
        ],
        "focused-tests",
    )
    check_result("focused")
    if platform != "windows":
        # Only selected real tests enter the sanitized executable. Unrelated
        # baseline AVX-512 test constructors can execute before CPU dispatch.
        sanitizer = platform == "clang"
        flags = (
            "-fsanitize=address,undefined -fno-omit-frame-pointer" if sanitizer else ""
        )
        build = "preflight-sanitized" if sanitizer else "preflight-focused"
        run(
            [
                "cmake",
                "-S",
                source,
                "-B",
                build,
                "-G",
                "Ninja",
                "-DBUILD_TESTING=ON",
                "-DCMAKE_BUILD_TYPE=Debug",
                f"-DCMAKE_PROJECT_INCLUDE={automation / 'focused.cmake'}",
                f"-DCONTRIBUTION_SOURCE=tests/UnitTests/{test_file}",
                f"-DCMAKE_C_FLAGS={flags}",
                f"-DCMAKE_CXX_FLAGS={flags}",
                f"-DCMAKE_OUTPUT_DIRECTORY={source / build / 'bin'}",
            ],
            "focused-configure",
            env=env,
        )
        run(
            [
                "cmake",
                "--build",
                build,
                "--target",
                "ContributionTests",
                "--parallel",
                "2",
            ],
            "focused-build",
            env=env,
        )
        command = [source / build / "bin" / f"ContributionTests{suffix}"]
        if not sanitizer:
            command = [
                "valgrind",
                "--error-exitcode=99",
                "--leak-check=full",
                "--show-leak-kinds=all",
                "--errors-for-leak-kinds=definite,indirect,possible",
                *command,
            ]
        run(
            [
                *command,
                f"--gtest_filter={test_filter}",
                f"--gtest_output=json:{results / 'instrumented.json'}",
            ],
            "instrumented-tests",
            env=env,
        )
        check_result("instrumented")


if __name__ == "__main__":
    main()
