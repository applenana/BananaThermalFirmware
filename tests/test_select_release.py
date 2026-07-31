from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "select_release.py"
SPEC = importlib.util.spec_from_file_location("select_release", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
select_release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(select_release)


class SelectReleaseTests(unittest.TestCase):
    def run_main(
        self,
        *,
        tags: list[str],
        states: dict[str, str],
        requested_tag: str = "",
        minimum_tag: str = "v1.7.0",
    ) -> dict[str, str]:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "github-output.txt"
            environment = {
                "UPSTREAM_REPOSITORY": "manufacturer/official-firmware",
                "GITHUB_REPOSITORY": "owner/public-firmware",
                "GITHUB_TOKEN": "test-token",
                "GITHUB_OUTPUT": str(output_path),
                "REQUESTED_TAG": requested_tag,
                "MINIMUM_FIRMWARE_TAG": minimum_tag,
            }
            with (
                mock.patch.dict(os.environ, environment, clear=True),
                mock.patch.object(select_release, "git_tags", return_value=tags),
                mock.patch.object(
                    select_release,
                    "release_state",
                    side_effect=lambda _repository, tag, _token: states[tag],
                ),
            ):
                select_release.main()

            return dict(
                line.split("=", 1)
                for line in output_path.read_text(encoding="utf-8").splitlines()
            )

    def test_ignores_tags_older_than_minimum(self) -> None:
        outputs = self.run_main(
            tags=["v1.6.0"],
            states={},
        )
        self.assertEqual(outputs, {"tag": "", "release_state": "none"})

    def test_selects_first_unpublished_tag_at_or_above_minimum(self) -> None:
        outputs = self.run_main(
            tags=["v1.6.0", "v1.7.0", "v1.8.0"],
            states={"v1.7.0": "published", "v1.8.0": "missing"},
        )
        self.assertEqual(
            outputs,
            {"tag": "v1.8.0", "release_state": "missing"},
        )

    def test_rejects_manual_tag_older_than_minimum(self) -> None:
        with self.assertRaises(SystemExit):
            self.run_main(
                tags=["v1.6.0", "v1.7.0"],
                states={},
                requested_tag="v1.6.0",
            )


if __name__ == "__main__":
    unittest.main()
