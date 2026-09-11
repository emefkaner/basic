#!/usr/bin/env python3
"""Tuerschild: grosser Serifen-Buchstabe, darueber der Name in Schreibschrift.

Vorbild ist das klassische Kinderzimmer-Tuerschild aus zwei Lagen: ein
grosser Anfangsbuchstabe (hier rosa), quer darueber der ganze Name in
Schreibschrift (creme), der links und rechts ueber den Buchstaben
hinausragt. Zwei Teile, zwei Farben, flach gedruckt, dann verklebt.

    python3 generate.py                      # Elsie
    python3 generate.py --name Emilia        # anderer Name, gleicher Stil
    python3 generate.py --name Elsie --hoehe 200

Es entstehen zwei Varianten desselben Schilds:

A) Kleben -- zwei einfarbige Teile, nacheinander gedruckt:
  1. BUCHSTABE  -- der Anfangsbuchstabe, BUCHSTABE_DICKE dick.
  2. NAME       -- der Schriftzug, NAME_DICKE dick. Liegt im Druck flach
                   auf dem Bett; verklebt wird er auf der Vorderseite des
                   Buchstabens. Beide STLs teilen denselben Ursprung, der
                   Schriftzug steht in der Datei bereits an seinem Platz
                   -- im Slicer beide laden, dann sieht man die Lage; zum
                   Drucken trotzdem einzeln, sie haben verschiedene Farben.

B) AMS -- ein Druck, zwei Filamente, die Farben uebereinander gestapelt:
   Farbe 1 von z 0 bis BUCHSTABE_DICKE (Buchstabe PLUS Unterlage unter
   dem ganzen Schriftzug, damit dessen ueberstehende Enden nicht
   schweben), Farbe 2 von da bis NAME_DICKE hoeher (der Schriftzug).
   Sie beruehren sich in einer Ebene und verschmelzen beim Drucken --
   kein Kleber, kein Verrutschen, ein einziger Farbwechsel.

Schreibschrift besteht aus Inseln: der Punkt auf dem i, oft auch der
Anfangsbuchstabe, haengen nicht am Rest. Ein Schriftzug aus drei Teilen
laesst sich aber nicht gerade aufkleben. Deshalb wird jede Insel ueber
einen schmalen Steg an den naechsten Nachbarn angebunden -- gepruefte
Zusammenhaengigkeit, nicht Hoffnung.

Mesh-Technik wie in den Nachbarprojekten (Schalen-Union, keine
Booleans); die Grundbausteine kommen aus hochzeitsornament/generate.py.
"""

import argparse
import math
import os
import struct
import sys

HIER = os.path.dirname(os.path.abspath(__file__))

# Mesh-Grundbausteine aus dem Hochzeitsornament -- ueber den Dateipfad
# geladen, nicht per "import generate": das hiesse sonst dieses Modul
# selbst (gleicher Name) und dreht sich im Kreis.
import importlib.util                                               # noqa: E402
_spec = importlib.util.spec_from_file_location(
    "hochzeitsornament_generate",
    os.path.join(HIER, "..", "hochzeitsornament", "generate.py"))
_ho = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ho)
prisma_mit_loechern = _ho.prisma_mit_loechern
prisma = _ho.prisma
kanten_pruefen = _ho.kanten_pruefen
volumen = _ho.volumen
punkt_in_polygon = _ho.punkt_in_polygon
flaeche_signiert = _ho.flaeche_signiert
from fontTools.ttLib import TTFont                                  # noqa: E402
from fontTools.pens.recordingPen import DecomposingRecordingPen     # noqa: E402

# ---------------------------------------------------------------------------
# Parameter
# ---------------------------------------------------------------------------
NAME = "Elsie"
BUCHSTABE_HOEHE = 240.0    # Versalhoehe des grossen Buchstabens, mm
BUCHSTABE_DICKE = 6.0
# Die Vorlage ist ein schmaler, hoher Didone-Buchstabe (Verhaeltnis
# Breite/Hoehe rund 0,65). Liberation Serif Bold ist ein Times-Schnitt und
# fast quadratisch -- deshalb in x gestaucht. Der Stamm wird dabei
# duenner, die Balken bleiben: das rueckt ihn in Richtung Vorlage.
BUCHSTABE_SCHMAL = 0.72
NAME_SPUR = 1.0            # Laufweite; Great Vibes verbindet nur bei 100 %
NAME_DICKE = 4.0
NAME_BREITE_FAKTOR = 1.7   # Schriftzug so viel breiter als der Buchstabe (Vorlage)
NAME_MITTE = 0.52          # Schriftzugmitte auf dieser Hoehe des Buchstabens
STEG_BREITE = 2.5          # Verbindungssteg zwischen Inseln der Schreibschrift
STEG_UEBER = 1.5           # so weit laeuft der Steg in beide Inseln hinein

