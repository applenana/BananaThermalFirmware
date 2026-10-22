"""Duplex reflection invariants for booklet cutting and binding guides."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import update_booklet_support as support


class BookletSupport(unittest.TestCase):
    def test_dashes_are_symmetric(self):
        for length in (287,200,137.5,95):
            for dash,gap in [(2,1.5),(3,2)]:
                spans=support.symmetric_dashes(5,5+length,dash,gap)
                mirrored=[(10+length-b,10+length-a) for a,b in reversed(spans)]
                self.assertEqual(len(spans),len(mirrored))
                for original,reflected in zip(spans,mirrored):
                    for a,b in zip(original,reflected):self.assertAlmostEqual(a,b)
                self.assertTrue(all(a<b and a>=5 and b<=5+length for a,b in spans))

    def test_fold_axes_reflect_on_duplex(self):
        for size in ('a6','a7'):
            cfg=support.config(size)
            self.assertEqual(cfg['folds'],sorted(cfg['w']-x for x in cfg['folds']))
            self.assertEqual(cfg['row']*2,cfg['h'])

    def test_new_names_preserve_originals(self):
        for size in ('a6','a7'):
            for model in ('24','28','32'):
                source,draft,target=support.paths(size,model)
                self.assertNotEqual(source,target)
                self.assertEqual(draft.name,target.name)


if __name__=='__main__':unittest.main()
