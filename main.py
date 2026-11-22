#!/usr/bin/env python3
"""Deterministic daily news image generator — PURE PYTHON STDLIB ONLY.

Produces exactly one file: /output/entry.png (PNG, 1024x1024).
All news content hardcoded. No network access. Byte-identical output
on every run (no timestamps, no randomness, no embedded metadata).

No third-party imports. PNG chunks (IHDR/IDAT/IEND) written manually
with struct + zlib. Text rendered from an inline bitmap font (font.py).
"""

import os
import struct
import zlib

from font import GLYPHS, CELL_W, CELL_H, cell_w, line_h, text_w

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
WIDTH = 1024
HEIGHT = 1024
OUTPUT_FILE = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")

# High-contrast limited palette.
BG_COLOR = (14, 17, 23)          # near-black background
INK_COLOR = (245, 245, 245)      # near-white text
ACCENT_COLOR = (231, 76, 60)     # strong red accent for main story
MUTED_COLOR = (139, 145, 155)    # muted grey for secondary text

PAD = 40

DATE_LINE_MAIN = "THE WORLD IN ONE DAY"
DATE_LINE_SUB = "SUNDAY 22 NOVEMBER 2026"

# Hardcoded news content (no network access at runtime).
NEWS = {
    "main": {
        "headline": "RUSSIAN MISSILES LAND IN POLAND",
        "sub": 'NATO condemns airspace violation; Rutte vows to defend "every inch"',
    },
    "supporting": [
        {
            "headline": "IRAN STRIKES U.S. BASES IN BAHRAIN",
            "sub": "IRGC missile-drone attack on U.S. positions; civilian facility hit.",
        },
        {
            "headline": "COP31 DEADLOCKED IN OVERTIME",
            "sub": "Draft deal drops fossil fuels; EU says good deal or no deal.",
        },
        {
            "headline": "TECH STOCKS CRASH ON WALL STREET",
            "sub": "Nasdaq -5.3%, worst week since 2020; Nvidia -14%.",
        },
    ],
}

FOOTER = 'Sources: AP · Reuters · Washington Post'

