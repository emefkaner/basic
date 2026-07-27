#!/usr/bin/env python3
"""
Erzeugt eine SVG-Ansicht des Schutzrings aus den Meshes von generate.py.

Kleiner Software-Renderer: Isometrische Projektion, Rueckseiten-Aussortierung,
Maleralgorithmus (hinten nach vorne) und einfache Lambert-Schattierung.
Bewusst ohne externe Bibliotheken.
"""

import math
import os

import generate as g


LICHT = (-0.45, -0.62, 0.65)       # Lichtrichtung (normiert)


def projizieren(punkt, drehung, tilt):
    x, y, z = punkt
    cw, sw = math.cos(drehung), math.sin(drehung)
    xs = x * cw - y * sw
    ys = x * sw + y * cw
    sx = xs
    sy = -(ys * math.sin(tilt) + z * math.cos(tilt))
    tiefe = -ys * math.cos(tilt) + z * math.sin(tilt)
    return sx, sy, tiefe


def normale(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    laenge = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / laenge, ny / laenge, nz / laenge


def drehen_z(dreiecke, winkel):
    cw, sw = math.cos(winkel), math.sin(winkel)
    return [tuple((x * cw - y * sw, x * sw + y * cw, z) for (x, y, z) in t)
            for t in dreiecke]


def schattieren(basis, intensitaet):
    return "#%02x%02x%02x" % tuple(
        max(0, min(255, int(k * intensitaet))) for k in basis)


def rendern(teile, drehung, skala, tilt, rand=14.0):
    """teile: Liste (dreiecke, basisfarbe) -> (svg_fragmente, breite, hoehe)."""
    flaechen = []
    for dreiecke, farbe in teile:
        for tri in dreiecke:
            p = [projizieren(v, drehung, tilt) for v in tri]
            n = normale(*tri)
            # Blickrichtung im gedrehten System auf die Weltnormale zurueckrechnen
            cw, sw = math.cos(drehung), math.sin(drehung)
            nx = n[0] * cw - n[1] * sw
            ny = n[0] * sw + n[1] * cw
            sicht = -ny * math.cos(tilt) + n[2] * math.sin(tilt)
            if sicht <= 0.0:
                continue                                  # Rueckseite
            hell = 0.32 + 0.68 * max(0.0, nx * LICHT[0] + ny * LICHT[1] + n[2] * LICHT[2])
            tiefe = sum(q[2] for q in p) / 3.0
            flaechen.append((tiefe, p, schattieren(farbe, hell)))

    flaechen.sort(key=lambda f: f[0])

    xs = [q[0] for _, p, _ in flaechen for q in p]
    ys = [q[1] for _, p, _ in flaechen for q in p]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    fragmente = []
    for _, p, farbe in flaechen:
        pts = " ".join("%.2f,%.2f" % ((q[0] - minx) * skala + rand,
                                      (q[1] - miny) * skala + rand) for q in p)
        fragmente.append('<polygon points="%s" fill="%s"/>' % (pts, farbe))

    return (fragmente,
            (maxx - minx) * skala + 2 * rand,
            (maxy - miny) * skala + 2 * rand)


def bild(pfad, teile, drehung, skala, titel, untertitel, tilt=math.radians(26.0)):
    fragmente, breite, hoehe = rendern(teile, drehung, skala, tilt)
    kopf = 34.0
    fuss = 26.0
    zeilen = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
        'viewBox="0 0 %.1f %.1f">' % (breite, hoehe + kopf + fuss, breite, hoehe + kopf + fuss),
        '<rect width="100%%" height="100%%" fill="#fbfbfa"/>',
        '<text x="%.1f" y="23" font-family="sans-serif" font-size="16" font-weight="600" '
        'text-anchor="middle" fill="#1a1a1a">%s</text>' % (breite / 2.0, titel),
        '<g transform="translate(0,%.1f)" shape-rendering="crispEdges">' % kopf,
    ]
    zeilen.extend(fragmente)
    zeilen.append('</g>')
    zeilen.append('<text x="%.1f" y="%.1f" font-family="sans-serif" font-size="12" '
                  'text-anchor="middle" fill="#555">%s</text>'
                  % (breite / 2.0, hoehe + kopf + 17, untertitel))
    zeilen.append('</svg>')
    with open(pfad, "w") as f:
        f.write("\n".join(zeilen))
    return os.path.basename(pfad)


