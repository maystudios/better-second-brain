#!/usr/bin/env python3
"""Generate assets/social-preview.png (1280x640).

The background is the REAL knowledge graph of a 368-page second brain (382 nodes,
2161 edges, 9 communities) laid out force-directed and coloured by community -- the
genuine "second brain graph" look, not a decorative motif. Node/edge structure is
the anonymised `assets/graph-sample.json` (degrees + communities + edges, no labels).

Deterministic. Re-run:  python assets/make_social.py
Deps: Pillow, networkx, numpy (all ship with graphify).
"""
from __future__ import annotations
import json, math
from pathlib import Path
import networkx as nx
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = Path(__file__).resolve().parent
W, H, S = 1280, 640, 2            # final size + supersample factor
FONTS = "C:/Windows/Fonts"
BG = (8, 10, 16)                   # near-black, Obsidian-graph dark
PALETTE = [(122,162,255),(94,234,212),(167,139,250),(96,165,250),(192,132,252),
           (52,211,153),(240,171,252),(56,189,248),(251,191,36)]


def font(name, size):
    return ImageFont.truetype(f"{FONTS}/{name}.ttf", size)


# ---- load real graph + force layout ----
d = json.loads((HERE / "graph-sample.json").read_text())
n, comm, deg, edges = d["n"], d["community"], d["degree"], d["edges"]
G = nx.Graph()
G.add_nodes_from(range(n))
G.add_edges_from(edges)
pos = nx.spring_layout(G, k=1.05 / math.sqrt(n), iterations=90, seed=5)
xs = [pos[i][0] for i in range(n)]
ys = [pos[i][1] for i in range(n)]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
PAD = 70 * S
CW, CH = W * S, H * S


def P(i):
    x = PAD + (pos[i][0] - x0) / (x1 - x0) * (CW - 2 * PAD)
    y = PAD + (pos[i][1] - y0) / (y1 - y0) * (CH - 2 * PAD)
    return x, y


def col(i, a=255):
    c = PALETTE[comm[i] % len(PALETTE)]
    return (c[0], c[1], c[2], a)


# ---- render background at 2x ----
base = Image.new("RGB", (CW, CH), BG)
# subtle vertical sheen
sh = Image.new("L", (1, CH))
for y in range(CH):
    sh.putpixel((0, y), int(10 * (1 - y / CH)))
base = ImageChops.add(base, Image.merge("RGB", [sh.resize((CW, CH))] * 3))

edge_layer = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
ed = ImageDraw.Draw(edge_layer)
for s, t in edges:
    ed.line([P(s), P(t)], fill=col(s, 30), width=S)
base = Image.alpha_composite(base.convert("RGBA"), edge_layer).convert("RGB")

# glow layer: every node, brightness ~ degree; blurred + added
glow = Image.new("RGB", (CW, CH), (0, 0, 0))
gd = ImageDraw.Draw(glow)
dmax = max(deg) or 1
for i in range(n):
    x, y = P(i)
    r = (3 + math.sqrt(deg[i]) * 2.4) * S
    a = 0.30 + 0.70 * (deg[i] / dmax)
    c = PALETTE[comm[i] % len(PALETTE)]
    gd.ellipse([x - r, y - r, x + r, y + r], fill=(int(c[0]*a), int(c[1]*a), int(c[2]*a)))
glow = glow.filter(ImageFilter.GaussianBlur(7 * S))
base = ImageChops.add(base, glow)

# crisp nodes on top
nodes = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
nd = ImageDraw.Draw(nodes)
for i in range(n):
    x, y = P(i)
    r = (1.6 + math.sqrt(deg[i]) * 1.25) * S
    nd.ellipse([x - r, y - r, x + r, y + r], fill=col(i, 255),
               outline=(*BG, 255), width=max(1, S // 2))
base = Image.alpha_composite(base.convert("RGBA"), nodes).convert("RGB")

# ---- downscale for clean anti-aliasing ----
img = base.resize((W, H), Image.LANCZOS)

# ---- left dark gradient so the title reads over the graph ----
grad = Image.new("L", (W, 1))
for x in range(W):
    t = min(1.0, max(0.0, (x - 60) / (W * 0.62)))
    grad.putpixel((x, 0), int(238 * (1 - t) ** 1.4))
mask = grad.resize((W, H))
overlay = Image.new("RGB", (W, H), BG)
img = Image.composite(overlay, img, mask)
# faint overall floor for legibility
img = Image.composite(Image.new("RGB", (W, H), BG), img, Image.new("L", (W, H), 26))

draw = ImageDraw.Draw(img)
PADX, WHITE, MUTE, ACC = 84, (238, 242, 255), (154, 166, 192), (138, 180, 255)

# title (fit)
size = 80
while font("seguisb", size).getlength("Better Second Brain") > W * 0.62 and size > 54:
    size -= 2
f_t = font("seguisb", size)
ty = 232
draw.text((PADX, ty), "Better Second Brain", font=f_t, fill=WHITE)
# thin accent rule under title
draw.rectangle([PADX + 2, ty + size + 14, PADX + 64, ty + size + 18], fill=ACC)

f_s = font("segoeui", 31)
draw.text((PADX, ty + size + 34), "An LLM-maintained knowledge base,", font=f_s, fill=MUTE)
draw.text((PADX, ty + size + 72), "on Andrej Karpathy's LLM Wiki pattern.", font=f_s, fill=MUTE)

f_stat = font("seguisb", 26)
draw.text((PADX, ty + size + 130),
          "Measured: -56% tokens per query, on a real 368-page brain.",
          font=f_stat, fill=ACC)

f_mark = font("consola", 24)
draw.text((PADX, H - 66), "github.com/maystudios/better-second-brain", font=f_mark, fill=(96, 110, 138))

img.save(HERE / "social-preview.png")
print(f"wrote social-preview.png  ({W}x{H})  from {n} nodes / {len(edges)} edges")
