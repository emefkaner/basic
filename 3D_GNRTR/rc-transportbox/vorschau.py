#!/usr/bin/env python3
"""Ansichten der RC-Transportbox (Renderer wie in den Nachbarprojekten)."""

import argparse
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


def falz_detail(pfad, p):
    """Massstaeblicher Schnitt durch die Stossfuge Wanne/Deckel.

    Der Falz liegt in der Wandstaerke und ist von aussen unsichtbar --
    deshalb hier als Schnitt statt als 3D-Ansicht. Gezeichnet wird in
    (Wandrichtung, Hoehe); aussen ist rechts.
    """
    W, FT, FS, FH = g.WAND, g.FALZ_T, g.FALZ_SP, g.FALZ_H
    z_fach = p["z_fach"]
    z_rand = p["wanne_innen_h"]
    # Wandkoordinaten: 0 = Wanneninnenkante, W = Aussenkante
    x0, x1 = -19.0, W + 21.0
    y0, y1 = z_fach - 7.0, z_rand + g.DECKEL_INNEN * 0.5
    skala = 11.0
    kopf, fuss = 4.5, 5.5
    oy0, oy1 = -y1 - kopf, -y0 + fuss

    def poly(pts, fill, stroke):
        d = " ".join("%.3f,%.3f" % (x, -y) for x, y in pts)
        return ('<polygon points="%s" fill="%s" fill-opacity="0.9" '
                'stroke="%s" stroke-width="0.12"/>' % (d, fill, stroke))

    z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
         'viewBox="%.2f %.2f %.2f %.2f">'
         % ((x1 - x0) * skala, (oy1 - oy0) * skala, x0, oy0, x1 - x0, oy1 - oy0),
         '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="#fbfbfa"/>'
         % (x0, oy0, x1 - x0, oy1 - oy0),
         '<text x="%.2f" y="%.2f" font-family="sans-serif" font-size="1.7" '
         'font-weight="600" text-anchor="middle" fill="#1a1a1a">'
         'Stufenfalz im Schnitt &#8212; aussen rechts</text>'
         % ((x0 + x1) / 2.0, -y1 - 1.2)]

    # Wanne: unten volle Wand, oben die Falzstufe (Innenkante um FT zurueck)
    z.append(poly([(0, y0), (W, y0), (W, z_rand), (FT, z_rand),
                   (FT, z_fach), (0, z_fach)], "#78818c", "#39414b"))
    # Deckel: Wandring plus Lippe, die in die Stufe greift
    dz = z_rand + g.DECKEL_INNEN * 0.5
    z.append(poly([(0 + FS, z_fach + 0.5), (FT - FS, z_fach + 0.5),
                   (FT - FS, z_rand), (W, z_rand), (W, dz), (0, dz),
                   (0, z_rand), (0 + FS, z_rand)], "#3a6eb2", "#12294a"))

    def label(x, y, t, anker="middle", farbe="#1a1a1a"):
        z.append('<text x="%.2f" y="%.2f" font-family="sans-serif" '
                 'font-size="1.15" text-anchor="%s" fill="%s">%s</text>'
                 % (x, -y, anker, farbe, t))

    def masslinie(xa, ya, xb, yb):
        z.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" '
                 'stroke="#1a1a1a" stroke-width="0.09"/>' % (xa, -ya, xb, -yb))

    masslinie(W + 1.5, z_fach, W + 1.5, z_rand)
    label(W + 2.0, (z_fach + z_rand) / 2, "Falz %.0f tief" % FH, "start")
    masslinie(FS, z_fach + 1.5, FT - FS, z_fach + 1.5)
    label((FT) / 2, z_fach + 2.2, "Lippe %.1f" % (FT - 2 * FS))
    masslinie(0, y0 + 1.0, W, y0 + 1.0)
    label(W / 2, y0 + 1.7, "Wand %.1f" % W)
    label(x1 - 0.5, z_rand + 1.4, "buendige Aussenfuge", "end", "#b03030")
    z.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#b03030" '
             'stroke-width="0.09" stroke-dasharray="0.7 0.5"/>'
             % (FT, -z_rand, x1 - 0.5, -z_rand))
    label(x0 + 0.5, z_fach + 3.0, "Kofferinneres", "start", "#666")
    label(x0 + 0.5, z_rand + 5.0, "Deckel", "start", "#12294a")
    label(x1 - 0.5, z_fach - 3.5, "Wanne", "end", "#39414b")
    z.append('<text x="%.2f" y="%.2f" font-family="sans-serif" font-size="1.2" '
             'text-anchor="middle" fill="#555">'
             '%.2f mm Spiel je Flanke - Deckel liegt auf der Wannenwand auf, '
             'nicht auf der Lippe</text>'
             % ((x0 + x1) / 2.0, -y0 + 3.2, FS))
    z.append('</svg>')
    with open(pfad, "w") as f:
        f.write("\n".join(z))


