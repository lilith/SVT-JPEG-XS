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
  SvtJpegxsUnitTests --gtest_filter='LogCallback.*:LogDefault.*'
```

Validation: hosted compiler and memory-check results pending. The C++ change
matches the repository's `format-coding.sh` output. No public API changes.
