# Fork-only contribution tooling; submission branches keep upstream build files.

contribution-preflight:
    gh workflow run contribution-preflight.yaml --ref main

contribution-status run:
    gh run view {{run}} --json status,conclusion,jobs --jq '{status,conclusion,jobs:[.jobs[]|{databaseId,name,status,conclusion}]}'

contribution-lint:
    uvx black --check .github/contribution/*.py
    npm exec --yes --package=markdownlint-cli -- markdownlint -c .github/config/.markdown-lint.yml .github/contribution/*.md

contribution-format output:
    python3 -B .github/contribution/format.py '{{output}}'
