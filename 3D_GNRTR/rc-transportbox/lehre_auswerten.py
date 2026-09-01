#!/usr/bin/env python3
"""Ein Foto der gedruckten Passlehre in Millimeter uebersetzen.

Die Lehre ist nicht nur ein Test, sie ist ein Messmittel: ihre Masze
stammen aus dem Generator, sie ist also die genaueste Bezugsflaeche, die
zur Verfuegung steht. Ein Foto senkrecht von oben, auf dem alle vier
Plattenecken zu sehen sind, reicht -- ueber die Ecken wird die
Perspektive herausgerechnet (Homographie, dasselbe Verfahren wie in
kontur_aus_foto.py), danach ist jeder Bildpunkt ein Millimeterwert in
Muldenkoordinaten.

Gemessen wird:
  * das LOCH -- alles, was auf der Platte nicht Plattenfarbe ist. Deckt
    es sich mit g["mulde"], stimmen Druck und Kalibrierung.
  * das SPIEL -- durch das Loch sieht man den Untergrund. Wo Untergrund
    sichtbar ist, ist Luft. (Lehre also auf etwas legen, das sich vom
    Bauteil unterscheidet -- Holz taugt gut, es ist warmbraun, der
    Controller neutralgrau.)
  * ein FARBIGES TEIL des Gegenstands, per Vorgabe --farbe. Der Abzug
    des Controllers ist orange und damit eindeutig zu finden; genau so
    wurden seine 35,4 x 31,2 mm und seine Lage bestimmt, nachdem er im
    ersten Lehrendruck zur Haelfte auf dem Material auflag.

Aufruf:  python3 lehre_auswerten.py foto.jpg [--farbe orange] [--bild]

Achtung: kalibriert wird auf die AKTUELLEN Plattenmasze aus dem
Generator. Ein Foto einer aelteren Lehre wird deshalb um deren
Groeszenunterschied verzerrt gemessen (nach der Kuerzung der Muldenluft
rund 2,4 %). Fuer eine Neumessung also die aktuelle Lehre fotografieren.
"""

import argparse
import math
import os
import sys
import warnings

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate as G                                    # noqa: E402
import kontur_aus_foto as K                             # noqa: E402


def platte_finden(rgb):
    """Die rote Lehre als groesste zusammenhaengende rote Flaeche."""
    from skimage import measure, morphology
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    maske = (r > 90) & (r > g * 1.45) & (r > b * 1.45)
    maske = morphology.remove_small_holes(maske, area_threshold=200000)
    maske = morphology.remove_small_objects(maske, min_size=20000)
    if maske.sum() < 5000:
        raise SystemExit("FEHLER: keine rote Lehre im Bild gefunden")
    lab = measure.label(maske)
    from skimage.measure import regionprops
    return lab == max(regionprops(lab), key=lambda p: p.area).label


def blattmaske(rgb, ecken, einzug=0.02):
    """Exakt das Viereck der vier Ecken -- NICHT die konvexe Huelle.

    Bei schraeg liegender Platte greift die Huelle darueber hinaus und
    der Untergrund zaehlt als Teil (der Fehler, der bei der A4-Messung
    293 x 265 statt 215 x 151 ergeben hat).
    """
    from skimage.draw import polygon2mask
    mx = sum(e[0] for e in ecken) / 4.0
    my = sum(e[1] for e in ecken) / 4.0
    innen = [(e[0] + (mx - e[0]) * einzug, e[1] + (my - e[1]) * einzug)
             for e in ecken]
    return polygon2mask(rgb.shape[:2], [(y, x) for (x, y) in innen])


FARBEN = {
    # Name: Test auf (r, g, b) als Funktion
    "orange": lambda r, g, b: (r > 130) & (g > r * 0.35) & (g < r * 0.80)
                              & (b < r * 0.55),
    "gruen":  lambda r, g, b: (g > 90) & (g > r * 1.25) & (g > b * 1.25),
    "blau":   lambda r, g, b: (b > 90) & (b > r * 1.25) & (b > g * 1.25),
}


