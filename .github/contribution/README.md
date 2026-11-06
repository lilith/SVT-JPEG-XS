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

The matrix runs GCC and Clang on Ubuntu 24.04 and MSVC on Windows Server 2022.
Linux builds request `-Wall -Wextra -Werror`. Windows uses the project's
`Build/windows/build.bat 2022 release test` command. All cells run the complete
ordinary unit suite and require every focused regression to complete without
skips. GCC cells additionally use Valgrind; Clang cells use ASan/UBSan.

The sanitizer executable links the selected real test source and production
objects, excluding unrelated AVX-512 test constructors. This lets each patch be
tested independently on AVX2 machines without adding the BMI2 registration fix
to the other submission branches. The complete ordinary unit suite still uses
the unmodified upstream unit-test target.

## Contribution checks

`format-coding.sh` was run in exported copies of all four branches on
2026-11-06 with clang-format 21.1.8. Every changed C/C++ file already matched.
Black 26.10.1 found one missing blank line in the combined branch's Python
checker; that formatting-only correction preserves its Python AST. Markdown
lint found one table separator spacing issue in the combined branch's audit;
the separator was corrected without changing its content.

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
