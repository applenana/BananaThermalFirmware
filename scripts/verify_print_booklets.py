#!/usr/bin/env python3
"""Check native DOCX structure, imposition and actual rendered text coverage.

Rendering is a prerequisite. This is not a substitute for inspecting every PNG
or for the printer's duplex folded proof on the selected stock.
"""
import argparse
from collections import Counter
import hashlib
import json
import re
import unicodedata
from zipfile import ZipFile
from lxml import etree
import pdfplumber
from build_print_booklets import MODELS, ROOT, OUTPUT, stem, pairs, LOGICAL
from print_booklet_content import BODY_PAGES

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "v": "urn:schemas-microsoft-com:vml"}
def normalized(value):
    return re.sub(r"[\s\u200b\ufeff]", "", unicodedata.normalize("NFKC", value))

def verify(model):
    errors = []; details = []
    def check(test, message):
        if not test: errors.append(message)
    plan = pairs()
    sides=LOGICAL//2
    check(len(plan) == sides and sorted(n for pair in plan for n in pair) == list(range(1,LOGICAL+1)), "imposition must contain each logical page once")
    check(plan[:2] == [(LOGICAL,1),(2,LOGICAL-1)], "cover / blank inside-cover imposition")
    source = OUTPUT / (stem(model)+".docx")
    with ZipFile(source) as archive:
        xml = etree.fromstring(archive.read("word/document.xml"))
        settings = etree.fromstring(archive.read("word/settings.xml"))
        styles = etree.fromstring(archive.read("word/styles.xml"))
        media = [archive.read(n) for n in archive.namelist() if n.startswith("word/media/")]
    check(len(xml.xpath(".//w:sectPr", namespaces=NS)) == 1, "one A4 section")
    size = xml.find(".//w:pgSz", NS)
    check(abs(int(size.get('{'+NS['w']+'}w'))/1440*25.4-297) < .1 and
          abs(int(size.get('{'+NS['w']+'}h'))/1440*25.4-210) < .1, "A4 landscape dimensions")
    for tag in ("bookFoldPrinting", "bookFoldRevPrinting", "mirrorMargins", "printTwoOnOne"):
        check(not settings.xpath("./w:"+tag, namespaces=NS), "must not apply a second imposition: "+tag)
    check(not xml.xpath(".//w:hyperlink", namespaces=NS), "offline content must not depend on hyperlinks")
    authored_text=''.join(xml.xpath('.//w:t/text()',namespaces=NS))
    for phrase in ('触屏为选配，默认款不带触屏', '购买时可在购物平台选择触屏版本',
                   '两种版本均可通过实体按键操作菜单', '本页适用于选配触屏的版本',
                   '相关项目需配合触屏硬件使用', '触屏版点按偏移'):
        check(phrase in authored_text, 'touchscreen option qualification missing: '+phrase)
    for phrase in ('本机没有','本设备没有','没有可见光','快捷菜单','复位孔','联系售后','不要','不能','不是','不代表','不等于'):
        check(phrase not in authored_text, 'editorial regression: '+phrase)
    embedded_hashes={hashlib.sha256(data).digest() for data in media}
    original=ROOT/'docs/assets/devices'/f'standard-{model}-controls.png'
    check(hashlib.sha256(original.read_bytes()).digest() in embedded_hashes, 'original hardware line art must be embedded')
    for rejected in (ROOT/'docs/assets/devices').glob(f'standard-{model}-*-print.png'):
        check(hashlib.sha256(rejected.read_bytes()).digest() not in embedded_hashes, 'rejected redrawn hardware schematic embedded')
    for style in ('Title','Heading1','Heading2','Heading3'):
        node = styles.xpath(f'./w:style[@w:styleId="{style}"]', namespaces=NS)[0]
        check(not node.xpath('.//w:pBdr', namespaces=NS), "no heading rules")
        check(all(c.get('{'+NS['w']+'}val') == '000000' for c in node.xpath('.//w:color',namespaces=NS)), "black heading styles")
    check(len(xml.xpath(".//w:tbl", namespaces=NS)) >= 10, "editable native reference tables")
    raw_dir = ROOT/'.work/print-booklets/references'
    raw_hashes = {hashlib.sha256(p.read_bytes()).digest() for p in raw_dir.glob('*.png')}
    check(not any(hashlib.sha256(data).digest() in raw_hashes for data in media), "raw CAD reference embedded")
    paras = xml.xpath('./w:body/w:p', namespaces=NS)
    check(len(paras) == sides, "one anchor per physical A4 side")
    check(len(xml.xpath('.//w:txbxContent', namespaces=NS)) == BODY_PAGES*3+2, "native body frames + furniture + covers")
    proof = ROOT/'.work/print-booklets'/model/'render'/(stem(model)+'.pdf')
    with pdfplumber.open(proof) as pdf:
        check(len(pdf.pages) == sides, "rendered A4 side count")
        for side,(page,pair,anchor) in enumerate(zip(pdf.pages, plan, paras),1):
            check(abs(page.width-297/25.4*72)<.2 and abs(page.height-210/25.4*72)<.2, f"side {side}: PDF A4 size")
            for half,logical in enumerate(pair):
                left = half*page.width/2; right = (half+1)*page.width/2
                crop = page.crop((left,0,right,page.height))
                actual = normalized(crop.extract_text(x_tolerance=1,y_tolerance=3) or '')
                shapes = []
                for shape in anchor.xpath('.//v:shape', namespaces=NS):
                    x = float(re.search(r'margin-left:([\d.]+)pt',shape.get('style')).group(1))
                    if (x > page.width/2) == bool(half): shapes.append(shape)
                expected = ''.join(''.join(p.xpath('.//w:t/text()',namespaces=NS)) for shape in shapes for p in shape.xpath('.//w:txbxContent//w:p', namespaces=NS))
                expected = normalized(expected)
                missing = Counter(expected)-Counter(actual)
                extra = Counter(actual)-Counter(expected)
                check(not missing, f"side {side} logical {logical}: missing text {dict(missing)}")
                check(not extra, f"side {side} logical {logical}: unexpected text {dict(extra)}")
                if logical in (2,LOGICAL-1):
                    check(not actual and not crop.images, f"side {side}: inside covers must be blank")
                    continue
                # Nothing may be clipped at paper edge or cross the fold. Tables can
                # extend slightly past the paragraph start because of cell margins.
                visible_chars=[c for c in crop.chars if normalized(c['text'])]
                check(all(c['x0'] >= left+12/25.4*72 and c['x1'] <= right-12/25.4*72 for c in visible_chars), f"side {side} logical {logical}: horizontal safe area")
                if logical not in (1,LOGICAL):
                    body_chars=[c for c in crop.chars if 20/25.4*72 < c['top'] < 195/25.4*72]
                    lowest=max((c['bottom'] for c in body_chars),default=0)
                    check(lowest < 191/25.4*72, f"side {side} body {logical-2}: body exceeds frame")
                    check(f'{logical-2:02d}' in actual, f"side {side}: printed body number")
                    details.append(dict(body_page=logical-2, side=side, half='right' if half else 'left', last_text_mm=round(lowest/72*25.4,1)))
        check(not any(normalized(c['text']) for c in pdf.pages[1].chars) and not pdf.pages[1].images, "second A4 side entirely blank")
    report = dict(model=model, docx=str(source), logical_pages=LOGICAL, body_pages=BODY_PAGES,
                  a4_sides=sides, sheets=LOGICAL//4, errors=errors, text_extent=sorted(details,key=lambda d:d['body_page']))
    (ROOT/'.work/print-booklets'/model/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return errors

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model',choices=['all',*MODELS],default='all'); args=parser.parse_args()
    failures=0
    for model in MODELS if args.model=='all' else [args.model]:
        errors=verify(model); failures+=len(errors)
        print(f'{model}: '+('PASS' if not errors else '\n'+'\n'.join(errors)))
    raise SystemExit(1 if failures else 0)
