#!/usr/bin/env python3
"""Generate assets/demo.gif: a synthetic terminal demo of the BSB one-paste install.

Deterministic (Pillow). Renders a tidy "asciinema-style" terminal that types the
install flow. Re-run after changing the script lines:
    python assets/make_demo.py
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 980, 560
OUT = Path(__file__).resolve().parent / "demo.gif"
FONTS = "C:/Windows/Fonts"
mono = ImageFont.truetype(f"{FONTS}/consola.ttf", 21)
monob = ImageFont.truetype(f"{FONTS}/consolab.ttf", 21)
ui = ImageFont.truetype(f"{FONTS}/seguisb.ttf", 18)

BG = (13, 17, 23)
BAR = (22, 27, 34)
LH = 30           # line height
X0, Y0 = 34, 86   # text origin

C = {
    "comment": (110, 118, 137),
    "prompt": (63, 185, 80),
    "cmd": (214, 222, 235),
    "out": (139, 148, 178),
    "ok": (86, 211, 100),
    "done": (126, 231, 135),
    "user": (210, 168, 255),
    "agent": (125, 211, 252),
    "dim": (98, 110, 132),
}

# (kind, text). cmd lines get typed char-by-char; others appear whole.
LINES = [
    ("comment", "# paste the install prompt into Claude Code / Codex in an empty folder"),
    ("cmd", "git clone https://github.com/maystudios/better-second-brain ."),
    ("out", "Cloning into '.'... done."),
    ("cmd", 'python scripts/init_brain.py --domain "Rust web frameworks" --fresh --yes'),
    ("ok", "update DOMAIN/LITMUS in CLAUDE.md (2 lines) + bsb.config.md"),
    ("ok", "reset index.md / log.md / roadmap.md  ->  empty brain"),
    ("done", "Brain ready. Drop a source in raw/ or say:  ingest <url>"),
    ("user", "you:   ingest https://docs.rs/axum"),
    ("agent", "agent: wrote 1 source page, updated 6 wiki pages, logged it."),
    ("dim", "/graphify  ->  382 nodes, 9 communities   |   query: -56% read tokens vs raw"),
]


def base():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 52], fill=BAR)
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([26 + i * 26, 19, 40 + i * 26, 33], fill=col)
    d.text((W // 2 - 150, 16), "Claude Code  ·  better-second-brain", font=ui, fill=(139, 148, 178))
    return im


def render(done_lines, partial, cursor):
    im = base()
    d = ImageDraw.Draw(im)
    y = Y0
    rows = list(done_lines)
    if partial is not None:
        rows.append(partial)
    for kind, text in rows:
        x = X0
        if kind in ("cmd", "user"):
            d.text((x, y), "$", font=monob, fill=C["prompt"])
            x += d.textlength("$ ", font=mono)
        if kind == "ok" or kind == "done":
            d.text((x, y), ">" if kind == "done" else "+", font=monob, fill=C[kind]); x += d.textlength("  ", font=mono) + 8
        col = C.get(kind, C["cmd"])
        if kind == "cmd":
            col = C["cmd"]
        if kind == "user":
            col = C["user"]
        if kind == "agent":
            col = C["agent"]
        d.text((x, y), text, font=monob if kind == "done" else mono, fill=col)
        y += LH
    if cursor:
        # blinking block cursor at end of last row
        lx = X0
        k, t = rows[-1]
        if k in ("cmd", "user"):
            lx += d.textlength("$ ", font=mono)
        lx += d.textlength(t, font=mono)
        d.rectangle([lx + 2, y - LH + 3, lx + 13, y - LH + 23], fill=(214, 222, 235))
    return im


frames, durs = [], []
done = []
for kind, text in LINES:
    if kind in ("cmd",):
        step = 7
        for i in range(0, len(text) + 1, step):
            frames.append(render(done, (kind, text[:i]), (i // step) % 2 == 0)); durs.append(45)
        frames.append(render(done, (kind, text), True)); durs.append(380)
        done.append((kind, text))
    else:
        done.append((kind, text))
        frames.append(render(done, None, False)); durs.append(620)
# final hold with blink
done.append(("cmd", ""))
for j in range(10):
    frames.append(render(done[:-1], ("cmd", ""), j % 2 == 0)); durs.append(420)

frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durs, loop=0,
               optimize=True, disposal=2)
print(f"wrote {OUT}  ({len(frames)} frames)")
