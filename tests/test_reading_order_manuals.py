"""Reading-order originals must not contain production-sheet arrangements."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_reading_order_manuals as originals


class ReadingOrderManuals(unittest.TestCase):
    def test_booklet_page_counts_and_paper_pairs(self):
        for size,total in [('a6',32),('a7',28)]:
            cfg=originals.config(size)
            self.assertEqual(cfg['logical'],total)
            self.assertEqual(cfg['body']+4,total)
            self.assertEqual(total%4,0)
            self.assertEqual(cfg['w']*2,210 if size=='a6' else 148.5)

    def test_source_and_output_are_different_files(self):
        for size in ('a6','a7'):
            for model in ('24','28','32'):
                source=originals.source_path(size,model)
                self.assertNotEqual(source.name,originals.draft(size,model).name)
                self.assertIn('原始单页顺序版',originals.stem(size,model))


if __name__=='__main__':unittest.main()