def auswerten(pfad, farbe="orange", bild=False):
    import numpy as np
    from skimage import measure, morphology

    g = G.abgeleitet()
    LX, LY = g["fachC_l"], g["fachC_t"]
    print("Lehre laut Generator: %.1f x %.1f mm" % (LX, LY))

    rgb = K.bild_laden(pfad)
    r, gr, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    hell = rgb.mean(axis=2)
    rot = platte_finden(rgb)
    ecken = K.ecken_finden(rot)
    quer = math.dist(ecken[0], ecken[1]) >= math.dist(ecken[1], ecken[2])
    ziel = [(0, 0), (LY, 0), (LY, LX), (0, LX)] if quer else \
           [(0, 0), (LX, 0), (LX, LY), (0, LY)]
    H = K.homographie(ecken, ziel)
    blatt = blattmaske(rgb, ecken)

    loch = blatt & (~rot)
    loch = morphology.remove_small_objects(loch, min_size=3000)
    loch = morphology.remove_small_holes(loch, area_threshold=30000)
    lab = measure.label(loch)
    loch = lab == max(measure.regionprops(lab), key=lambda p: p.area).label

    def punkte(maske, schritt=5):
        ys, xs = np.nonzero(maske)
        return [K.anwenden(H, (float(x), float(y)))
                for x, y in zip(xs[::schritt], ys[::schritt])]

    def kontur(maske, tol=1.2):
        ks = measure.find_contours(maske.astype(float), 0.5)
        k = measure.approximate_polygon(max(ks, key=len), tolerance=tol)
        p = [K.anwenden(H, (c, rr)) for (rr, c) in k]
        return p[:-1] if math.dist(p[0], p[-1]) < 0.5 else p

    lk = kontur(loch)
    # In Muldenkoordinaten drehen: die Lage im Bild ist unbekannt, also
    # alle vier Drehungen (mal Spiegelung) gegen die Sollmulde pruefen.
    px = ziel[2][0]
    py = ziel[2][1]

    def dreh(pts, k, sp):
        out = []
        for (x, y) in pts:
            u, v = (px - x, y) if sp else (x, y)
            out.append([(u, v), (py - v, u), (px - u, py - v), (v, px - u)][k])
        return out

    mulde = g["mulde"]
    best = None
    for k in range(4):
        for sp in (False, True):
            t = dreh(lk, k, sp)
            d = sum(min(math.dist(p, q) for q in mulde) for p in t) / len(t)
            if best is None or d < best[0]:
                best = (d, k, sp)
    d, k, sp = best
    print("Lage erkannt (Drehung %d, gespiegelt=%s), mittlerer Randabstand "
          "zur Soll-Mulde %.2f mm" % (k, sp, d))
    if d > 6.0:
        print("WARNUNG: das gemessene Loch passt schlecht zur Konstruktion "
              "-- ist das die aktuelle Lehre?")

    t = dreh(lk, k, sp)
    xs = [p[0] for p in t]
    ys = [p[1] for p in t]
    mx = [p[0] for p in mulde]
    my = [p[1] for p in mulde]
    print("Loch gemessen:     %.1f x %.1f mm" % (max(xs) - min(xs),
                                                 max(ys) - min(ys)))
    print("Mulde konstruiert: %.1f x %.1f mm" % (max(mx) - min(mx),
                                                 max(my) - min(my)))

    # Spiel: Untergrund durch das Loch. Holz ist warm, das Teil neutral.
    holz = loch & (r > b * 1.12) & (r < b * 1.75) & (hell > 60)
    holz = morphology.remove_small_objects(holz, min_size=800)
    print("sichtbares Spiel: %.1f %% der Muldenflaeche"
          % (100.0 * holz.sum() / max(1, loch.sum())))

    treffer = FARBEN[farbe](r, gr, b) & blatt
    treffer = morphology.remove_small_objects(treffer, min_size=400)
    lab = measure.label(treffer)
    x0k = min(x for (x, _) in g["kontur"])
    y0k = min(y for (_, y) in g["kontur"])
    for i, p in enumerate(sorted(measure.regionprops(lab),
                                 key=lambda q: -q.area)[:4]):
        pm = dreh(kontur(lab == p.label, 0.8), k, sp)
        ox = [q[0] for q in pm]
        oy = [q[1] for q in pm]
        drin = sum(1 for q in pm if G.punkt_in_polygon(q, mulde))
        print("%s %d: %.1f x %.1f mm, konturrelativ x %.1f..%.1f y %.1f..%.1f"
              % (farbe, i, max(ox) - min(ox), max(oy) - min(oy),
                 min(ox) - x0k, max(ox) - x0k, min(oy) - y0k, max(oy) - y0k))
        print("   frei in der Mulde: %d von %d Umrisspunkten" % (drin, len(pm)))

    if bild:
        from PIL import Image
        ueber = rgb.copy()
        ueber[holz] = np.array([0, 255, 0])
        ueber[treffer] = np.array([255, 0, 255])
        ziel_pfad = os.path.splitext(pfad)[0] + "_lehre.png"
        Image.fromarray(ueber.astype("uint8")).save(ziel_pfad)
        print("Kontrollbild: %s (gruen = Spiel, magenta = %s)"
              % (ziel_pfad, farbe))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("foto")
    ap.add_argument("--farbe", choices=sorted(FARBEN), default="orange",
                    help="farbiges Teil, das gesucht werden soll")
    ap.add_argument("--bild", action="store_true", help="Kontrollbild schreiben")
    args = ap.parse_args()
    auswerten(args.foto, args.farbe, args.bild)


if __name__ == "__main__":
    main()
