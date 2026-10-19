#!/usr/bin/env python3
"""Single version-aware firmware release matrix shared by release tooling."""

from __future__ import annotations

import argparse
import json
import re


TAG_PATTERN = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
CUTOVER_VERSION = (1, 8, 0)

HISTORICAL_VARIANTS = (
    {"platformio_environment": "sketch3m_fs5m"},
    {"platformio_environment": "sketch3m_fs5m_stable"},
    {"platformio_environment": "sketch1m_fs1m"},
)

UNIFIED_VARIANTS = (
    ("dual_sketch3m_fs5m", "dual", 8, 5, 300_000_000, "performance"),
    ("dual_sketch3m_fs5m_stable", "dual", 8, 5, 220_000_000, "stable"),
    ("dual_sketch1m_fs1m", "dual", 2, 1, 300_000_000, "performance"),
    ("standard_sketch3m_fs5m", "standard", 8, 5, 300_000_000, "performance"),
    ("standard_sketch3m_fs5m_stable", "standard", 8, 5, 220_000_000, "stable"),
    ("standard_sketch1m_fs1m", "standard", 2, 1, 300_000_000, "performance"),
)


def version_key(tag: str) -> tuple[int, int, int]:
    match = TAG_PATTERN.fullmatch(tag)
    if not match:
        raise ValueError(f"unsupported tag format: {tag}")
    return tuple(int(part) for part in match.groups())


def release_contract(tag: str) -> dict:
    if version_key(tag) < CUTOVER_VERSION:
        return {"schema_version": 1, "variants": HISTORICAL_VARIANTS}
    variants = tuple(
        {
            "platformio_environment": environment,
            "hardware_profile": profile,
            "flash_bytes": flash_mb * 1024 * 1024,
            "filesystem_bytes": filesystem_mb * 1024 * 1024,
            "cpu_hz": cpu_hz,
            "stability_profile": stability,
        }
        for environment, profile, flash_mb, filesystem_mb, cpu_hz, stability
        in UNIFIED_VARIANTS
    )
    return {"schema_version": 2, "variants": variants}


def expected_assets(tag: str) -> set[str]:
    environments = (
        item["platformio_environment"] for item in release_contract(tag)["variants"]
    )
    return {
        *(f"banana-thermal-{tag}-{environment}.uf2" for environment in environments),
        "manifest.json",
        "SHA256SUMS",
        "SHA256SUMS.sig",
        "firmware-release-allowed-signers",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--environments", action="store_true")
    args = parser.parse_args()
    contract = release_contract(args.tag)
    if args.environments:
        for variant in contract["variants"]:
            print(variant["platformio_environment"])
    else:
        print(json.dumps(contract, ensure_ascii=False))


if __name__ == "__main__":
    main()