def detail_steckverbindung(pfad, anzahl_segmente=3):
    """Massstaebliche Detailzeichnung der Stossstelle, von oben gesehen.

    Die Verzahnung liegt in den Stirnflaechen und ist in einer 3D-Ansicht
    zwangslaeufig verdeckt -- deshalb hier als Draufsicht. Das Bild ist so
    gedreht, dass die Stossfuge waagerecht auf der Bildmitte liegt:
    radiale Richtung nach rechts, Bogenrichtung nach oben.
    """
    phi = 2.0 * math.pi / anzahl_segmente
    dreh = -phi                                   # Fuge auf die x-Achse legen

    def gedreht(poly, extra):
        w = dreh + extra
        cw, sw = math.cos(w), math.sin(w)
        return [(x * cw - y * sw, x * sw + y * cw) for x, y in poly]

    unten = gedreht(g.segment_profil(anzahl_segmente), 0.0)        # mit Zapfen
    oben = gedreht(g.segment_profil(anzahl_segmente), phi)         # mit Nut

    # Ausschnitt so gross, dass der Klotz samt Auslauf und ein Stueck der
    # normalen Wand zu sehen ist; seitlich Platz fuer die Beschriftung.
    x0, x1 = g.R_INNEN - 20.0, g.R_KLOTZ + 18.0
    y0, y1 = -40.0, 40.0
    skala = 8.0
    kopf, fuss = 5.5, 7.0                          # in mm der Zeichenebene
    oy0, oy1 = -y1 - kopf, -y0 + fuss               # SVG-y der Gesamtflaeche

    def pfad_von(poly):
        return " ".join("%.3f,%.3f" % (x, -y) for x, y in poly)

    z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
         'viewBox="%.2f %.2f %.2f %.2f">'
         % ((x1 - x0) * skala, (oy1 - oy0) * skala, x0, oy0, x1 - x0, oy1 - oy0),
         '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="#fbfbfa"/>'
         % (x0, oy0, x1 - x0, oy1 - oy0),
         # Die Segmente laufen ueber den Ausschnitt hinaus -> abschneiden,
         # damit sie nicht in Titel- und Fusszeile ragen.
         '<clipPath id="feld"><rect x="%.2f" y="%.2f" width="%.2f" height="%.2f"/></clipPath>'
         % (x0, -y1, x1 - x0, y1 - y0),
         '<text x="%.2f" y="%.2f" font-family="sans-serif" font-size="2.4" '
         'font-weight="600" text-anchor="middle" fill="#1a1a1a">'
         'Steckverbindung, von oben gesehen</text>'
         % ((x0 + x1) / 2.0, -y1 - 1.8)]

    z.append('<g clip-path="url(#feld)">')
    z.append('<polygon points="%s" fill="#42965c" fill-opacity="0.85" stroke="#16341f" '
             'stroke-width="0.12"/>' % pfad_von(oben))
    z.append('<polygon points="%s" fill="#3a6eb2" fill-opacity="0.85" stroke="#122c4d" '
             'stroke-width="0.12"/>' % pfad_von(unten))
    z.append('</g>')

    # Stossfuge andeuten
    z.append('<line x1="%.2f" y1="0" x2="%.2f" y2="0" stroke="#c02020" '
             'stroke-width="0.09" stroke-dasharray="1.1 0.8"/>' % (x0 + 0.5, x1 - 0.5))

    def label(x, y, text, anker="middle"):
        z.append('<text x="%.2f" y="%.2f" font-family="sans-serif" font-size="1.15" '
                 'text-anchor="%s" fill="#1a1a1a">%s</text>' % (x, -y, anker, text))

    def masslinie(xa, ya, xb, yb, text, tx, ty, anker="middle"):
        z.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#1a1a1a" '
                 'stroke-width="0.11"/>' % (xa, -ya, xb, -yb))
        label(tx, ty, text, anker)

    r_s = g.R_SCHWALBE
    a_zapfen = g.SCHWALBE_TIEFE

    masslinie(r_s - g.SCHWALBE_KOPF / 2, a_zapfen, r_s + g.SCHWALBE_KOPF / 2, a_zapfen,
              "Kopf %.1f" % g.SCHWALBE_KOPF, r_s, a_zapfen + 0.9)
    masslinie(r_s - g.SCHWALBE_HALS / 2, -1.6, r_s + g.SCHWALBE_HALS / 2, -1.6,
              "Hals %.1f" % g.SCHWALBE_HALS, r_s, -3.7)
    masslinie(g.R_KLOTZ - 1.6, 0.0, g.R_KLOTZ - 1.6, a_zapfen,
              "Tiefe %.1f" % g.SCHWALBE_TIEFE, g.R_KLOTZ - 2.2, a_zapfen / 2, "end")
    masslinie(g.R_INNEN, -37.0, g.R_AUSSEN, -37.0,
              "Wand %.1f" % g.WANDSTAERKE, (g.R_INNEN + g.R_AUSSEN) / 2, -39.2)
    masslinie(g.R_INNEN, 21.0, g.R_KLOTZ, 21.0,
              "Klotz %.1f dick" % (g.R_KLOTZ - g.R_INNEN),
              (g.R_INNEN + g.R_KLOTZ) / 2, 21.9)

    label(x0 + 1.0, 30.0, "Ringmitte", "start")
    label(x1 - 1.0, 30.0, "aussen", "end")
    label(x0 + 1.0, -14.0, "Segment mit", "start")
    label(x0 + 1.0, -16.5, "Zapfen", "start")
    label(x0 + 1.0, 8.0, "Segment mit", "start")
    label(x0 + 1.0, 5.5, "Nut", "start")

    z.append('<text x="%.2f" y="%.2f" font-family="sans-serif" font-size="1.7" '
             'text-anchor="middle" fill="#555">'
             '%.2f mm Spiel je Flanke - der Zapfen wird von oben eingeschoben</text>'
             % ((x0 + x1) / 2.0, -y0 + 3.8, g.SPIEL))
    z.append('</svg>')

    with open(pfad, "w") as f:
        f.write("\n".join(z))


