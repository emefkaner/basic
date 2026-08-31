#!/usr/bin/env python3
"""Echte Controller-Silhouette aus einem Foto auf der Passlehre.

Die aus dem Tray-Foto abgenommene Kontur war grundlegend falsch -- der
Controller passte nicht einmal ansatzweise in die gedruckte Lehre. Statt
weiter zu schaetzen wird die Silhouette hier GEMESSEN:

  1. Der Controller liegt flach auf der roten Passlehre (144 x 204 mm),
     in der Lage, in der er spaeter in der Mulde liegt.
  2. Ein Foto senkrecht von oben, alle vier Ecken der Platte im Bild.
  3. Dieses Skript findet die Platte, rechnet ueber ihre vier Ecken die
     Perspektive heraus (Homographie) und vermisst darin den Controller.

Warum die Lehre als Bezug taugt: sie ist 8 mm dick, der Controller liegt
also auf ihrer Oberseite -- genau in der Ebene, ueber die kalibriert
wird. Die Auflageflaeche des Controllers und die Kalibrierebene sind
damit dieselbe, und genau diese Kontur braucht die Mulde.

Aufruf:  python3 kontur_aus_foto.py foto.jpg [--zeige]
Ergebnis: KONTUR_ROH-Block zum Einsetzen in generate.py + Kontrollbild.
"""

import argparse
import math
import os
import warnings

warnings.filterwarnings("ignore")

LEHRE_X, LEHRE_Y = 144.0, 204.0        # Massze der roten Passlehre


def bild_laden(pfad):
    from PIL import Image
    import numpy as np
    im = Image.open(pfad).convert("RGB")
    # auf handliche Groesse bringen, sonst dauert alles ewig
    if max(im.size) > 1600:
        f = 1600.0 / max(im.size)
        im = im.resize((int(im.size[0] * f), int(im.size[1] * f)))
    return np.asarray(im, dtype=float)


def platte_finden(rgb):
    """Die rote Passlehre im Bild als Maske.

    Rot heisst hier: R deutlich groesser als G und B. Das trennt die
    Platte sowohl vom Controller (grau) als auch von Holz und Tisch.
    """
    import numpy as np
    from skimage import measure, morphology
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    maske = (r > 90) & (r > g * 1.5) & (r > b * 1.5)
    maske = morphology.remove_small_holes(maske, area_threshold=20000)
    maske = morphology.remove_small_objects(maske, min_size=20000)
    if maske.sum() < 5000:
        raise SystemExit("FEHLER: keine rote Platte im Bild gefunden")
    # groesste zusammenhaengende Flaeche
    lab = measure.label(maske)
    groesste = max(measure.regionprops(lab), key=lambda p: p.area)
    return (lab == groesste.label)


def ecken_finden(maske):
    """Die vier Ecken der Platte.

    Die Platte kann teilweise vom Controller verdeckt sein; deshalb nicht
    die Kontur abfahren, sondern die vier Extremwerte von (x+y), (x-y)
    nehmen -- die liegen auch dann auf den echten Ecken, wenn eine Kante
    unterbrochen ist.
    """
    import numpy as np
    ys, xs = np.nonzero(maske)
    s, d = xs + ys, xs - ys
    ecken = [(xs[np.argmin(s)], ys[np.argmin(s)]),     # links oben
             (xs[np.argmax(d)], ys[np.argmax(d)]),     # rechts oben
             (xs[np.argmax(s)], ys[np.argmax(s)]),     # rechts unten
             (xs[np.argmin(d)], ys[np.argmin(d)])]     # links unten
    return [(float(x), float(y)) for x, y in ecken]


def homographie(quelle, ziel):
    """Projektive Abbildung Bild -> Millimeter (DLT, 4 Punktepaare)."""
    import numpy as np
    A = []
    for (x, y), (u, v) in zip(quelle, ziel):
        A.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        A.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
    _, _, V = np.linalg.svd(np.array(A, dtype=float))
    H = V[-1].reshape(3, 3)
    return H / H[2, 2]


def anwenden(H, p):
    import numpy as np
    q = H @ np.array([p[0], p[1], 1.0])
    return (float(q[0] / q[2]), float(q[1] / q[2]))


