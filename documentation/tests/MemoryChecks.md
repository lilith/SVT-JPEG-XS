# Memory checks for decoder row reconstruction and helper tests

The optional root `justfile` provides repeatable unit-test and Memcheck commands.
CMake, Ninja, GoogleTest, and Valgrind perform the checks; `just` only supplies command shortcuts.
Run each build or check sequentially with resource limits appropriate to your machine.
Set `TMPDIR` to an existing scratch directory on disk before running tests.

```sh
just unit-build
just unit
just memcheck
```

`memcheck` enables origin tracking, full leak checks, and an error exit status for memory errors
and definite/indirect leaks. It retains both test output and the Valgrind report under
`Build/linux/memcheck/logs/`. Choose a new log directory for another run; existing results are preserved.
The existing CPU checks and disabled tests still apply, so inspect GoogleTest's summary for coverage.

A focused check of the decoder rows, BMI2 helpers, and logging subprocesses:

```sh
just memcheck Build/linux/memcheck/bin/SvtJpegxsUnitTests Build/linux/memcheck/focused-logs '*DecoderSdTail*:unpack_planes_to_lanes.*:pack_group_planes_pdep.*:pack_groups_masked_pdep.*:LogCallback.*:LogDefault.*'
just unit-sanitizer-build
ASAN_OPTIONS=halt_on_error=1:detect_leaks=1 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 just unit Build/linux/memcheck-sanitized/bin/SvtJpegxsUnitTests '*DecoderSdTail*:unpack_planes_to_lanes.*:pack_group_planes_pdep.*:pack_groups_masked_pdep.*:LogCallback.*:LogDefault.*'
```

## Regression coverage

- `DecoderSdTail.ReconstructsEveryRowAndPreservesStridePadding`: full and partial final precincts
  with whole-frame inverse RCT. The temporary frame buffer is poisoned; every pixel and padding sample
  is checked against an analytic RCT result. Ten of 36 cases fail before the final-precinct fix.
- `DecoderSdTail.WithoutColourTransformWritesEveryRow`: undecomposed components in the per-precinct
  output path. Coefficients vary by row and column, and strided output starts with poison values.
  Twenty-four of 36 cases fail before all precinct rows are written.
- BMI2 helper tests: compile registration with the baseline unit-test flags. Function-scoped BMI2
  attributes provide PDEP/PEXT. Compiling GoogleTest registration with AVX-512 can cause sanitizer
  startup to execute unsupported instructions before any runtime CPU check on an AVX2-only machine.
- Logging subprocesses: use GoogleTest's temporary-directory selection and destroy the thread
  container before `_exit()`. The logging assertions and message counts are unchanged.

On 2026-11-06 the focused set passed 78/78 under Valgrind and AddressSanitizer/UBSan. The Valgrind
parent process freed all allocations; the logging children had no definite, indirect, or possible leaks.
