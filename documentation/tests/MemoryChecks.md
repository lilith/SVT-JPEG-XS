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

## Full-suite follow-up

The full unit executable at `62ff8c39` (the first Sd correction) was checked with origin tracking
and full leak checks on 2026-11-06. GoogleTest reported 12,386 passed, 22 skipped and 47 disabled
tests. Memcheck reported zero errors and no allocations remaining in the parent. Valgrind masks
AVX2 GFNI on this host, accounting for one additional skip relative to the native run.
One logging child reported 64 possibly lost bytes from its joined thread container; the cleanup
above removes that report in the focused fixed run. No suppressions or relaxed assertions were used.

The updated fork at `9623b216` passed the full native suite: 12,426 passed, 18 skipped and 47 disabled.
The fixed row output, helper registration and logging subprocesses passed 78/78 under Memcheck and
AddressSanitizer/UBSan. The original full sweep and the focused fixed checks have distinct source
revisions; these results do not claim a second full Memcheck sweep of the updated binary.

The [reported-skip and disabled-case audit](SkippedAndDisabled.md) replaces the two invalid
configuration skips with rejection assertions. The full native suite then passes 12,428 tests with
16 explicit hardware skips and 47 opt-in benchmark/diagnostic instances. All 16 explicitly skipped
ISA tests plus AVX2 GFNI complete under SDE emulation (17/17, no skips).
