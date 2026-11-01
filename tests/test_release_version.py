from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release_version.py"
_spec = importlib.util.spec_from_file_location("release_version", SCRIPT)
assert _spec is not None and _spec.loader is not None
release_version = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(release_version)


class ReleaseVersionTests(unittest.TestCase):
    def test_latest_version_picks_highest_semver_not_lexical(self) -> None:
        tags = ["v1.0.0", "v1.10.0", "v1.9.9", "not-a-version", "v2.0"]
        self.assertEqual(release_version.latest_version(tags), (1, 10, 0))

    def test_latest_version_without_tags_starts_at_zero(self) -> None:
        self.assertEqual(release_version.latest_version([]), (0, 0, 0))

    def test_default_bump_is_patch(self) -> None:
        self.assertEqual(release_version.bump_kind([]), "patch")
        self.assertEqual(release_version.bump_kind(["bug", "docs"]), "patch")

    def test_minor_and_major_labels(self) -> None:
        self.assertEqual(release_version.bump_kind(["minor"]), "minor")
        self.assertEqual(release_version.bump_kind([" Major "]), "major")

    def test_major_wins_over_minor_when_both_present(self) -> None:
        self.assertEqual(release_version.bump_kind(["minor", "major"]), "major")

    def test_next_version_resets_lower_components(self) -> None:
        self.assertEqual(release_version.next_version((1, 1, 1), "patch"), (1, 1, 2))
        self.assertEqual(release_version.next_version((1, 1, 1), "minor"), (1, 2, 0))
        self.assertEqual(release_version.next_version((1, 1, 1), "major"), (2, 0, 0))

    def test_unknown_bump_raises(self) -> None:
        with self.assertRaises(ValueError):
            release_version.next_version((1, 0, 0), "huge")

    def test_main_prints_next_tag_for_labels(self) -> None:
        import io
        from contextlib import redirect_stdout

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = release_version.main(
                ["--labels", "minor,bug", "--tags", "v1.1.1", "v1.0.0"]
            )
        self.assertEqual(code, 0)
        self.assertEqual(buffer.getvalue(), "v1.2.0\n")


if __name__ == "__main__":
    unittest.main()
