# Agent instructions

## Versioning (required for every change)

Every change that lands in `master` gets a release. The version in
`pyproject.toml` must always equal the version of the release the change
produces. CI enforces this on every PR (`version` job in
`.github/workflows/quality.yml`) and fails if the two differ.

Before you finish a change:

1. Decide the bump from the change, and label the PR to match:
   - `major` for breaking changes
   - `minor` for new features
   - no label for fixes, docs, and internal changes (patch)
2. Get the expected version. The latest tag comes from git, so run:

   ```bash
   python scripts/release_version.py --labels <labels>
   ```

   Pass the same comma-separated labels you set on the PR, for example
   `--labels minor`. It prints the release tag, such as `v1.2.0`.
3. Set `version` in `pyproject.toml` to that value without the `v`, for
   example `version = "1.2.0"`.
4. Check it locally:

   ```bash
   python scripts/release_version.py --labels <labels> --check-pyproject pyproject.toml
   ```

Merging to `master` publishes the release automatically
(`.github/workflows/release.yml`). The tag is the source of truth. Never
create tags or GitHub releases by hand.

## Checks before finishing

```bash
python -m ruff check src tests scripts run.py
python -m ruff format --check src tests scripts run.py
PYTHONPATH=src python -m unittest discover -s tests
```