FONT_BUCHSTABE = os.path.join(HIER, "LiberationSerif-Bold.ttf")
FONT_NAME = os.path.join(HIER, "GreatVibes-Regular.ttf")
BEZIER_SCHRITTE = 10

# Bett Bambu H2S, vorsichtig 350 x 320, 20 mm Rand
BETT_X, BETT_Y, BETT_RAND = 350.0, 320.0, 20.0

# ---------------------------------------------------------------------------
# Schrift -> Konturen (mit Font-Parameter, sonst wie im Hochzeitsornament)
# ---------------------------------------------------------------------------
_fonts = {}


def font(pfad):
    if pfad not in _fonts:
        _fonts[pfad] = TTFont(pfad)
    return _fonts[pfad]


def _quad(p0, p1, p2, schritte=BEZIER_SCHRITTE):
    pts = []
    for k in range(1, schritte + 1):
        t = k / schritte
        u = 1.0 - t
        pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return pts


def glyph_konturen(pfad, zeichen):
    """Konturen eines Zeichens in Font-Einheiten, Beziers abgeflacht."""
    f = font(pfad)
    name = f.getBestCmap()[ord(zeichen)]
    # DecomposingRecordingPen, nicht RecordingPen: zusammengesetzte Glyphen
    # (das i in Great Vibes = Strich + Punkt als Komponenten) liefern sonst
    # gar keine Kontur -- der Buchstabe fehlte im Schriftzug, und "Elsie"
    # las sich als "Else". Erst beim Zaehlen der Glyphen aufgefallen.
    pen = DecomposingRecordingPen(f.getGlyphSet())
    f.getGlyphSet()[name].draw(pen)
    konturen, aktuelle, letzter = [], [], None
    for op, args in pen.value:
        if op == "moveTo":
            aktuelle = [args[0]]
            letzter = args[0]
        elif op == "lineTo":
            aktuelle.append(args[0])
            letzter = args[0]
        elif op == "qCurveTo":
            punkte = list(args)
            ziel = punkte[-1]
            offs = punkte[:-1]
            start = letzter
            if ziel is None:
                ziel = ((offs[0][0] + offs[-1][0]) / 2.0,
                        (offs[0][1] + offs[-1][1]) / 2.0)
            for k, off in enumerate(offs):
                if k < len(offs) - 1:
                    mitte = ((off[0] + offs[k + 1][0]) / 2.0,
                             (off[1] + offs[k + 1][1]) / 2.0)
                else:
                    mitte = ziel
                aktuelle.extend(_quad(start, off, mitte))
                start = mitte
            letzter = ziel
        elif op == "curveTo":
            p0 = letzter
            p1, p2, p3 = args
            for k in range(1, BEZIER_SCHRITTE + 1):
                t = k / BEZIER_SCHRITTE
                u = 1.0 - t
                aktuelle.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                                 u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
            letzter = p3
        elif op == "closePath":
            if len(aktuelle) >= 3:
                if (abs(aktuelle[0][0] - aktuelle[-1][0]) < 1e-9
                        and abs(aktuelle[0][1] - aktuelle[-1][1]) < 1e-9):
                    aktuelle.pop()
                konturen.append(aktuelle)
            aktuelle = []
    return konturen, f["hmtx"][name][0]


def polygon_saeubern(poly, min_abstand=0.05):
    """Punkte, die nach dem Skalieren aufeinanderliegen, entfernen --
    eine Kante der Laenge 0 laesst das Ear-Clipping haengen."""
    out = []
    for p in poly:
        if not out or math.dist(p, out[-1]) >= min_abstand:
            out.append(p)
    while len(out) > 2 and math.dist(out[0], out[-1]) < min_abstand:
        out.pop()
    return out


