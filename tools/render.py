#!/usr/bin/env python3
"""Renderiza posts 1080x1350 do @riansites a partir de um JSON.

Uso: python3 -I tools/render.py spec.json pasta_saida

spec.json = lista de posts. Cada post:
{
  "file": "10h.png",
  "layout": "stat" | "headline",
  "tag": "TEXTO DO TOPO EM MAIUSCULAS",
  ... campos do layout ...
}

layout "stat":     big, small (opcional), headline, body, foot (opcional)
layout "headline": line1 (branco), line2 (destaque), body1, body2 (opcional)

Se o texto estourar a area util, o script falha com erro: encurte o texto.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
FD = "/usr/share/fonts/opentype/inter/"
BG, FG, MUTED, ACCENT, LINE = (11, 18, 32), (245, 247, 250), (148, 163, 184), (45, 212, 191), (30, 41, 59)
MAXW = W - 160
LIMIT_Y = H - 190  # texto nao pode passar daqui


def f(name, size):
    return ImageFont.truetype(FD + name, size)


def wrap(d, text, font, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(d, text, font, x, y, fill, spacing=1.18):
    for ln in wrap(d, text, font, MAXW):
        d.text((x, y), ln, font=font, fill=fill)
        y += int(font.size * spacing)
    return y


def base(tag):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([80, 90, 136, 96], fill=ACCENT)
    d.text((80, 116), tag, font=f("Inter-SemiBold.otf", 28), fill=ACCENT)
    d.line([80, H - 150, W - 80, H - 150], fill=LINE, width=2)
    d.text((80, H - 118), "@riansites", font=f("Inter-Bold.otf", 34), fill=FG)
    d.text((W - 80, H - 114), "Sites para clínicas de transplante capilar",
           font=f("Inter-Regular.otf", 26), fill=MUTED, anchor="ra")
    return img, d


def stat(p):
    img, d = base(p["tag"])
    bigfont = f("Inter-Black.otf", p.get("big_size", 300))
    d.text((80, 230), p["big"], font=bigfont, fill=ACCENT)
    y = 230 + int(bigfont.size * 1.0) + 70 if "small" not in p else 600
    if "small" in p:
        w = d.textlength(p["big"], font=bigfont)
        d.text((80 + w + 24, 380), p["small"], font=f("Inter-Bold.otf", 110), fill=MUTED)
    y = block(d, p["headline"], f("Inter-Bold.otf", 58), 80, y, FG)
    y += 36
    y = block(d, p["body"], f("Inter-Regular.otf", 38), 80, y, MUTED, 1.3)
    if p.get("foot"):
        d.text((80, H - 200), p["foot"], font=f("Inter-Medium.otf", 26), fill=MUTED)
    return img, y


def headline(p):
    img, d = base(p["tag"])
    y = block(d, p["line1"], f("Inter-ExtraBold.otf", 84), 80, 250, FG, 1.12)
    y += 20
    y = block(d, p["line2"], f("Inter-ExtraBold.otf", 84), 80, y, ACCENT, 1.12)
    y += 60
    d.line([80, y, 200, y], fill=ACCENT, width=6)
    y += 56
    y = block(d, p["body1"], f("Inter-Regular.otf", 40), 80, y, FG, 1.32)
    if p.get("body2"):
        y += 40
        y = block(d, p["body2"], f("Inter-SemiBold.otf", 40), 80, y, MUTED, 1.32)
    return img, y


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for p in spec:
        img, y = {"stat": stat, "headline": headline}[p["layout"]](p)
        if y > LIMIT_Y:
            raise SystemExit(f"TEXTO ESTOUROU em {p['file']} (y={y} > {LIMIT_Y}): encurte o texto")
        img.save(os.path.join(out, p["file"]), quality=95)
        print("ok", p["file"], "y_final=", y)


if __name__ == "__main__":
    main()