def draufsicht(pfad, p):
    """Massstaebliche Belegung der Wanne von oben.

    Zeigt, was den Platz wirklich belegt: die Controller-Silhouette, die
    Auto-Box und die zwei Hot-Wheels-Faecher -- plus die Restflaechen mit
    ihren Maszen. Die Restflaechen sehen im 3D-Bild groesser aus als sie
    sind, weil die Mulde konkav ist."""
    ix, iy = p["innen_x"] / 2.0, p["innen_y"] / 2.0
    ax, ay = p["aussen_x"] / 2.0, p["aussen_y"] / 2.0
    mx0, my0 = p["fachC_x0"], -p["fachC_t"] / 2.0
    kontur = [(x + mx0, y + my0) for (x, y) in p["kontur"]]
    s = 2.2
    rand = 26.0
    W = (2 * ax + 2 * rand) * s
    H = (2 * ay + 2 * rand) * s + 30

    def X(x):
        return (x + ax + rand) * s

    def Y(y):
        return (ay - y + rand) * s + 26

    z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
         'viewBox="0 0 %.0f %.0f">' % (W, H, W, H),
         '<rect width="100%%" height="100%%" fill="#fbfbfa"/>',
         '<text x="%.0f" y="20" font-family="sans-serif" font-size="15" '
         'font-weight="600" text-anchor="middle" fill="#1a1a1a">'
         'Wanne von oben &#8212; was den Platz belegt</text>' % (W / 2)]

    def poly(pts, fill, stroke, sw=1.0, dash=""):
        d = " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in pts)
        return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"'
                '%s/>' % (d, fill, stroke, sw,
                          ' stroke-dasharray="%s"' % dash if dash else ""))

    def txt(x, y, t, size=9.5, farbe="#1a1a1a", anker="middle", fett=False):
        z.append('<text x="%.1f" y="%.1f" font-family="sans-serif" '
                 'font-size="%.1f" text-anchor="%s" fill="%s"%s>%s</text>'
                 % (X(x), Y(y), size, anker, farbe,
                    ' font-weight="600"' if fett else "", t))

    z.append(poly(g.rundrechteck(2 * ax, 2 * ay, g.ECKRADIUS),
                  "#e9e9e6", "#8a8f96", 1.2))
    z.append(poly(g.rundrechteck(2 * ix, 2 * iy, g.ECKRADIUS - g.WAND),
                  "#f7f7f5", "#b8bcc2", 1.0))
    z.append(poly(kontur, "#c8663f", "#8d4225", 1.0))
    txt(mx0 + p["rad_pos"][0], my0 + p["rad_pos"][1] - 4, "Rad", 10, "#fff")
    txt(mx0 + p["griff_pos"][0] - 14, my0 + p["griff_pos"][1], "Griff", 10, "#fff")
    txt(mx0 + p["schnauz_pos"][0] + 26, my0 + p["schnauz_pos"][1] - 26,
        "Controller", 11, "#fff", fett=True)

    z.append(poly([(p["fachA_x0"], p["fachA_y0"]), (p["fachA_x1"], p["fachA_y0"]),
                   (p["fachA_x1"], p["fachA_y1"]), (p["fachA_x0"], p["fachA_y1"])],
                  "#b1483f", "#7d2a23", 1.0))
    txt((p["fachA_x0"] + p["fachA_x1"]) / 2.0,
        (p["fachA_y0"] + p["fachA_y1"]) / 2.0 + 6, "Auto-Box", 10, "#fff", fett=True)
    txt((p["fachA_x0"] + p["fachA_x1"]) / 2.0,
        (p["fachA_y0"] + p["fachA_y1"]) / 2.0 - 6, "100 x 50", 9, "#f4d7d2")

    hb, hl = p["hw_licht"]
    for nr, (x0, x1, y0, y1) in enumerate(p["hw"], 1):
        # rundrechteck liegt um (0,0) -> auf die Fachmitte verschieben
        z.append(poly([(px + (x0 + x1) / 2.0, py + (y0 + y1) / 2.0)
                       for px, py in g.rundrechteck(
                           x1 - x0 + 2 * g.HW_WAND, y1 - y0 + 2 * g.HW_WAND,
                           g.HW_ECKE + g.HW_WAND)], "#3a6eb2", "#12294a", 1.0))
        z.append(poly([(px + (x0 + x1) / 2.0, py + (y0 + y1) / 2.0)
                       for px, py in g.rundrechteck(x1 - x0, y1 - y0, g.HW_ECKE)],
                      "#dce6f4", "#12294a", 0.8))
        txt((x0 + x1) / 2.0, (y0 + y1) / 2.0 + 8, "Hot Wheels %d" % nr,
            9.5, "#12294a", fett=True)
        txt((x0 + x1) / 2.0, (y0 + y1) / 2.0 - 6, "%.0f x %.0f licht" % (hb, hl),
            8.5, "#3a5578")

    txt(0, iy + 12, "aussen %.0f x %.0f mm" % (p["aussen_x"], p["aussen_y"]),
        10, "#555")
    txt(0, -iy - 17, "Rest links: Keilform, unter 43 mm breit &#8212; kein "
                     "zweites Auto. Rest rechts: 15 mm Streifen.", 9, "#777")
    z.append('</svg>')
    with open(pfad, "w") as f:
        f.write("\n".join(z))


