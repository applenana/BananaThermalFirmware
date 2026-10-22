"""Copy approved A7 impositions, retaining only cover-side saddle-stitch guides."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

from lxml import etree
import pdfplumber
from PIL import Image

import build_compact_a7 as compact
from render_manuals import convert_with_word

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.work/a7-cover-guides'
OUTPUT = ROOT / 'artifacts/print-booklets/a7'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'v': 'urn:schemas-microsoft-com:vml'}


def paths(model):
    source = OUTPUT / (compact.stem(model) + '.docx')
    name = compact.stem(model).replace('_资料支持与双面对齐版', '_仅封面装订虚线版') + '.docx'
    return source, WORK / model / name, OUTPUT / name


def cleaned(xml):
    root = etree.fromstring(xml)
    removed = []
    anchors = root.find('w:body', NS).findall('w:p', NS)
    assert len(anchors) == 14
    for face, anchor in enumerate(anchors, 1):
        for run in list(anchor):
            lines = run.findall('.//v:line', NS)
            if not lines:
                continue
            ident = lines[0].get('id', '')
            assert ident.startswith(('CutH', 'CutV', 'Fold')), ident
            if ident.startswith(('CutH', 'CutV')) or face != 1:
                anchor.remove(run)
                removed.append(ident)
    return root, removed


def build(model):
    source, draft, _ = paths(model)
    draft.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(source) as src:
        root, removed = cleaned(src.read('word/document.xml'))
        with draft.open('xb') as stream, ZipFile(stream, 'w') as dst:
            for entry in src.infolist():
                data = (etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                        if entry.filename == 'word/document.xml' else src.read(entry.filename))
                dst.writestr(entry, data)
    evidence = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'removed_line_segments': len(removed), 'retained': 'Fold guides on cover side only'}
    (draft.parent / 'evidence.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print(model, evidence)


def render(model, renderer_path):
    _, draft, _ = paths(model)
    spec = importlib.util.spec_from_file_location('packaged_renderer', renderer_path)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    renderer.convert_to_pdf = convert_with_word
    pages = renderer.rasterize(str(draft), str(draft.parent / 'render'), 160,
                                verbose=True, emit_pdf=True)
    print(model, len(pages), 'A4 faces')
    # Brief visual review: one cover pair and one interior pair per model.
    for face in (1, 3):
        with Image.open(draft.parent / 'render' / f'page-{face}.png') as image:
            image.crop((0, 0, image.width // 2, image.height // 2)).save(
                draft.parent / f'preview-{face}.png')


def verify(model):
    source, draft, _ = paths(model)
    evidence = json.loads((draft.parent / 'evidence.json').read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == evidence['source_sha256']
    with ZipFile(source) as src, ZipFile(draft) as dst:
        assert src.namelist() == dst.namelist()
        expected, _ = cleaned(src.read('word/document.xml'))
        actual = etree.fromstring(dst.read('word/document.xml'))
        assert etree.tostring(expected, method='c14n') == etree.tostring(actual, method='c14n')
        for name in src.namelist():
            if name != 'word/document.xml':
                assert src.read(name) == dst.read(name), name
        for face, anchor in enumerate(actual.find('w:body', NS).findall('w:p', NS), 1):
            lines = anchor.findall('.//v:line', NS)
            assert (len(lines) > 0) == (face == 1)
            assert all(line.get('id', '').startswith('Fold1_') for line in lines)
    baseline = ROOT / '.work/compact-a7' / model / 'render' / (source.stem + '.pdf')
    max_text_delta = 0
    with pdfplumber.open(draft.parent / 'render' / (draft.stem + '.pdf')) as new, pdfplumber.open(baseline) as old:
        assert len(new.pages) == len(old.pages) == 14
        for before, after in zip(old.pages, new.pages):
            assert before.width == after.width and before.height == after.height
            assert before.extract_text() == after.extract_text()
            assert len(before.chars) == len(after.chars)
            for a, b in zip(before.chars, after.chars):
                assert a['text'] == b['text']
                delta = max(abs(a['x0'] - b['x0']), abs(a['top'] - b['top']))
                # Word PDF font positioning has sub-0.1pt serialization variation.
                assert delta < 0.1, delta
                max_text_delta = max(max_text_delta, delta)
            assert [(i['x0'], i['top'], i['width'], i['height']) for i in before.images] == [
                (i['x0'], i['top'], i['width'], i['height']) for i in after.images]
    report = {'sha256': hashlib.sha256(draft.read_bytes()).hexdigest(), 'a4_faces': 14,
              'finished_pages': 28, 'all_text_and_image_positions_preserved': True,
              'only_cover_side_fold_guides': True, 'max_text_export_delta_pt': max_text_delta}
    (draft.parent / 'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(model, report)


def publish(model):
    _, draft, output = paths(model)
    report = json.loads((draft.parent / 'verification.json').read_text())
    assert report['sha256'] == hashlib.sha256(draft.read_bytes()).hexdigest()
    with output.open('xb') as stream:
        stream.write(draft.read_bytes())
    print(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'render', 'verify', 'publish'])
    parser.add_argument('--renderer', type=Path)
    args = parser.parse_args()
    for model in ('24', '28', '32'):
        if args.action == 'render':
            render(model, args.renderer)
        else:
            globals()[args.action](model)
