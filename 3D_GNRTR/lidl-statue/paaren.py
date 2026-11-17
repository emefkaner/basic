"""Front- und Rueckansicht auf gleiche Lage bringen.

Mehransichts-Rekonstruktion setzt voraus, dass dieselbe Figur in beiden
Bildern gleich gross und gleich hoch sitzt. Beide werden deshalb
freigestellt, auf dieselbe Figurhoehe skaliert und mittig in eine
Leinwand gleichen Formats gesetzt.
"""
import sys
from collections import deque
import numpy as np
from PIL import Image


def freistellen(pfad, toleranz=60):
    im = Image.open(pfad).convert("RGB")
    a = np.array(im).astype(np.float32)
    h, w, _ = a.shape
    bg = a[2, 2].copy()
    kandidat = np.sqrt(((a - bg) ** 2).sum(axis=2)) < toleranz
    besucht = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if kandidat[y, x] and not besucht[y, x]:
                besucht[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if kandidat[y, x] and not besucht[y, x]:
                besucht[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and kandidat[ny, nx] and not besucht[ny, nx]:
                besucht[ny, nx] = True; q.append((ny, nx))
    alpha = np.where(besucht, 0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), "RGBA")


def zuschneiden(im):
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a > 128)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


ZIEL_H, LEINWAND = 1200, (900, 1400)     # Figurhoehe und Leinwand in px
aus = []
for pfad, name in ((sys.argv[1], "front"), (sys.argv[2], "rueck")):
    f = zuschneiden(freistellen(pfad))
    s = ZIEL_H / f.height
    f = f.resize((max(1, int(f.width * s)), ZIEL_H), Image.LANCZOS)
    blatt = Image.new("RGBA", LEINWAND, (255, 255, 255, 0))
    blatt.paste(f, ((LEINWAND[0] - f.width) // 2, (LEINWAND[1] - ZIEL_H) // 2), f)
    p = sys.argv[3] + "_" + name + ".png"
    blatt.save(p)
    aus.append((name, f.width, p))
    print("%-6s Figur %4d x %4d px -> %s" % (name, f.width, ZIEL_H, p))

print("Breitenverhaeltnis front/rueck: %.3f (1.0 waere identisch)"
      % (aus[0][1] / aus[1][1]))