def materialschnitt(pfad, p, zs=15.0):
    """Waagerechter Materialschnitt durch die fertige Wannengeometrie.

    Nicht aus der Planung gezeichnet, sondern aus den Dreiecken selbst:
    jedes Dreieck, das die Ebene z=zs schneidet, liefert ein Segment,
    danach entscheidet ein Strahl je Rasterpunkt (ungerade Zahl von
    Schnitten = Material). So sieht man sofort, ob ein Fach wirklich frei
    ist -- ein zugefuelltes Fach faellt in der 3D-Ansicht nicht auf."""
    schalen = g.teil_wanne(p)
    tris = [t for s_ in schalen for t in (s_[0] if isinstance(s_, tuple) else s_)]
    seg = []
    for (a, b, c) in tris:
        pts = []
        for q0, q1 in ((a, b), (b, c), (c, a)):
            if (q0[2] - zs) * (q1[2] - zs) < 0:
                t = (zs - q0[2]) / (q1[2] - q0[2])
                pts.append((q0[0] + (q1[0] - q0[0]) * t,
                            q0[1] + (q1[1] - q0[1]) * t))
        if len(pts) == 2:
            seg.append(pts)
    ix = p["innen_x"] / 2.0 + g.WAND
    iy = p["innen_y"] / 2.0 + g.WAND
    step = 1.5
    rows = []
    y = iy
    while y > -iy:
        xs = []
        for (q0, q1) in seg:
            if min(q0[1], q1[1]) <= y <= max(q0[1], q1[1]) and abs(q1[1] - q0[1]) > 1e-12:
                t = (y - q0[1]) / (q1[1] - q0[1])
                if 0.0 <= t <= 1.0:
                    xs.append(q0[0] + (q1[0] - q0[0]) * t)
        row, x = [], -ix
        while x < ix:
            row.append(sum(1 for xv in xs if xv < x) % 2 == 1)
            x += step
        rows.append(row)
        y -= step
    b = len(rows[0])
    W, H = b * 4 + 40, len(rows) * 4 + 80
    z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
         'viewBox="0 0 %d %d">' % (W, H, W, H),
         '<rect width="100%%" height="100%%" fill="#fbfbfa"/>',
         '<text x="%d" y="24" font-family="sans-serif" font-size="15" '
         'font-weight="600" text-anchor="middle" fill="#1a1a1a">'
         'Materialschnitt auf halber Fachhoehe (z = %.0f mm)</text>'
         % (W / 2, zs)]
    for i, row in enumerate(rows):
        x0 = None
        for j, voll in enumerate(row + [False]):
            if voll and x0 is None:
                x0 = j
            elif not voll and x0 is not None:
                z.append('<rect x="%d" y="%d" width="%d" height="4" '
                         'fill="#5a6672"/>' % (20 + x0 * 4, 40 + i * 4,
                                               (j - x0) * 4))
                x0 = None
    z.append('<text x="%d" y="%d" font-family="sans-serif" font-size="12" '
             'text-anchor="middle" fill="#555">grau = Material, weiss = Luft '
             '- die Hot-Wheels-Faecher sind durchgehend offen</text>'
             % (W / 2, len(rows) * 4 + 64))
    z.append('</svg>')
    with open(pfad, "w") as f:
        f.write("\n".join(z))


