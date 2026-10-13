#!/usr/bin/env python3
"""Generate print-ready A4 one-sheet eight-page mini-zines from content/*.yaml."""
from pathlib import Path
import argparse
import os
import yaml
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader

BASE = Path(__file__).resolve().parent
CONTENT = BASE / "content"
OUT = BASE / "output"
INK, MUTED, ACCENT = "#25343c", "#52646a", "#176e73"

def find_font():
    choices = [
        os.environ.get("JAPANESE_FONT", ""),
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
    ]
    for path in choices:
        if path and Path(path).exists():
            return path
    raise SystemExit("Japanese font not found. Set JAPANESE_FONT=/path/to/Japanese-font.ttf")

def make_panel(number, title, subtitle, entries, vol, fontpath):
    image = Image.new("RGB", (620, 877), "white")
    d = ImageDraw.Draw(image)
    def font(size): return ImageFont.truetype(fontpath, size)
    d.rectangle((10, 10, 610, 867), outline="#d7e1df", width=2)
    d.rectangle((10, 10, 610, 82), fill=ACCENT)
    d.text((30, 27), title, fill="white", font=font(32))
    d.text((572, 825), str(number), fill=MUTED, font=font(19))
    if number == 1:
        d.text((35, 168), f"VOL. {vol}", fill=ACCENT, font=font(28))
        # Wrap cover title to prevent bleed into adjacent panels.
        words = title.split()
        lines, line = [], ""
        for word in words:
            test = (line + " " + word).strip()
            if d.textbbox((0, 0), test, font=font(40))[2] > 545 and line:
                lines.append(line); line = word
            else: line = test
        if line: lines.append(line)
        for i, t in enumerate(lines): d.text((35, 230 + i*55), t, fill=INK, font=font(40))
        d.text((35, 385), subtitle, fill=MUTED, font=font(23))
        d.text((35, 685), "JAPAN POCKET ZINES", fill=ACCENT, font=font(23))
        d.text((35, 725), "Fold • Explore • Decode", fill=INK, font=font(20))
    else:
        n = len(entries)
        gap = min(145, 695 / max(n, 1))
        for i, (japanese, romaji, meaning) in enumerate(entries):
            y = int(108 + i*gap)
            size = 34
            while size > 18 and d.textbbox((0,0), japanese, font=font(size))[2] > 558:
                size -= 1
            d.text((28,y), japanese, fill=INK, font=font(size))
            d.text((30,y+48), romaji, fill=ACCENT, font=font(19))
            d.text((30,y+77), meaning, fill=MUTED, font=font(18))
    return image

def build_one(source, fontpath):
    data = yaml.safe_load(source.read_text(encoding="utf8"))
    assert len(data["pages"]) == 7, f"{source}: expected seven inside pages"
    panels = {1: make_panel(1, data["title"], data["subtitle"], [], data["volume"], fontpath)}
    for number, info in enumerate(data["pages"], start=2):
        panels[number] = make_panel(number, info["title"], "", info["entries"], data["volume"], fontpath)
    sheet = Image.new("RGB", (2480, 1754), "white")
    # Standard eight-page slit-fold imposition:
    # top row upside-down 5,4,3,2; bottom row upright 6,7,8,1
    for col, number in enumerate([5,4,3,2]):
        sheet.paste(panels[number].rotate(180), (col*620, 0))
    for col, number in enumerate([6,7,8,1]):
        sheet.paste(panels[number], (col*620, 877))
    return data, sheet

def instructions(c):
    w,h=landscape(A4)
    c.setFont("Helvetica-Bold",22);c.drawString(45,h-65,"HOW TO FOLD YOUR MINI-ZINE")
    steps=[
        "1. Print the first four pages on A4 landscape, single-sided, at 100% scale.",
        "2. Fold a sheet lengthwise in half, then unfold.",
        "3. Fold widthwise in half, unfold; fold each short edge to the middle.",
        "4. Unfold. Cut along the center horizontal fold, ONLY across the two middle panels.",
        "5. Fold lengthwise. Push the ends together so the slit opens into a diamond.",
        "6. Collapse into an eight-page booklet, with the cover on the outside.",
        "The inverted panels on the print sheet are intentional."
    ]
    c.setFont("Helvetica",12)
    for i,step in enumerate(steps):c.drawString(45,h-112-i*36,step)
    x,y,ww,hh=140,75,540,110
    c.setStrokeColorRGB(.1,.45,.46);c.setLineWidth(2);c.rect(x,y,ww,hh)
    for j in range(1,4):c.line(x+ww*j/4,y,x+ww*j/4,y+hh)
    c.line(x,y+hh/2,x+ww,y+hh/2)
    c.setStrokeColorRGB(.8,.2,.2);c.setLineWidth(5)
    c.line(x+ww/4,y+hh/2,x+3*ww/4,y+hh/2)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--font", help="Path to Japanese-capable TTF/TTC font")
    args=parser.parse_args()
    fontpath=args.font or find_font()
    OUT.mkdir(exist_ok=True)
    combined=canvas.Canvas(str(OUT/"japan-pocket-zines.pdf"),pagesize=landscape(A4))
    for source in sorted(CONTENT.glob("*.yaml")):
        data,sheet=build_one(source,fontpath)
        sheet.save(OUT/f"volume-{data['volume']}-preview.png")
        w,h=landscape(A4)
        combined.drawImage(ImageReader(sheet),0,0,w,h)
        combined.showPage()
    instructions(combined)
    combined.save()
    print(f"Created {OUT/'japan-pocket-zines.pdf'}")

if __name__=="__main__":
    main()