def main():
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    os.makedirs(ziel, exist_ok=True)

    # Grobere Aufloesung -- reicht fuer die Ansicht und haelt die SVG klein
    g.BOGEN_SCHRITT_GRAD = 3.0
    g.VERRUNDUNG_STUFEN = 4

    blau = (58, 110, 178)
    gruen = (66, 150, 92)

    # 1) Zusammengesteckter Ring aus zwei Halbschalen
    seg = g.segment_mesh(2)
    ring = [(drehen_z(seg, 0.0), blau),
            (drehen_z(seg, math.pi), gruen)]
    bild(os.path.join(ziel, "ansicht_ring_2teilig.svg"), ring,
         drehung=math.radians(35), skala=1.45,
         titel="Zusammengesteckt: 2 Halbschalen",
         untertitel="Aussen %.0f mm - Hoehe %.0f mm - Oberkante R%.1f verrundet"
                    % (g.AUSSEN_DURCHMESSER, g.HOEHE, g.VERRUNDUNG))

    # 2) Einzelnes Segment, wie es auf dem Druckbett liegt
    bild(os.path.join(ziel, "ansicht_segment_2teilig.svg"), [(seg, blau)],
         drehung=math.radians(35), skala=1.45,
         titel="Ein Segment (2x drucken)",
         untertitel="links Schwalbenschwanz-Nut, rechts Zapfen")

    detail_steckverbindung(os.path.join(ziel, "ansicht_steckverbindung.svg"))

    for name in ("ansicht_ring_2teilig.svg", "ansicht_segment_2teilig.svg",
                 "ansicht_steckverbindung.svg"):
        p = os.path.join(ziel, name)
        print("%-32s %6.0f kB" % (name, os.path.getsize(p) / 1024.0))


if __name__ == "__main__":
    main()
