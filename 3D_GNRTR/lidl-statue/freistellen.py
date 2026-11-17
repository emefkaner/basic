"""Blauen Hintergrund per Flutfuellung vom Rand entfernen.

Kein globaler Farbschluessel: Jeans und Hemd sind auch blau. Gefuellt
wird nur, was vom Bildrand aus zusammenhaengend die Hintergrundfarbe
hat -- Innenflaechen bleiben damit unangetastet.
"""
import sys
from collections import deque
from PIL import Image
import numpy as np

quelle, ziel_png, ziel_weiss = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(quelle).convert("RGB")
a = np.array(im).astype(np.float32)
h, w, _ = a.shape
bg = a[2, 2].copy()

abstand = np.sqrt(((a - bg) ** 2).sum(axis=2))
kandidat = abstand < 60          # nah genug an der Hintergrundfarbe

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

# weicher Saum: je naeher an der Hintergrundfarbe, desto transparenter
alpha = np.where(besucht, 0.0, 1.0)
saum = besucht.copy()
for _ in range(1):                       # eine Pixelreihe nach innen glaetten
    nach_innen = np.zeros_like(saum)
    nach_innen[1:, :] |= saum[:-1, :]; nach_innen[:-1, :] |= saum[1:, :]
    nach_innen[:, 1:] |= saum[:, :-1]; nach_innen[:, :-1] |= saum[:, 1:]
    rand = nach_innen & ~saum
    alpha[rand] = np.clip(abstand[rand] / 120.0, 0.0, 1.0)

rgba = np.dstack([a.astype(np.uint8), (alpha * 255).astype(np.uint8)])
out = Image.fromarray(rgba, "RGBA")
# auf doppelte Groesse, damit der Dienst nicht selbst hochskaliert
out = out.resize((out.width * 2, out.height * 2), Image.LANCZOS)
out.save(ziel_png)

weiss = Image.new("RGB", out.size, (255, 255, 255))
weiss.paste(out, (0, 0), out)
weiss.save(ziel_weiss, quality=95)

ys, xs = np.where(alpha > 0.5)
print("Figur belegt x %d..%d, y %d..%d von %d x %d" % (xs.min(), xs.max(), ys.min(), ys.max(), w, h))
print("Hintergrundanteil: %.0f %%" % (100 * besucht.mean()))
print("geschrieben:", ziel_png, "und", ziel_weiss, out.size)
