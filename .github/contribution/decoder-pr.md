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
SvtJpegxsUnitTests --gtest_filter='*DecoderSdTail*'
```

Validation: hosted compiler and memory-check results pending. The C/C++ changes
match the repository's `format-coding.sh` output. No public API changes.
