#!/usr/bin/env python3
"""Render imposed DOCX booklets through the skill renderer and installed Word.

All PDF/PNG proof files stay in ignored .work, not in the delivery directory.
"""
import argparse
import importlib.util
from pathlib import Path
from render_manuals import convert_with_word, ROOT
from build_print_booklets import MODELS, OUTPUT, stem


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderer", required=True, type=Path)
    parser.add_argument("--model", choices=["all", *MODELS], default="all")
    parser.add_argument("--dpi", type=int, default=140)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("packaged_renderer", args.renderer)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    renderer.convert_to_pdf = convert_with_word
    for model in MODELS if args.model == "all" else [args.model]:
        target = ROOT / ".work/print-booklets" / model / "render"
        pages = renderer.rasterize(str(OUTPUT / (stem(model) + ".docx")),
                                   str(target), args.dpi, verbose=True, emit_pdf=True)
        print(f"{model}: {len(pages)} A4 sides")
