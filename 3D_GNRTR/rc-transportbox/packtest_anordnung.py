#!/usr/bin/env python3
"""Kleinstmoegliche Anordnung aus Controllermulde + Auto-Box.

Ergebnis ist BOX_NEBEN_MULDE in generate.py. Nach jeder Aenderung an
der Kontur oder an den Boxmaszen neu laufen lassen.

Verfahren: die Mulde in ein 1-mm-Raster legen und um den Wandabstand
aufblasen. Dann jede Lage der Box (beide Achsrichtungen, 1-mm-Raster)
daraufhin pruefen, ob sie eine belegte Zelle trifft. Fuer jede gueltige
Lage das umschliessende Rechteck aus Mulde und Box bilden -- das ist das
Innenmass des Koffers. Das kleinste gewinnt.

Kein Raten, keine Handanordnung: der Suchraum ist vollstaendig.
"""
import sys, math
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import generate as G

WAND = 3.0                    # Steg zwischen Box und Mulde / Aussenwand
g = G.abgeleitet()
mulde = g["mulde"]
mx0 = min(p[0] for p in mulde)
my0 = min(p[1] for p in mulde)
mulde = [(x - mx0, y - my0) for (x, y) in mulde]
MW = max(p[0] for p in mulde)
MH = max(p[1] for p in mulde)
print("Mulde: %.1f x %.1f mm" % (MW, MH))

# Fachmasz NICHT hier nachrechnen, sondern vom Generator holen -- sonst
# laufen Werkzeug und Bauteil auseinander (genau so ist die Box einmal in
# ein Fach geplant worden, das die Rippen wieder zugebaut haben).
BX, BY = g["box_l"], g["box_t"]
print("Auto-Box-Fach: %.1f x %.1f mm (Box %.0f x %.0f + %.1f mm Luft je Seite)"
      % (BX, BY, G.AUTOBOX_B, G.AUTOBOX_L, G.AUTOBOX_LUFT))

# Raster: Rand von RAND mm um die Mulde herum, 1 mm Zellen
RAND = 140
W = int(MW + 2 * RAND) + 2
H = int(MH + 2 * RAND) + 2
belegt = np.zeros((H, W), dtype=np.uint8)

# Mulde rastern (Punkt-in-Polygon je Zelle waere zu langsam -> scanline)
kanten = [(mulde[i], mulde[(i + 1) % len(mulde)]) for i in range(len(mulde))]
for row in range(H):
    y = row - RAND + 0.5
    xs = []
    for (a, b) in kanten:
        if (a[1] > y) != (b[1] > y):
            xs.append(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
    xs.sort()
    for i in range(0, len(xs) - 1, 2):
        c0 = int(math.floor(xs[i] + RAND))
        c1 = int(math.ceil(xs[i + 1] + RAND))
        belegt[row, max(0, c0):min(W, c1 + 1)] = 1

# um WAND aufblasen (Manhattan reicht: quadratisches Strukturelement)
k = int(math.ceil(WAND))
auf = belegt.copy()
for dy in range(-k, k + 1):
    for dx in range(-k, k + 1):
        auf |= np.roll(np.roll(belegt, dy, axis=0), dx, axis=1)
belegt = auf

pre = np.zeros((H + 1, W + 1), dtype=np.int32)
pre[1:, 1:] = np.cumsum(np.cumsum(belegt, axis=0), axis=1)


def besetzt(x0, y0, bx, by):
    c0 = int(round(x0 + RAND)); c1 = int(round(x0 + bx + RAND))
    r0 = int(round(y0 + RAND)); r1 = int(round(y0 + by + RAND))
    if c0 < 0 or r0 < 0 or c1 >= W or r1 >= H:
        return True
    return (pre[r1, c1] - pre[r0, c1] - pre[r1, c0] + pre[r0, c0]) > 0


best = []
for (bx, by) in ((BX, BY), (BY, BX)):
    y = -RAND + 1
    while y + by < MH + RAND:
        x = -RAND + 1
        while x + bx < MW + RAND:
            if not besetzt(x, y, bx, by):
                ix0 = min(0.0, x) - WAND
                ix1 = max(MW, x + bx) + WAND
                iy0 = min(0.0, y) - WAND
                iy1 = max(MH, y + by) + WAND
                innen_x = ix1 - ix0
                innen_y = iy1 - iy0
                best.append((innen_x * innen_y, innen_x, innen_y,
                             x, y, bx, by))
            x += 1.0
        y += 1.0

best.sort()
print("\ngueltige Lagen: %d" % len(best))
print("\nDie fuenf kleinsten Innenmasse:")
gesehen = set()
for (a, ix, iy, x, y, bx, by) in best:
    key = (round(ix), round(iy))
    if key in gesehen:
        continue
    gesehen.add(key)
    print("  innen %6.1f x %6.1f mm  -> aussen %6.1f x %6.1f  (Flaeche %5.0f cm2)"
          "   Box bei x %.0f y %.0f, %.0f x %.0f"
          % (ix, iy, ix + 2 * G.WAND, iy + 2 * G.WAND, a / 100.0,
             x, y, bx, by))
    if len(gesehen) >= 5:
        break

a, ix, iy, x, y, bx, by = best[0]
print("\nBESTE: Koffer aussen %.0f x %.0f x 66 mm" % (ix + 2 * G.WAND, iy + 2 * G.WAND))
print("bisher:              266 x 238 x 66 mm")
print("Flaeche: %.0f statt %.0f cm2 (%.0f %% weniger)"
      % (a / 100.0, 266 * 238 / 100.0,
         100 * (1 - a / (266.0 * 238.0))))
print("\nIn generate.py eintragen:  BOX_NEBEN_MULDE = (%.1f, %.1f)" % (x, y))
