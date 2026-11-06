# Fork contribution preparation

The four submission branches start at upstream commit
`4d7e116c3ef259529a0917060e5b113834ed4894` and contain separate logical changes:

| Branch | Scope | Focused regression cases |
| --- | --- | ---: |
| `fix-sd-decoder-rows` | Reconstruct all undecomposed component rows | 72 |
| `fix-bmi2-test-registration` | Register BMI2 tests without AVX-512 constructors | 3 |
| `fix-logging-test-cleanup` | Release logging subprocess thread buffers | 3 |
| `test-four-component-decomposition` | Assert rejection of invalid decomposition | 30 |

The existing `fix-memory-checks` branch retains the combined investigation and
test tooling. Fork-only workflows and submission descriptions live on `main`,
outside the four proposed upstream patches.

## Reproduce the preflight

Run the manual **Fork contribution preflight** workflow on the fork's `main`.
It checks out each submission branch separately, records its source commit, and
retains build logs and GoogleTest JSON reports as workflow artifacts.
The `patch` and `compiler` inputs can select a single matrix cell for a rerun.

The matrix runs GCC and Clang on Ubuntu 24.04 and MSVC on Windows Server 2022.
Linux builds request `-Wall -Wextra -Werror`. Windows uses the project's
`Build/windows/build.bat 2022 release test` command. All cells run the complete
ordinary unit suite and require every applicable focused regression to complete
without skips. The logging subprocess fixture is POSIX-only: its Windows cell
builds and runs the complete Windows suite and explicitly verifies zero
applicable focused tests. GCC cells additionally use Valgrind; Clang cells use
ASan/UBSan.

The sanitizer executable links the selected real test source and production
objects, excluding unrelated AVX-512 test constructors. This lets each patch be
tested independently on AVX2 machines without adding the BMI2 registration fix
to the other submission branches. The complete ordinary unit suite still uses
the unmodified upstream unit-test target.

Clang's ordinary Release unit executable also hits the baseline AVX-512
registration crash before running tests on an AVX2 runner. Therefore the Clang
cells for the decoder, logging, and decomposition branches explicitly apply the
separate BMI2 registration change, commit
`66adfcd86bc5504d49fe49e74fb1e6960e300163`, before building. The workflow artifacts
retain the exact prerequisite patch and its commit. No production code is
overlaid. Submit the BMI2 registration change first; the other three patches
remain separate contributions. Clang results for those three branches include
this disclosed test-harness prerequisite.

## Contribution checks

`format-coding.sh` was run in exported copies of all four branches on
2026-11-06 with clang-format 21.1.8. Every changed C/C++ file already matched.
Black 26.10.1 found one missing blank line in the combined branch's Python
checker; that formatting-only correction preserves its Python AST. Markdown
lint found one table separator spacing issue in the combined branch's audit;
the separator was corrected without changing its content.

The first hosted GCC 13.3 preflight passed all 72 decoder pixel cases, but its
Debug Memcheck run found undefined reads when GoogleTest printed padding in
`SdTailCase` as raw bytes. The decoder submission and combined branches now
provide a field-based `PrintTo` overload. No pixel assertions were changed.

The [initial run](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42289623446)
is retained as failure evidence. The corrected runs verify all 12 required patch/compiler combinations.
[Per-cell results and source commits](validation-results.json) retain the
individual successful job links; older failed attempts remain visible.

The decoder branch documents row reconstruction in the existing decoder design
document. No proposed patch changes the public API or license. Existing
assertions remain intact. CPU-dependent tests and opt-in timing/diagnostic tests
retain their existing guards.

## Merge gates

The fork preflight is supplemental evidence. Upstream's own required CI and at
least one code-owner approval remain merge requirements from
[CONTRIBUTING.md](https://github.com/OpenVisualCloud/SVT-JPEG-XS/blob/4d7e116c3ef259529a0917060e5b113834ed4894/CONTRIBUTING.md).
No upstream pull request is opened by this workflow.

Draft descriptions:

- [Decoder rows](decoder-pr.md)
- [BMI2 registration](bmi2-pr.md)
- [Logging subprocess cleanup](logging-pr.md)
- [Invalid decomposition assertions](decomposition-pr.md)

## Verified results, 2026-11-06

All 12 patch/compiler combinations pass their complete ordinary unit suites.
The focused checks complete without skips:

| Patch | GCC and Valgrind | Clang and ASan/UBSan | Windows/MSVC |
| --- | ---: | ---: | ---: |
| Decoder rows | 72/72 | 72/72 | 72/72 |
| BMI2 registration | 3/3 | 3/3 | 3/3 |
| Logging subprocess cleanup | 3/3 | 3/3 | 0 applicable, full suite passes |
| Decomposition rejection | 30/30 | 30/30 | 30/30 |

Compilers: GCC 13.3 and Clang 18.1.3 on Ubuntu 24.04; MSVC 19.44 on
Windows Server 2022. Every focused Memcheck run reports zero errors. The logging
children have zero definite, indirect, or possible leaks. The Clang prerequisite
is disclosed above and recorded in the artifacts.

Full-suite CPU-dependent skips vary with the runner; the 47 pre-existing disabled
timing/diagnostic instances remain disabled. The two invalid-decomposition skips
are replaced by rejection assertions only on the decomposition branch. These
are GoogleTest execution counts, not an exhaustive claim about every legacy
fixture's internal parameter loop.

The original manual linter returned success without selecting files when the
dispatch SHA differed from the checked-out branch. The fork's manual mode now
uses an explicit contribution-file filter and validates the entire selection.
Real Super-linter checks pass for [fork tooling](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42294662786),
[combined tooling](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42294667048),
and [decoder documentation](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42294670932).
Black's log confirms two Python files checked on the fork tooling branch.
The pull-request lint mode retains its upstream behavior.
