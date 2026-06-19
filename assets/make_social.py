#!/usr/bin/env python3
"""Compose assets/social-preview.png (1280x640): the AI-generated knowledge-graph
banner background (assets/banner-bg.png) with a clean, crisp title overlay on the
dark left side. The background is image-model art; the text is rendered here so it
is always sharp and legible (image models garble text).

Re-run after changing copy:  python assets/make_social.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1280, 640
FONTS = "C:/Windows/Fonts"


def font(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}.ttf", size)


img = Image.open(HERE / "banner-bg.png").convert("RGB").resize((W, H), Image.LANCZOS)

# Gentle left-to-right darkening so the title is always legible over any glow.
grad = Image.new("L", (W, 1))
for x in range(W):
    t = min(1.0, max(0.0, (x - 40) / (W * 0.60)))
    grad.putpixel((x, 0), int(165 * (1 - t) ** 1.5))
img = Image.composite(Image.new("RGB", (W, H), (6, 8, 14)), img, grad.resize((W, H)))

draw = ImageDraw.Draw(img)
PADX = 84
WHITE, MUTE, ACC = (240, 244, 255), (170, 182, 210), (143, 184, 255)

# Title, fit to the left region.
size = 76
while font("seguisb", size).getlength("Better Second Brain") > 560 and size > 52:
    size -= 2
f_t = font("seguisb", size)
ty = 214
draw.text((PADX, ty), "Better Second Brain", font=f_t, fill=WHITE)
draw.rectangle([PADX + 2, ty + size + 16, PADX + 60, ty + size + 20], fill=ACC)

f_s = font("segoeui", 30)
draw.text((PADX, ty + size + 38), "An LLM-maintained knowledge base,", font=f_s, fill=MUTE)
draw.text((PADX, ty + size + 76), "on Andrej Karpathy's LLM Wiki pattern.", font=f_s, fill=MUTE)

f_stat = font("seguisb", 25)
draw.text((PADX, ty + size + 132),
          "Measured: -56% tokens per query, on a real 368-page brain.",
          font=f_stat, fill=ACC)

draw.text((PADX, H - 62), "github.com/maystudios/better-second-brain",
          font=font("consola", 23), fill=(124, 138, 168))

img.save(HERE / "social-preview.png")
print(f"wrote social-preview.png ({W}x{H}) over AI knowledge-graph background")