def glyphen_setzen(pfad, text, skala=None, hoehe_mm=None, breite_mm=None,
                   spur=1.0):
    """Text setzen -> je Glyphe (aussen, [loecher]) in mm.

    Anders als im Hochzeitsornament werden Loecher JE GLYPHE bestimmt.
    In Schreibschrift ueberlappen sich Nachbarbuchstaben, und eine Kontur
    des einen laege dann "in" dem anderen -- die globale Zaehlung hielte
    sie faelschlich fuer ein Loch. Innerhalb einer Glyphe stimmt die
    Zaehlung; die Ueberlappung zwischen Glyphen erledigt die Schalen-Union.
    Rueckgabe zusaetzlich: Breite, Hoehe, Skala.
    """
    f = font(pfad)
    x = 0.0
    glyphen = []
    for z in text:
        if z == " ":
            x += 0.30 * f["head"].unitsPerEm
            continue
        konturen, adv = glyph_konturen(pfad, z)
        glyphen.append([[(px + x, py) for (px, py) in k] for k in konturen])
        x += adv * spur
    xs = [p[0] for g_ in glyphen for k in g_ for p in k]
    ys = [p[1] for g_ in glyphen for k in g_ for p in k]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    if skala is None:
        skala = (breite_mm / (maxx - minx)) if breite_mm else hoehe_mm / (maxy - miny)
    ergebnis = []
    for g_ in glyphen:
        kont = [polygon_saeubern([((px - minx) * skala, (py - miny) * skala)
                                  for (px, py) in k]) for k in g_]
        kont = [k for k in kont if len(k) >= 3]
        gruppen = []
        for i, k in enumerate(kont):
            tiefe = sum(1 for j, o in enumerate(kont)
                        if j != i and punkt_in_polygon(k[0], o))
            gruppen.append((tiefe, k))
        for i, (t, a) in enumerate(gruppen):
            if t % 2:
                continue
            loecher = [k for j, (tt, k) in enumerate(gruppen)
                       if tt % 2 == 1 and punkt_in_polygon(k[0], a)]
            ergebnis.append((a, loecher))
    return ergebnis, (maxx - minx) * skala, (maxy - miny) * skala, skala


# ---------------------------------------------------------------------------
# Zusammenhang der Schreibschrift
# ---------------------------------------------------------------------------

