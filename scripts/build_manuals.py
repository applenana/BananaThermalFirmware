#!/usr/bin/env python3
"""Build page-designed editable manuals; PDF export is a separate QA step."""
import argparse
from pathlib import Path
from io import BytesIO
import subprocess
from manual_layout import ROOT, MANUALS, build


def extract_sources(directory: Path):
    """Retain only each supplied PDF's embedded hardware drawing, not its FAQ."""
    import pdfplumber
    from PIL import Image
    out = ROOT / "docs/assets/devices"
    out.mkdir(parents=True, exist_ok=True)
    for size, short in (("2.4", "24"), ("2.8", "28"), ("3.2", "32")):
        matches = list(directory.glob(size + "*.pdf"))
        if len(matches) != 1:
            raise ValueError(f"Expected one PDF beginning with {size}: {matches}")
        with pdfplumber.open(matches[0]) as pdf:
            img = pdf.pages[0].images[0]
            data = img["stream"].get_data()
            try:
                picture = Image.open(BytesIO(data))
            except Exception:
                picture = Image.frombytes("RGB", img["srcsize"], data)
            picture.convert("RGB").save(out / f"standard-{short}-controls.png")
        if short == "32":
            # Its labels are PDF text, not pixels in the embedded drawing.
            # Keep those labels by rendering the cropped PDF after removing only
            # the separate contact QR and its caption outside the hardware art.
            from pypdf import PdfReader, PdfWriter
            from pypdf.generic import ContentStream
            from reportlab.pdfgen.canvas import Canvas
            reader = PdfReader(matches[0])
            writer = PdfWriter()
            writer.add_page(reader.pages[0])
            page = writer.pages[0]
            qr_names = {
                name for name, ref in page["/Resources"]["/XObject"].items()
                if ref.get_object().get("/Width") == 243
                and ref.get_object().get("/Height") == 317
            }
            content = ContentStream(page.get_contents(), writer)
            content.operations = [(operands, op) for operands, op in content.operations
                                  if not (op == b"Do" and operands[0] in qr_names)]
            page.replace_contents(content)
            overlay = BytesIO()
            canvas = Canvas(overlay, pagesize=(595.32, 841.92))
            canvas.setFillColorRGB(1, 1, 1)
            canvas.rect(508, 841.92 - 306, 67, 12, stroke=0, fill=1)
            canvas.save()
            page.merge_page(PdfReader(overlay).pages[0])
            page.cropbox.lower_left = (30, 841.92 - 374.47)
            page.cropbox.upper_right = (575, 841.92 - 80)
            work = ROOT / ".work/manuals/source-drawings"
            work.mkdir(parents=True, exist_ok=True)
            cropped = work / "standard-32.pdf"
            with cropped.open("wb") as stream:
                writer.write(stream)
            subprocess.run(["pdftoppm", "-cropbox", "-scale-to", "1800", "-png",
                            "-singlefile", str(cropped), str(out / "standard-32-controls")],
                           check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["all", *MANUALS], default="all")
    parser.add_argument("--extract-source-drawings", type=Path)
    args = parser.parse_args()
    if args.extract_source_drawings:
        extract_sources(args.extract_source_drawings)
    for profile in MANUALS if args.profile == "all" else [args.profile]:
        print(build(profile))
