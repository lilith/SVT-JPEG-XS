# fix(tests): register BMI2 helpers independently of AVX-512

Move the three BMI2 pack/unpack helper tests out of the AVX-512 test object
library. Their GoogleTest registration should run with the baseline test flags;
the helper functions retain function-scoped instruction-set attributes.

Building registration with AVX-512 can execute unsupported instructions before
the test's CPU guard on an AVX2 machine, including sanitizer startup. Require
AVX2 and BMI2 before invoking these helpers and retain all comparison assertions.

Base: `4d7e116c3ef259529a0917060e5b113834ed4894` (SVT-JPEG-XS 0.11.0).

Reproduce after configuring with `BUILD_TESTING=ON`:

```sh
Bin/Release/SvtJpegxsUnitTests --gtest_filter='unpack_planes_to_lanes.*:pack_group_planes_pdep.*:pack_groups_masked_pdep.*'
```

Validation on 2026-11-06: full unit suites pass with GCC 13.3 and Clang 18.1 on
Ubuntu 24.04 and MSVC 19.44 on Windows Server 2022. Linux builds use
`-Wall -Wextra -Werror`. All three focused cases complete without skips on each
compiler, including Valgrind (zero errors) and ASan/UBSan. Formatting matches
`format-coding.sh`; no production-code or public API changes.

Evidence: [GCC](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42291525543/job/128145891498),
[Windows](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42291525543/job/128145891879),
[Clang and sanitizers](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42292655944/job/128149798834).
