#!/usr/bin/env python3
"""Add offline resource pages and duplex-symmetric production guides to A6/A7.

The approved originals remain untouched. Only the outer sheet is edited;
existing body frames and page order are preserved verbatim.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Mm, Pt
from docx.text.paragraph import Paragraph
from lxml import etree
from PIL import Image, ImageChops, ImageDraw
import pdfplumber

import build_print_booklets as base
import build_a6_booklets as a6
import build_a7_booklets as a7
from manual_layout import el, font
from render_manuals import convert_with_word
from verify_print_booklets import normalized

ROOT=base.ROOT
WORK=ROOT/'.work/booklet-support'
ASSET=ROOT/'docs/assets/manual-design/qq-group-1002979587.jpg'
QR_SOURCE=Path('C:/Users/applenana/Downloads/qrcode_1792490970158.jpg')
NS={**a6.NS,'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
EDIT_SUFFIX='_资料支持与双面对齐版'
PROJECTS=[('上位机','NextBananaThermalStudio'),
          ('Python 上位机','BananaThermal-Studio'),
          ('在线文档与固件','BananaThermalFirmware')]
PREFIX='https://github.com/applenana/'


def config(size):
    return dict(builder=a6,w=210,h=297,half=105,row=148.5,text=88,x=[114],y=10,height=131,
                pages=16,folds=[105],copies=2) if size=='a6' else dict(
                builder=a7,w=297,h=210,half=74.25,row=105,text=61.25,x=[81.25,229.75],
                y=7,height=91,pages=30,folds=[74.25,222.75],copies=4)


def paths(size,model):
    builder=config(size)['builder'];stem=builder.stem(model)
    source=builder.OUTPUT/(stem+'.docx')
    draft=WORK/size/model/(stem+EDIT_SUFFIX+'.docx')
    target=builder.OUTPUT/draft.name
    return source,draft,target


def paragraph(doc,text,size,bold=False,after=0,before=0,center=False):
    p=doc.add_paragraph();pf=p.paragraph_format
    pf.space_before=Pt(before);pf.space_after=Pt(after)
    pf.line_spacing=Pt(size+2.5)
    pf.keep_with_next=False;pf.widow_control=False
    if center:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    font(p.add_run(text),size,bold)
    return p


def resources(doc,size):
    """Use the previously blank inside back cover; retain back-cover quick tips."""
    start=len(doc._element.body)
    small=size=='a7'
    paragraph(doc,'资料与交流支持',12 if small else 16,True,after=3)
    paragraph(doc,'扫码加入 QQ 群，获取更多资料与交流支持。',8.5 if small else 10,after=2)
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(0)
    p.paragraph_format.line_spacing=1
    width=30 if small else 36
    pic=p.add_run().add_picture(str(ASSET),width=Mm(width))
    # Native crop only: retain the exact original JPEG, its quiet zone and colours.
    crop=(.07,.277,.07,.239)
    with Image.open(ASSET) as im:
        ratio=im.height*(1-crop[1]-crop[3])/(im.width*(1-crop[0]-crop[2]))
    pic.height=Mm(width*ratio)
    fill=pic._inline.xpath('.//pic:blipFill')[0]
    fill.insert(1,el('a:srcRect',l=7000,t=27700,r=7000,b=23900))
    pic._inline.docPr.set('descr','QQ 群 1002979587 加群二维码')
    paragraph(doc,'QQ群 1002979587',9.5 if small else 11,True,after=5,center=True)
    paragraph(doc,'开源项目',10 if small else 12,True,after=3)
    for label,repo in PROJECTS:
        paragraph(doc,label,9 if small else 10.5,True,after=0)
        # Deliberate wrap at a path boundary; full address remains readable offline.
        paragraph(doc,PREFIX+'\n'+repo,8 if small else 9.5,after=3 if small else 6)
    nodes=list(doc._element.body)[start-1:-1]
    for node in nodes:doc._element.body.remove(node)
    return nodes


def symmetric_dashes(start,end,dash=2,gap=1.5):
    """Explicit symmetric solid segments: reflection cannot change dash phase."""
    mid=(start+end)/2;step=dash+gap
    result=[]
    n=int((end-start)/2/step)+1
    for k in range(-n,n+1):
        a=max(start,mid+k*step-dash/2);b=min(end,mid+k*step+dash/2)
        if b>a+.05:result.append((a,b))
    return result


def guide(anchor,x0,y0,x1,y1,ident,fold=False):
    """Draw in paper coordinates, not paragraph/margin-relative coordinates."""
    vertical=abs(x1-x0)<.001
    spans=symmetric_dashes(y0 if vertical else x0,y1 if vertical else x1,
                           dash=3 if fold else 2,gap=2 if fold else 1.5)
    for i,(a,b) in enumerate(spans):
        x,y,w,h=(x0,a,0,b-a) if vertical else (a,y0,b-a,0)
        a7.guide(anchor,x,y,w,h,f'{ident}_{i}')
        line=anchor[-1][0][0]
        stroke=line.find('{'+NS['v']+'}stroke')
        stroke.set('dashstyle','solid')
        line.set('strokeweight','0.4pt' if fold else '0.5pt')
        line.set('strokecolor','#A0A0A0' if fold else '#8C8C8C')


def remove_guides(anchor):
    for run in list(anchor):
        if any(n.tag=='{'+NS['v']+'}line' for n in run.iter()):anchor.remove(run)


def body_signature(doc):
    """Canonical frames beyond the outer sheet, independent of guide edits."""
    result=[]
    for anchor in list(doc._element.body)[:-1][2:]:
        result.append([etree.tostring(n,method='c14n') for n in anchor.iter('{'+NS['v']+'}shape')])
    return result


def build(size,model):
    cfg=config(size);source,draft,target=paths(size,model)
    draft.parent.mkdir(parents=True,exist_ok=True)
    doc=Document(source);prior=body_signature(doc)
    anchors=list(doc._element.body)[:-1]
    assert len(anchors)==cfg['pages']
    # Keep all back-cover quick tips, update only the existing resource footer.
    for shape in anchors[0].iter('{'+NS['v']+'}shape'):
        texts=list(shape.iter(qn('w:t')))
        for t in texts:
            if t.text=='产品资料与固件':t.text='更多资料与交流支持见封三'
            elif t.text=='github.com/applenana/':t.text='QQ群 1002979587'
            elif t.text=='BananaThermalFirmware':t.text='扫码与开源项目地址见内封底'
    nodes=resources(doc,size)
    for row in range(2):
        for col,x in enumerate(cfg['x']):
            base.box(Paragraph(anchors[1],doc._body),deepcopy(nodes),x,
                     row*cfg['row']+cfg['y'],cfg['text'],cfg['height'],80000+row*10+col)
    for i,anchor in enumerate(anchors,1):
        remove_guides(anchor)
        guide(anchor,5,cfg['h']/2,cfg['w']-5,cfg['h']/2,f'CutH{i}')
        if size=='a7':guide(anchor,cfg['w']/2,5,cfg['w']/2,cfg['h']-5,f'CutV{i}')
        # Both sides of the outer sheet have identical, reflection-symmetric folds.
        if i<=2:
            for x in cfg['folds']:
                for row in range(2):
                    guide(anchor,x,row*cfg['row']+5,x,(row+1)*cfg['row']-5,
                          f'Fold{i}_{x}_{row}',True)
    assert body_signature(doc)==prior,'body frames changed'
    doc.core_properties.subject+=' 资料支持及双面辅助线校正版'
    doc.save(draft)
    evidence={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'qr_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest(),
              'source_body_preserved':True,'output':str(target)}
    (draft.parent/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    print(draft)


def render(size,model,renderer_path):
    _,draft,_=paths(size,model)
    spec=importlib.util.spec_from_file_location('packaged_renderer',renderer_path)
    renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
    renderer.convert_to_pdf=convert_with_word
    pages=renderer.rasterize(str(draft),str(draft.parent/'render'),160,verbose=True,emit_pdf=True)
    print(size,model,len(pages),'faces')


def verify(size,model):
    cfg=config(size);source,draft,_=paths(size,model)
    errors=[]
    def check(value,label):
        if not value:errors.append(label)
    doc=Document(draft);old=Document(source)
    check(body_signature(doc)==body_signature(old),'body frames changed')
    text=''.join(doc._element.body.itertext())
    for label,repo in PROJECTS:check(repo in text,'project missing '+repo)
    check('1002979587' in text,'group missing')
    anchors=list(doc._element.body)[:-1]
    geometries=[]
    with pdfplumber.open(draft.parent/'render'/(draft.stem+'.pdf')) as pdf:
        check(len(pdf.pages)==cfg['pages'],'page count')
        for face,(page,anchor) in enumerate(zip(pdf.pages,anchors),1):
            # PDF line coordinates are the printed output, not the intended XML positions.
            def is_guide(line):
                color=line.get('stroking_color')
                colors=color if isinstance(color,(list,tuple)) else [color]
                return colors[0] is not None and .35<=line['linewidth']<=.55 and all(
                    min(abs(c-140/255),abs(c-160/255))<.004 for c in colors)
            lines=[l for l in page.lines if is_guide(l)]
            cut=[l for l in lines if abs(l['linewidth']-.5)<.03]
            expected=len(symmetric_dashes(5,cfg['w']-5))
            if size=='a7':expected+=len(symmetric_dashes(5,cfg['h']-5))
            check(len(cut)==expected,f'face {face} cutting segment count {len(cut)}/{expected}')
            geometry=[(l['x0'],l['top'],l['x1'],l['bottom'],l['linewidth']) for l in lines]
            geometries.append(geometry)
            # Compare the actual back-side vector geometry after a physical left/right flip.
            if face%2==0:
                before=geometries[-2]
                mirror=[(page.width-x1,y0,page.width-x0,y1,w) for x0,y0,x1,y1,w in geometry]
                for line in before:
                    delta=min(max(abs(a-b) for a,b in zip(line,m)) for m in mirror)
                    check(delta<.09,f'faces {face-1}/{face} mirrored line mismatch {delta:.3f}pt')
            # Verify every native text frame against the rendered cell to detect overflow.
            for row in range(2):
                for col in range(2 if size=='a6' else 4):
                    left=col*page.width/(2 if size=='a6' else 4);top=row*page.height/2
                    crop=page.crop((left,top,left+page.width/(2 if size=='a6' else 4),top+page.height/2))
                    native=[]
                    for shape in anchor.iter('{'+NS['v']+'}shape'):
                        style=shape.get('style');x=float(re.search(r'margin-left:([\d.]+)pt',style)[1])
                        y=float(re.search(r'margin-top:([\d.]+)pt',style)[1])
                        if left<=x<crop.bbox[2] and top<=y<crop.bbox[3]:
                            native.extend(t.text or '' for t in shape.iter(qn('w:t')))
                    expected_text=Counter(normalized(''.join(native)))
                    actual=Counter(normalized(crop.extract_text(x_tolerance=1,y_tolerance=2) or ''))
                    check(expected_text==actual,f'face {face} cell {row},{col} missing/extra {dict(expected_text-actual)}/{dict(actual-expected_text)}')
                    if face==2 and col%2==1:
                        check(len(crop.images)==1,f'resource QR missing {row},{col}')
                        chars=[c for c in crop.chars if normalized(c['text'])]
                        check(max(c['bottom'] for c in chars)<top+(cfg['row']-5)/25.4*72,'resource footer overflow')
        max_delta=0
        # Symmetry about both paper axes is useful for independent printer flip settings too.
        for page,geometry in zip(pdf.pages,geometries):
            for line in geometry:
                x0,y0,x1,y1,w=line
                for reflected in [(page.width-x1,y0,page.width-x0,y1,w),
                                  (x0,page.height-y1,x1,page.height-y0,w)]:
                    delta=min(max(abs(a-b) for a,b in zip(reflected,m)) for m in geometry)
                    max_delta=max(max_delta,delta)
        check(max_delta<.09,f'axis symmetry mismatch {max_delta:.3f}pt')
    evidence=json.loads((draft.parent/'evidence.json').read_text(encoding='utf-8'))
    check(hashlib.sha256(source.read_bytes()).hexdigest()==evidence['source_sha256'],'original changed')
    pixel_matches=0;visual_differences=[];review_images=[]
    for face in range(3,cfg['pages']+1):
        baseline=ROOT/f'.work/{size}-booklets'/model/'render'/f'page-{face}.png'
        latest=draft.parent/'render'/f'page-{face}.png'
        with Image.open(baseline).convert('RGB') as before,Image.open(latest).convert('RGB') as after:
            check(before.size==after.size,f'face {face} raster size')
            cols=2 if size=='a6' else 4
            for row in range(2):
                for col in range(cols):
                    # Exclude only the paper split boundaries occupied by guide lines.
                    box=(round(col*after.width/cols)+4,round(row*after.height/2)+4,
                         round((col+1)*after.width/cols)-4,round((row+1)*after.height/2)-4)
                    equal=ImageChops.difference(before.crop(box),after.crop(box)).getbbox() is None
                    if not equal:
                        old_cell=before.crop(box);new_cell=after.crop(box)
                        delta=ImageChops.difference(old_cell,new_cell)
                        bounds=delta.getbbox()
                        around=(max(0,bounds[0]-35),max(0,bounds[1]-30),
                                min(new_cell.width,bounds[2]+35),min(new_cell.height,bounds[3]+30))
                        old_crop=old_cell.crop(around);new_crop=new_cell.crop(around)
                        canvas=Image.new('RGB',(old_crop.width*2+15,old_crop.height+24),'white')
                        ImageDraw.Draw(canvas).text((3,3),f'{size} {model} face {face} cell {row},{col}: before / after',fill='black')
                        canvas.paste(old_crop,(0,24));canvas.paste(new_crop,(old_crop.width+15,24))
                        review_images.append(canvas)
                        visual_differences.append([face,row,col])
                    pixel_matches+=int(equal)
    if review_images:
        canvas=Image.new('RGB',(max(im.width for im in review_images),sum(im.height+10 for im in review_images)),'#eeeeee')
        y=0
        for im in review_images:canvas.paste(im,(0,y));y+=im.height+10
        canvas.save(draft.parent/'raster-differences.png')
        review=draft.parent/'visual-review.json'
        approved=json.loads(review.read_text(encoding='utf-8')) if review.exists() else {}
        check(approved.get('reviewed_cells')==visual_differences and approved.get('sha256')==hashlib.sha256(draft.read_bytes()).hexdigest(),
              'raster differences need visual review')
    report={'errors':errors,'draft_sha256':hashlib.sha256(draft.read_bytes()).hexdigest(),
            'duplex_max_vector_error_mm':round(max_delta/72*25.4,4),
            'unchanged_body_raster_cells':pixel_matches,'raster_difference_cells':visual_differences}
    (draft.parent/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(size,model,report)
    return errors


def publish(size,model):
    _,draft,target=paths(size,model)
    report=json.loads((draft.parent/'verification.json').read_text(encoding='utf-8'))
    assert not report['errors'],report['errors']
    assert report['draft_sha256']==hashlib.sha256(draft.read_bytes()).hexdigest()
    with draft.open('rb') as source,target.open('xb') as out:shutil.copyfileobj(source,out)
    print(target)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['build','render','verify','publish'])
    p.add_argument('--size',choices=['all','a6','a7'],default='all')
    p.add_argument('--model',choices=['all','24','28','32'],default='all')
    p.add_argument('--renderer',type=Path)
    args=p.parse_args()
    if args.action=='build' and not ASSET.exists():
        ASSET.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(QR_SOURCE,ASSET)
    errors=0
    for size in ['a6','a7'] if args.size=='all' else [args.size]:
        for model in ['24','28','32'] if args.model=='all' else [args.model]:
            if args.action=='build':build(size,model)
            elif args.action=='render':render(size,model,args.renderer)
            elif args.action=='verify':errors+=len(verify(size,model))
            else:publish(size,model)
    raise SystemExit(bool(errors))
