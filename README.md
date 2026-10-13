# Japan Pocket Zines: editable source

Four eight-page mini-zines, each printed on one A4 landscape sheet and folded with one central cut.

## Contents

- `content/*.yaml`: Editable Japanese text, Rōmaji, English and page titles.
- `generate.py`: Reusable renderer, consistent cover and panel design.
- `output/japan-pocket-zines.pdf`: Regenerated five-page PDF (four print sheets + one instructions page).
- `output/volume-*-preview.png`: Full-sheet previews.

## Build

```bash
python3 -m pip install -r requirements.txt
python3 generate.py
```

The renderer needs a Japanese-capable font. On Linux, install Noto Sans CJK.
On macOS, if auto-detection fails, supply an installed Japanese font:

```bash
python3 generate.py --font '/path/to/your/Japanese-font.ttc'
```

You can also set `JAPANESE_FONT` in the environment.

## Editing

Change the Japanese, Rōmaji or English in the YAML files, then rerun `generate.py`.
Each YAML volume has seven inside pages; page 1 is the generated cover.
The generator places top panels upside-down in the correct fold order.

## Print

Print pages 1–4, single-sided, A4 landscape, 100% / actual size.
Page 5 contains shared folding instructions.

## Provenance and limitations

This is a **reconstructed, editable source project**, not the original ephemeral
Python notebook/source used to make every earlier PDF. The content follows the
conversation's four zines, with a few entries reformatted to fit the shared template.
It has not received a professional Japanese-language review. In particular,
verify vegetarian requirements directly with restaurants: dashi and sauces
can contain fish even when the dish looks vegetarian.

No font files are bundled.
