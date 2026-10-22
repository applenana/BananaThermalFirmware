#!/usr/bin/env python3
"""Flow the offline A7 manual into at most 24 body pages, then impose on A4."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import importlib.util
from collections import Counter
import shutil

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Mm,Pt
from docx.text.paragraph import Paragraph
from lxml import etree
from PIL import Image,ImageDraw
import pdfplumber

import build_print_booklets as base
import build_a6_booklets as a6
import build_a7_booklets as a7
import update_booklet_support as support
from manual_layout import el,font,inline,picture
from print_booklet_content import book,MODELS
from verify_print_booklets import normalized

ROOT=base.ROOT;WORK=ROOT/'.work/compact-a7';WIDTH=61.25
LOGICAL=28;BODY=24
PREFIX='BananaThermal_'


def stem(model):
    return f'BananaThermal_{MODELS[model]["size"]}寸单光_随附说明书_A7成册_A4四套拼版_v1.8_精简28面_资料支持与双面对齐版'


def pp(doc,text,size=7.5,bold=False,before=0,after=1.5):
    p=doc.add_paragraph();pf=p.paragraph_format
    pf.space_before=Pt(before);pf.space_after=Pt(after);pf.line_spacing=Pt(9.5 if size<=8 else size+2)
    pf.keep_together=True;pf.widow_control=False
    inline(p,text,size)
    for r in p.runs:
        if bold:r.bold=True
    return p


def mark(node,ident,name=None):
    p=node if node.tag==qn('w:p') else next(node.iter(qn('w:p')))
    p.insert(0,el('w:bookmarkStart',**{'w:id':ident,'w:name':name or f'block{ident:04d}'}))
    p.append(el('w:bookmarkEnd',**{'w:id':ident}))


def table(doc,headers,rows,widths):
    base.TEXT_W=WIDTH
    before=set(doc._element.body);base.reference_table(doc,headers,rows,widths)
    nodes=[n for n in doc._element.body if n not in before]
    for node in nodes:
        if node.tag==qn('w:p'):doc._element.body.remove(node);continue
        for p in node.iter(qn('w:p')):
            from docx.text.paragraph import Paragraph
            para=Paragraph(p,doc._body)
            pf=para.paragraph_format;pf.space_before=pf.space_after=Pt(0)
            pf.line_spacing=Pt(9.2);pf.keep_together=True;pf.keep_with_next=False;pf.widow_control=False
            for run in para.runs:font(run,7,run.bold,'FFFFFF' if run.font.color.rgb and str(run.font.color.rgb)=='FFFFFF' else '000000')
        for p in list(node.iter(qn('w:tr')))[0].iter(qn('w:p')):
            from docx.text.paragraph import Paragraph
            Paragraph(p,doc._body).paragraph_format.keep_with_next=True
        for m in node.iter(qn('w:tblCellMar')):
            for child in m:child.set(qn('w:w'),'35' if child.tag in (qn('w:top'),qn('w:bottom')) else '45')


def figure(doc,block):
    _,name,caption,width,crop=block
    if 'menu-flow' in name:
        pp(doc,'A/B 两键操作流程：进入 → 选择 → 确认 → 调值 → 返回保存。',7.5,after=2);return
    if 'alarm-hysteresis' in name:
        pp(doc,caption,7.5,after=2);return
    with Image.open(ROOT/'docs/assets'/name) as im:
        l,t,r,b=crop or (0,0,0,0);ratio=im.height*(1-t-b)/(im.width*(1-l-r))
    max_h=35 if 'controls' in name else 27 if 'rear-manual' in name else 32
    w=min(WIDTH,max_h/ratio)
    start=len(doc.paragraphs);picture(doc,name,caption,w/25.4,crop)
    for p in doc.paragraphs[start:]:
        p.paragraph_format.space_before=Pt(1);p.paragraph_format.space_after=Pt(2)
        p.paragraph_format.keep_together=True
        if p.style.name=='Caption':
            p.paragraph_format.line_spacing=Pt(8)
            for run in p.runs:font(run,6.5,False,base.GRAY)


def flow(model):
    source=a6.OUTPUT/(a6.stem(model)+'.docx');doc=Document(source)
    for node in list(doc._element.body):
        if node.tag!=qn('w:sectPr'):doc._element.body.remove(node)
    sec=doc.sections[0];sec.orientation=WD_ORIENT.PORTRAIT
    sec.page_width=Mm(74.25);sec.page_height=Mm(105)
    sec.left_margin=Mm(6);sec.right_margin=Mm(7)
    sec.top_margin=Mm(10);sec.bottom_margin=Mm(7)
    sec.header_distance=sec.footer_distance=Mm(3)
    normal=doc.styles['Normal'];normal.font.size=Pt(8);normal.paragraph_format.line_spacing=Pt(10.5)
    # Hide no content: all source prose, steps, table rows and hardware drawings retained.
    topics=[];meta=[];counter=1
    for topic,item in enumerate(book(model),1):
        start=set(doc._element.body)
        p=pp(doc,item['title'],10,True,before=3 if topic>1 else 0,after=3)
        p.paragraph_format.keep_with_next=True
        pp(doc,item['lead'],7.5,after=2).paragraph_format.keep_with_next=True
        step=0
        for block in item['blocks']:
            kind,*v=block
            if kind=='p':pp(doc,v[0])
            elif kind=='h':pp(doc,v[0],8.5,True,before=3,after=1).paragraph_format.keep_with_next=True
            elif kind=='n':pp(doc,'**'+v[0]+'**　'+v[1],7.5,before=2,after=3)
            elif kind=='s':
                step+=1;pp(doc,f'**{step:02d} {v[0]}**　{v[1]}',7.5,before=1,after=2)
            elif kind=='t':table(doc,*v)
            elif kind=='toc':
                for title,ref in v[0]:
                    p=pp(doc,title+'\t'+ref,7.5,after=2)
                    p.paragraph_format.tab_stops.add_tab_stop(Mm(WIDTH-1),2)
            elif kind=='i':figure(doc,block)
            else:raise ValueError(kind)
        nodes=[n for n in doc._element.body if n not in start]
        topics.append(counter)
        for node in nodes:
            mark(node,counter);record={'id':counter,'topic':topic,'tag':node.tag}
            if node.tag==qn('w:tbl'):
                record['rows']=[]
                for index,row in enumerate(list(node.iter(qn('w:tr')))[1:],1):
                    name=f'row{counter:04d}_{index:02d}'
                    mark(row,10000+counter*100+index,name);record['rows'].append(name)
            meta.append(record);counter+=1
    work=WORK/model;work.mkdir(parents=True,exist_ok=True)
    doc.save(work/'flow.docx')
    doc.save(work/'flow-original.docx')
    (work/'meta.json').write_text(json.dumps({'topics':topics,'blocks':meta},ensure_ascii=False,indent=2),encoding='utf-8')
    print(model,'flow blocks',len(meta))


def paginate(model):
    work=WORK/model
    result=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass',
            '-File',str(ROOT/'scripts/paginate_booklet.ps1'),'-InputDocx',str(work/'flow.docx'),
            '-OutputJson',str(work/'pagination.json'),'-OutputPdf',str(work/'flow.pdf')],capture_output=True,timeout=180)
    if result.returncode:raise RuntimeError((result.stdout+result.stderr).decode('utf-8',errors='replace'))
    print(result.stdout.decode('utf-8',errors='replace'))


def topic_ranges(model):
    work=WORK/model
    meta=json.loads((work/'meta.json').read_text(encoding='utf-8'))
    pagination=json.loads((work/'pagination.json').read_text(encoding='utf-8-sig'))
    positions={p['name']:p['page'] for p in pagination['blocks']}
    ranges={}
    for record in meta['blocks']:
        pages=[positions[f'block{record["id"]:04d}']]+[positions[n] for n in record.get('rows',[])]
        ranges.setdefault(record['topic'],[]).extend(pages)
    return {n:(min(pages),max(pages)) for n,pages in ranges.items()}


def reference(text,ranges):
    def format_range(a,b):
        low=ranges[int(a)][0];high=ranges[int(b or a)][1]
        return str(low) if low==high else f'{low}–{high}'
    return re.sub(r'第\s*(\d+)\s*(?:[–—\-至]\s*(\d+)\s*)?页',
                  lambda m:'第 '+format_range(m[1],m[2])+' 页',text)


def remap(model):
    work=WORK/model;ranges=topic_ranges(model)
    doc=Document(work/'flow-original.docx')
    for node in doc._element.body.iter(qn('w:t')):
        if node.text:node.text=reference(node.text,ranges)
    # Contents references are printed without the surrounding 第 / 页.
    for p in doc.paragraphs:
        if '\t' in p.text:
            original=p.text.split('\t')[-1]
            if re.fullmatch(r'\d+(?:–\d+)?',original):
                a,*b=original.split('–');low=ranges[int(a)][0];high=ranges[int(b[0] if b else a)][1]
                new=str(low) if low==high else f'{low}–{high}'
                for t in p._p.iter(qn('w:t')):
                    if t.text==original:t.text=new
    doc.save(work/'flow.docx')
    (work/'references.json').write_text(json.dumps(ranges,ensure_ascii=False,indent=2),encoding='utf-8')
    print(model,'updated references',ranges)


def build(model):
    work=WORK/model
    meta=json.loads((work/'meta.json').read_text(encoding='utf-8'))
    pagination=json.loads((work/'pagination.json').read_text(encoding='utf-8-sig'))
    assert pagination['pages']==BODY,('body page budget',pagination['pages'])
    stable={str(k):list(v) for k,v in topic_ranges(model).items()}
    assert stable==json.loads((work/'references.json').read_text(encoding='utf-8')),'references moved; remap and repaginate'
    positions={p['name']:p['page'] for p in pagination['blocks']}
    flow_doc=Document(work/'flow.docx')
    flow_nodes=[n for n in flow_doc._element.body if n.tag!=qn('w:sectPr')]
    assert len(flow_nodes)==len(meta['blocks'])
    pages={p:[] for p in range(1,BODY+1)}
    for node,record in zip(flow_nodes,meta['blocks']):
        if node.tag!=qn('w:tbl'):
            pages[positions[f'block{record["id"]:04d}']].append(deepcopy(node));continue
        rows=list(node.iter(qn('w:tr')))
        groups={}
        for row,name in zip(rows[1:],record['rows']):groups.setdefault(positions[name],[]).append(row)
        for page,part_rows in groups.items():
            fragment=deepcopy(node)
            for row in list(fragment.iter(qn('w:tr'))):fragment.remove(row)
            fragment.append(deepcopy(rows[0]))
            for row in part_rows:fragment.append(deepcopy(row))
            pages[page].append(fragment)
    # Same source package retains original line art and image relationship IDs.
    doc=flow_doc
    for node in list(doc._element.body):
        if node.tag!=qn('w:sectPr'):doc._element.body.remove(node)
    sec=doc.sections[0];sec.orientation=WD_ORIENT.LANDSCAPE
    sec.page_width=Mm(297);sec.page_height=Mm(210)
    sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Mm(0)
    sec.header_distance=sec.footer_distance=Mm(0)
    doc.styles['Title'].font.size=Pt(16)
    doc.styles['Title'].paragraph_format.line_spacing=Pt(20)
    doc.styles['Title'].paragraph_format.space_after=Pt(3)
    doc.styles['Caption'].font.size=Pt(7)
    doc.styles['Caption'].paragraph_format.line_spacing=Pt(10)
    base.TEXT_W=WIDTH
    contents={}
    # Cover references use the compact topic map rather than the legacy A7 map.
    original_cover={1:base.compose_cover(doc,model),28:base.compose_back(doc,model)}
    for logical,nodes in original_cover.items():
        source_text=[(t,t.text) for node in nodes for t in node.iter(qn('w:t'))]
        nodes=a7.restyle(nodes,True)
        for t,text in source_text:
            if text:t.text=reference(text,topic_ranges(model))
        contents[logical]=nodes
    # Existing footer is a compact pointer; quick-operation guidance stays intact.
    for node in contents[28]:
        for t in node.iter(qn('w:t')):
            if t.text=='产品资料与固件':t.text='更多资料与交流支持见封三'
            elif t.text=='github.com/applenana/':t.text='QQ群 1002979587'
            elif t.text=='BananaThermalFirmware':t.text='扫码与开源项目地址见内封底'
    contents[27]=support.resources(doc,'a7')
    for n,nodes in pages.items():
        # Textboxes are independent logical pages; discard pagination-only bookmarks.
        for node in nodes:
            for e in list(node.iter()):
                if e.tag in (qn('w:bookmarkStart'),qn('w:bookmarkEnd')):e.getparent().remove(e)
                elif e.tag==qn('w:t') and e.text:
                    e.text=e.text.replace('本页适用于选配触屏的版本','本节适用于选配触屏的版本')
                elif e.tag==qn('w:spacing') and e.get(qn('w:lineRule'))=='exact':
                    # A repeating table header in an independent frame needs a small
                    # extra bottom allowance versus Word's continuous page flow.
                    value=int(e.get(qn('w:line'),'0'))
                    if 180<=value<=210:e.set(qn('w:line'),str(value-6))
        if nodes and nodes[0].tag==qn('w:p'):
            Paragraph(nodes[0],doc._body).paragraph_format.space_before=Pt(0)
        if nodes and nodes[-1].tag==qn('w:tbl'):
            spacer=el('w:p');spacer.append(el('w:pPr'));spacer[0].append(el('w:spacing',**{'w:line':1,'w:lineRule':'exact','w:after':0}));nodes.append(spacer)
        contents[n+2]=nodes
    for nodes in contents.values():
        for node in nodes:
            if node.getparent() is not None:node.getparent().remove(node)
    # Earlier throwaway cover nodes were composed only to allocate relationships.
    for node in list(doc._element.body):
        if node.tag!=qn('w:sectPr'):doc._element.body.remove(node)
    sid=50000
    for face,pair in enumerate(base.pairs(LOGICAL),1):
        anchor=doc.add_paragraph();pf=anchor.paragraph_format
        pf.page_break_before=face>1;pf.space_before=pf.space_after=Pt(0);pf.line_spacing=Pt(1)
        support.guide(anchor._p,5,105,292,105,f'CutH{face}')
        support.guide(anchor._p,148.5,5,148.5,205,f'CutV{face}')
        if face<=2:
            for x in (74.25,222.75):
                for row in range(2):support.guide(anchor._p,x,row*105+5,x,(row+1)*105-5,f'Fold{face}_{x}_{row}',True)
        for row in range(2):
            for col in range(2):
                for half,logical in enumerate(pair):
                    if logical==2:continue
                    x=col*148.5+half*74.25+(6 if half==0 else 7);oy=row*105
                    if logical in (1,27,28):y,height=7,91
                    else:y,height=10,88
                    sid+=1;base.box(anchor,deepcopy(contents[logical]),x,oy+y,WIDTH,height,sid)
                    if logical not in (1,27,28):
                        number=logical-2
                        for text,fy in [(f'BANANA THERMAL   {MODELS[model]["size"]} 寸单光',4),
                                        (f'使用说明书                         {number:02d}',99)]:
                            p=pp(doc,text,6.5,after=0);p.paragraph_format.line_spacing=Pt(8)
                            p._p.getparent().remove(p._p);sid+=1
                            base.box(anchor,[p._p],x,oy+fy,WIDTH,4,sid)
    doc.core_properties.subject='A7 成册 28 面 A4 横向四套 7 张双面 A4 骑马订'
    doc.core_properties.keywords='A7;28 pages;four copies;saddle stitch;QQ 1002979587'
    target=work/(stem(model)+'.docx');doc.save(target)
    evidence={'source':str(a6.OUTPUT/(a6.stem(model)+'.docx')),'topic_ranges':stable,
              'body_pages':BODY,'logical_pages':LOGICAL,'a4_faces':14,'a4_sheets':7,
              'pairs':base.pairs(LOGICAL),'body_font_pt':7.5,'table_font_pt':7}
    (work/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    print(target)


def render(model,renderer_path):
    work=WORK/model;target=work/(stem(model)+'.docx')
    spec=importlib.util.spec_from_file_location('packaged_renderer',renderer_path)
    renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
    renderer.convert_to_pdf=support.convert_with_word
    pages=renderer.rasterize(str(target),str(work/'render'),160,verbose=True,emit_pdf=True)
    print(model,len(pages),'A4 faces')
    for face in range(1,15):
        with Image.open(work/'render'/f'page-{face}.png') as im:
            im.crop((0,0,round(im.width/2),round(im.height/2))).save(work/'render'/f'proof-{face}.png')


def verify(model):
    work=WORK/model;target=work/(stem(model)+'.docx');errors=[]
    def check(value,msg):
        if not value:errors.append(msg)
    doc=Document(target);anchors=[n for n in doc._element.body if n.tag==qn('w:p')]
    check(len(anchors)==14,'14 A4 faces')
    geometry=[];bottoms=[]
    with pdfplumber.open(work/'render'/(stem(model)+'.pdf')) as pdf:
        check(len(pdf.pages)==14,'rendered face count')
        for face,(page,anchor,pair) in enumerate(zip(pdf.pages,anchors,base.pairs(LOGICAL)),1):
            check(abs(page.width-297/25.4*72)<.2 and abs(page.height-210/25.4*72)<.2,'A4 landscape')
            lines=[l for l in page.lines if .35<=l['linewidth']<=.55 and isinstance(l['stroking_color'],float)
                   and min(abs(l['stroking_color']-.549),abs(l['stroking_color']-.627))<.003]
            current=[(l['x0'],l['top'],l['x1'],l['bottom'],l['linewidth']) for l in lines];geometry.append(current)
            expected=140+(76 if face<=2 else 0)
            check(len(current)==expected,f'face {face} guide segment count')
            if face%2==0:
                mirrored=[(page.width-x1,y0,page.width-x0,y1,w) for x0,y0,x1,y1,w in current]
                check(all(min(max(abs(a-b) for a,b in zip(line,m)) for m in mirrored)<.09 for line in geometry[-2]),f'face {face} duplex guides')
            for row in range(2):
                for col in range(4):
                    left=col*page.width/4;top=row*page.height/2
                    crop=page.crop((left,top,left+page.width/4,top+page.height/2))
                    logical=pair[col%2];native=[]
                    for shape in anchor.iter('{'+support.NS['v']+'}shape'):
                        style=shape.get('style');x=float(re.search(r'margin-left:([\d.]+)pt',style)[1]);y=float(re.search(r'margin-top:([\d.]+)pt',style)[1])
                        if left<=x<crop.bbox[2] and top<=y<crop.bbox[3]:native.extend(t.text or '' for t in shape.iter(qn('w:t')))
                    expected_text=Counter(normalized(''.join(native)))
                    actual=Counter(normalized(crop.extract_text(x_tolerance=1,y_tolerance=1.5) or ''))
                    check(actual==expected_text,f'face {face} cell {row},{col} missing/extra {dict(expected_text-actual)}/{dict(actual-expected_text)}')
                    if logical==2:check(not actual and not crop.images,'inside front blank')
                    chars=[c for c in crop.chars if normalized(c['text'])]
                    check(all(c['x0']>=left+4/25.4*72 and c['x1']<=left+page.width/4-4/25.4*72 for c in chars),f'face {face} horizontal safety')
                    if logical not in (1,2,27,28):
                        body=[c for c in chars if top+8/25.4*72<c['top']<top+98/25.4*72]
                        bottom=max((c['bottom']-top for c in body),default=0)/72*25.4
                        check(bottom<=98,f'body {logical-2} bottom {bottom:.2f}')
                        bottoms.append(bottom)
                        check(f'{logical-2:02d}' in normalized(crop.extract_text() or ''),'page number')
                    if logical==27:check(len(crop.images)==1,'QQ QR image')
    # Compare all source flow text with the first copy's body frames. Repeated table headers
    # are the only added body text; all rows, instructions and prose must survive imposition.
    flow_doc=Document(work/'flow.docx')
    source=Counter(normalized(''.join(t.text or '' for t in flow_doc._element.body.iter(qn('w:t'))).replace(
        '本页适用于选配触屏的版本','本节适用于选配触屏的版本')))
    actual=Counter()
    for anchor,pair in zip(anchors,base.pairs(LOGICAL)):
        for shape in anchor.iter('{'+support.NS['v']+'}shape'):
            style=shape.get('style');x=float(re.search(r'margin-left:([\d.]+)pt',style)[1])/(72/25.4);y=float(re.search(r'margin-top:([\d.]+)pt',style)[1])/(72/25.4)
            if x<148.5 and abs(y-10)<.01:
                actual.update(normalized(''.join(t.text or '' for t in shape.iter(qn('w:t')))))
    check(not source-actual,'source flow content missing '+str(dict(source-actual)))
    report={'errors':errors,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'body_pages':24,'total_pages':28,'a4_faces':14,'a4_sheets':7,
            'max_body_bottom_mm':round(max(bottoms),2),'duplex_vector_tolerance_mm':.03}
    (work/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(model,report)
    return errors


def publish(model):
    work=WORK/model;target=work/(stem(model)+'.docx')
    report=json.loads((work/'verification.json').read_text(encoding='utf-8'))
    assert not report['errors'],report['errors']
    assert report['sha256']==hashlib.sha256(target.read_bytes()).hexdigest()
    review=json.loads((work/'visual-review.json').read_text(encoding='utf-8'))
    assert review['sha256']==report['sha256'] and review['reviewed_faces']==list(range(1,15)),'visual QA missing'
    output=a7.OUTPUT/target.name
    with target.open('rb') as source,output.open('xb') as out:shutil.copyfileobj(source,out)
    print(output)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['flow','paginate','remap','build','render','verify','publish'])
    p.add_argument('--renderer',type=Path)
    p.add_argument('--model',choices=['all','24','28','32'],default='all');args=p.parse_args()
    for model in MODELS if args.model=='all' else [args.model]:
        if args.action=='render':render(model,args.renderer)
        else:globals()[args.action](model)
