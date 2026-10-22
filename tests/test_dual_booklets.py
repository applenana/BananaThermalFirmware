import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_dual_print_booklets as builder
from dual_booklet_content import book, parallax_book, illustrated_book


class DualBooklets(unittest.TestCase):
    def test_content_and_affirmative_copy(self):
        pages = book()
        self.assertEqual(len(pages), 24)
        text = str(pages)
        for phrase in ('不要', '不能', '不是', '没有', '不支持', '无法', '不应', '单光', 'standard'):
            self.assertNotIn(phrase, text)
        for token in ('dual_sketch3m_fs5m', 'dual_sketch3m_fs5m_stable', 'dual_sketch1m_fs1m'):
            self.assertIn(token, text)

    def test_all_twenty_eight_faces_imposed_once(self):
        pairs = builder.base.pairs(builder.TOTAL)
        self.assertEqual(len(pairs), 14)
        self.assertEqual(sorted(n for pair in pairs for n in pair), list(range(1, 29)))
        self.assertEqual(pairs[0], (28, 1))
        self.assertEqual(pairs[1], (2, 27))

    def test_a4_copy_counts_and_dimensions(self):
        for size, expected in [('a5', 1), ('a6', 2), ('a7', 4)]:
            cfg = builder.CONFIG[size]
            self.assertEqual(cfg['rows'] * cfg['cols'], expected)
            self.assertEqual(cfg['w'] * 2 * cfg['cols'], cfg['pw'])
            self.assertEqual(cfg['h'] * cfg['rows'], cfg['ph'])

    def test_expanded_edition_directions_and_configuration(self):
        pages = parallax_book()
        self.assertEqual(len(pages), 28)
        direction_tables = [b for b in pages[16]['blocks'] if b[0] == 't']
        self.assertEqual(direction_tables[0][2], [
            ['X偏移', '摄像头画面向下', '摄像头画面向上'],
            ['Y偏移', '摄像头画面向右', '摄像头画面向左']])
        self.assertEqual(direction_tables[1][2], [
            ['热像X', '热像画面向左', '热像画面向右'],
            ['热像Y', '热像画面向上', '热像画面向下']])
        text = str(pages)
        for token in ('量贩版', '预留测距接口', '联系卖家购买', '中距离', '**200**'):
            self.assertIn(token, text)
        for phrase in ('不要', '不能', '不是', '没有', '不支持', '无法', '不应'):
            self.assertNotIn(phrase, text)
        self.assertIn(('视差对齐与融合', '15–21'), pages[0]['blocks'][1][1])
        self.assertIn(('升级与问题速查', '26–28'), pages[0]['blocks'][1][1])

    def test_expanded_edition_has_separate_output_and_32_faces(self):
        previous = builder.EDITION
        try:
            old = builder.stem('a7')
            builder.select_edition('parallax')
            self.assertEqual(builder.TOTAL, 32)
            self.assertEqual(len(builder.base.pairs(builder.TOTAL)), 16)
            self.assertNotEqual(old, builder.stem('a7'))
            self.assertIn('视差详解与测距选配版', builder.stem('a7'))
        finally:
            builder.select_edition(previous)

    def test_illustrated_edition_keeps_old_plans_and_inserts_four_guides(self):
        pages = illustrated_book()
        self.assertEqual(len(pages), 32)
        names=[]
        for number in (16,18,20,22):
            blocks=pages[number-1]['blocks']
            images=[b[1] for b in blocks if b[0]=='i']
            self.assertEqual(len(images),1)
            self.assertIn('parallax-',images[0])
            names.extend(images)
        self.assertEqual(len(set(names)),4)
        for name in names:
            asset=builder.ROOT/'docs/assets'/name
            self.assertTrue(asset.is_file())
            self.assertTrue(asset.with_suffix('.svg').is_file())
        self.assertEqual(len(book()),24)
        self.assertEqual(len(parallax_book()),28)
        # The original native direction tables survive unchanged on body page 19.
        self.assertEqual(pages[18]['blocks'],parallax_book()[16]['blocks'])
        for phrase in ('不要','不能','不是','没有','不支持','无法','不应'):
            self.assertNotIn(phrase,str(pages))
        self.assertIn(('照片与 Studio','26–27'),pages[0]['blocks'][1][1])
        previous=builder.EDITION
        try:
            builder.select_edition('illustrated')
            self.assertEqual(builder.TOTAL,36)
            self.assertEqual(len(builder.base.pairs(builder.TOTAL)),18)
            self.assertIn('36面_视差图解版',builder.stem('a7'))
            self.assertEqual(builder.base.pairs(builder.TOTAL)[0],(36,1))
        finally:
            builder.select_edition(previous)


if __name__ == '__main__':
    unittest.main()
