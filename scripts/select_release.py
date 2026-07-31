#!/usr/bin/env python3
"""Select one official firmware tag that still needs a complete release."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


TAG_PATTERN = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
ENVIRONMENTS = (
    "sketch3m_fs5m",
    "sketch3m_fs5m_stable",
    "sketch1m_fs1m",
)


def fail(message: str) -> "NoReturn":
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def git_tags(upstream_repository: str) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "ls-remote",
            "--tags",
            "--refs",
            f"git@github.com:{upstream_repository}.git",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    tags: list[str] = []
    for line in result.stdout.splitlines():
        _, ref = line.split("\t", 1)
        tag = ref.removeprefix("refs/tags/")
        if TAG_PATTERN.fullmatch(tag):
            tags.append(tag)
    return sorted(set(tags), key=version_key)


def version_key(tag: str) -> tuple[int, int, int]:
    match = TAG_PATTERN.fullmatch(tag)
    if not match:
        fail(f"unsupported tag format: {tag}")
    return tuple(int(part) for part in match.groups())


def expected_assets(tag: str) -> set[str]:
    return {
        *(f"banana-thermal-{tag}-{environment}.uf2" for environment in ENVIRONMENTS),
        "manifest.json",
        "SHA256SUMS",
        "SHA256SUMS.sig",
        "firmware-release-allowed-signers",
    }


def get_release(repository: str, tag: str, token: str) -> dict | None:
    encoded_tag = urllib.parse.quote(tag, safe="")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/releases/tags/{encoded_tag}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "banana-thermal-firmware-sync",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def release_state(repository: str, tag: str, token: str) -> str:
    release = get_release(repository, tag, token)
    if release is None:
        return "missing"

    actual = {asset["name"] for asset in release.get("assets", [])}
    complete = expected_assets(tag) <= actual
    if release.get("draft"):
        return "draft"
    if release.get("prerelease"):
        fail(f"{tag} already exists as a prerelease; manual review required")
    if not complete:
        missing = sorted(expected_assets(tag) - actual)
        fail(
            f"{tag} is already public but incomplete; refusing to mutate it. "
            f"Missing assets: {', '.join(missing)}"
        )
    return "published"


def write_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        fail("GITHUB_OUTPUT is not set")
    with open(output_path, "a", encoding="utf-8") as output:
        output.write(f"{name}={value}\n")


def main() -> None:
    upstream_repository = os.environ["UPSTREAM_REPOSITORY"]
    public_repository = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    requested_tag = os.environ.get("REQUESTED_TAG", "").strip()
    minimum_tag = os.environ.get("MINIMUM_FIRMWARE_TAG", "v1.7.0").strip()

    if not TAG_PATTERN.fullmatch(minimum_tag):
        fail("MINIMUM_FIRMWARE_TAG must use the form vMAJOR.MINOR.PATCH")

    minimum_version = version_key(minimum_tag)
    tags = [
        tag
        for tag in git_tags(upstream_repository)
        if version_key(tag) >= minimum_version
    ]
    if requested_tag:
        if not TAG_PATTERN.fullmatch(requested_tag):
            fail("manual tag must use the form vMAJOR.MINOR.PATCH")
        if version_key(requested_tag) < minimum_version:
            fail(
                f"manual tag is older than the minimum published version "
                f"({minimum_tag})"
            )
        if requested_tag not in tags:
            fail("manual tag does not exist in the official upstream repository")
        candidates = [requested_tag]
    else:
        candidates = tags

    for tag in candidates:
        state = release_state(public_repository, tag, token)
        if state != "published":
            print(f"Selected one pending firmware release ({state}).")
            write_output("tag", tag)
            write_output("release_state", state)
            return

    print("All eligible official firmware tags are already published.")
    write_output("tag", "")
    write_output("release_state", "none")


if __name__ == "__main__":
    main()
