"""Small-format page-reference and saddle-stitch invariants."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_compact_a7 as compact


class CompactA7(unittest.TestCase):
    def test_28_faces_fit_seven_duplex_sheets(self):
        pairs=compact.base.pairs(compact.LOGICAL)
        self.assertEqual(len(pairs),14)
        self.assertEqual(len(pairs)//2,7)
        self.assertEqual(sorted(n for pair in pairs for n in pair),list(range(1,29)))
        self.assertEqual(pairs[:2],[(28,1),(2,27)])
        self.assertEqual(compact.BODY+4,compact.LOGICAL)

    def test_page_references_follow_compacted_topics(self):
        ranges={7:(6,6),25:(21,21),27:(22,23)}
        self.assertEqual(compact.reference('见第 7 页，参阅第 25–27 页。',ranges),
                         '见第 6 页，参阅第 21–23 页。')
        self.assertEqual(compact.reference('320×240 v1.8.0',ranges),'320×240 v1.8.0')


if __name__=='__main__':unittest.main()
