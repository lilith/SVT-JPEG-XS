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

Validation: hosted compiler and memory-check results pending. All 30 matrix
cases must complete without skips. The C++ change matches the repository's
`format-coding.sh` output. No production-code or public API changes.
