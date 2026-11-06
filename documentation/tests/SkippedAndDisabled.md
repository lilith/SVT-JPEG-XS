# Reported skips and disabled cases

This audit covers the x86 unit executable after the memory-check fixes. The previous native
summary had 18 explicit skips and 47 disabled instances.

| Category | Instances | Treatment |
|---|---:|---|
| Four-component H=1/V=2 configurations | 2 | Check `SvtJxsErrorBadParameter` and empty output |
| AVX-512 instruction paths unavailable on the host | 16 | Keep CPU guards; exercise assertions under ISA emulation |
| Dequantization timing benchmarks | 8 | Explicit opt-in; ordinary correctness tests remain enabled |
| Inverse-DWT timing benchmarks | 38 | Explicit opt-in; ordinary correctness tests remain enabled |
| VLC matrix-printing diagnostic | 1 | Explicit opt-in; the asserting VLC round-trip test remains enabled |

## Corrected configuration checks

`FourComponentEncodeParam.ValidatesDecomposition` retains the success assertions for valid
configurations. It checks rejection for vertical decomposition greater than horizontal instead
of skipping those two inputs. All 30 format/decomposition cases pass natively and under Memcheck,
with zero memory errors and no allocations remaining at process exit.

The full updated native suite passes 12,428 tests, with 16 explicit hardware skips and 47 disabled
benchmark/diagnostic instances. These are GoogleTest execution counts. Legacy frame fixtures also
contain early returns for unsupported geometry or ISA configurations; the reported pass count is
not a measure of exhaustive configuration coverage.

## Instruction coverage

All 16 explicitly skipped AVX-512 tests and the AVX2 GFNI test masked by Valgrind pass under
Intel SDE Sapphire Rapids emulation: **17/17 completed, zero skips and zero failures**.
This is emulated instruction execution. Native AVX-512 execution and Memcheck coverage of those
AVX-512 instructions remain unmeasured on this host.

The caller supplies the exact test filter and expected count. A JSON-result check rejects missing,
skipped, unexecuted, or failed cases, including an accidentally empty filter result.

```sh
just unit-sde /path/to/sde64 Build/linux/memcheck/bin/SvtJpegxsUnitTests '<colon-separated-test-names>' new-isa-logs 17
```

The 16 names appear in the full native skip summary; add `pack_data_groups.AVX2_GFNI` to cover
Valgrind's additional feature-mask limitation. Run builds and checks sequentially with appropriate
resource limits. Set `TMPDIR` to an existing scratch directory on disk.

## Optional developer tools

The disabled names identify timing loops or a printing diagnostic. They are not default correctness
gates. Run them explicitly on hardware that supports their instruction set when those measurements
or matrix output are wanted:

```sh
just unit-disabled
just unit-disabled Build/linux/memcheck/bin/SvtJpegxsUnitTests 'VLC.DISABLED_VariableLenghtCodingPrintMatrix'
```

The opt-in benchmark/diagnostic suite was classified from source in this audit; it was not run as
a performance campaign. No benchmark timings or speed comparisons are claimed.
