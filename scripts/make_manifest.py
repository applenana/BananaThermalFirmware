#!/usr/bin/env python3
"""Create a firmware manifest without exposing the upstream commit SHA."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    dist = Path(os.environ["DIST_DIR"])
    tag = os.environ["FIRMWARE_TAG"]
    source_commit = os.environ["SOURCE_COMMIT"]
    source_commit_digest = hashlib.sha256(source_commit.encode("ascii")).hexdigest()

    artifacts = []
    for path in sorted(dist.glob("*.uf2")):
        artifacts.append(
            {
                "file": path.name,
                "size": path.stat().st_size,
                "sha256": sha256(path),
                "platformio_environment": path.stem.rsplit("-", 1)[-1],
            }
        )

    if len(artifacts) != 3:
        raise SystemExit(f"expected exactly 3 UF2 artifacts, found {len(artifacts)}")

    manifest = {
        "schema_version": 1,
        "firmware_tag": tag,
        "source_revision_sha256": source_commit_digest,
        "builder": {
            "platformio_core": "6.1.19",
            "workflow_repository": os.environ["GITHUB_REPOSITORY"],
            "workflow_run_id": os.environ["GITHUB_RUN_ID"],
            "workflow_run_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
        },
        "artifacts": artifacts,
    }
    (dist / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
