#!/usr/bin/env python3
"""Ansichten der RC-Transportbox (Renderer wie in den Nachbarprojekten)."""

import math
import os

import generate as g

LICHT = (-0.42, -0.55, 0.72)


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


def bild(pfad, teile, drehung, skala, titel, untertitel, tilt=math.radians(28)):
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
            hell = 0.32 + 0.68 * max(0.0, nx * LICHT[0] + ny * LICHT[1]
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
              'viewBox="0 0 %.1f %.1f">' % (b, h + 56, b, h + 56),
              '<rect width="100%" height="100%" fill="#fbfbfa"/>',
              '<text x="%.1f" y="24" font-family="sans-serif" font-size="16" '
              'font-weight="600" text-anchor="middle" fill="#1a1a1a">%s</text>'
              % (b / 2, titel),
              '<g transform="translate(0,34)" shape-rendering="crispEdges">']
    for _, p, farbe in flaechen:
        pts = " ".join("%.2f,%.2f" % ((q[0] - minx) * skala + 15,
                                      (q[1] - miny) * skala + 15) for q in p)
        zeilen.append('<polygon points="%s" fill="%s"/>' % (pts, farbe))
    zeilen.append('</g>')
    zeilen.append('<text x="%.1f" y="%.1f" font-family="sans-serif" font-size="12" '
                  'text-anchor="middle" fill="#555">%s</text>'
                  % (b / 2, h + 48, untertitel))
    zeilen.append('</svg>')
    with open(pfad, "w") as f:
        f.write("\n".join(zeilen))


def main():
    p = g.abgeleitet()
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")

    grau = (120, 125, 132)
    blau = (58, 110, 178)
    orange = (200, 122, 44)
    rot = (196, 70, 60)

    def flach(schalen):
        out = []
        for e in schalen:
            sch = e[0] if (isinstance(e, tuple) and len(e) == 2
                           and isinstance(e[0], list)) else e
            out.extend(sch)
        return out

    wanne = flach(g.teil_wanne(p))
    deckel = flach(g.teil_deckel(p))
    griff = flach(g.teil_griff(p))

    # 1) Wanne offen, Blick in die Faecher; Attrappen des Inhalts
    box_att = g.prisma([(p["fachA_x0"] + 4, -g.AUTOBOX_L / 2),
                        (p["fachA_x0"] + 4 + g.AUTOBOX_B, -g.AUTOBOX_L / 2),
                        (p["fachA_x0"] + 4 + g.AUTOBOX_B, g.AUTOBOX_L / 2),
                        (p["fachA_x0"] + 4, g.AUTOBOX_L / 2)], 0.0, g.AUTOBOX_H)
    mx0 = p["fachC_x0"]
    my0 = -p["fachC_t"] / 2.0
    ctrl_att = g.prisma([(x + mx0, y + my0) for (x, y) in p["kontur"]],
                        1.0, g.CTRL_H)
    bild(os.path.join(ziel, "ansicht_wanne_offen.svg"),
         [(wanne, grau), (box_att, rot), (ctrl_att, (200, 90, 60))],
         drehung=math.radians(28), skala=1.8,
         titel="Wanne: Konturmulde + Auto-Box (Attrappen rot)",
         untertitel="Controllerfach als Pistolen-Mulde nach Tray-Vorbild, "
                    "Klemmrippen an der Kontur",
         tilt=math.radians(52))

    # 1b) Wanne leer, damit die Mulde selbst sichtbar ist
    bild(os.path.join(ziel, "ansicht_wanne_leer.svg"),
         [(wanne, grau)],
         drehung=math.radians(28), skala=1.8,
         titel="Wanne leer: die Konturmulde",
         untertitel="Fuellschale mit pistolenfoermigem Loch, 26 mm tief, "
                    "8 Klemmrippen",
         tilt=math.radians(55))

    # 2) Deckel in Drucklage (Innenseite oben)
    bild(os.path.join(ziel, "ansicht_deckel_innen.svg"),
         [(deckel, blau)],
         drehung=math.radians(205), skala=2.0,
         titel="Deckel in Drucklage (Innenseite oben)",
         untertitel="Federboegen halten den Inhalt nieder - vorn "
                    "Schnappzungen - hinten Scharnieraugen - aussen T-Nuten",
         tilt=math.radians(42))

    # 3) Geschlossener Koffer mit Griff
    z_top = p["wanne_innen_h"] + g.DECKEL_INNEN + g.BODEN
    deckel_zu = [tuple((-x, y, z_top - z) for (x, y, z) in tri)
                 for tri in deckel]
    griff_zu = [tuple((x, y, z + z_top) for (x, y, z) in tri) for tri in griff]
    bild(os.path.join(ziel, "ansicht_koffer_zu.svg"),
         [(wanne, grau), (deckel_zu, blau), (griff_zu, orange)],
         drehung=math.radians(32), skala=2.0,
         titel="Geschlossen, mit eingeschobenem Griff",
         untertitel="aussen %.0f x %.0f x %.0f mm plus Griff"
                    % (p["aussen_x"], p["aussen_y"], z_top + g.BODEN),
         tilt=math.radians(22))

    for name in ("ansicht_wanne_offen.svg", "ansicht_deckel_innen.svg",
                 "ansicht_koffer_zu.svg"):
        print("%-28s %6.0f kB"
              % (name, os.path.getsize(os.path.join(ziel, name)) / 1024.0))


if __name__ == "__main__":
    main()
