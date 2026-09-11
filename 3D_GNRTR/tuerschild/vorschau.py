#!/usr/bin/env python3
"""Vorderansicht des Tuerschilds als SVG -- so, wie es an der Tuer haengt."""
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


if __name__ == "__main__":
    main()
