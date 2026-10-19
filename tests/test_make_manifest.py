from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "scripts"))

import make_manifest  # noqa: E402
from release_matrix import release_contract  # noqa: E402


class MakeManifestTests(unittest.TestCase):
    def _generate(self, dist: Path, tag: str) -> dict:
        for variant in release_contract(tag)["variants"]:
            environment_name = variant["platformio_environment"]
            (dist / f"banana-thermal-{tag}-{environment_name}.uf2").write_bytes(
                environment_name.encode("ascii")
            )
        environment = {
            "DIST_DIR": str(dist),
            "FIRMWARE_TAG": tag,
            "SOURCE_COMMIT": "a" * 40,
            "GITHUB_REPOSITORY": "applenana/BananaThermalFirmware",
            "GITHUB_RUN_ID": "123",
            "GITHUB_RUN_ATTEMPT": "1",
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            make_manifest.main()
        return json.loads((dist / "manifest.json").read_text(encoding="utf-8"))

    def test_preserves_schema_v1_for_historical_three_artifact_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._generate(Path(temporary), "v1.7.9")
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(len(manifest["artifacts"]), 3)
            self.assertNotIn("hardware_profile", manifest["artifacts"][0])

    def test_generates_schema_v2_from_exact_six_artifact_matrix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            dist = Path(temporary)
            tag = "v1.8.0"
            manifest = self._generate(dist, tag)
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual(len(manifest["artifacts"]), 6)
            self.assertEqual(
                {item["hardware_profile"] for item in manifest["artifacts"]},
                {"dual", "standard"},
            )


if __name__ == "__main__":
    unittest.main()
