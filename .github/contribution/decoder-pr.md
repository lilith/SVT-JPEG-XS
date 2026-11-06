# fix(decoder): reconstruct every undecomposed component row

Two reconstruction paths omit rows from components left undecomposed by `Sd`.
With whole-frame inverse colour transformation, an exact-multiple final precinct
uses a zero remainder as its copy height. Without colour transformation, the
per-precinct path converts only the first row of a multi-row precinct.

Use the remaining image height to bound the final copy, and convert every row in
the per-precinct path. The decoder design document now describes this behavior.

The regression checks every sample and strided padding in 72 cases: full and
partial final precincts, vertical decomposition 0 through 2, 8-bit and 12-bit
output, with and without colour transformation. Before their respective fixes,
10 of the first 36 cases and 24 of the second 36 cases fail.

Base: `4d7e116c3ef259529a0917060e5b113834ed4894` (SVT-JPEG-XS 0.11.0).

Reproduce after configuring with `BUILD_TESTING=ON`:

```sh
Bin/Release/SvtJpegxsUnitTests --gtest_filter='*DecoderSdTail*'
```

Validation on 2026-11-06: full unit suites pass with GCC 13.3 and Clang 18.1 on
Ubuntu 24.04 and MSVC 19.44 on Windows Server 2022. Linux builds use
`-Wall -Wextra -Werror`. All 72 focused cases pass under Valgrind (zero errors)
and ASan/UBSan. Formatting matches `format-coding.sh`; no public API changes.

The Clang full-suite check explicitly includes the separate BMI2 test-registration
prerequisite, commit `66adfcd86bc5504d49fe49e74fb1e6960e300163`, to avoid its baseline
startup crash on an AVX2 runner. That prerequisite changes tests only and is not
included in this patch.

Evidence: [GCC](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42291997083/job/128147501542),
[Windows](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42291997083/job/128147501121),
[Clang and sanitizers](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42292655944/job/128149799208).
