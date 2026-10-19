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
sys.path.insert(0, str(REPOSITORY / "scripts"))
from release_matrix import release_contract  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_package(dist: Path, tag: str) -> None:
    contract = release_contract(tag)
    variants = contract["variants"]
    artifacts = []
    for variant in variants:
        environment = variant["platformio_environment"]
        filename = f"banana-thermal-{tag}-{environment}.uf2"
        path = dist / filename
        path.write_bytes(f"test-{environment}".encode())
        artifact = {
            "file": filename,
            "size": path.stat().st_size,
            "sha256": sha256(path),
            "platformio_environment": environment,
        }
        if contract["schema_version"] == 2:
            artifact.update(variant)
        artifacts.append(artifact)

    (dist / "firmware-release-allowed-signers").write_text(
        "banana-thermal-firmware ssh-ed25519 test\n",
        encoding="utf-8",
    )
    (dist / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": contract["schema_version"],
                "firmware_tag": tag,
                "source_revision_sha256": "a" * 64,
                "builder": {"platformio_core": "6.1.19"},
                "artifacts": artifacts,
            }
        ),
        encoding="utf-8",
    )
    checksum_names = [
        *(artifact["file"] for artifact in artifacts),
        "manifest.json",
        "firmware-release-allowed-signers",
    ]
    (dist / "SHA256SUMS").write_text(
        "".join(f"{sha256(dist / name)}  ./{name}\n" for name in checksum_names),
        encoding="utf-8",
    )


class VerifyReleasePackageTests(unittest.TestCase):
    def run_validator(
        self, dist: Path, tag: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--dist",
                str(dist),
                "--tag",
                tag,
                "--unsigned",
            ],
            capture_output=True,
            text=True,
        )

    def test_accepts_exact_unsigned_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            create_package(dist, "v1.7.0")
            result = self.run_validator(dist, "v1.7.0")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_accepts_six_artifact_schema_v2_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            create_package(dist, "v1.8.0")
            result = self.run_validator(dist, "v1.8.0")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_unexpected_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            create_package(dist, "v1.8.0")
            (dist / "source.txt").write_text("must not ship", encoding="utf-8")
            result = self.run_validator(dist, "v1.8.0")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("extra=['source.txt']", result.stderr)

    def test_rejects_modified_firmware(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            create_package(dist, "v1.8.0")
            environment = release_contract("v1.8.0")["variants"][0][
                "platformio_environment"
            ]
            target = dist / f"banana-thermal-v1.8.0-{environment}.uf2"
            target.write_bytes(b"tampered")
            result = self.run_validator(dist, "v1.8.0")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SHA-256 mismatch", result.stderr)

    def test_rejects_schema_v2_metadata_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            create_package(dist, "v1.8.0")
            manifest_path = dist / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"][0]["hardware_profile"] = "standard"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            checksum_names = [
                *(artifact["file"] for artifact in manifest["artifacts"]),
                "manifest.json",
                "firmware-release-allowed-signers",
            ]
            (dist / "SHA256SUMS").write_text(
                "".join(
                    f"{sha256(dist / name)}  ./{name}\n" for name in checksum_names
                ),
                encoding="utf-8",
            )
            result = self.run_validator(dist, "v1.8.0")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("metadata mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
