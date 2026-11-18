import importlib.util
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import starthermal_release as release


class StarThermalReleaseTests(unittest.TestCase):
    def make_package(self, folder):
        root = Path(folder)
        build = root / 'build'
        build.mkdir()
        binary = b'STARTHERMAL-FIRMWARE:v0.1.0'.ljust(300, b'\0')
        (build / 'firmware.bin').write_bytes(binary)
        blocks = []
        for i in range(2):
            block = bytearray(512)
            struct.pack_into('<8I', block, 0, 0x0A324655, 0x9E5D5157, 0x2000,
                             0x10000000 + i * 256, 256, i, 2, 0xE48BFF56)
            block[32:288] = binary[i*256:(i+1)*256].ljust(256, b'\0')
            struct.pack_into('<I', block, 508, 0x0AB16F30)
            blocks.append(block)
        (build / 'firmware.uf2').write_bytes(b''.join(blocks))
        dist = root / 'dist'
        with patch.dict(os.environ, {'GITHUB_REPOSITORY':'applenana/BananaThermalFirmware',
                                    'GITHUB_RUN_ID':'1','GITHUB_RUN_ATTEMPT':'1'}):
            release.package(dist, 'StarThermal-v0.1.0', build, 'a'*40)
        return dist

    def test_package_and_unsigned_verification(self):
        with tempfile.TemporaryDirectory() as folder:
            dist = self.make_package(folder)
            release.verify(dist, 'StarThermal-v0.1.0', signed=False)
            self.assertEqual(len(list(dist.iterdir())), 5)

    def test_rejects_extra_source_file(self):
        with tempfile.TemporaryDirectory() as folder:
            dist = self.make_package(folder)
            (dist/'main.cpp').write_text('private')
            with self.assertRaises(ValueError):
                release.verify(dist,'StarThermal-v0.1.0',signed=False)

    def test_rejects_modified_binary(self):
        with tempfile.TemporaryDirectory() as folder:
            dist = self.make_package(folder)
            (dist/'StarThermal-v0.1.0.bin').write_bytes(b'tampered')
            with self.assertRaises(ValueError):
                release.verify(dist,'StarThermal-v0.1.0',signed=False)

    def test_rejects_different_uf2_payload_even_with_recomputed_hashes(self):
        with tempfile.TemporaryDirectory() as folder:
            dist = self.make_package(folder)
            image = dist/'StarThermal-v0.1.0.uf2'
            data=bytearray(image.read_bytes()); data[100] ^= 1; image.write_bytes(data)
            with self.assertRaises(ValueError):
                release.validate_images(dist/'StarThermal-v0.1.0.bin', image, 'StarThermal-v0.1.0')

    def test_tag_names_are_isolated(self):
        self.assertEqual(release.release_tag('v99.0.0'), 'StarThermal-v99.0.0')
        for tag in ('v1.0', 'v1.0.0-rc1', 'v01.0.0', '../v1.0.0', 'StarThermal-v1.0.0'):
            with self.assertRaises(ValueError): release.release_tag(tag)

    def test_selector_uses_product_tag_and_skips_published(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'output'
            env={'STARTHERMAL_SOURCE_REPOSITORY':'owner/private','GITHUB_REPOSITORY':'owner/public',
                 'GITHUB_TOKEN':'test','GITHUB_OUTPUT':str(output)}
            complete={'assets':[{'name':n} for n in release.asset_names('StarThermal-v0.1.0')]}
            with patch.dict(os.environ,env,clear=True), patch.object(release,'git_tags',return_value=['v0.1.0','v0.1.1']), patch.object(release,'get_release',side_effect=[complete,None]) as get:
                release.select()
                self.assertEqual(get.call_args.args[1], 'StarThermal-v0.1.1')
            self.assertIn('tag=StarThermal-v0.1.1',output.read_text())

    def test_public_release_is_never_repaired(self):
        with tempfile.TemporaryDirectory() as folder:
            env={'STARTHERMAL_SOURCE_REPOSITORY':'owner/private','GITHUB_REPOSITORY':'owner/public',
                 'GITHUB_TOKEN':'test','GITHUB_OUTPUT':str(Path(folder)/'output')}
            with patch.dict(os.environ,env,clear=True), patch.object(release,'git_tags',return_value=['v0.1.0']), patch.object(release,'get_release',return_value={'assets':[]}):
                with self.assertRaises(ValueError): release.select()


if __name__ == '__main__': unittest.main()
