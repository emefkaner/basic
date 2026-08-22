#!/usr/bin/env python3
"""Ansichten des Hochzeitsornaments (Renderer wie in den Nachbarprojekten)."""

import math
import os

import generate as g

LICHT = (-0.4, -0.55, 0.73)


def projizieren(p, drehung, tilt):
    x, y, z = p
    cw, sw = math.cos(drehung), math.sin(drehung)
    xs = x * cw - y * sw
    ys = x * sw + y * cw
    return (xs, -(ys * math.sin(tilt) + z * math.cos(tilt)),
            -ys * math.cos(tilt) + z * math.sin(tilt))


def normale(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
    l = math.sqrt(sum(k * k for k in n)) or 1.0
    return tuple(k / l for k in n)


def bild(pfad, teile, drehung, skala, titel, tilt):
    flaechen = []
    cw, sw = math.cos(drehung), math.sin(drehung)
    for dreiecke, farbe in teile:
        for tri in dreiecke:
            p = [projizieren(v, drehung, tilt) for v in tri]
            n = normale(*tri)
            nx = n[0] * cw - n[1] * sw
            ny = n[0] * sw + n[1] * cw
            if -ny * math.cos(tilt) + n[2] * math.sin(tilt) <= 0:
                continue
            hell = 0.34 + 0.66 * max(0.0, nx * LICHT[0] + ny * LICHT[1]
                                     + n[2] * LICHT[2])
            flaechen.append((sum(q[2] for q in p) / 3.0, p,
                             "#%02x%02x%02x" % tuple(
                                 max(0, min(255, int(k * hell))) for k in farbe)))
    flaechen.sort(key=lambda f: f[0])
    xs = [q[0] for _, p, _ in flaechen for q in p]
    ys = [q[1] for _, p, _ in flaechen for q in p]
    minx, miny = min(xs), min(ys)
    b = (max(xs) - minx) * skala + 30
    h = (max(ys) - miny) * skala + 30
    zeilen = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
              'viewBox="0 0 %.1f %.1f">' % (b, h + 40, b, h + 40),
              '<rect width="100%" height="100%" fill="#211f1b"/>',
              '<text x="%.1f" y="26" font-family="Georgia,serif" font-size="17" '
              'text-anchor="middle" fill="#e8d9a8">%s</text>' % (b / 2, titel),
              '<g transform="translate(0,36)" shape-rendering="crispEdges">']
    for _, p, farbe in flaechen:
        pts = " ".join("%.2f,%.2f" % ((q[0] - minx) * skala + 15,
                                      (q[1] - miny) * skala + 15) for q in p)
        zeilen.append('<polygon points="%s" fill="%s"/>' % (pts, farbe))
    zeilen.append('</g></svg>')
    with open(pfad, "w") as f:
        f.write("\n".join(zeilen))


def main():
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    gold = (212, 175, 55)
    dunkelgold = (160, 125, 28)

    herz_schalen, _ = g.teil_herz()
    # Schalen 0-2 sind Platte/Rahmen/Oese, der Rest ist Schrift --
    # im Render heller, damit die Lesbarkeit beurteilbar ist
    herz = [tri for s, _ in herz_schalen[:3] for tri in s]
    schrift = [tri for s, _ in herz_schalen[3:] for tri in s]
    sockel = [tri for s, _ in g.teil_sockel() for tri in s]

    # Frontal (Druckansicht, Schrift lesbar)
    hell = (240, 216, 140)
    bild(os.path.join(ziel, "ansicht_herz_front.svg"),
         [(herz, gold), (schrift, hell)], drehung=0.0, skala=3.4,
         titel="Herz frontal (Drucklage)", tilt=math.radians(88))

    # Aufgestellt: das flach gedruckte Herz (Ebene XY, Schrift +Z) wird um
    # 90 Grad minus Nutneigung um die X-Achse aufgerichtet; die Herzspitze
    # sitzt am Nutboden.
    alle_y = [v[1] for tri in herz for v in tri]
    y_spitze = min(alle_y)
    a = math.radians(90.0 - g.NUT_NEIGUNG)
    ca, sa = math.cos(a), math.sin(a)
    nutboden = g.SOCKEL_HOEHE - g.NUT_TIEFE

    def aufrichten(tri):
        out = []
        for (x, y, z) in tri:
            yy = y - y_spitze
            out.append((x, yy * ca - z * sa, yy * sa + z * ca + nutboden))
        return tuple(out)

    herz_auf = [aufrichten(tri) for tri in herz + schrift]
    bild(os.path.join(ziel, "ansicht_aufgestellt.svg"),
         [(sockel, dunkelgold), (herz_auf, gold)],
         drehung=math.radians(18), skala=2.6,
         titel="Auf dem Tisch: Herz im Sockel", tilt=math.radians(70))

    for name in ("ansicht_herz_front.svg", "ansicht_aufgestellt.svg"):
        print("%-26s %6.0f kB"
              % (name, os.path.getsize(os.path.join(ziel, name)) / 1024.0))


if __name__ == "__main__":
    main()
