"""Neutral generated placeholder pictures (never real photos): a soft background with a
simple silhouette. Used by the seed, the smoke test and the landing-page screenshots."""

import io
import random

from PIL import Image, ImageDraw, ImageFilter

PALETTES = [
    ((236, 239, 255), (199, 210, 254), (99, 102, 241)),
    ((255, 241, 230), (254, 215, 170), (234, 88, 12)),
    ((230, 250, 243), (167, 243, 208), (5, 150, 105)),
    ((253, 236, 246), (251, 207, 232), (219, 39, 119)),
    ((239, 246, 255), (191, 219, 254), (37, 99, 235)),
    ((245, 243, 255), (221, 214, 254), (124, 58, 237)),
    ((255, 251, 235), (253, 230, 138), (202, 138, 4)),
    ((240, 253, 250), (153, 246, 228), (13, 148, 136)),
]


def silhouette(seed: int, size: int = 800, fmt: str = "JPEG", hair: bool | None = None) -> bytes:
    rnd = random.Random(seed)
    bg, mid, fg = PALETTES[seed % len(PALETTES)]
    img = Image.new("RGB", (size, size), bg)
    d = ImageDraw.Draw(img)
    for i in range(size):  # vertical gradient
        t = i / size
        c = tuple(int(bg[k] * (1 - t) + mid[k] * t) for k in range(3))
        d.line([(0, i), (size, i)], fill=c)
    for _ in range(5):  # soft bokeh circles
        r = rnd.randint(size // 12, size // 5)
        x, y = rnd.randint(0, size), rnd.randint(0, size // 2)
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(min(255, v + 12) for v in mid))
    img = img.filter(ImageFilter.GaussianBlur(radius=size // 40))
    d = ImageDraw.Draw(img)
    cx = size // 2 + rnd.randint(-size // 20, size // 20)
    head = int(size * rnd.uniform(0.13, 0.16))
    hy = int(size * 0.42)
    shade = tuple(int(v * 0.85) for v in fg)
    d.ellipse([cx - int(head * 2.1), hy + int(head * 1.3), cx + int(head * 2.1), hy + int(head * 5.2)], fill=shade)
    d.rectangle([cx - int(head * 0.45), hy + head // 2, cx + int(head * 0.45), hy + int(head * 1.6)], fill=shade)
    d.ellipse([cx - head, hy - head, cx + head, hy + head], fill=fg)
    if hair if hair is not None else rnd.random() < 0.5:
        d.ellipse([cx - int(head * 1.15), hy - int(head * 1.05), cx + int(head * 1.15), hy + int(head * 0.2)], fill=shade)
        d.rectangle([cx - int(head * 1.15), hy - int(head * 0.2), cx - int(head * 0.8), hy + int(head * 1.4)], fill=shade)
        d.rectangle([cx + int(head * 0.8), hy - int(head * 0.2), cx + int(head * 1.15), hy + int(head * 1.4)], fill=shade)
    buf = io.BytesIO()
    img.save(buf, fmt, quality=88) if fmt == "JPEG" else img.save(buf, fmt)
    return buf.getvalue()


def avatar(seed: int) -> bytes:
    return silhouette(seed + 100, size=320)


def cover(seed: int) -> bytes:
    bg, mid, fg = PALETTES[seed % len(PALETTES)]
    img = Image.new("RGB", (1200, 400), bg)
    d = ImageDraw.Draw(img)
    for x in range(1200):
        t = x / 1200
        d.line([(x, 0), (x, 400)], fill=tuple(int(mid[k] * (1 - t) + fg[k] * t * 0.6 + bg[k] * t * 0.4) for k in range(3)))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    return buf.getvalue()
