#!/usr/bin/env python3
"""Independent StarThermal release contract. Never publish upstream details."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys

from select_release import get_release, git_tags, write_output
from release_matrix import TAG_PATTERN, version_key

PRODUCT = "starthermal"
PREFIX = "StarThermal-"
HARDWARE = "starthermal-rp2040-8m"
MAX_IMAGE = 3_141_632
SIGNERS = "starthermal-allowed-signers"


def release_tag(source_tag: str) -> str:
    if not TAG_PATTERN.fullmatch(source_tag):
        raise ValueError("Expected an official vMAJOR.MINOR.PATCH source tag")
    return PREFIX + source_tag


def source_tag(tag: str) -> str:
    if not tag.startswith(PREFIX):
        raise ValueError("Expected a StarThermal release tag")
    source = tag[len(PREFIX):]
    release_tag(source)
    return source


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def asset_names(tag: str, signed: bool = True) -> set[str]:
    source_tag(tag)
    return {f"{tag}.bin", f"{tag}.uf2", "manifest.json", "SHA256SUMS", SIGNERS} | (
        {"SHA256SUMS.sig"} if signed else set()
    )


def select() -> None:
    upstream = os.environ["STARTHERMAL_SOURCE_REPOSITORY"]
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", upstream):
        raise ValueError("Invalid private source configuration")
    minimum = os.environ.get("MINIMUM_FIRMWARE_TAG", "v0.1.0")
    requested = os.environ.get("REQUESTED_TAG", "").strip()
    release_tag(minimum)
    if requested:
        release_tag(requested)
    tags = [tag for tag in git_tags(upstream) if version_key(tag) >= version_key(minimum)]
    if requested and requested not in tags:
        raise ValueError("Requested official tag is unavailable or below the minimum")
    for tag in ([requested] if requested else tags):
        public_tag = release_tag(tag)
        release = get_release(os.environ["GITHUB_REPOSITORY"], public_tag,
                              os.environ["GITHUB_TOKEN"])
        state = "missing"
        if release is not None:
            names = [item["name"] for item in release.get("assets", [])]
            if release.get("draft"):
                state = "draft"
            elif release.get("prerelease") or len(names) != len(set(names)) or set(names) != asset_names(public_tag):
                raise ValueError("An existing public StarThermal release violates the contract")
            else:
                continue
        write_output("source_tag", tag)
        write_output("tag", public_tag)
        write_output("release_state", state)
        print(f"Selected {public_tag} ({state}).")
        return
    for name in ("source_tag", "tag", "release_state"):
        write_output(name, "")
    print("No unpublished official StarThermal tags.")


def validate_images(binary: Path, uf2: Path, tag: str) -> None:
    data = binary.read_bytes()
    if not 256 <= len(data) <= MAX_IMAGE:
        raise ValueError("Firmware image size is invalid")
    marker = f"STARTHERMAL-FIRMWARE:{source_tag(tag)}".encode("ascii")
    if marker not in data:
        raise ValueError("Firmware product/version identity does not match the release")
    packed = uf2.read_bytes()
    count = (len(data) + 255) // 256
    if len(packed) != count * 512:
        raise ValueError("UF2 does not cover the exact binary image")
    for i in range(count):
        block = packed[i * 512:(i + 1) * 512]
        magic0, magic1, flags, address, size, index, total, family = struct.unpack_from("<8I", block)
        if ((magic0, magic1, flags, address, size, index, total, family) !=
                (0x0A324655, 0x9E5D5157, 0x2000, 0x10000000 + i * 256, 256, i, count, 0xE48BFF56)
                or struct.unpack_from("<I", block, 508)[0] != 0x0AB16F30):
            raise ValueError("UF2 contains an invalid RP2040 block")
        expected = data[i * 256:(i + 1) * 256]
        payload = block[32:288]
        if payload[:len(expected)] != expected or any(b not in (0, 255) for b in payload[len(expected):]):
            raise ValueError("UF2 payload differs from the OTA binary")


def artifact_metadata(tag: str, suffix: str) -> dict:
    return {
        "file": f"{tag}.{suffix}", "format": suffix,
        "role": "ota" if suffix == "bin" else "recovery",
        "hardware_id": HARDWARE, "flash_bytes": 8 * 1024 * 1024,
        "max_firmware_bytes": MAX_IMAGE,
        "transfer_protocol": "serial-ota-v1" if suffix == "bin" else "rp2040-uf2",
    }


def package(dist: Path, tag: str, build: Path, commit: str) -> None:
    import shutil
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", commit):
        raise ValueError("Invalid source revision")
    dist.mkdir(parents=True, exist_ok=False)
    for suffix in ("bin", "uf2"):
        shutil.copyfile(build / f"firmware.{suffix}", dist / f"{tag}.{suffix}")
    validate_images(dist / f"{tag}.bin", dist / f"{tag}.uf2", tag)
    shutil.copyfile(Path(__file__).resolve().parents[1] / "keys" / SIGNERS, dist / SIGNERS)
    artifacts = []
    for suffix in ("bin", "uf2"):
        item = artifact_metadata(tag, suffix)
        path = dist / item["file"]
        item.update(size=path.stat().st_size, sha256=sha256(path))
        artifacts.append(item)
    manifest = {
        "schema_version": 3, "product_id": PRODUCT, "device_model": "StarThermal",
        "firmware_tag": tag, "firmware_version": source_tag(tag)[1:],
        "source_revision_sha256": hashlib.sha256(commit.encode("ascii")).hexdigest(),
        "builder": {"platformio_core": "6.1.19",
                    "workflow_repository": os.environ["GITHUB_REPOSITORY"],
                    "workflow_run_id": os.environ["GITHUB_RUN_ID"],
                    "workflow_run_attempt": os.environ["GITHUB_RUN_ATTEMPT"]},
        "artifacts": artifacts,
    }
    (dist / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    names = sorted(asset_names(tag, signed=False) - {"SHA256SUMS"})
    (dist / "SHA256SUMS").write_text("".join(f"{sha256(dist / name)}  ./{name}\n" for name in names), encoding="ascii")
    verify(dist, tag, signed=False)


def verify(dist: Path, tag: str, signed: bool = True) -> None:
    paths = list(dist.iterdir())
    if any(p.is_symlink() or not p.is_file() for p in paths) or {p.name for p in paths} != asset_names(tag, signed):
        raise ValueError("Release must contain exactly the allowed regular files")
    checksums = {}
    for line in (dist / "SHA256SUMS").read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  \./([^/\\\s]+)", line)
        if not match or match[2] in checksums:
            raise ValueError("Invalid checksum entry")
        checksums[match[2]] = match[1]
    if set(checksums) != asset_names(tag, signed=False) - {"SHA256SUMS"}:
        raise ValueError("Checksum file set mismatch")
    if any(sha256(dist / name) != digest for name, digest in checksums.items()):
        raise ValueError("Release checksum mismatch")
    manifest = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
    if (manifest.get("schema_version") != 3 or manifest.get("product_id") != PRODUCT
            or manifest.get("device_model") != "StarThermal" or manifest.get("firmware_tag") != tag
            or manifest.get("firmware_version") != source_tag(tag)[1:]
            or not re.fullmatch(r"[0-9a-f]{64}", manifest.get("source_revision_sha256", ""))):
        raise ValueError("Manifest product/version mismatch")
    builder = manifest.get("builder", {})
    if builder.get("workflow_repository") != "applenana/BananaThermalFirmware" or builder.get("platformio_core") != "6.1.19":
        raise ValueError("Manifest builder mismatch")
    items = manifest.get("artifacts", [])
    if len(items) != 2:
        raise ValueError("Manifest must contain exactly two firmware images")
    for suffix in ("bin", "uf2"):
        expected = artifact_metadata(tag, suffix)
        matches = [item for item in items if item.get("file") == expected["file"]]
        if len(matches) != 1 or any(matches[0].get(k) != v for k, v in expected.items()):
            raise ValueError("Manifest hardware/transport mismatch")
        path = dist / expected["file"]
        if matches[0].get("size") != path.stat().st_size or matches[0].get("sha256") != sha256(path):
            raise ValueError("Manifest artifact integrity mismatch")
    validate_images(dist / f"{tag}.bin", dist / f"{tag}.uf2", tag)
    trusted = Path(__file__).resolve().parents[1] / "keys" / SIGNERS
    if (dist / SIGNERS).read_bytes() != trusted.read_bytes():
        raise ValueError("Signing identity mismatch")
    if signed:
        with (dist / "SHA256SUMS").open("rb") as message:
            result = subprocess.run(["ssh-keygen", "-Y", "verify", "-f", str(trusted),
                                     "-I", "starthermal-firmware", "-n", "file", "-s",
                                     str(dist / "SHA256SUMS.sig")], stdin=message, capture_output=True)
        if result.returncode:
            raise ValueError("Release signature verification failed")
    print("StarThermal release package verified.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("select", "package", "verify"))
    parser.add_argument("--dist", type=Path)
    parser.add_argument("--tag")
    parser.add_argument("--build", type=Path)
    parser.add_argument("--unsigned", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "select":
            select()
        elif args.command == "package":
            package(args.dist, args.tag, args.build, os.environ["SOURCE_COMMIT"])
        else:
            verify(args.dist, args.tag, signed=not args.unsigned)
    except Exception:
        # Never print exceptions containing a private remote URL or source path.
        print("StarThermal release validation failed; review private diagnostics/configuration.", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
