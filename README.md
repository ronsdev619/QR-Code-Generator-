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