# Scales per element.
SCALE_MAIN_TITLE = 6
SCALE_MAIN_SUB = 4
SCALE_MAIN_HEAD = 8
SCALE_MAIN_SUBHEAD = 4
SCALE_SUPPORT_HEAD = 4
SCALE_SUPPORT_SUB = 3
SCALE_FOOTER = 3


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, color):
        self.w = w
        self.h = h
        r, g, b = color
        self.pix = bytearray([r, g, b] * (w * h))

    def idx(self, x, y):
        return (y * self.w + x) * 3

    def rect(self, x0, y0, x1, y1, color):
        r, g, b = color
        for y in range(y0, y1):
            base = (y * self.w + x0) * 3
            for x in range(x0, x1):
                self.pix[base] = r
                self.pix[base + 1] = g
                self.pix[base + 2] = b
                base += 3

    def put_glyph(self, ch, x, y, scale, color):
        g = GLYPHS.get(ch)
        if g is None:
            return
        r, g2, b = color
        for bitrow in g:
            col = x
            for bitpos in range(4, -1, -1):
                if bitrow & (1 << bitpos):
                    for dy in range(scale):
                        py = y + dy
                        if py >= self.h:
                            continue
                        base = (py * self.w + col) * 3
                        for dx in range(scale):
                            px = col + dx
                            if px >= self.w:
                                break
                            self.pix[base] = r
                            self.pix[base + 1] = g2
                            self.pix[base + 2] = b
                            base += 3
                col += scale
            y += scale

    def put_text(self, text, x, y, scale, color):
        text = text.upper()
        cx = x
        for ch in text:
            self.put_glyph(ch, cx, y, scale, color)
            cx += cell_w(scale)
        return cx

    def save_png(self, path):
        w, h = self.w, self.h
        row_bytes = bytearray()
        for y in range(h):
            row_bytes.append(0)  # filter type 0
            base = y * w * 3
            row_bytes.extend(self.pix[base:base + w * 3])

        compressed = zlib.compress(row_bytes, 6)

        def chunk(ctype, data):
            c = ctype if isinstance(ctype, bytes) else ctype.encode("ascii")
            crc = zlib.crc32(c + data) & 0xFFFFFFFF
            return struct.pack(">I", len(data)) + c + data + struct.pack(">I", crc)

        png = bytearray()
        png.extend(b"\x89PNG\r\n\x1a\n")
        png.extend(chunk("IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)))
        png.extend(chunk("IDAT", compressed))
        png.extend(chunk("IEND", b""))

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(png)
        print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def wrap_text(text, scale, max_w):
    """Word-wrap text so each line fits within max_w (in pixels)."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        tw = text_w(trial, scale)
        if tw <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def put_lines(canvas, lines, x, y, scale, color, gap=4):
    """Draw multiple wrapped lines; returns final y cursor."""
    for ln in lines:
        canvas.put_text(ln, x, y, scale, color)
        y += line_h(scale) + gap
    return y


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    c = Canvas(WIDTH, HEIGHT, BG_COLOR)
    pad = PAD
    col_w = WIDTH - 2 * pad

    # ---- Masthead (top, centered) ----
    y = pad + 6
    c.put_text(DATE_LINE_MAIN, (WIDTH - text_w(DATE_LINE_MAIN, SCALE_MAIN_TITLE)) // 2,
               y, SCALE_MAIN_TITLE, INK_COLOR)
    y += line_h(SCALE_MAIN_TITLE) + 22
    c.put_text(DATE_LINE_SUB, (WIDTH - text_w(DATE_LINE_SUB, SCALE_MAIN_SUB)) // 2,
               y, SCALE_MAIN_SUB, MUTED_COLOR)
    y += line_h(SCALE_MAIN_SUB) + 30

    # Accent rule under masthead (thick red bar)
    rule_w = 340
    c.rect((WIDTH - rule_w) // 2, y, (WIDTH - rule_w) // 2 + rule_w, y + 12, ACCENT_COLOR)
    y += 52

    # ---- Main story panel ----
    # Red block accent on the left of headline
    block_w = 16
    block_h = line_h(SCALE_MAIN_HEAD) + 16
    c.rect(pad - 10, y - 8, pad - 10 + block_w, y - 8 + block_h, ACCENT_COLOR)

    # Wrap main headline into lines with gap between them
    head_lines = wrap_text(NEWS["main"]["headline"], SCALE_MAIN_HEAD, col_w - block_w - 24)
    cx = pad + block_w + 24
    cy = y - 8 + 8
    for ln in head_lines:
        c.put_text(ln, cx, cy, SCALE_MAIN_HEAD, ACCENT_COLOR)
        cy += line_h(SCALE_MAIN_HEAD) + 16   # gap between wrapped lines
    y = cy + 36

    # Sub-headline (wrapped, larger gap between lines)
    sub_lines = wrap_text(NEWS["main"]["sub"], SCALE_MAIN_SUBHEAD, col_w)
    y = put_lines(c, sub_lines, pad, y, SCALE_MAIN_SUBHEAD, INK_COLOR, gap=8)
    y += 70

    # ---- Supporting items (three rows, full width) ----
    for idx, item in enumerate(NEWS["supporting"]):
        # headline (may wrap)
        h_lines = wrap_text(item["headline"], SCALE_SUPPORT_HEAD, col_w)
        y = put_lines(c, h_lines, pad, y, SCALE_SUPPORT_HEAD, INK_COLOR, gap=4)
        # sub (wrapped)
        s_lines = wrap_text(item["sub"], SCALE_SUPPORT_SUB, col_w)
        y = put_lines(c, s_lines, pad, y, SCALE_SUPPORT_SUB, MUTED_COLOR, gap=6)
        # gap between supporting blocks (larger for last one)
        y += 42 if idx < len(NEWS["supporting"]) - 1 else 28

    # ---- Footer (bottom, with breathing room) ----
    footer_y = HEIGHT - pad - line_h(SCALE_FOOTER) - 8
    # Push footer down if content ended too early
    if footer_y < y + 30:
        footer_y = y + 20
    c.put_text(FOOTER, pad, footer_y, SCALE_FOOTER, MUTED_COLOR)

    c.save_png(OUTPUT_FILE)


if __name__ == "__main__":
    main()
