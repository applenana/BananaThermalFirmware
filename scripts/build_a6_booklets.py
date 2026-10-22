#!/usr/bin/env python3
"""A4 portrait two-up production sheets for two identical A6 saddle-stitched books.

Build and render in ignored work space; publish only after QA. Existing DOCX
files are never overwritten. Content is shared with the approved touch edition.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
from zipfile import ZipFile

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.shared import Mm, Pt
from lxml import etree
import pdfplumber

import build_print_booklets as base
from print_booklet_content import MODELS, BODY_PAGES, book
from render_manuals import convert_with_word
from verify_print_booklets import normalized

ROOT = base.ROOT
WORK = ROOT / '.work/a6-booklets'
OUTPUT = ROOT / 'artifacts/print-booklets/a6'
W, H = 105, 148.5
TEXT_W = 88
LOGICAL = BODY_PAGES + 4
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'v': 'urn:schemas-microsoft-com:vml'}


def stem(model):
    return f"BananaThermal_{MODELS[model]['size']}寸单光_随附说明书_A6成册_A4双套拼版_v1.8"


def draft(model):
    return WORK / model / (stem(model) + '.docx')


def add_cut_guide(anchor, side):
    """Printable horizontal cutting guide, anchored without affecting text flow."""
    w, v = NS['w'], NS['v']
    run = etree.SubElement(anchor, '{'+w+'}r')
    pict = etree.SubElement(run, '{'+w+'}pict')
    line = etree.SubElement(pict, '{'+v+'}line', nsmap={'v': v})
    line.set('id', f'A6CutGuide{side}')
    line.set('from', '0pt,0pt')
    line.set('to', f'{200*72/25.4:.4f}pt,0pt')
    line.set('style',
             f'position:absolute;margin-left:{5*72/25.4:.4f}pt;'
             f'margin-top:{H*72/25.4:.4f}pt;'
             f'width:{200*72/25.4:.4f}pt;height:0pt;z-index:9000;'
             'mso-position-horizontal-relative:page;'
             'mso-position-vertical-relative:page')
    line.set('strokecolor', '#8C8C8C')
    line.set('strokeweight', '0.5pt')
    etree.SubElement(line, '{'+v+'}stroke').set('dashstyle', 'dash')
    etree.SubElement(line, '{urn:schemas-microsoft-com:office:word}wrap').set('type', 'none')


def restyle(nodes, kind='body'):
    """Reflow native text, tables and illustrations independently, not page scaling."""
    sizes = {11:9.5, 10.5:9, 11.5:10, 12:10.5, 13:10.5, 14:12,
             18:14, 19:15, 25:20, 9:7.5, 8.5:7, 8:6.5, 10:8.5}
    for node in nodes:
        diagram = any(value in ''.join(node.xpath('.//wp:docPr/@descr'))
                      for value in ('两键操作流程','高温报警示例','热像画面功能示意'))
        image_scale = .98 if diagram else .70
        for element in node.iter():
            if element.tag in (qn('w:sz'), qn('w:szCs')):
                old = int(element.get(qn('w:val'))) / 2
                element.set(qn('w:val'), str(int(sizes.get(old, old)*2)))
            elif element.tag == qn('w:spacing'):
                for attr in ('before','after'):
                    key=qn('w:'+attr)
                    if key in element.attrib:
                        element.set(key,str(round(int(element.get(key))*.55)))
                if element.get(qn('w:lineRule')) == 'exact':
                    old=int(element.get(qn('w:line')))
                    element.set(qn('w:line'),str(round(old*.78)))
            elif element.tag == qn('w:ind'):
                for attr in ('left','right'):
                    key=qn('w:'+attr)
                    if key in element.attrib:
                        element.set(key,str(round(int(element.get(key))*.72)))
            elif element.tag in (qn('wp:extent'), qn('a:ext')):
                for attr in ('cx','cy'):
                    if attr in element.attrib:
                        element.set(attr,str(round(int(element.get(attr))*image_scale)))
            elif element.tag in (qn('w:top'), qn('w:bottom')) and element.getparent().tag == qn('w:tblCellMar'):
                element.set(qn('w:w'),'35')
            elif element.tag in (qn('w:left'), qn('w:right')) and element.getparent().tag == qn('w:tblCellMar'):
                element.set(qn('w:w'),'65')
        for pp in node.iter(qn('w:p')):
            if pp.xpath('./w:pPr/w:pStyle[@w:val="Heading1"]'):
                spacing=pp.find(qn('w:pPr')).find(qn('w:spacing'))
                if spacing is None:
                    from docx.oxml import OxmlElement
                    spacing=OxmlElement('w:spacing'); pp.find(qn('w:pPr')).append(spacing)
                spacing.set(qn('w:line'),'350'); spacing.set(qn('w:lineRule'),'exact')
    return nodes


def build(model):
    base.TEXT_W=TEXT_W
    doc=Document(); base.setup(doc,model)
    sec=doc.sections[0]; sec.orientation=WD_ORIENT.PORTRAIT
    sec.page_width=Mm(210); sec.page_height=Mm(297)
    normal=doc.styles['Normal']; normal.font.size=Pt(9.5)
    normal.paragraph_format.line_spacing=Pt(13)
    for name,size,line in [('Title',20,26),('Heading 1',14,18),('Heading 2',10.5,14),('Caption',7.5,10)]:
        st=doc.styles[name]; st.font.size=Pt(size); st.paragraph_format.line_spacing=Pt(line)
        st.paragraph_format.space_before=Pt(4 if name=='Heading 2' else 0)
        st.paragraph_format.space_after=Pt(4)
    doc.core_properties.subject='A6 成册 A4 竖向上下双套预拼版 32 面 骑马订'
    doc.core_properties.keywords='A6; A4 portrait; two copies; saddle stitch; standard; v1.8'
    plan=book(model); sid=2000
    for side,pair in enumerate(base.pairs()):
        anchor=doc.add_paragraph(); pf=anchor.paragraph_format
        pf.page_break_before=side>0; pf.space_before=pf.space_after=Pt(0); pf.line_spacing=Pt(1)
        add_cut_guide(anchor._p, side+1)
        for copy in range(2):
            for half,logical in enumerate(pair):
                if logical in (2,LOGICAL-1): continue
                x=half*W+(8 if half==0 else 9); oy=copy*H
                if logical==1:
                    nodes=restyle(base.compose_cover(doc,model),'cover'); y,height=10,131
                elif logical==LOGICAL:
                    nodes=restyle(base.compose_back(doc,model),'cover'); y,height=10,131
                else:
                    number=logical-2; item=plan[number-1]
                    sid+=1; base.box(anchor,restyle(base.furniture(doc,model,item,number)),x,oy+5.5,TEXT_W,5,sid)
                    sid+=1; base.box(anchor,restyle(base.furniture(doc,model,item,number,True)),x,oy+140,TEXT_W,5,sid)
                    nodes=restyle(base.compose_body(doc,item,number)); y,height=14,123
                sid+=1; base.box(anchor,nodes,x,oy+y,TEXT_W,height,sid)
    target=draft(model); target.parent.mkdir(parents=True,exist_ok=True)
    doc.save(target)
    (target.parent/'imposition.json').write_text(json.dumps(dict(
        logical_pages=LOGICAL,body_pages=BODY_PAGES,a4_sides=16,a4_sheets=8,
        copies=2,cut_y_mm=148.5,fold_x_mm=105,
        sides=[dict(top=pair,bottom=pair) for pair in base.pairs()]),indent=2),encoding='utf-8')
    return target


def render(model,renderer_path):
    spec=importlib.util.spec_from_file_location('packaged_renderer',renderer_path)
    renderer=importlib.util.module_from_spec(spec); spec.loader.exec_module(renderer)
    renderer.convert_to_pdf=convert_with_word
    pages=renderer.rasterize(str(draft(model)),str(WORK/model/'render'),160,verbose=True,emit_pdf=True)
    print(f'{model}: {len(pages)} A4 sides')


def verify(model):
    errors=[]
    def check(test,msg):
        if not test: errors.append(msg)
    with ZipFile(draft(model)) as z:
        xml=etree.fromstring(z.read('word/document.xml'))
        settings=etree.fromstring(z.read('word/settings.xml'))
        media={hashlib.sha256(z.read(n)).digest() for n in z.namelist() if n.startswith('word/media/')}
    size=xml.find('.//w:pgSz',NS)
    check(abs(int(size.get(qn('w:w')))/1440*25.4-210)<.1 and
          abs(int(size.get(qn('w:h')))/1440*25.4-297)<.1,'A4 portrait geometry')
    for tag in ('bookFoldPrinting','bookFoldRevPrinting','mirrorMargins','printTwoOnOne'):
        check(not settings.xpath('./w:'+tag,namespaces=NS),'second imposition '+tag)
    anchors=xml.xpath('./w:body/w:p',namespaces=NS)
    check(len(anchors)==16,'16 physical A4 sides')
    check(len(xml.xpath('.//w:txbxContent',namespaces=NS))==(BODY_PAGES*3+2)*2,'editable frames duplicated twice')
    check(hashlib.sha256((ROOT/'docs/assets/devices'/f'standard-{model}-controls.png').read_bytes()).digest() in media,'original hardware drawing')
    texts=''.join(xml.xpath('.//w:t/text()',namespaces=NS))
    previous=base.OUTPUT/(base.stem(model)+'.docx')
    with ZipFile(previous) as source:
        previous_xml=etree.fromstring(source.read('word/document.xml'))
    original_text=normalized(''.join(previous_xml.xpath('.//w:t/text()',namespaces=NS)))
    check(Counter(normalized(texts))==Counter(original_text+original_text),
          'approved content preserved twice')
    for phrase in ('默认款不带触屏','选配触屏','相关项目需配合触屏硬件使用'):
        check(phrase in texts,'touch option missing '+phrase)
    for phrase in ('本机没有','本设备没有','没有可见光','快捷菜单','复位孔','联系售后','不要','不能','不是','不代表','不等于'):
        check(phrase not in texts,'editorial regression '+phrase)
    details=[]
    with pdfplumber.open(WORK/model/'render'/(stem(model)+'.pdf')) as pdf:
        check(len(pdf.pages)==16,'rendered page count')
        for side,(page,pair,anchor) in enumerate(zip(pdf.pages,base.pairs(),anchors),1):
            check(abs(page.width-210/25.4*72)<.2 and abs(page.height-297/25.4*72)<.2,'rendered geometry')
            all_shapes=anchor.xpath('.//v:shape',namespaces=NS)
            for copy in range(2):
                for half,logical in enumerate(pair):
                    left=half*page.width/2; top=copy*page.height/2
                    crop=page.crop((left,top,left+page.width/2,top+page.height/2))
                    actual=normalized(crop.extract_text(x_tolerance=1,y_tolerance=2) or '')
                    shapes=[]
                    for shape in all_shapes:
                        style=shape.get('style')
                        x=float(re.search(r'margin-left:([\d.]+)pt',style).group(1))
                        y=float(re.search(r'margin-top:([\d.]+)pt',style).group(1))
                        if (x>page.width/2)==bool(half) and (y>page.height/2)==bool(copy): shapes.append(shape)
                    expected=normalized(''.join(''.join(p.xpath('.//w:t/text()',namespaces=NS)) for shape in shapes for p in shape.xpath('.//w:txbxContent//w:p',namespaces=NS)))
                    label=f'side {side} copy {copy+1} logical {logical}'
                    missing=Counter(expected)-Counter(actual); extra=Counter(actual)-Counter(expected)
                    check(not missing,label+' missing '+str(dict(missing)))
                    check(not extra,label+' extra '+str(dict(extra)))
                    if logical in (2,LOGICAL-1):
                        check(not actual and not crop.images,label+' blank inside cover'); continue
                    chars=[c for c in crop.chars if normalized(c['text'])]
                    check(all(c['x0']>=left+6/25.4*72 and c['x1']<=left+page.width/2-6/25.4*72 for c in chars),label+' horizontal safety')
                    check(all(c['top']>=top+4/25.4*72 and c['bottom']<=top+page.height/2-3/25.4*72 for c in chars),label+' vertical safety')
                    if logical not in (1,LOGICAL):
                        body=[c for c in chars if top+13/25.4*72<c['top']<top+139/25.4*72]
                        lowest=max((c['bottom']-top for c in body),default=0)/72*25.4
                        check(lowest<137,label+' body overflow '+str(round(lowest,1)))
                        check(f'{logical-2:02d}' in actual,label+' body number')
                        details.append(dict(side=side,copy=copy+1,body=logical-2,bottom_mm=round(lowest,1)))
            check(side!=2 or (not any(normalized(c['text']) for c in page.chars) and not page.images),'blank second A4 face')
    report=dict(model=model,errors=errors,body_pages=BODY_PAGES,copies=2,sides=16,extent=details)
    (WORK/model/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(model+(': PASS' if not errors else ':\n'+'\n'.join(errors)))
    return errors


def publish(model):
    report=json.loads((WORK/model/'verification.json').read_text(encoding='utf-8'))
    if report['errors']: raise RuntimeError('QA failed')
    OUTPUT.mkdir(parents=True,exist_ok=True)
    target=OUTPUT/(stem(model)+'.docx')
    with draft(model).open('rb') as source,target.open('xb') as output:
        shutil.copyfileobj(source,output)
    return target


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['build','render','verify','publish'])
    parser.add_argument('--model',choices=['all',*MODELS],default='all')
    parser.add_argument('--renderer',type=Path)
    args=parser.parse_args(); failures=0
    for model in MODELS if args.model=='all' else [args.model]:
        if args.action=='build': print(build(model))
        elif args.action=='render': render(model,args.renderer)
        elif args.action=='verify': failures+=len(verify(model))
        else: print(publish(model))
    raise SystemExit(bool(failures))
