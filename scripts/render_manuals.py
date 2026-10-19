#!/usr/bin/env python3
"""Use the packaged DOCX PNG renderer with Windows Word PDF export.

The bundled Windows runtime has Poppler but no LibreOffice. This adapter replaces
only the PDF conversion step; page rasterization still runs through render_docx.py.
Requires installed Microsoft Word, PowerShell, and the Codex documents skill.
"""
import argparse
import importlib.util
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def convert_with_word(doc_path, user_profile, convert_tmp_dir, stem, verbose=False):
    target = Path(convert_tmp_dir) / (stem + ".pdf")
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
         "-File", str(ROOT / "scripts/export_manual_pdf.ps1"),
         "-InputDocx", str(Path(doc_path).resolve()), "-OutputPdf", str(target)],
        capture_output=True, timeout=180,
    )
    log = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    if result.returncode or not target.is_file():
        raise RuntimeError("Word PDF export failed: " + log)
    return str(target), log


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderer", required=True, type=Path)
    parser.add_argument("--profile", choices=["all", "standard", "dual"], default="all")
    parser.add_argument("--dpi", type=int, default=140)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("packaged_renderer", args.renderer)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    renderer.convert_to_pdf = convert_with_word
    from build_manuals import MANUALS
    for profile in MANUALS if args.profile == "all" else [args.profile]:
        stem = MANUALS[profile][1]
        out = ROOT / ".work/manuals" / profile
        pages = renderer.rasterize(str(ROOT / "artifacts" / (stem + ".docx")),
                                   str(out), args.dpi, verbose=True, emit_pdf=True)
        shutil.copy2(out / (stem + ".pdf"), ROOT / "artifacts" / (stem + ".pdf"))
        print(f"{profile}: {len(pages)} pages")
