#!/usr/bin/env python3
"""The World Today - 21 November 2026.

Draws a newspaper front page that sums up Saturday 21 November 2026
in one 1024x1024 image. Pure standard library: the PNG encoder below
is written by hand (zlib + struct), no Pillow, no network, and the
output is byte-for-byte deterministic across runs.

Usage:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes entry.png into $MAKEFUN_OUTPUT_DIR (default /output).
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------- font
# A small 5x7 bitmap font, drawn from scratch. Each glyph is 7 rows of
# 5 bits. Only the characters the page actually uses are defined; all
# page text is set in capitals.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "01010", "11111", "01010"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

# Colours (R, G, B).
PAPER = (246, 241, 229)
CARD = (255, 253, 246)
INK = (25, 25, 25)
RED = (158, 27, 27)
BLUE = (31, 58, 95)
TEAL = (46, 107, 98)
GOLD = (192, 138, 30)
NIGHT = (18, 32, 58)
GREY = (120, 116, 108)
LIGHT = (232, 226, 210)


def char_width(scale):
    return 5 * scale + scale  # glyph + one blank column


def text_width(text, scale):
    return len(text) * char_width(scale) - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    cw = char_width(scale)
    per_line = max(1, max_width // cw)
    lines = []
    for raw in text.split("\n"):
        words = raw.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if len(trial) <= per_line:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                # A single over-long word is hard-split.
                while len(word) > per_line:
                    lines.append(word[:per_line])
                    word = word[per_line:]
                cur = word
        if cur:
            lines.append(cur)
    return lines


class Canvas:
    """A plain RGB pixel buffer with tiny vector helpers."""

    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.px = bytearray(colour) * (width * height)

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o], self.px[o + 1], self.px[o + 2] = colour

    def rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                o = base + (xx - x0) * 3
                self.px[o], self.px[o + 1], self.px[o + 2] = colour

    def hline(self, x, y, w, colour, thick=1):
        self.rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.rect(x, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        """Bresenham line with a square brush of side `thick`."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        while True:
            self.rect(x0 - half, y0 - half, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            span = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.rect(cx - span, yy, span * 2 + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=2):
        for yy in range(cy - r, cy + r + 1):
            outer = int((r * r - (yy - cy) ** 2) ** 0.5)
            inner_r = max(0, r - thick)
            inner = int((inner_r * inner_r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= inner_r else 0
            self.rect(cx - outer, yy, outer - inner, 1, colour)
            self.rect(cx + inner + 1, yy, outer - inner, 1, colour)

    def triangle(self, x0, y0, x1, y1, x2, y2, colour):
        """Filled triangle by horizontal scanlines."""
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / (by - ay) if by != ay else 0
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / (cy - by) if cy != by else 0
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / (cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = sorted((int(xa), int(xb)))
            self.rect(lo, y, hi - lo + 1, 1, colour)

    def text(self, x, y, s, scale, colour):
        """Draw text at top-left (x, y). Unknown chars become blanks."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, colour)
            cx += char_width(scale)
        return cx

    def text_centred(self, cx, y, s, scale, colour):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, colour)


# ---------------------------------------------------------------- png
def write_png(path, canvas):
    """Deterministic PNG: IHDR + one IDAT per row, filter byte 0."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        start = y * stride
        raw += canvas.px[start:start + stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n"
    blob += chunk(b"IHDR", ihdr)
    blob += chunk(b"IDAT", comp)
    blob += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(blob)
    return len(blob)


# ------------------------------------------------------- illustrations
def draw_skyline(c, x, y, w, h):
    """Night sky over a city, with three intercept arcs rising."""
    c.rect(x, y, w, h, NIGHT)
    # Stars, fixed pattern.
    for sx, sy in ((12, 10), (48, 26), (96, 8), (150, 30), (205, 12),
                   (260, 24), (310, 8), (350, 28), (400, 14), (455, 26)):
        if sx < w - 4:
            c.rect(x + sx, y + sy, 3, 3, (255, 255, 240))
    # Moon.
    c.disc(x + w - 46, y + 22, 13, (240, 230, 190))
    c.disc(x + w - 42, y + 18, 11, NIGHT)
    # Buildings, fixed heights, with lit windows.
    heights = (46, 70, 54, 88, 62, 96, 58, 78, 50, 84, 66, 58)
    bw = w // len(heights)
    base = y + h
    for i, bh in enumerate(heights):
        bx = x + i * bw + 2
        c.rect(bx, base - bh, bw - 4, bh, (10, 18, 36))
        for wy in range(base - bh + 8, base - 6, 14):
            for wx in (bx + 5, bx + bw - 11):
                if (wx + wy) % 3 == 0:
                    c.rect(wx, wy, 4, 5, (255, 214, 110))
    # Three intercept arcs, drawn as short line segments.
    for ax0, apex in ((30, 46), (150, 30), (280, 40)):
        prev = None
        for t in range(0, 21):
            px = x + ax0 + t * 6
            py = y + h - 20 - int(apex * (1 - ((t - 10) / 10.0) ** 2))
            if prev is not None:
                c.line(prev[0], prev[1], px, py, (255, 255, 240), 2)
            prev = (px, py)
        c.disc(px, py, 4, (255, 200, 90))
        for dx, dy in ((8, 0), (-8, 0), (0, 8), (0, -8), (6, 6), (-6, -6)):
            c.line(px, py, px + dx, py + dy, (255, 200, 90), 2)


def draw_courthouse(c, x, y, w, h):
    """A courthouse front: pediment, four columns, steps."""
    c.rect(x, y, w, h, (222, 214, 196))
    cx = x + w // 2
    c.triangle(cx - 92, y + 34, cx + 92, y + 34, cx, y + 6, (140, 126, 104))
    c.disc(cx, y + 24, 7, (246, 241, 229))
    for i in range(4):
        colx = x + 22 + i * 52
        c.rect(colx, y + 38, 16, h - 62, (246, 241, 229))
        c.rect(colx - 3, y + 34, 22, 6, (200, 190, 168))
        c.rect(colx - 3, y + h - 26, 22, 6, (200, 190, 168))
    c.rect(x + 8, y + h - 18, w - 16, 5, (180, 170, 148))
    c.rect(x + 14, y + h - 11, w - 28, 5, (160, 150, 130))


def draw_globe(c, x, y, w, h):
    """A small globe with a rising sun behind it."""
    cx = x + w // 2
    cy = y + h // 2 + 4
    r = min(w, h) // 2 - 8
    c.disc(cx + 26, cy - 26, 10, GOLD)
    for dx, dy in ((14, 0), (-14, 0), (0, 14), (0, -14), (10, 10), (-10, -10)):
        c.line(cx + 26, cy - 26, cx + 26 + dx, cy - 26 + dy, GOLD, 2)
    c.disc(cx, cy, r, TEAL)
    c.ring(cx, cy, r, (20, 60, 52), 2)
    c.line(cx - r, cy, cx + r, cy, (140, 200, 185), 2)
    c.line(cx, cy - r, cx, cy + r, (140, 200, 185), 2)
    c.line(cx - r + 8, cy - r // 2, cx + r - 8, cy - r // 2, (140, 200, 185), 2)
    c.line(cx - r + 8, cy + r // 2, cx + r - 8, cy + r // 2, (140, 200, 185), 2)


def draw_podium(c, x, y, w, h):
    """A speaker's podium with two small flags behind it."""
    c.rect(x, y, w, h, (222, 214, 196))
    # Two flags on poles.
    for fx, stripes in ((x + 18, ((178, 34, 52), (255, 255, 255), (178, 34, 52))),
                        (x + w - 58, ((34, 139, 34), (255, 255, 255), (178, 34, 52)))):
        c.vline(fx + 4, y + 8, 44, INK, 2)
        for i, col in enumerate(stripes):
            c.rect(fx + 6, y + 8 + i * 9, 30, 9, col)
    # Microphone and podium.
    c.line(x + w // 2, y + 26, x + w // 2, y + 44, INK, 2)
    c.disc(x + w // 2, y + 24, 5, INK)
    c.rect(x + w // 2 - 34, y + 46, 68, h - 52, (120, 92, 60))
    c.rect(x + w // 2 - 34, y + 46, 68, 5, (90, 66, 42))


def draw_chart(c, x, y, w, h):
    """A falling market line with an arrowhead."""
    c.rect(x, y, w, h, (255, 253, 246))
    c.line(x + 8, y + h - 12, x + w - 8, y + h - 12, GREY, 1)
    c.line(x + 8, y + 8, x + 8, y + h - 12, GREY, 1)
    pts = [(x + 12, y + 16), (x + 40, y + 22), (x + 68, y + 18),
           (x + 96, y + 30), (x + 124, y + 34), (x + 152, y + 48),
           (x + 180, y + 52), (x + 208, y + 66), (x + 236, y + h - 22)]
    for a, b in zip(pts, pts[1:]):
        c.line(a[0], a[1], b[0], b[1], RED, 3)
    ex, ey = pts[-1]
    c.line(ex, ey, ex - 12, ey - 2, RED, 3)
    c.line(ex, ey, ex - 2, ey - 12, RED, 3)
    c.disc(pts[3][0], pts[3][1], 4, RED)


def draw_flame(c, x, y, w, h):
    """A flame over two small houses."""
    c.rect(x, y, w, h, (245, 222, 190))
    for hx in (x + 18, x + w - 78):
        c.rect(hx, y + h - 30, 60, 30, (120, 92, 60))
        c.triangle(hx - 4, y + h - 30, hx + 64, y + h - 30, hx + 30, y + h - 52, (90, 66, 42))
        c.rect(hx + 24, y + h - 16, 12, 16, (60, 44, 28))
    cx = x + w // 2
    base = y + h - 4
    c.triangle(cx - 15, base, cx + 15, base, cx, y + 2, (220, 90, 20))
    c.triangle(cx - 9, base, cx + 9, base, cx, y + 14, (245, 170, 30))
    c.triangle(cx - 4, base, cx + 4, base, cx, y + 26, (255, 220, 90))


def draw_crowd(c, x, y, w, h):
    """A crowd of heads with a placard at each end."""
    c.rect(x, y, w, h, (222, 214, 196))
    for px in (x + 4, x + w - 52):
        c.vline(px + 22, y + 6, 36, INK, 2)
        c.rect(px, y + 2, 48, 26, INK)
        c.rect(px + 2, y + 4, 44, 22, CARD)
        c.line(px + 8, y + 12, px + 40, y + 12, RED, 2)
        c.line(px + 8, y + 19, px + 34, y + 19, RED, 2)
    heads = [(x + 84, 18), (x + 124, 26), (x + 164, 16), (x + 204, 26),
             (x + 244, 18), (x + 284, 26), (x + 324, 16), (x + 364, 24)]
    for hx, hy in heads:
        if hx > x + w - 70:
            continue
        c.disc(hx, y + hy, 9, (70, 58, 44))
        c.rect(hx - 11, y + hy + 10, 22, h - hy - 10, (70, 58, 44))


# ------------------------------------------------------------- panels
def panel(c, x, y, w, h):
    c.rect(x, y, w, h, CARD)
    c.rect(x, y, w, 2, INK)
    c.rect(x, y + h - 2, w, 2, INK)
    c.rect(x, y, 2, h, INK)
    c.rect(x + w - 2, y, 2, h, INK)


def story_block(c, x, y, w, h, kicker, headline, deck, art, art_h,
                head_scale=3, deck_scale=2):
    """Kicker + headline + deck + illustration inside a panel."""
    panel(c, x, y, w, h)
    pad = 14
    inner = w - 2 * pad
    cy = y + pad
    c.text(x + pad, cy, kicker, 2, RED)
    cy += 16
    for line in wrap_text(headline, inner, head_scale):
        c.text(x + pad, cy, line, head_scale, INK)
        cy += 7 * head_scale + 4
    cy += 2
    for line in wrap_text(deck, inner, deck_scale):
        c.text(x + pad, cy, line, deck_scale, INK)
        cy += 7 * deck_scale + 3
    art_y = y + h - art_h - 10
    if art_y > cy + 4:
        art(c, x + pad, art_y, inner, art_h)
    return cy


def build():
    c = Canvas(WIDTH, HEIGHT, PAPER)

    # Masthead.
    c.text_centred(WIDTH // 2, 30, "THE WORLD TODAY", 6, INK)
    c.hline(24, 84, WIDTH - 48, INK, 3)
    c.text_centred(WIDTH // 2, 96, "SATURDAY, 21 NOVEMBER 2026", 3, INK)
    c.hline(24, 126, WIDTH - 48, INK, 2)

    # Lead row: Riyadh (left, wide) and Paris (right).
    story_block(c, 24, 140, 640, 330, "MIDDLE EAST",
                "MISSILES OVER RIYADH",
                "SAUDI AIR DEFENCES INTERCEPT THREE BALLISTIC "
                "MISSILES FIRED TOWARD THE CAPITAL BEFORE DAWN",
                draw_skyline, 108, head_scale=5, deck_scale=2)
    story_block(c, 688, 140, 312, 330, "FRANCE",
                "THREE OFFICERS JAILED FOR RACIST BEATING",
                "PARIS COURT UPHOLDS RACISM AS AN AGGRAVATING "
                "FACTOR IN THE 2020 ATTACK ON MICHEL ZECLER",
                draw_courthouse, 92, head_scale=3, deck_scale=2)

    # Middle row: COP31, Trump and Iran, markets.
    story_block(c, 24, 490, 312, 210, "CLIMATE",
                "COP31 TALKS DEADLOCKED",
                "SUMMIT IN OVERTIME AS 200 NATIONS SPLIT OVER "
                "FOSSIL FUELS",
                draw_globe, 56, head_scale=3, deck_scale=2)
    story_block(c, 356, 490, 312, 210, "DIPLOMACY",
                "TRUMP: IRAN WANTS A DEAL",
                "TEHRAN SEEKS DIPLOMACY; TRUMP WANTS A REAL DEAL",
                draw_podium, 56, head_scale=3, deck_scale=2)
    story_block(c, 688, 490, 312, 210, "MARKETS",
                "WALL STREET IN CORRECTION",
                "S&P 500 DOWN 3.7% AS AI SHARES SELL OFF",
                draw_chart, 56, head_scale=3, deck_scale=2)

    # Bottom row: Palisades verdict and the European protests.
    story_block(c, 24, 714, 478, 246, "CALIFORNIA",
                "PALISADES FIRE ARSONIST CONVICTED",
                "JURY CONVICTS RINDERKNECHT OVER THE 2025 BLAZE "
                "THAT KILLED 12 AND DESTROYED 6,800 STRUCTURES",
                draw_flame, 48, head_scale=4, deck_scale=2)
    story_block(c, 522, 714, 478, 246, "EUROPE",
                "YOUNG EUROPE MARCHES",
                "PROTESTERS RALLY ACROSS THE CONTINENT OVER "
                "LIVING COSTS, HOUSING AND CLIMATE",
                draw_crowd, 48, head_scale=4, deck_scale=2)

    # Footer.
    c.hline(24, 972, WIDTH - 48, INK, 2)
    c.text_centred(WIDTH // 2, 982,
                   "SOURCES: REUTERS - AP - LE MONDE - AFP", 2, INK)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, canvas)
    print(f"wrote {path} ({size} bytes, {WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
