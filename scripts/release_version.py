"""Compute the next release tag from existing ``vX.Y.Z`` tags and PR labels.

The highest existing tag is the source of truth. A ``major`` or ``minor`` label
on the merged PR bumps that component; anything else is a ``patch`` release.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable

Version = tuple[int, int, int]

TAG_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
BUMP_LABELS = ("major", "minor")  # checked in priority order; default is patch
START_VERSION: Version = (0, 0, 0)


def parse_tag(tag: str) -> Version | None:
    match = TAG_PATTERN.match(tag.strip())
    if match is None:
        return None
    major, minor, patch = (int(part) for part in match.groups())
    return major, minor, patch


def latest_version(tags: Iterable[str]) -> Version:
    parsed = [version for tag in tags if (version := parse_tag(tag)) is not None]
    return max(parsed, default=START_VERSION)


def bump_kind(labels: Iterable[str]) -> str:
    normalized = {label.strip().lower() for label in labels}
    for kind in BUMP_LABELS:
        if kind in normalized:
            return kind
    return "patch"


def next_version(current: Version, bump: str) -> Version:
    major, minor, patch = current
    if bump == "major":
        return major + 1, 0, 0
    if bump == "minor":
        return major, minor + 1, 0
    if bump == "patch":
        return major, minor, patch + 1
    raise ValueError(f"unknown bump kind: {bump}")


def format_tag(version: Version) -> str:
    return "v{}.{}.{}".format(*version)


def _git_tags() -> list[str]:
    completed = subprocess.run(
        ["git", "tag", "--list", "v*"],  # noqa: S607 - fixed git argv
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.splitlines()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--labels",
        default="",
        help="Comma-separated PR labels, e.g. 'minor,bug'.",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=None,
        help="Existing tags to consider; defaults to the tags in this repository.",
    )
    args = parser.parse_args(argv)

    tags = args.tags if args.tags is not None else _git_tags()
    labels = [label for label in args.labels.split(",") if label.strip()]
    current = latest_version(tags)
    version = next_version(current, bump_kind(labels))
    print(format_tag(version))
    return 0


if __name__ == "__main__":
    sys.exit(main())
