"""A7 page-reference and four-copy production invariants."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_a7_booklets as a7


def semantic(blocks):
    result=[]
    for kind,*v in blocks:
        if kind in ('p','h'): result.append(v[0])
        elif kind in ('s','n'): result.extend(v)
        elif kind=='t': result.extend(c for row in v[1] for c in row)
        elif kind=='toc': result.extend(c for row in v[0] for c in row)
        elif kind=='i': result.extend(v[:2])
        else: raise ValueError(kind)
    return result


class A7Booklets(unittest.TestCase):
    def test_imposition(self):
        pairs=a7.base.pairs(a7.LOGICAL)
        self.assertEqual(len(pairs),30)
        self.assertEqual(sorted(n for pair in pairs for n in pair),list(range(1,61)))
        self.assertEqual(pairs[:2],[(60,1),(2,59)])
        self.assertTrue(all(sum(pair)==61 for pair in pairs))
        self.assertEqual((2*a7.W*2,a7.H*2),(297,210))

    def test_references(self):
        self.assertEqual(a7.reference('见第 7 页，参阅第 25–27 页。'),'见第 13–14 页，参阅第 49–54 页。')
        self.assertEqual(a7.reference('v1.8.0 320×240 32 Hz'),'v1.8.0 320×240 32 Hz')

    def test_source_content_and_steps_preserved(self):
        for model in a7.MODELS:
            plan=a7.plan(model)
            self.assertEqual(len(plan),56)
            for n,source in enumerate(a7.remap(a7.book(model))):
                with self.subTest(model=model,topic=n+1):
                    first,second=plan[2*n:2*n+2]
                    self.assertEqual(semantic(first['blocks']+second['blocks']),semantic(a7.expand(source['blocks'])))
                    self.assertEqual(first['lead']+second['lead'],source['lead'])
                    self.assertEqual(second['step_offset'],sum(b[0]=='s' for b in first['blocks']))
            self.assertFalse(any(b[0]=='toc' for b in plan[0]['blocks']))
            self.assertEqual(sum(len(b[1]) for b in plan[1]['blocks'] if b[0]=='toc'),9)


if __name__=='__main__':unittest.main()