def controller_lage(pfad, p):
    """Erklaerbild: wie der Controller in der Mulde liegt.

    Oben links die Silhouette in der Orientierung des Nutzerfotos (Rad
    links, Griffende rechts) mit der Stelle, an der dort das Hot Wheels
    lag; oben rechts dieselbe Form um 90 Grad gedreht in der Wanne; unten
    ein Hoehenschnitt, der zeigt, was in der 30 mm tiefen Mulde steckt und
    was frei in den Deckelraum ragt."""
    mx0, my0 = p["fachC_x0"], -p["fachC_t"] / 2.0
    kontur = p["kontur"]
    foto = [(190.0 - y, x) for (x, y) in kontur]
    W, H = 1120, 800
    z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
         'viewBox="0 0 %d %d">' % (W, H, W, H),
         '<rect width="100%%" height="100%%" fill="#fbfbfa"/>',
         '<text x="%d" y="30" font-family="sans-serif" font-size="18" '
         'font-weight="600" text-anchor="middle" fill="#1a1a1a">'
         'So liegt der Controller in der Mulde</text>' % (W / 2)]

    def txt(x, y, t, size=12, farbe="#444", anker="middle", fett=False):
        z.append('<text x="%.1f" y="%.1f" font-family="sans-serif" '
                 'font-size="%d" text-anchor="%s" fill="%s"%s>%s</text>'
                 % (x, y, size, anker, farbe,
                    ' font-weight="600"' if fett else "", t))

    # ---- oben links: Orientierung wie auf dem Foto
    ox, oy, fs = 40, 96, 2.15
    z.append('<polygon points="%s" fill="#c8663f" stroke="#8d4225" '
             'stroke-width="1.6"/>'
             % " ".join("%.1f,%.1f" % (ox + x * fs, oy + y * fs)
                        for x, y in foto))
    txt(ox + 205, 74, "1 - wie auf deinem Foto, von oben", 14, "#1a1a1a",
        "middle", True)
    txt(ox + 30 * fs, oy + 30 * fs, "Rad", 12, "#fff")
    txt(ox + 150 * fs, oy + 95 * fs, "Griff", 12, "#fff")
    z.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5" '
             'fill="#e5dcf2" fill-opacity="0.75" stroke="#7d3fa8" '
             'stroke-width="2"/>'
             % (ox + 75 * fs, oy + 2 * fs, 88 * fs, 35 * fs))
    txt(ox + 119 * fs, oy + 24 * fs, "Hot Wheels", 12, "#4b2570", "middle", True)

    # ---- oben rechts: Einbaulage
    bx, by, sc = 620, 96, 1.42
    ix, iy = p["innen_x"] / 2.0, p["innen_y"] / 2.0

    def X(x):
        return bx + (x + ix) * sc

    def Y(y):
        return by + (iy - y) * sc

    z.append('<polygon points="%s" fill="#f2f2ef" stroke="#b8bcc2" '
             'stroke-width="1.4"/>'
             % " ".join("%.1f,%.1f" % (X(x), Y(y))
                        for x, y in g.rundrechteck(2 * ix, 2 * iy, 8)))
    z.append('<polygon points="%s" fill="#c8663f" stroke="#8d4225" '
             'stroke-width="1.4"/>'
             % " ".join("%.1f,%.1f" % (X(x + mx0), Y(y + my0))
                        for x, y in kontur))
    for (x0, x1, y0, y1) in p["hw"]:
        z.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6" '
                 'fill="#e5dcf2" stroke="#7d3fa8" stroke-width="1.6"/>'
                 % (X(x0), Y(y1), (x1 - x0) * sc, (y1 - y0) * sc))
    z.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
             'fill="#b1483f" stroke="#7d2a23" stroke-width="1.4"/>'
             % (X(p["fachA_x0"]), Y(p["fachA_y1"]),
                (p["fachA_x1"] - p["fachA_x0"]) * sc,
                (p["fachA_y1"] - p["fachA_y0"]) * sc))
    txt(bx + ix * sc, 74, "2 - dieselbe Form in der Wanne (90 Grad gedreht)",
        14, "#1a1a1a", "middle", True)
    txt(X(mx0 + p["rad_pos"][0]), Y(my0 + p["rad_pos"][1]), "Rad", 12, "#fff")
    txt(X(mx0 + p["griff_pos"][0]), Y(my0 + p["griff_pos"][1]) + 4, "Griff",
        12, "#fff")
    txt(X((p["fachA_x0"] + p["fachA_x1"]) / 2.0),
        Y((p["fachA_y0"] + p["fachA_y1"]) / 2.0), "Auto-Box", 12, "#fff",
        "middle", True)

    # ---- unten: Hoehenschnitt
    hy, hs, hx = 700, 4.0, 150
    txt(hx + 160, 436, "3 - Hoehenschnitt: was steckt drin, was ragt heraus",
        14, "#1a1a1a", "middle", True)

    def HY(zz):
        return hy - zz * hs

    z.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#dfe1e4" '
             'stroke="#8a8f96"/>'
             % (hx - 26, HY(p["wanne_innen_h"]), 26,
                p["wanne_innen_h"] * hs))
    z.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#dfe1e4" '
             'stroke="#8a8f96"/>'
             % (hx + 170, HY(p["wanne_innen_h"]), 26,
                p["wanne_innen_h"] * hs))
    z.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" '
             'stroke="#8a8f96" stroke-dasharray="5 4"/>'
             % (hx - 26, HY(p["wanne_innen_h"] + g.DECKEL_INNEN), 222,
                g.DECKEL_INNEN * hs))
    z.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#c8663f"/>'
             % (hx, HY(g.CTRL_GEHAEUSE_D), 105, g.CTRL_GEHAEUSE_D * hs))
    z.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#2b2b30"/>'
             % (hx + 107, HY(g.CTRL_H), 60, g.CTRL_H * hs))
    txt(hx + 52, HY(g.CTRL_GEHAEUSE_D) + 26, "Gehaeuse", 12, "#fff")
    txt(hx + 137, HY(g.CTRL_H) + 26, "Rad", 12, "#fff")
    for zz, t in ((0, "0  Muldenboden"), (g.MULDE_HOEHE, "30  Muldenkante"),
                  (p["wanne_innen_h"], "39  Wannenrand"),
                  (g.CTRL_GEHAEUSE_D, "42  Gehaeuse"),
                  (g.CTRL_H, "57  Rad"),
                  (p["wanne_innen_h"] + g.DECKEL_INNEN, "60  Deckeldecke")):
        z.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#aaa" '
                 'stroke-width="0.8" stroke-dasharray="3 3"/>'
                 % (hx - 34, HY(zz), hx + 232, HY(zz)))
        txt(hx + 240, HY(zz) + 4, t, 12, "#555", "start")
    txt(620, 560, "Der Controller ist 42 mm dick, die Mulde nur 30 mm tief.",
        13, "#444", "start")
    txt(620, 582, "Er steckt also 30 mm in der Mulde und steht 12 mm heraus,",
        13, "#444", "start")
    txt(620, 604, "das Drehrad 27 mm. Ueber dem Wannenrand hat der Deckel",
        13, "#444", "start")
    txt(620, 626, "21 mm lichte Hoehe - beides passt hinein, das Rad mit",
        13, "#444", "start")
    txt(620, 648, "3 mm Luft. Deshalb Rad nach OBEN einlegen.",
        13, "#444", "start")
    z.append('</svg>')
    with open(pfad, "w") as f:
        f.write("\n".join(z))


