#!/usr/bin/env python3
"""SVG-Ansichten des Fernrohrhalters: Baugruppe und Einzelteile.

Renderer wie im Schutzring-Projekt: isometrische Projektion,
Rueckseiten-Aussortierung, Maleralgorithmus, Lambert-Schattierung.
"""

import math
import os

import generate as g


LICHT = (-0.45, -0.62, 0.65)


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


def schattieren(basis, hell):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(k * hell))) for k in basis)


def bild(pfad, teile, drehung, skala, titel, untertitel, tilt=math.radians(22)):
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
            hell = 0.30 + 0.70 * max(0.0, nx * LICHT[0] + ny * LICHT[1]
                                     + n[2] * LICHT[2])
            flaechen.append((sum(q[2] for q in p) / 3.0, p,
                             schattieren(farbe, hell)))
    flaechen.sort(key=lambda f: f[0])
    xs = [q[0] for _, p, _ in flaechen for q in p]
    ys = [q[1] for _, p, _ in flaechen for q in p]
    minx, miny = min(xs), min(ys)
    b = (max(xs) - minx) * skala + 28
    h = (max(ys) - miny) * skala + 28
    zeilen = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
              'viewBox="0 0 %.1f %.1f">' % (b, h + 58, b, h + 58),
              '<rect width="100%" height="100%" fill="#fbfbfa"/>',
              '<text x="%.1f" y="24" font-family="sans-serif" font-size="16" '
              'font-weight="600" text-anchor="middle" fill="#1a1a1a">%s</text>'
              % (b / 2, titel),
              '<g transform="translate(0,34)" shape-rendering="crispEdges">']
    for _, p, farbe in flaechen:
        pts = " ".join("%.2f,%.2f" % ((q[0] - minx) * skala + 14,
                                      (q[1] - miny) * skala + 14) for q in p)
        zeilen.append('<polygon points="%s" fill="%s"/>' % (pts, farbe))
    zeilen.append('</g>')
    zeilen.append('<text x="%.1f" y="%.1f" font-family="sans-serif" font-size="12" '
                  'text-anchor="middle" fill="#555">%s</text>'
                  % (b / 2, h + 50, untertitel))
    zeilen.append('</svg>')
    with open(pfad, "w") as f:
        f.write("\n".join(zeilen))


def rot_y(t, winkel):
    cw, sw = math.cos(winkel), math.sin(winkel)
    return [tuple((x * cw + z * sw, y, -x * sw + z * cw) for (x, y, z) in tri)
            for tri in t]


def rot_x(t, winkel):
    cw, sw = math.cos(winkel), math.sin(winkel)
    return [tuple((x, y * cw - z * sw, y * sw + z * cw) for (x, y, z) in tri)
            for tri in t]


def zylinder_x(r, x0, x1, seg=48):
    """Liegender Zylinder entlang X (nur fuer die Fernrohr-Attrappe).

    In kurze Abschnitte gestueckelt: der Maleralgorithmus sortiert nach
    Dreiecks-Schwerpunkt, und ein 300 mm langes Manteldreieck sortiert
    gegen die kleinteilige Schelle zwangslaeufig falsch."""
    t = []
    schritt = 20.0
    x = x0
    while x < x1 - 1e-9:
        x2 = min(x + schritt, x1)
        t.extend(g.kegelstumpf(0, 0, r, r, x, x2, seg))
        x = x2
    return rot_y(t, math.pi / 2)


def main():
    p = g.abgeleitet()
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    os.makedirs(ziel, exist_ok=True)

    grau = (150, 150, 155)
    blau = (58, 110, 178)
    gruen = (66, 150, 92)
    orange = (196, 118, 40)
    rohrfarbe = (205, 60, 60)

    platte = [tri for s in g.teil_grundplatte(p) for tri in s]
    gabel = [tri for s in g.teil_drehgabel(p) for tri in s]
    schelle = [tri for s in g.teil_rohrschelle(p) for tri in s]
    stift = [tri for s in g.teil_achsstift(p) for tri in s]

    # --- Baugruppe -------------------------------------------------------
    pivot_z = g.PLATTE_H + p["pivot_z"]
    gabel_a = g.verschieben(gabel, 0, 0, g.PLATTE_H)

    # Schelle: Rohrachse von Z nach X kippen, Oeffnung (+X) zeigt nach +Z
    schelle_a = rot_y(g.verschieben(schelle, 0, 0, -g.SCHELLE_LAENGE / 2.0),
                      -math.pi / 2)
    schelle_a = g.verschieben(schelle_a, 0, 0, pivot_z)

    # Achsstifte von aussen durch die Arme
    stift_r = rot_x(stift, math.pi / 2)      # zeigt jetzt nach -Y
    stift_rechts = g.verschieben(stift_r, 0, p["arm_aussen_y"] + 1.0, pivot_z)
    stift_links = rot_x(stift, -math.pi / 2)
    stift_links = g.verschieben(stift_links, 0, -(p["arm_aussen_y"] + 1.0), pivot_z)

    # Fernrohr-Attrappe
    # Attrappe minimal duenner als das echte Rohr, sonst flackert die
    # Darstellung gegen die Schelleninnenseite (Maleralgorithmus)
    rohr = zylinder_x(g.ROHR_D / 2.0 - 1.5, -140, 170, 60)
    rohr = g.verschieben(rohr, 0, 0, pivot_z)

    bild(os.path.join(ziel, "ansicht_baugruppe.svg"),
         [(platte, grau), (gabel_a, blau), (schelle_a, gruen),
          (stift_rechts, orange), (stift_links, orange), (rohr, rohrfarbe)],
         drehung=math.radians(30), skala=1.35,
         titel="Fernrohrhalter, zusammengebaut",
         untertitel="grau Grundplatte - blau Drehgabel (schwenkt) - gruen "
                    "Rohrschelle (neigt) - orange Achsstifte - rot Fernrohr")

    # --- Einzelteile -----------------------------------------------------
    abstand = 0.0
    teile_nebeneinander = []
    for mesh, farbe, platz in ((platte, grau, 130), (gabel, blau, 120),
                               (schelle, gruen, 90), (stift, orange, 40)):
        teile_nebeneinander.append((g.verschieben(mesh, abstand, 0, 0), farbe))
        abstand += platz
    bild(os.path.join(ziel, "ansicht_teile.svg"), teile_nebeneinander,
         drehung=math.radians(25), skala=1.35,
         titel="Die vier Teile, jeweils in Drucklage",
         untertitel="Grundplatte 1x - Drehgabel 1x - Rohrschelle 1x - "
                    "Achsstift 2x, alle ohne Stuetzen druckbar")

    for name in ("ansicht_baugruppe.svg", "ansicht_teile.svg"):
        print("%-28s %6.0f kB"
              % (name, os.path.getsize(os.path.join(ziel, name)) / 1024.0))


if __name__ == "__main__":
    main()
