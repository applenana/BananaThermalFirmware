#!/usr/bin/env python3
"""Strictly validate the public firmware release allowlist and its hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ENVIRONMENTS = (
    "sketch3m_fs5m",
    "sketch3m_fs5m_stable",
    "sketch1m_fs1m",
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"release package validation failed: {message}")


def parse_checksums(path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  \./([^/\s]+)", line)
        if not match:
            fail(f"invalid SHA256SUMS line: {line!r}")
        digest, filename = match.groups()
        if filename in checksums:
            fail(f"duplicate SHA256SUMS entry: {filename}")
        checksums[filename] = digest
    return checksums


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--unsigned", action="store_true")
    args = parser.parse_args()

    dist = args.dist.resolve()
    firmware_files = {
        f"banana-thermal-{args.tag}-{environment}.uf2"
        for environment in ENVIRONMENTS
    }
    checksum_files = {
        *firmware_files,
        "manifest.json",
        "firmware-release-allowed-signers",
    }
    expected_files = {
        *checksum_files,
        "SHA256SUMS",
    }
    if not args.unsigned:
        expected_files.add("SHA256SUMS.sig")

    actual_files = {
        path.name
        for path in dist.iterdir()
        if path.is_file()
    }
    if actual_files != expected_files:
        fail(
            "unexpected file allowlist; "
            f"missing={sorted(expected_files - actual_files)}, "
            f"extra={sorted(actual_files - expected_files)}"
        )
    if any(path.is_dir() for path in dist.iterdir()):
        fail("subdirectories are not allowed")

    checksums = parse_checksums(dist / "SHA256SUMS")
    if set(checksums) != checksum_files:
        fail("SHA256SUMS does not cover the exact expected file set")
    for filename, expected_digest in checksums.items():
        if sha256(dist / filename) != expected_digest:
            fail(f"SHA-256 mismatch: {filename}")

    manifest = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1:
        fail("unsupported manifest schema")
    if manifest.get("firmware_tag") != args.tag:
        fail("manifest firmware tag mismatch")
    if not SHA256_PATTERN.fullmatch(manifest.get("source_revision_sha256", "")):
        fail("invalid source revision digest")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != len(ENVIRONMENTS):
        fail("manifest must contain exactly three firmware artifacts")
    by_environment = {
        artifact.get("platformio_environment"): artifact
        for artifact in artifacts
        if isinstance(artifact, dict)
    }
    if set(by_environment) != set(ENVIRONMENTS):
        fail("manifest environment set mismatch")
    for environment in ENVIRONMENTS:
        artifact = by_environment[environment]
        filename = f"banana-thermal-{args.tag}-{environment}.uf2"
        path = dist / filename
        if artifact.get("file") != filename:
            fail(f"manifest filename mismatch: {environment}")
        if artifact.get("size") != path.stat().st_size:
            fail(f"manifest size mismatch: {filename}")
        if artifact.get("sha256") != sha256(path):
            fail(f"manifest SHA-256 mismatch: {filename}")

    builder = manifest.get("builder")
    if not isinstance(builder, dict) or builder.get("platformio_core") != "6.1.19":
        fail("unexpected PlatformIO Core version")

    print(f"Validated {len(actual_files)} allowlisted release files.")


if __name__ == "__main__":
    main()
