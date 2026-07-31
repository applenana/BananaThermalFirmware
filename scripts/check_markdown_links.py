#!/usr/bin/env python3
"""Check repository-local Markdown links without making network requests."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "#")
GITHUB_ROUTE_PREFIXES = ("../../releases",)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    markdown_files = sorted(root.rglob("*.md"))
    broken: list[tuple[Path, str]] = []

    for document in markdown_files:
        text = document.read_text(encoding="utf-8")
        for raw_target in LINK_PATTERN.findall(text):
            target = raw_target.strip().strip("<>")
            if target.startswith(EXTERNAL_PREFIXES + GITHUB_ROUTE_PREFIXES):
                continue
            path_part = unquote(target.split("#", 1)[0])
            if path_part and not (document.parent / path_part).resolve().exists():
                broken.append((document.relative_to(root), raw_target))

    if broken:
        for document, target in broken:
            print(f"{document}: broken link: {target}", file=sys.stderr)
        raise SystemExit(1)

    print(f"Validated {len(markdown_files)} Markdown files with no broken links.")


if __name__ == "__main__":
    main()
