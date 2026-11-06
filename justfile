# Optional developer shortcuts; invoke resource limits through the calling environment.
set shell := ["bash", "-euo", "pipefail", "-c"]

unit-build build_dir="Build/linux/memcheck" jobs="4":
    mkdir -p "{{build_dir}}"
    cmake -S . -B "{{build_dir}}" -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_FLAGS_RELEASE="-O3 -DNDEBUG -g" -DCMAKE_CXX_FLAGS_RELEASE="-O3 -DNDEBUG -g" -DBUILD_TESTING=ON -DBUILD_APPS=OFF -DNATIVE=OFF -DJPEGXS_LTO=OFF -DCMAKE_OUTPUT_DIRECTORY="$(cd "{{build_dir}}" && pwd)/bin"
    cmake --build "{{build_dir}}" --target SvtJpegxsUnitTests --parallel "{{jobs}}"

unit-sanitizer-build build_dir="Build/linux/memcheck-sanitized" jobs="4":
    mkdir -p "{{build_dir}}"
    cmake -S . -B "{{build_dir}}" -G Ninja -DCMAKE_BUILD_TYPE=Debug -DSANITIZER=Address -DCMAKE_C_FLAGS="-fsanitize=undefined -fno-omit-frame-pointer" -DCMAKE_CXX_FLAGS="-fsanitize=undefined -fno-omit-frame-pointer" -DBUILD_TESTING=ON -DBUILD_APPS=OFF -DNATIVE=OFF -DJPEGXS_LTO=OFF -DCMAKE_OUTPUT_DIRECTORY="$(cd "{{build_dir}}" && pwd)/bin"
    cmake --build "{{build_dir}}" --target SvtJpegxsUnitTests --parallel "{{jobs}}"

unit binary="Build/linux/memcheck/bin/SvtJpegxsUnitTests" filter="*":
    "{{binary}}" '--gtest_filter={{filter}}'

# Logs are retained, and memory errors or definite/indirect leaks fail the command.
memcheck binary="Build/linux/memcheck/bin/SvtJpegxsUnitTests" log_dir="Build/linux/memcheck/logs" filter="*":
    mkdir -p "{{log_dir}}"
    if test -e "{{log_dir}}/memcheck.log" || test -e "{{log_dir}}/unit.log"; then echo "Choose a new log directory to preserve existing results" >&2; exit 2; fi
    valgrind --error-exitcode=99 --track-origins=yes --leak-check=full --show-leak-kinds=all --errors-for-leak-kinds=definite,indirect --num-callers=30 --error-limit=no '--log-file={{log_dir}}/memcheck.log' "{{binary}}" '--gtest_filter={{filter}}' > "{{log_dir}}/unit.log" 2>&1

# Existing timing benchmarks and print diagnostics remain opt-in.
unit-disabled binary="Build/linux/memcheck/bin/SvtJpegxsUnitTests" filter="*DISABLED_*":
    "{{binary}}" --gtest_also_run_disabled_tests '--gtest_filter={{filter}}'

# Execute a caller-selected ISA set under Sapphire Rapids emulation; require every case to run.
unit-sde sde binary filter log_dir expected:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p '{{log_dir}}'
    log_dir=$(cd '{{log_dir}}' && pwd)
    if test -e "$log_dir/unit.log" || test -e "$log_dir/results.json"; then
        echo "Choose a new log directory to preserve existing results" >&2
        exit 2
    fi
    '{{sde}}' -spr -- '{{binary}}' '--gtest_filter={{filter}}' "--gtest_output=json:$log_dir/results.json" > "$log_dir/unit.log" 2>&1
    python3 tests/scripts/check_gtest_results.py "$log_dir/results.json" '{{expected}}'