def controller_maske(rgb, platte):
    """Alles, was auf der Platte liegt und nicht rot ist."""
    import numpy as np
    from skimage import morphology, measure
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    rot = (r > 90) & (r > g * 1.5) & (r > b * 1.5)
    # Huelle der Platte, damit auch die Muldenoeffnung dazugehoert
    huelle = morphology.convex_hull_image(platte)
    maske = huelle & (~rot)
    maske = morphology.remove_small_objects(maske, min_size=3000)
    maske = morphology.remove_small_holes(maske, area_threshold=3000)
    if maske.sum() < 2000:
        raise SystemExit("FEHLER: kein Controller auf der Platte erkannt")
    lab = measure.label(maske)
    groesste = max(measure.regionprops(lab), key=lambda p: p.area)
    return (lab == groesste.label)


def kontur_messen(pfad, zeige=False):
    import numpy as np
    from skimage import measure
    rgb = bild_laden(pfad)
    platte = platte_finden(rgb)
    ecken = ecken_finden(platte)
    # Zielrechteck: lange Seite der Platte = 204 mm
    d1 = math.dist(ecken[0], ecken[1])
    d2 = math.dist(ecken[1], ecken[2])
    if d1 >= d2:
        ziel = [(0, 0), (LEHRE_Y, 0), (LEHRE_Y, LEHRE_X), (0, LEHRE_X)]
    else:
        ziel = [(0, 0), (LEHRE_X, 0), (LEHRE_X, LEHRE_Y), (0, LEHRE_Y)]
    H = homographie(ecken, ziel)
    print("Platte erkannt, Ecken im Bild: %s" %
          ", ".join("(%.0f,%.0f)" % e for e in ecken))
    print("Kalibriert auf %.0f x %.0f mm" % (ziel[2][0], ziel[2][1]))

    maske = controller_maske(rgb, platte)
    konturen = measure.find_contours(maske.astype(float), 0.5)
    if not konturen:
        raise SystemExit("FEHLER: keine Controllerkontur gefunden")
    k = max(konturen, key=len)
    k = measure.approximate_polygon(k, tolerance=1.5)
    mm = [anwenden(H, (c, r)) for (r, c) in k]
    if math.dist(mm[0], mm[-1]) < 0.5:
        mm = mm[:-1]
    xs = [p[0] for p in mm]
    ys = [p[1] for p in mm]
    print("Silhouette: %d Punkte, %.1f x %.1f mm"
          % (len(mm), max(xs) - min(xs), max(ys) - min(ys)))
    ueber = [p for p in mm
             if not (-2 <= p[0] <= ziel[2][0] + 2 and -2 <= p[1] <= ziel[2][1] + 2)]
    if ueber:
        print("WARNUNG: %d Punkte liegen ausserhalb der Platte -- der "
              "Controller ragt ueber die Lehre hinaus, die Kontur ist dort "
              "abgeschnitten." % len(ueber))
    return mm, ziel


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("foto")
    ap.add_argument("--zeige", action="store_true",
                    help="Kontrollbild als SVG danebenlegen")
    args = ap.parse_args()
    mm, ziel = kontur_messen(args.foto)

    print("\n# --- gemessene Kontur, in generate.py einsetzen ---")
    print("CTRL_KONTUR_GEMESSEN = [")
    for x, y in mm:
        print("    (%.1f, %.1f)," % (x, y))
    print("]")

    if args.zeige:
        pfad = os.path.splitext(args.foto)[0] + "_kontur.svg"
        xs = [p[0] for p in mm]
        ys = [p[1] for p in mm]
        s = 3.0
        z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" '
             'height="%.0f">' % (ziel[2][0] * s + 40, ziel[2][1] * s + 40),
             '<rect width="100%%" height="100%%" fill="#fbfbfa"/>',
             '<rect x="20" y="20" width="%.1f" height="%.1f" fill="#e8352a"/>'
             % (ziel[2][0] * s, ziel[2][1] * s),
             '<polygon points="%s" fill="#4a4f57"/>'
             % " ".join("%.1f,%.1f" % (20 + x * s, 20 + y * s) for x, y in mm),
             '</svg>']
        with open(pfad, "w") as f:
            f.write("\n".join(z))
        print("\nKontrollbild: %s" % pfad)


if __name__ == "__main__":
    main()
