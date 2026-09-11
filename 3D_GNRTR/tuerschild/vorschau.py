#!/usr/bin/env python3
"""Ansichten des Tuerschilds als SVG.

  ansicht_vorne.svg      -- so, wie es an der Tuer haengt (beide Varianten
                            sehen von vorn gleich aus).
  ansicht_ams_schnitt.svg -- Waagrechter Schnitt durch die AMS-Variante auf
                            Hoehe der Schriftzugmitte: unten Farbe 1, oben
                            Farbe 2, ohne Fuge dazwischen.
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import generate as G


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else G.NAME
    zeichen = name[0].upper()
    _, b_gl, b_br, b_ho = G.teil_buchstabe(zeichen)
    _, n_gl, stege, _, n_br, n_ho, (dx, dy) = G.teil_name(name, b_br, b_ho)
    xs = [p[0] for a, _ in n_gl for p in a] + [p[0] for a, _ in b_gl for p in a]
    ys = [p[1] for a, _ in n_gl for p in a] + [p[1] for a, _ in b_gl for p in a]
    x0, x1, y0, y1 = min(xs) - 15, max(xs) + 15, min(ys) - 15, max(ys) + 25
    s = 2.4
    W, H = (x1 - x0) * s, (y1 - y0) * s

    def pfad(aussen, loecher):
        d = ""
        for k in [aussen] + list(loecher):
            d += "M " + " L ".join("%.1f %.1f" % ((x - x0) * s, (y1 - y) * s)
                                   for x, y in k) + " Z "
        return d

    z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f">' % (W, H),
         '<rect width="100%" height="100%" fill="#f4efe8"/>',
         '<text x="%.0f" y="18" font-family="sans-serif" font-size="14" '
         'font-weight="600" text-anchor="middle" fill="#333">Tuerschild "%s" -- '
         'Buchstabe %.0f mm hoch, Schriftzug %.0f mm breit</text>'
         % (W / 2, name, b_ho, n_br)]
    # Buchstabe rosa, mit leichtem Schatten (er steht 6 mm vor der Tuer)
    for a, ls in b_gl:
        z.append('<path d="%s" fill="#b9a09a" fill-rule="evenodd" transform="translate(3,3)"/>' % pfad(a, ls))
    for a, ls in b_gl:
        z.append('<path d="%s" fill="#e8a9b5" fill-rule="evenodd" stroke="#d48fa0" stroke-width="0.6"/>' % pfad(a, ls))
    # Schriftzug creme, Schatten fuer die 4 mm Aufbau
    for a, ls in n_gl:
        z.append('<path d="%s" fill="#b7aa96" fill-rule="evenodd" transform="translate(2.5,2.5)"/>' % pfad(a, ls))
    for st in stege:
        z.append('<path d="%s" fill="#b7aa96" transform="translate(2.5,2.5)"/>' % pfad(st, []))
    for st in stege:
        z.append('<path d="%s" fill="#f1e6d2"/>' % pfad(st, []))
    for a, ls in n_gl:
        z.append('<path d="%s" fill="#f1e6d2" fill-rule="evenodd" stroke="#cdbfa6" stroke-width="0.6"/>' % pfad(a, ls))
    z.append('<text x="%.0f" y="%.0f" font-family="sans-serif" font-size="11" '
             'text-anchor="middle" fill="#666">Stege zwischen den Inseln: %d '
             '(gleiche Farbe wie der Schriftzug)</text>' % (W / 2, H - 6, len(stege)))
    z.append("</svg>")
    ziel = os.path.join(HIER, "stl", "ansicht_vorne.svg")
    with open(ziel, "w") as f:
        f.write("\n".join(z))
    print("geschrieben:", ziel)
    ams_schnitt(name, b_gl, n_gl, stege)


def _laeufe(x0, x1, drin, schritt=0.4):
    """Zusammenhaengende x-Bereiche, in denen drin(x) wahr ist."""
    aus, start, x = [], None, x0
    while x <= x1:
        if drin(x):
            if start is None:
                start = x
        elif start is not None:
            aus.append((start, x))
            start = None
        x += schritt
    if start is not None:
        aus.append((start, x1))
    return aus


def ams_schnitt(name, b_gl, n_gl, stege):
    """Schnitt durch den AMS-Stapel auf Hoehe der Schriftzugmitte."""
    b_ho = max(p[1] for a, _ in b_gl for p in a)
    y = G.NAME_MITTE * b_ho
    xs = [p[0] for a, _ in list(b_gl) + list(n_gl) for p in a]
    x0, x1 = min(xs) - 10, max(xs) + 10
    unten = _laeufe(x0, x1, lambda x: G.im_material((x, y), list(b_gl) + list(n_gl), stege))
    oben = _laeufe(x0, x1, lambda x: G.im_material((x, y), n_gl, stege))
    s, sz = 2.4, 12.0          # z stark ueberhoeht, sonst sieht man nichts
    W = (x1 - x0) * s
    kopf, fuss = 46.0, 34.0
    H = kopf + (G.BUCHSTABE_DICKE + G.NAME_DICKE) * sz + fuss
    boden = H - fuss

    def bal(l, r, z0, z1, farbe, rand):
        return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                'stroke="%s" stroke-width="0.5"/>'
                % ((l - x0) * s, boden - z1 * sz, (r - l) * s, (z1 - z0) * sz,
                   farbe, rand))

    z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f">' % (W, H),
         '<rect width="100%" height="100%" fill="#f4efe8"/>',
         '<text x="%.0f" y="18" font-family="sans-serif" font-size="14" '
         'font-weight="600" text-anchor="middle" fill="#333">AMS-Variante "%s" '
         '-- Schnitt auf Hoehe der Schriftzugmitte</text>' % (W / 2, name),
         '<text x="%.0f" y="34" font-family="sans-serif" font-size="11" '
         'text-anchor="middle" fill="#666">ein Druck, ein Farbwechsel bei '
         '%.0f mm (z stark ueberhoeht)</text>' % (W / 2, G.BUCHSTABE_DICKE)]
    for l, r in unten:
        z.append(bal(l, r, 0.0, G.BUCHSTABE_DICKE, "#e8a9b5", "#d48fa0"))
    for l, r in oben:
        z.append(bal(l, r, G.BUCHSTABE_DICKE, G.BUCHSTABE_DICKE + G.NAME_DICKE,
                     "#f1e6d2", "#cdbfa6"))
    z.append('<line x1="0" y1="%.1f" x2="%.0f" y2="%.1f" stroke="#999" '
             'stroke-width="1" stroke-dasharray="4 3"/>' % (boden, W, boden))
    z.append('<text x="6" y="%.0f" font-family="sans-serif" font-size="10" '
             'fill="#888">Druckbett</text>' % (boden + 13))
    z.append('<text x="%.0f" y="%.0f" font-family="sans-serif" font-size="11" '
             'text-anchor="middle" fill="#666">Farbe 1 rosa 0..%.0f mm '
             '(Buchstabe + Unterlage) &#183; Farbe 2 creme %.0f..%.0f mm '
             '(Schriftzug)</text>'
             % (W / 2, H - 8, G.BUCHSTABE_DICKE, G.BUCHSTABE_DICKE,
                G.BUCHSTABE_DICKE + G.NAME_DICKE))
    z.append("</svg>")
    ziel = os.path.join(HIER, "stl", "ansicht_ams_schnitt.svg")
    with open(ziel, "w") as f:
        f.write("\n".join(z))
    print("geschrieben:", ziel)


if __name__ == "__main__":
    main()
