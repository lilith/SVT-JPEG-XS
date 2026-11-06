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
SvtJpegxsUnitTests --gtest_filter='unpack_planes_to_lanes.*:pack_group_planes_pdep.*:pack_groups_masked_pdep.*'
```

Validation: hosted compiler and memory-check results pending. All three tests
must complete without skips on AVX2/BMI2 hardware. The C++ change matches the
repository's `format-coding.sh` output. No production-code or public API changes.
