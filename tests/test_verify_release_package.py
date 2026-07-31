from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "scripts" / "verify_release_package.py"
TAG = "v1.7.0"
ENVIRONMENTS = (
    "sketch3m_fs5m",
    "sketch3m_fs5m_stable",
    "sketch1m_fs1m",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_package(dist: Path) -> None:
    artifacts = []
    for environment in ENVIRONMENTS:
        filename = f"banana-thermal-{TAG}-{environment}.uf2"
        path = dist / filename
        path.write_bytes(f"test-{environment}".encode())
        artifacts.append(
            {
                "file": filename,
                "size": path.stat().st_size,
                "sha256": sha256(path),
                "platformio_environment": environment,
            }
        )

    (dist / "firmware-release-allowed-signers").write_text(
        "banana-thermal-firmware ssh-ed25519 test\n",
        encoding="utf-8",
    )
    (dist / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "firmware_tag": TAG,
                "source_revision_sha256": "a" * 64,
                "builder": {"platformio_core": "6.1.19"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    checksum_names = [
        *(f"banana-thermal-{TAG}-{environment}.uf2" for environment in ENVIRONMENTS),
        "manifest.json",
        "firmware-release-allowed-signers",
    ]
    (dist / "SHA256SUMS").write_text(
        "".join(f"{sha256(dist / name)}  ./{name}\n" for name in checksum_names),
        encoding="utf-8",
    )


class VerifyReleasePackageTests(unittest.TestCase):
    def run_validator(self, dist: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--dist",
                str(dist),
                "--tag",
                TAG,
                "--unsigned",
            ],
            capture_output=True,
            text=True,
        )

    def test_accepts_exact_unsigned_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            create_package(dist)
            result = self.run_validator(dist)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unexpected_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            create_package(dist)
            (dist / "source.txt").write_text("must not ship", encoding="utf-8")
            result = self.run_validator(dist)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("extra=['source.txt']", result.stderr)

    def test_rejects_modified_firmware(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            create_package(dist)
            target = dist / f"banana-thermal-{TAG}-{ENVIRONMENTS[0]}.uf2"
            target.write_bytes(b"tampered")
            result = self.run_validator(dist)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SHA-256 mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
