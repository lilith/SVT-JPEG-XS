# fix(tests): release logging subprocess buffers before exit

The concurrent logging test exits its child process with `_exit()` while the
joined thread container is still in scope. Destruct the container before that
exit so memory checkers can observe its cleanup. Use GoogleTest's temporary
directory selection for the child's output file.

The logging message counts and complete-line assertions are unchanged. This
changes the test harness only.

Base: `4d7e116c3ef259529a0917060e5b113834ed4894` (SVT-JPEG-XS 0.11.0).

Reproduce after configuring with `BUILD_TESTING=ON`:

```sh
valgrind --error-exitcode=99 --leak-check=full --show-leak-kinds=all \
  --errors-for-leak-kinds=definite,indirect,possible \
  Bin/Release/SvtJpegxsUnitTests --gtest_filter='LogCallback.*:LogDefault.*'
```

Validation on 2026-11-06: GCC 13.3 and Clang 18.1 builds on Ubuntu 24.04 use
`-Wall -Wextra -Werror` and pass the full unit suites. All three focused logging
cases pass under Valgrind (zero errors and zero definite, indirect, or possible
leaks in parent and children) and ASan/UBSan. Formatting matches
`format-coding.sh`; no public API changes.

The Clang full-suite check explicitly applies the separate BMI2 test-registration
prerequisite, commit `66adfcd86bc5504d49fe49e74fb1e6960e300163`.

The Windows Server 2022/MSVC 19.44 build and full unit suite also pass. Upstream
compiles this POSIX subprocess fixture only outside `_WIN32`; the Windows check
explicitly verifies zero applicable focused logging tests.

Evidence: [GCC](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42291525543/job/128145891766),
[Windows](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42291525543/job/128145892016),
[Clang and sanitizers](https://github.com/lilith/SVT-JPEG-XS/actions/runs/42292655944/job/128149799158).
