# QR-Code-Generator

A QR code generator and decoder built from scratch in Python — no `qrcode` or `zxing` library does the encoding. It implements the ISO/IEC 18004 pipeline by hand: byte-mode bit stream construction, Reed–Solomon error correction, module placement via the zig-zag data pattern, all 8 masking patterns, and BCH format-information encoding, for Version 1 (21×21) symbols at ECC level L.

Includes a Tkinter GUI with accessible color presets (colorblind-safe palettes, WCAG contrast checking), a matching decoder that reads a generated matrix back to text, and a pandas/matplotlib analytics dashboard that tracks generation history.

## Features

- **From-scratch QR encoding** — mode indicator, character count, byte-mode data, Reed–Solomon(26,19) ECC, all 8 mask patterns, BCH(15,5) format info
- **Matching decoder** — unmasks, extracts the zig-zag bit stream, runs RS error correction, and parses the byte-mode payload back to text
- **GUI** (`qr_gui.py`) — live character counter, console-style generation log, PNG export with a spec-compliant quiet zone
- **Accessible customization** (`qr_customizer.py`) — colorblind-safe presets (deuteranopia/protanopia/tritanopia), WCAG contrast ratio validation, module shape variants
- **Analytics** (`qr_analytics.py`) — every generation attempt is logged to CSV; view success rate, text-length distribution, and ECC usage as charts
- **Unit tests** (`test_qr.py`, `test_qr_logger.py`) — 13 tests covering the encode/matrix/generate pipeline and the logger

## How it works

```
qr_gui.py ──┬──> qr_generator.py ──┬──> qr_encoder.py   (bit stream, RS ECC)
            │                      └──> qr_matrix.py    (placement, masking, format info)
            │                      └──> qr_analytics.py (CSV logging)
            └──> qr_customizer.py  (color/shape presets, accessibility checks)

qr_decoder.py  ── standalone, reverses qr_encoder.py + qr_matrix.py to read a matrix back to text
```

| Module | Responsibility |
|---|---|
| `qr_encoder.py` | Text → bit stream → codewords → Reed–Solomon ECC |
| `qr_matrix.py` | Builds the 21×21 grid: finder/timing/dark patterns, data placement, masking, format info |
| `qr_decoder.py` | Reverses the pipeline: unmask → extract bits → RS decode → parse byte-mode payload |
| `qr_generator.py` | Orchestrates encode → build → render, plus the CLI demo/logging entry points |
| `qr_customizer.py` | Color/shape presets and accessibility validation, applied on top of the raw matrix |
| `qr_gui.py` | Tkinter front end |
| `qr_analytics.py` | CSV logging + matplotlib dashboards |
## Demo

`python qr_generator.py` runs five fixed test strings through the full pipeline and writes each console trace to `demo_1.txt`–`demo_5.txt`. They're deliberately chosen to exercise both the happy path and the input validation:

| # | Input | Demonstrates |
|---|---|---|
| 1 | `known` | Baseline byte-mode encode |
| 2 | `We've succeeded!` | Punctuation in the payload |
| 3 | `~¡256_-_aA&ñ` | Extended Latin-1 characters (¡, ñ) |
| 4 | `From α to ɷ...` | Rejected — Greek/IPA characters fall outside ISO-8859-1, so encoding raises a caught `UnicodeEncodeError` |
| 5 | `Sugarplum_Fairy_Nightmare` | Rejected — 25 bytes exceeds the 17-character Version 1/Level L capacity |

The last two fail on purpose: they show `qr_encoder.py`'s validation catching bad input and `qr_generator.py` logging it as a failed attempt (visible in the analytics dashboard) rather than crashing.

## Limitations

This is a Version 1 / ECC level L implementation only — the smallest QR symbol size, which caps input at **17 characters** in byte mode (ISO-8859-1). Larger versions, alphanumeric/numeric/kanji modes, and higher ECC levels aren't implemented. It's meant to demonstrate the algorithm clearly, not to replace a production QR library for real-world capacity needs.

## Install & run

```bash
pip install -r requirements.txt

# GUI
python qr_gui.py

# CLI demo — generates 5 sample QR codes, writes text-art output files,
# and prints a recent-activity summary
python qr_generator.py

# Tests
python -m unittest test_qr.py test_qr_logger.py -v
```

