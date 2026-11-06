# test: assert invalid four-component decomposition rejection

The four-component encoding matrix currently skips the two cases where vertical
decomposition exceeds horizontal decomposition. Assert
`SvtJxsErrorBadParameter` and empty encoded output for those inputs instead.

All valid configuration success assertions remain intact. The matrix continues
to cover all 30 format/decomposition cases, with the two invalid inputs now
checking the existing rejection contract.

Base: `4d7e116c3ef259529a0917060e5b113834ed4894` (SVT-JPEG-XS 0.11.0).

Reproduce after configuring with `BUILD_TESTING=ON`:

```sh
Bin/Release/SvtJpegxsUnitTests --gtest_filter='*FourComponentEncodeParam*'
```

Validation on 2026-11-06: full unit suites pass with GCC 13.3 and Clang 18.1 on
Ubuntu 24.04 and MSVC 19.44 on Windows Server 2022. Linux builds use
`-Wall -Wextra -Werror`. All 30 focused cases complete without skips, including
Valgrind (zero errors) and ASan/UBSan. Formatting matches `format-coding.sh`;
no production-code or public API changes.

The Clang full-suite check explicitly applies the separate BMI2 test-registration
prerequisite, commit `66adfcd86bc5504d49fe49e74fb1e6960e300163`.

Evidence: [GCC](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42291525543/job/128145891910),
[Windows](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42294274524/job/128155361190),
[Clang and sanitizers](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42292655944/job/128149799267).
