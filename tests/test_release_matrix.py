from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "scripts"))

from release_matrix import expected_assets, release_contract  # noqa: E402


class ReleaseMatrixTests(unittest.TestCase):
    def test_historical_contract_remains_schema_v1_with_three_variants(self) -> None:
        contract = release_contract("v1.7.9")
        self.assertEqual(contract["schema_version"], 1)
        self.assertEqual(len(contract["variants"]), 3)
        self.assertEqual(len(expected_assets("v1.7.9")), 7)

    def test_unified_contract_uses_schema_v2_with_six_variants(self) -> None:
        contract = release_contract("v1.8.0")
        self.assertEqual(contract["schema_version"], 2)
        self.assertEqual(len(contract["variants"]), 6)
        self.assertEqual(len(expected_assets("v1.8.0")), 10)
        self.assertEqual(
            {variant["hardware_profile"] for variant in contract["variants"]},
            {"dual", "standard"},
        )


if __name__ == "__main__":
    unittest.main()
