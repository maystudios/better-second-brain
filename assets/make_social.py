#!/usr/bin/env python3
"""Generate assets/social-preview.png (1280x640) for the GitHub repo social card.

Deterministic, dependency-light (Pillow). Re-run after changing copy:
    python assets/make_social.py
"""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
OUT = Path(__file__).resolve().parent / "social-preview.png"
FONTS = "C:/Windows/Fonts"


def font(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}.ttf", size)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def text_w(draw, s, f, tracking=0):
    if tracking == 0:
        return draw.textlength(s, font=f)
    return sum(draw.textlength(c, font=f) + tracking for c in s) - tracking


def draw_tracked(draw, xy, s, f, fill, tracking):
    x, y = xy
    for c in s:
        draw.text((x, y), c, font=f, fill=fill)
        x += draw.textlength(c, font=f) + tracking


# --- canvas + vertical gradient ---
img = Image.new("RGB", (W, H))
top, bot = (9, 13, 26), (15, 26, 52)
px = img.load()
for y in range(H):
    row = lerp(top, bot, y / (H - 1))
    for x in range(W):
        px[x, y] = row
draw = ImageDraw.Draw(img, "RGBA")

# --- soft radial glow (top-left, blue) ---
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r in range(520, 0, -8):
    a = int(26 * (1 - r / 520))
    gd.ellipse([180 - r, 60 - r, 180 + r, 60 + r], fill=(80, 150, 255, a))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

# --- faint knowledge-graph motif (right side) ---
import random
random.seed(7)
nodes = []
cx, cy = 1000, 330
for i in range(16):
    ang = i * (2 * math.pi / 16) + random.uniform(-0.2, 0.2)
    rad = random.uniform(70, 230)
    nodes.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad * 0.8))
nodes.append((cx, cy))
for i, a in enumerate(nodes):
    for b in nodes[i + 1:]:
        if math.dist(a, b) < 200:
            draw.line([a, b], fill=(120, 170, 255, 26), width=2)
for i, (x, y) in enumerate(nodes):
    big = i == len(nodes) - 1
    rr = 9 if big else random.uniform(3, 6)
    col = (125, 211, 252, 150) if big else (120, 170, 255, 70)
    draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)

# --- text block (left) ---
PAD = 84
SKY = (125, 211, 252)
WHITE = (245, 248, 255)
MUTE = (170, 182, 214)

f_eyebrow = font("seguisb", 25)
draw_tracked(draw, (PAD, 120), "OPEN-SOURCE   /   MIT   /   ONE PASTE TO INSTALL", f_eyebrow, SKY, 3)

# Title (fit to width)
size = 92
while True:
    f_title = font("segoeuib", size)
    if text_w(draw, "Better Second Brain", f_title) <= W - 2 * PAD - 40 or size <= 60:
        break
    size -= 2
draw.text((PAD, 168), "Better Second Brain", font=f_title, fill=WHITE)

f_sub = font("segoeui", 34)
draw.text((PAD, 168 + size + 26), "Karpathy's LLM Wiki, batteries-included and measured.", font=f_sub, fill=MUTE)

# --- stat chips ---
chips = ["-56% read tokens", "validated on a real 368-page brain", "graph + self-healing"]
f_chip = font("seguisb", 24)
x, y = PAD, 470
for c in chips:
    tw = draw.textlength(c, font=f_chip)
    w = tw + 44
    draw.rounded_rectangle([x, y, x + w, y + 52], radius=26, fill=(27, 39, 71, 235),
                           outline=(90, 130, 200, 90), width=1)
    draw.ellipse([x + 18, y + 22, x + 30, y + 34], fill=(94, 234, 212))
    draw.text((x + 38, y + 12), c, font=f_chip, fill=(207, 232, 255))
    x += w + 16
    if x > W - 320:  # wrap
        x, y = PAD, y + 66

# --- footer ---
f_foot = font("consola", 25)
draw.text((PAD, H - 70), "github.com/maystudios/better-second-brain", font=f_foot, fill=(120, 140, 180))

img.save(OUT)
print(f"wrote {OUT}  ({img.size[0]}x{img.size[1]})")
