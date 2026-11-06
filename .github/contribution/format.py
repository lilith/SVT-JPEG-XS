"""Run upstream formatting on exported submission trees, preserving the checkout."""

import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

output = Path(sys.argv[1]).expanduser().resolve()
output.mkdir(parents=True, exist_ok=True)
results = []
for branch in (
    "fix-sd-decoder-rows",
    "fix-bmi2-test-registration",
    "fix-logging-test-cleanup",
    "test-four-component-decomposition",
):
    tree = output / branch
    tree.mkdir(exist_ok=False)
    archive_data = subprocess.check_output(["git", "archive", branch])
    with tarfile.open(fileobj=io.BytesIO(archive_data)) as archive:
        archive.extractall(tree, filter="data")
    files = subprocess.check_output(
        ["git", "diff", "--name-only", "4d7e116c", branch], text=True
    ).splitlines()
    before = {
        name: (tree / name).read_bytes()
        for name in files
        if (tree / name).suffix in (".c", ".cc", ".cpp", ".cu", ".h", ".hpp")
        and (tree / name).is_file()
    }
    with (output / f"{branch}-format.log").open("w") as log:
        subprocess.run(
            ["bash", "./format-coding.sh"],
            cwd=tree,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
    changed = [
        name for name, data in before.items() if (tree / name).read_bytes() != data
    ]
    results.append({"branch": branch, "changed_files_needing_format": changed})
(output / "format-results.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))
if any(item["changed_files_needing_format"] for item in results):
    raise SystemExit(1)