def _schneiden(a, b, c, d):
    def kr(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (kr(a, b, c) * kr(a, b, d) < 0) and (kr(c, d, a) * kr(c, d, b) < 0)


def beruehren(A, B):
    """Ueberlappen zwei Konturen (Eckpunkt innen oder Kanten kreuzen)?"""
    ax = [p[0] for p in A]; ay = [p[1] for p in A]
    bx = [p[0] for p in B]; by = [p[1] for p in B]
    if max(ax) < min(bx) or max(bx) < min(ax) or max(ay) < min(by) or max(by) < min(ay):
        return False
    if any(punkt_in_polygon(p, B) for p in A[::3]) or any(punkt_in_polygon(p, A) for p in B[::3]):
        return True
    n, m = len(A), len(B)
    for i in range(0, n, 2):
        for j in range(0, m, 2):
            if _schneiden(A[i], A[(i + 1) % n], B[j], B[(j + 1) % m]):
                return True
    return False


def komponenten(konturen):
    """Zusammenhangskomponenten der Aussenkonturen (Union-Find)."""
    n = len(konturen)
    eltern = list(range(n))

    def wurzel(i):
        while eltern[i] != i:
            eltern[i] = eltern[eltern[i]]
            i = eltern[i]
        return i

    for i in range(n):
        for j in range(i + 1, n):
            if beruehren(konturen[i], konturen[j]):
                eltern[wurzel(i)] = wurzel(j)
    gruppen = {}
    for i in range(n):
        gruppen.setdefault(wurzel(i), []).append(i)
    return list(gruppen.values())


def steg_zwischen(A, B, breite, ueber):
    """Rechteckiger Steg zwischen den naechsten Punkten zweier Konturen,
    beidseitig um `ueber` in die Konturen hinein verlaengert."""
    best = None
    for p in A:
        for q in B:
            d = math.dist(p, q)
            if best is None or d < best[0]:
                best = (d, p, q)
    d, p, q = best
    if d < 1e-6:
        return None, 0.0
    ux, uy = (q[0] - p[0]) / d, (q[1] - p[1]) / d
    nx, ny = -uy * breite / 2.0, ux * breite / 2.0
    p2 = (p[0] - ux * ueber, p[1] - uy * ueber)
    q2 = (q[0] + ux * ueber, q[1] + uy * ueber)
    return [(p2[0] + nx, p2[1] + ny), (q2[0] + nx, q2[1] + ny),
            (q2[0] - nx, q2[1] - ny), (p2[0] - nx, p2[1] - ny)], d


def inseln_anbinden(glyphen):
    """Alle Inseln des Schriftzugs ueber Stege verbinden.

    Solange mehr als eine Komponente da ist: die kleinste Komponente an
    ihren naechsten Nachbarn in einer anderen Komponente anbinden.
    Rueckgabe: Liste der Stege (Polygone) und die ueberbrueckten Abstaende.
    """
    aussen = [a for (a, _) in glyphen]
    stege, abstaende = [], []
    for _ in range(len(aussen)):
        komp = komponenten(aussen + stege)
        if len(komp) <= 1:
            break
        komp.sort(key=lambda k: sum(abs(flaeche_signiert(
            (aussen + stege)[i])) for i in k))
        klein = komp[0]
        andere = [i for k in komp[1:] for i in k]
        alle = aussen + stege
        best = None
        for i in klein:
            for j in andere:
                s, d = steg_zwischen(alle[i], alle[j], STEG_BREITE, STEG_UEBER)
                if s is not None and (best is None or d < best[0]):
                    best = (d, s)
        if best is None:
            break
        stege.append(best[1])
        abstaende.append(best[0])
    return stege, abstaende


# ---------------------------------------------------------------------------
# Teile
# ---------------------------------------------------------------------------

def teil_buchstabe(zeichen):
    glyphen, br, ho, _ = glyphen_setzen(FONT_BUCHSTABE, zeichen,
                                        hoehe_mm=BUCHSTABE_HOEHE)
    glyphen = [([(x * BUCHSTABE_SCHMAL, y) for (x, y) in a],
                [[(x * BUCHSTABE_SCHMAL, y) for (x, y) in l] for l in ls])
               for (a, ls) in glyphen]
    br *= BUCHSTABE_SCHMAL
    schalen = []
    for aussen, loecher in glyphen:
        schalen.append(prisma_mit_loechern(aussen, loecher, 0.0, BUCHSTABE_DICKE))
    return schalen, glyphen, br, ho


def teil_ams(b_glyphen, n_glyphen, stege):
    """Dieselben zwei Farben, aber als EIN Druck fuer die AMS.

    Statt zu kleben werden die Farben uebereinander gestapelt:

        z 0 .. BUCHSTABE_DICKE                Farbe 1 (rosa)
        z BUCHSTABE_DICKE .. + NAME_DICKE     Farbe 2 (creme)

    Farbe 1 ist nicht nur der Buchstabe, sondern der Buchstabe UND der
    Umriss des Schriftzugs: der Schriftzug ragt links und rechts weit
    ueber den Buchstaben hinaus und haette dort sonst nichts unter sich.
    Mit der Unterlage steht jeder Punkt des Schriftzugs auf rosa Material
    -- nichts schwebt, keine Stuetzen, und die Lagen verschmelzen im Druck
    zu einem Stueck.

    Beide Koerper teilen den Ursprung und beruehren sich genau in der
    Ebene z = BUCHSTABE_DICKE; sie ueberlappen sich nirgends. Im Slicer
    als mehrteiliges Objekt laden, je Teil ein Filament.
    """
    z_naht = BUCHSTABE_DICKE
    rosa = []
    for aussen, loecher in b_glyphen:
        rosa.append(prisma_mit_loechern(aussen, loecher, 0.0, z_naht))
    for aussen, loecher in n_glyphen:
        rosa.append(prisma_mit_loechern(aussen, loecher, 0.0, z_naht))
    for s in stege:
        rosa.append(prisma(s, 0.0, z_naht))
    creme = []
    for aussen, loecher in n_glyphen:
        creme.append(prisma_mit_loechern(aussen, loecher, z_naht,
                                         z_naht + NAME_DICKE))
    for s in stege:
        creme.append(prisma(s, z_naht, z_naht + NAME_DICKE))
    return rosa, creme


def teil_name(name, buchstabe_breite, buchstabe_hoehe):
    breite = min(NAME_BREITE_FAKTOR * buchstabe_breite,
                 BETT_X - 2 * BETT_RAND)
    glyphen, br, ho, _ = glyphen_setzen(FONT_NAME, name, breite_mm=breite,
                                        spur=NAME_SPUR)
    # an seinen Platz: mittig ueber dem Buchstaben, Mitte auf NAME_MITTE
    dx = (buchstabe_breite - br) / 2.0
    dy = NAME_MITTE * buchstabe_hoehe - ho / 2.0
    glyphen = [([(x + dx, y + dy) for (x, y) in a],
                [[(x + dx, y + dy) for (x, y) in l] for l in ls])
               for (a, ls) in glyphen]
    stege, abstaende = inseln_anbinden(glyphen)
    schalen = []
    for aussen, loecher in glyphen:
        schalen.append(prisma_mit_loechern(aussen, loecher, 0.0, NAME_DICKE))
    for s in stege:
        schalen.append(prisma(s, 0.0, NAME_DICKE))
    return schalen, glyphen, stege, abstaende, br, ho, (dx, dy)


# ---------------------------------------------------------------------------
# Pruefungen, Ausgabe
# ---------------------------------------------------------------------------

def stl_schreiben(pfad, dreiecke, name):
    with open(pfad, "wb") as f:
        f.write(("Tuerschild - " + name).encode("ascii", "replace")
                .ljust(80, b" ")[:80])
        f.write(struct.pack("<I", len(dreiecke)))
        for (a, b, c) in dreiecke:
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            l = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(struct.pack("<12fH", nx / l, ny / l, nz / l,
                                a[0], a[1], a[2], b[0], b[1], b[2],
                                c[0], c[1], c[2], 0))


def bauen(ziel, name, schalen):
    tris = [t for s in schalen for t in s]
    offen = sum(kanten_pruefen(s, gerade_erlaubt=True) for s in schalen)
    stl_schreiben(os.path.join(ziel, name), tris, name)
    xs = [v[0] for t in tris for v in t]
    ys = [v[1] for t in tris for v in t]
    print("%-38s %3d Schalen %6d Dreiecke  %5.1f x %5.1f mm  ~%5.0f cm3  "
          "offene Kanten: %d" % (name, len(schalen), len(tris),
                                 max(xs) - min(xs), max(ys) - min(ys),
                                 sum(volumen(s) for s in schalen) / 1000.0,
                                 offen))
    return offen


def bett_pruefen(breite, hoehe, name):
    b, h = BETT_X - 2 * BETT_RAND, BETT_Y - 2 * BETT_RAND
    if (breite <= b and hoehe <= h) or (hoehe <= b and breite <= h):
        return None
    return ("%s (%.0f x %.0f) passt nicht mit %.0f mm Rand aufs Bett %.0f x %.0f"
            % (name, breite, hoehe, BETT_RAND, BETT_X, BETT_Y))


def im_material(p, glyphen=(), polygone=()):
    """Liegt der Punkt in einer der Glyphen (ausserhalb ihrer Loecher)
    oder in einem der einfachen Polygone (Stege)?"""
    for a, ls in glyphen:
        if punkt_in_polygon(p, a) and not any(punkt_in_polygon(p, l) for l in ls):
            return True
    return any(punkt_in_polygon(p, s) for s in polygone)


def z_bereich(schalen):
    zs = [v[2] for s in schalen for t in s for v in t]
    return min(zs), max(zs)


def ams_pruefen(b_gl, n_gl, stege, rosa, creme):
    """Der AMS-Stapel: Farben sauber getrennt, nichts schwebt, ein Stueck."""
    fehler = []
    z_naht = BUCHSTABE_DICKE
    r0, r1 = z_bereich(rosa)
    c0, c1 = z_bereich(creme)
    if abs(r0) > 1e-6 or abs(r1 - z_naht) > 1e-6:
        fehler.append("Farbe 1 liegt bei z %.2f..%.2f statt 0..%.2f"
                      % (r0, r1, z_naht))
    if abs(c0 - z_naht) > 1e-6 or abs(c1 - (z_naht + NAME_DICKE)) > 1e-6:
        fehler.append("Farbe 2 liegt bei z %.2f..%.2f statt %.2f..%.2f"
                      % (c0, c1, z_naht, z_naht + NAME_DICKE))
    if c0 + 1e-6 < r1:
        fehler.append("Farben ueberlappen sich in z")
    # Steht jeder Punkt der oberen Farbe auf Material der unteren?
    xs = [p[0] for a, _ in n_gl for p in a] + [p[0] for s in stege for p in s]
    ys = [p[1] for a, _ in n_gl for p in a] + [p[1] for s in stege for p in s]
    n, gesamt, getragen = 90, 0, 0
    for i in range(n):
        for j in range(n):
            p = (min(xs) + (max(xs) - min(xs)) * (i + 0.5) / n,
                 min(ys) + (max(ys) - min(ys)) * (j + 0.5) / n)
            if not im_material(p, n_gl, stege):
                continue
            gesamt += 1
            if im_material(p, list(b_gl) + list(n_gl), stege):
                getragen += 1
    if getragen != gesamt:
        fehler.append("%d von %d Rasterpunkten der oberen Farbe schweben"
                      % (gesamt - getragen, gesamt))
    komp = komponenten([a for a, _ in b_gl] + [a for a, _ in n_gl] + list(stege))
    if len(komp) != 1:
        fehler.append("untere Farbe zerfaellt in %d Teile" % len(komp))
    return fehler, gesamt


def klebeflaeche(name_glyphen, buchstabe_glyphen):
    """Wieviel des Schriftzugs liegt auf dem Buchstaben (Rasterprobe)?"""
    xs = [p[0] for a, _ in name_glyphen for p in a]
    ys = [p[1] for a, _ in name_glyphen for p in a]
    drauf = gesamt = 0
    n = 70
    for i in range(n):
        for j in range(n):
            p = (min(xs) + (max(xs) - min(xs)) * (i + 0.5) / n,
                 min(ys) + (max(ys) - min(ys)) * (j + 0.5) / n)
            im_namen = any(punkt_in_polygon(p, a) and not any(
                punkt_in_polygon(p, l) for l in ls) for a, ls in name_glyphen)
            if not im_namen:
                continue
            gesamt += 1
            if any(punkt_in_polygon(p, a) and not any(
                    punkt_in_polygon(p, l) for l in ls) for a, ls in buchstabe_glyphen):
                drauf += 1
    return drauf / float(max(1, gesamt))


def main():
    global BUCHSTABE_HOEHE
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default=NAME)
    ap.add_argument("--buchstabe", default=None,
                    help="grosser Buchstabe (Standard: Anfangsbuchstabe des Namens)")
    ap.add_argument("--hoehe", type=float, default=BUCHSTABE_HOEHE,
                    help="Hoehe des grossen Buchstabens in mm")
    args = ap.parse_args()
    BUCHSTABE_HOEHE = args.hoehe
    name = args.name
    zeichen = args.buchstabe or name[0].upper()

    ziel = os.path.join(HIER, "stl")
    os.makedirs(ziel, exist_ok=True)
    for alt in os.listdir(ziel):
        if alt.startswith("tuerschild_") and alt.endswith(".stl"):
            os.remove(os.path.join(ziel, alt))

    b_schalen, b_gl, b_br, b_ho = teil_buchstabe(zeichen)
    n_schalen, n_gl, stege, abst, n_br, n_ho, (dx, dy) = teil_name(name, b_br, b_ho)

    print("Tuerschild '%s': Buchstabe %s %.0f mm hoch (%.0f breit, %.0f dick), "
          "Schriftzug %.0f x %.0f mm (%.0f dick)"
          % (name, zeichen, b_ho, b_br, BUCHSTABE_DICKE, n_br, n_ho, NAME_DICKE))
    print("Schriftzug liegt %.0f mm links und rechts ueber den Buchstaben hinaus, "
          "Mitte auf %.0f %% der Buchstabenhoehe"
          % (-dx, 100 * NAME_MITTE))
    if stege:
        print("Inseln angebunden: %d Steg(e) a %.1f mm breit, ueberbrueckt %s mm"
              % (len(stege), STEG_BREITE,
                 ", ".join("%.1f" % a for a in abst)))
    else:
        print("Schriftzug haengt von selbst zusammen, keine Stege noetig")
    komp = komponenten([a for a, _ in n_gl] + stege)
    if len(komp) != 1:
        raise SystemExit("FEHLER: Schriftzug zerfaellt in %d Teile" % len(komp))
    print("Zusammenhang geprueft: ein Stueck")
    anteil = klebeflaeche(n_gl, b_gl)
    print("Klebeflaeche: %.0f %% des Schriftzugs liegen auf dem Buchstaben"
          % (100 * anteil))
    # Ein E besteht ueberwiegend aus Leerraum; der Schriftzug liegt also
    # vor allem ueber den Innenraeumen und trifft Stamm und Balken nur
    # stellenweise. 15 % reichen bei 4 mm steifem Schriftzug voellig.
    if anteil < 0.15:
        raise SystemExit("FEHLER: zu wenig Klebeflaeche")
    for f_ in (bett_pruefen(b_br, b_ho, "Buchstabe"),
               bett_pruefen(n_br, n_ho, "Schriftzug")):
        if f_:
            raise SystemExit("FEHLER Bauraum: " + f_)
    print("Bauraum: beide Teile passen (auch zusammen: Buchstabe + Schriftzug "
          "hochkant nebeneinander %.0f x %.0f)" % (b_br + n_ho + 10, max(b_ho, n_br)))

    # --- Variante AMS: ein Druck, zwei Farben uebereinander ---------------
    rosa, creme = teil_ams(b_gl, n_gl, stege)
    ams_fehler, punkte = ams_pruefen(b_gl, n_gl, stege, rosa, creme)
    if ams_fehler:
        raise SystemExit("FEHLER AMS: " + "; ".join(ams_fehler))
    xs = [p[0] for a, _ in list(b_gl) + list(n_gl) for p in a]
    ys = [p[1] for a, _ in list(b_gl) + list(n_gl) for p in a]
    ams_br, ams_ho = max(xs) - min(xs), max(ys) - min(ys)
    print("\nAMS-Variante: Farbe 1 (Buchstabe + Unterlage des Schriftzugs) "
          "z 0..%.0f, Farbe 2 (Schriftzug) z %.0f..%.0f -- %.0f mm hoch, "
          "Grundflaeche %.0f x %.0f mm"
          % (BUCHSTABE_DICKE, BUCHSTABE_DICKE, BUCHSTABE_DICKE + NAME_DICKE,
             BUCHSTABE_DICKE + NAME_DICKE, ams_br, ams_ho))
    print("Farbtrennung geprueft: Ebene bei z %.0f, kein Ueberlapp, alle %d "
          "Rasterpunkte der oberen Farbe stehen auf der unteren, untere Farbe "
          "ein Stueck" % (BUCHSTABE_DICKE, punkte))
    f_ = bett_pruefen(ams_br, ams_ho, "AMS-Schild")
    if f_:
        raise SystemExit("FEHLER Bauraum: " + f_)

    fehler = 0
    sicher = "".join(c if c.isalnum() else "_" for c in name)
    fehler += bauen(ziel, "tuerschild_%s_1_buchstabe_%s_1x_drucken.stl"
                    % (sicher, zeichen), b_schalen)
    fehler += bauen(ziel, "tuerschild_%s_2_name_1x_drucken.stl" % sicher,
                    n_schalen)
    fehler += bauen(ziel, "tuerschild_%s_ams_filament1_rosa_1x_drucken.stl"
                    % sicher, rosa)
    fehler += bauen(ziel, "tuerschild_%s_ams_filament2_creme_1x_drucken.stl"
                    % sicher, creme)
    if fehler:
        raise SystemExit("FEHLER: %d offene Kanten" % fehler)
    print("\nAlle Schalen wasserdicht. Zwei Wege zum selben Schild:")
    print("  kleben -- Teile 1 und 2 einzeln flach drucken, Vorderseite oben, "
          "Schriftzug auf den Buchstaben kleben.")
    print("  AMS    -- nur die beiden ams-Dateien: zusammen laden ("
          "\"mehrteiliges Objekt?\" -> Ja), je Datei ein Filament, ein Druck. "
          "Ein Farbwechsel bei %.0f mm." % BUCHSTABE_DICKE)


if __name__ == "__main__":
    main()