def scharnier_ansicht(pfad, p, wanne, deckel_zu):
    """Blick von hinten auf das Scharnierband.

    Der Deckel wird gespiegelt gedruckt; ob seine Segmente wirklich in die
    Luecken der Wanne greifen, sieht man nur in der Einbaulage. Deshalb
    hier Wanne und geschlossener Deckel uebereinander, auf den hinteren
    Streifen beschnitten."""
    yb = p["aussen_y"] / 2.0 - 14.0
    wf = [t for t in wanne if all(q[1] > yb for q in t)]
    df = [t for t in deckel_zu if all(q[1] > yb for q in t)]
    bild(pfad, [(wf, (120, 125, 132)), (df, (58, 110, 178))],
         drehung=math.radians(180), skala=3.2,
         titel="Scharnierband von hinten (Wanne grau, Deckel blau)",
         untertitel="%d Segmente a %.0f mm, verzahnt - tragende Breite "
                    "%.0f mm, Achse: %.2f mm Rohfilament"
                    % (g.SCHARNIER_SEG, p["schar_breite"],
                       len(p["schar_wanne"]) * p["schar_breite"],
                       g.FILAMENT_D),
         tilt=math.radians(72))


def deckel_aussen(pfad, p):
    """Der Deckel so, wie er auf dem fertigen Koffer liegt.

    Der Deckel wird GESPIEGELT gedruckt. Ein Logo hat eine Leserichtung,
    steht in den Druckkoordinaten also verkehrt herum -- ob es am Ende
    richtig liegt, sieht man nur in dieser Ansicht. Genau das ist einmal
    durchgerutscht: der Schriftzug kam spiegelverkehrt aus dem Drucker.
    """
    gruppen = p.get("logo_gruppen") or []
    ax, ay = p["aussen_x"] / 2.0, p["aussen_y"] / 2.0
    s = 2.2
    W, H = 2 * ax * s + 40, 2 * ay * s + 80

    def X(x):
        return (-x + ax) * s + 20        # Spiegelung = Gebrauchslage

    def Y(y):
        return (ay - y) * s + 50

    z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
         'viewBox="0 0 %.0f %.0f">' % (W, H, W, H),
         '<rect width="100%%" height="100%%" fill="#fbfbfa"/>',
         '<text x="%.0f" y="30" font-family="sans-serif" font-size="16" '
         'font-weight="600" text-anchor="middle" fill="#1a1a1a">'
         'Deckel von aussen, fertiger Koffer</text>' % (W / 2),
         '<polygon points="%s" fill="#6b7078"/>'
         % " ".join("%.1f,%.1f" % (X(x), Y(y))
                    for x, y in g.rundrechteck(2 * ax, 2 * ay, g.ECKRADIUS))]
    for farbe, teile in gruppen:
        for f, loecher in teile:
            d = "M" + " ".join("%.1f,%.1f" % (X(x), Y(y)) for x, y in f) + " Z"
            for h in loecher:
                d += " M" + " ".join("%.1f,%.1f" % (X(x), Y(y))
                                     for x, y in h) + " Z"
            z.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, farbe))
    z.append('<text x="%.0f" y="%.0f" font-family="sans-serif" font-size="12" '
             'text-anchor="middle" fill="#555">%s</text>'
             % (W / 2, H - 16,
                "Schriftzug muss hier LESBAR sein" if gruppen
                else "kein Logo (keine logo.svg im Ordner)"))
    z.append('</svg>')
    with open(pfad, "w") as f_:
        f_.write("\n".join(z))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mit-griff", action="store_true",
                    help="Ansichten mit Steck-Tragegriff rendern")
    g.MIT_GRIFF = ap.parse_args().mit_griff

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
    griff = flach(g.teil_griff(p)) if g.MIT_GRIFF else []

    # 1) Wanne offen, Blick in die Faecher; Attrappen des Inhalts
    box_att = g.prisma([(p["fachA_x0"] + 4, -g.AUTOBOX_L / 2),
                        (p["fachA_x0"] + 4 + g.AUTOBOX_B, -g.AUTOBOX_L / 2),
                        (p["fachA_x0"] + 4 + g.AUTOBOX_B, g.AUTOBOX_L / 2),
                        (p["fachA_x0"] + 4, g.AUTOBOX_L / 2)], 0.0, g.AUTOBOX_H)
    mx0 = p["fachC_x0"]
    my0 = -p["fachC_t"] / 2.0
    # Attrappe zweiteilig: Gehaeuse bis CTRL_GEHAEUSE_D, darueber das
    # Drehrad -- so ist sichtbar, dass das Rad nach OBEN frei ausragt
    ctrl_att = g.prisma([(x + mx0, y + my0) for (x, y) in p["kontur"]],
                        1.0, g.CTRL_GEHAEUSE_D)
    rad_att = g.prisma(g.kreis(22.0, mx0 + p["rad_pos"][0],
                               my0 + p["rad_pos"][1], 32),
                       g.CTRL_GEHAEUSE_D, g.CTRL_H)
    hw_att = []
    for (x0, x1, y0, y1) in p["hw"]:
        hw_att += g.prisma([(x0 + g.HW_LUFT, y0 + g.HW_LUFT),
                            (x1 - g.HW_LUFT, y0 + g.HW_LUFT),
                            (x1 - g.HW_LUFT, y1 - g.HW_LUFT),
                            (x0 + g.HW_LUFT, y1 - g.HW_LUFT)], 0.0, g.HW_H)
    bild(os.path.join(ziel, "ansicht_wanne_offen.svg"),
         [(wanne, grau), (box_att, rot), (ctrl_att, (200, 90, 60)),
          (rad_att, (40, 40, 44)), (hw_att, (150, 60, 130))],
         drehung=math.radians(28), skala=1.8,
         titel="Wanne: Konturmulde + Auto-Box (Attrappen rot)",
         untertitel="Gehaeuse (hell) in der Mulde, Drehrad (dunkel) frei "
                    "nach oben, zwei Hot Wheels (violett) in Einzelfaechern",
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
                    "Schnappzungen - hinten Scharnieraugen"
                    + (" - aussen T-Nuten" if g.MIT_GRIFF else ""),
         tilt=math.radians(42))

    # 3) Geschlossener Koffer mit Griff
    z_top = p["wanne_innen_h"] + g.DECKEL_INNEN + g.BODEN
    deckel_zu = [tuple((-x, y, z_top - z) for (x, y, z) in tri)
                 for tri in deckel]
    griff_zu = [tuple((x, y, z + z_top) for (x, y, z) in tri) for tri in griff]
    lagen = [(wanne, grau), (deckel_zu, blau)]
    if griff_zu:
        lagen.append((griff_zu, orange))
    bild(os.path.join(ziel, "ansicht_koffer_zu.svg"),
         lagen,
         drehung=math.radians(32), skala=2.0,
         titel=("Geschlossen, mit eingeschobenem Griff" if griff_zu
                else "Geschlossen - glatte Aussenflaeche, nur die Falzfuge"),
         untertitel=("aussen %.0f x %.0f x %.0f mm plus Griff" if griff_zu
                     else "aussen %.0f x %.0f x %.0f mm")
                    % (p["aussen_x"], p["aussen_y"], z_top + g.BODEN),
         tilt=math.radians(22))

    falz_detail(os.path.join(ziel, "ansicht_falz_schnitt.svg"), p)
    draufsicht(os.path.join(ziel, "ansicht_draufsicht.svg"), p)
    materialschnitt(os.path.join(ziel, "ansicht_schnitt.svg"), p)
    controller_lage(os.path.join(ziel, "ansicht_controller_lage.svg"), p)
    scharnier_ansicht(os.path.join(ziel, "ansicht_scharnier.svg"), p,
                      wanne, deckel_zu)
    g.logo_flaechen(p)
    deckel_aussen(os.path.join(ziel, "ansicht_deckel_aussen.svg"), p)

    for name in ("ansicht_wanne_offen.svg", "ansicht_deckel_innen.svg",
                 "ansicht_koffer_zu.svg", "ansicht_falz_schnitt.svg",
                 "ansicht_draufsicht.svg", "ansicht_schnitt.svg",
                 "ansicht_controller_lage.svg", "ansicht_scharnier.svg",
                 "ansicht_deckel_aussen.svg"):
        print("%-28s %6.0f kB"
              % (name, os.path.getsize(os.path.join(ziel, name)) / 1024.0))


if __name__ == "__main__":
    main()
