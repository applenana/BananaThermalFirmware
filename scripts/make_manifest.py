#!/usr/bin/env python3
"""Create a firmware manifest without exposing the upstream commit SHA."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

try:
    from release_matrix import release_contract
except ModuleNotFoundError:
    from scripts.release_matrix import release_contract


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
    contract = release_contract(tag)

    artifacts = []
    expected_files = set()
    for variant in contract["variants"]:
        environment = variant["platformio_environment"]
        path = dist / f"banana-thermal-{tag}-{environment}.uf2"
        expected_files.add(path.name)
        if not path.is_file():
            raise SystemExit(f"missing expected UF2 artifact: {path.name}")
        artifact = {
            "file": path.name,
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "platformio_environment": environment,
        }
        if contract["schema_version"] == 2:
            artifact.update(variant)
        artifacts.append(artifact)
    actual_files = {path.name for path in dist.glob("*.uf2")}
    if actual_files != expected_files:
        raise SystemExit("UF2 artifact set does not match the release contract")

    manifest = {
        "schema_version": contract["schema_version"],
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
