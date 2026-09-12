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
# Laufweite. Bei 100 % stehen die Buchstaben genau auf Abstand -- in
# Schreibschrift heisst das: sie beruehren sich fast, aber eben nur fast
# (beim fetten Dancing Script blieb 1 mm Luft zwischen E und l). Dann
# braucht es einen Steg, und der ist duenner als jeder Strich der
# Schrift, also die Sollbruchstelle des ganzen Schilds. Enger gesetzt
# ueberlappen sich die Buchstaben wirklich und wachsen breit zusammen:
# bei 96 % ist der schmalste Uebergang 4,4 mm und damit so dick wie die
# duennsten Striche der Schrift selbst. uebergaenge_pruefen rechnet das
# jedes Mal nach.
NAME_SPUR = 0.96
NAME_DICKE = 4.0
NAME_BREITE_FAKTOR = 1.40  # Schriftzug so viel breiter als der Buchstabe
# Schriftzugmitte auf dieser Hoehe des Buchstabens. Die Vorlage hat ihn
# auf halber Hoehe; hier sitzt er tiefer, im unteren Drittel des E, und
# liegt damit auf dem unteren Balken auf statt ueber dem Mittelbalken.
NAME_MITTE = 0.32
NAME_VERSATZ = -21.0       # Schriftzug aus der Mitte nach links (mm)
UEBERGANG_MIN = 3.0        # so dick muss jede Verbindung mindestens sein
UEBERGANG_STOPP = 2.0      # darunter Abbruch
STEG_BREITE = 2.5          # Verbindungssteg zwischen Inseln der Schreibschrift
STEG_UEBER = 1.5           # so weit laeuft der Steg in beide Inseln hinein
# Eine Insel, die zu diesem Anteil auf dem grossen Buchstaben liegt,
# braucht keinen Steg: sie ruht auf ihm. Beim AMS-Druck verschmilzt sie
# ohnehin mit der Unterlage, beim Kleben wird sie einzeln aufgeklebt.
STUETZ_MIN = 0.70
RASTER = 0.3               # mm, Rasterweite der Strichbreitenmessung

FONT_BUCHSTABE = os.path.join(HIER, "LiberationSerif-Bold.ttf")


def _schrift(datei):
    return os.path.join(HIER, "schriften", datei)


# Kandidatinnen fuer den Schriftzug, alle SIL OFL (Lizenzen in schriften/).
# --schrift waehlt aus; schriftvergleich.py misst sie und zeichnet ein
# Blatt mit allen Vorschlaegen.
# Eintrag: Anzeigename, Datei, Charakter, Standardgewicht. Das Gewicht
# gilt nur fuer Variable Fonts (hier Dancing Script, Achse wght 400..700)
# -- die Buchstabenformen werden dabei wirklich fetter gezeichnet, nicht
# nachtraeglich aufgedickt. Bei statischen Schriften bleibt es None.
SCHRIFTEN = {
    "greatvibes":   ("Great Vibes", os.path.join(HIER, "GreatVibes-Regular.ttf"),
                     "festlich, starker Strichkontrast, grosse Schwuenge", None),
    "parisienne":   ("Parisienne", _schrift("Parisienne-Regular.ttf"),
                     "zierlich und ruhig, weniger Schnoerkel, gut lesbar", None),
    "alexbrush":    ("Alex Brush", _schrift("AlexBrush-Regular.ttf"),
                     "flott geschrieben, schraeg, gleichmaessig duenn", None),
    "sacramento":   ("Sacramento", _schrift("Sacramento-Regular.ttf"),
                     "monolinear und schlicht, modern, fast ohne Kontrast", None),
    "dancingscript": ("Dancing Script", _schrift("DancingScript.ttf"),
                      "verspielt und huepfend, freundlich, kindgerecht", 700.0),
    "kaushanscript": ("Kaushan Script", _schrift("KaushanScript-Regular.ttf"),
                      "kraeftiger Pinsel, laessig, sehr praesent", None),
    "pacifico":     ("Pacifico", _schrift("Pacifico-Regular.ttf"),
                     "dick und rund, Retro-Surf, robusteste Variante", None),
}
SCHRIFT = "dancingscript"        # gewaehlt: verspielt, und im fetten Schnitt
FONT_NAME = SCHRIFTEN[SCHRIFT][1]
GEWICHT = SCHRIFTEN[SCHRIFT][3]
BEZIER_SCHRITTE = 10

# Bett Bambu H2S, vorsichtig 350 x 320, 20 mm Rand
BETT_X, BETT_Y, BETT_RAND = 350.0, 320.0, 20.0

# ---------------------------------------------------------------------------
# Schrift -> Konturen (mit Font-Parameter, sonst wie im Hochzeitsornament)
# ---------------------------------------------------------------------------
_fonts = {}


def font(pfad):
    """Font laden; bei Variable Fonts auf GEWICHT festlegen.

    instantiateVariableFont backt die Gewichtsachse in die Umrisse ein --
    danach verhaelt sich die Datei wie eine statische Schrift, und die
    Konturen sind die echten fetten Formen des Entwerfers. Ein
    nachtraegliches Aufdicken per Offset waere etwas anderes: es blaeht
    auch die Rundungen auf und schliesst enge Punzen zu.
    """
    schluessel = (pfad, GEWICHT)
    if schluessel not in _fonts:
        f = TTFont(pfad)
        if GEWICHT is not None and "fvar" in f:
            from fontTools.varLib import instancer
            achse = {a.axisTag: a for a in f["fvar"].axes}["wght"]
            wert = min(max(GEWICHT, achse.minValue), achse.maxValue)
            f = instancer.instantiateVariableFont(f, {"wght": wert})
        _fonts[schluessel] = f
    return _fonts[schluessel]


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


def _balken(von, bis, breite):
    """Rechteck der Breite `breite` zwischen zwei Punkten."""
    d = math.dist(von, bis)
    if d < 1e-9:
        return None
    ux, uy = (bis[0] - von[0]) / d, (bis[1] - von[1]) / d
    nx, ny = -uy * breite / 2.0, ux * breite / 2.0
    return [(von[0] + nx, von[1] + ny), (bis[0] + nx, bis[1] + ny),
            (bis[0] - nx, bis[1] - ny), (von[0] - nx, von[1] - ny)]


def steg_breite(pA, pB, richtung, teileA, teileB, d):
    """Wie breit darf der Steg sein?

    Ein 2,5-mm-Haelschen zwischen zwei fetten Buchstaben ist eine
    Sollbruchstelle und sieht auch so aus. Wo zwei Striche fast
    aneinanderstossen, soll der Steg deshalb so breit werden wie die
    Striche selbst -- dann wirkt die Stelle wie eine Beruehrung.

    Gemessen wird das nicht an einer geschaetzten Strichstaerke, sondern
    am Ergebnis: fuer eine Kandidatenbreite werden die beiden Enden des
    Stegs (die Stuecke, die in die Buchstaben hineinlaufen) probeweise
    gerastert. Liegen beide zu mindestens 80 % im Material ihres
    Buchstabens, passt die Breite -- der Steg verschwindet dann im
    Strich, statt daneben in die Luft zu ragen. Von breit nach schmal
    probiert, die erste passende gewinnt.

    Und nur bei kurzen Luecken: je laenger die Bruecke, desto schlanker
    muss sie bleiben, sonst wird aus einem Steg ein Klotz. Ab 6 mm
    Luecke bleibt es bei STEG_BREITE.
    """
    obergrenze = STEG_BREITE + 2.0 * max(0.0, 6.0 - d)
    endeA = (pA[0] - richtung[0] * STEG_UEBER, pA[1] - richtung[1] * STEG_UEBER)
    endeB = (pB[0] + richtung[0] * STEG_UEBER, pB[1] + richtung[1] * STEG_UEBER)
    breite = obergrenze
    while breite > STEG_BREITE + 1e-9:
        a = _balken(endeA, pA, breite)
        b = _balken(endeB, pB, breite)
        if (a and b
                and flaechenanteil([(a, [])], teileA, n=24) >= 0.8
                and flaechenanteil([(b, [])], teileB, n=24) >= 0.8):
            return breite
        breite -= 0.5
    return STEG_BREITE


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
        return None, 0.0, None, None, None
    ux, uy = (q[0] - p[0]) / d, (q[1] - p[1]) / d
    nx, ny = -uy * breite / 2.0, ux * breite / 2.0
    p2 = (p[0] - ux * ueber, p[1] - uy * ueber)
    q2 = (q[0] + ux * ueber, q[1] + uy * ueber)
    return [(p2[0] + nx, p2[1] + ny), (q2[0] + nx, q2[1] + ny),
            (q2[0] - nx, q2[1] - ny), (p2[0] - nx, p2[1] - ny)], d, p, q, (ux, uy)


def flaechenanteil(teile, traeger, n=48):
    """Welcher Anteil der Flaeche von `teile` liegt auf `traeger`?

    Beides Listen von (aussen, loecher). Rasterprobe ueber die
    Huellflaeche von `teile`.
    """
    pts = [p for a, _ in teile for p in a]
    if not pts or not traeger:
        return 0.0
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    drin = ges = 0
    for i in range(n):
        for j in range(n):
            p = (x0 + (x1 - x0) * (i + 0.5) / n, y0 + (y1 - y0) * (j + 0.5) / n)
            if not im_material(p, teile):
                continue
            ges += 1
            if im_material(p, traeger):
                drin += 1
    return drin / float(max(1, ges))


def _komponente_teile(indizes, alle, glyphen):
    """Die (aussen, loecher) einer Komponente -- Stege haben keine Loecher."""
    return [glyphen[i] if i < len(glyphen) else (alle[i], []) for i in indizes]


def inseln_anbinden(glyphen, traeger=()):
    """Inseln des Schriftzugs verbinden -- aber nur, wo noetig.

    Eine Insel, die zu mindestens STUETZ_MIN auf dem grossen Buchstaben
    liegt, bekommt keinen Steg: sie ruht auf ihm (beim AMS-Druck
    verschmolzen, beim Kleben einzeln aufgeklebt). Das ist der Grund,
    warum der Schriftzug seitlich versetzt sitzt -- so landet der i-Punkt
    auf dem Mittelbalken des E statt an einem sichtbaren Stiel.

    Alle uebrigen Inseln werden wie bisher zusammengezogen: die kleinste
    freie Komponente an ihren naechsten Nachbarn in einer anderen freien
    Komponente. Ohne `traeger` verhaelt sich alles wie vorher.
    Rueckgabe: Stege, ueberbrueckte Abstaende, getragene Inseln
    [(indizes, anteil)].
    """
    aussen = [a for (a, _) in glyphen]
    stege, abstaende = [], []

    def getragen(indizes, alle):
        return flaechenanteil(_komponente_teile(indizes, alle, glyphen), traeger)

    for _ in range(len(aussen)):
        alle = aussen + stege
        komp = komponenten(alle)
        frei = [k for k in komp if getragen(k, alle) < STUETZ_MIN]
        if len(frei) <= 1:
            break
        frei.sort(key=lambda k: sum(abs(flaeche_signiert(alle[i])) for i in k))
        klein = frei[0]
        andere = [i for k in frei[1:] for i in k]
        best = None
        for i in klein:
            for j in andere:
                s, d, p, q, u = steg_zwischen(alle[i], alle[j], STEG_BREITE,
                                              STEG_UEBER)
                if s is not None and (best is None or d < best[0]):
                    best = (d, i, j, p, q, u)
        if best is None:
            break
        d, i, j, p, q, u = best
        # jetzt erst die Breite: so breit wie die Striche, die hier
        # zusammenkommen (bei kurzen Luecken), damit keine Sollbruch-
        # stelle entsteht
        breite = steg_breite(p, q, u,
                             _komponente_teile([i], alle, glyphen),
                             _komponente_teile([j], alle, glyphen), d)
        s = steg_zwischen(alle[i], alle[j], breite, STEG_UEBER)[0]
        stege.append(s)
        abstaende.append((d, breite))
    alle = aussen + stege
    ruhend = [(k, getragen(k, alle)) for k in komponenten(alle)
              if getragen(k, alle) >= STUETZ_MIN]
    return stege, abstaende, ruhend


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


def teil_name(name, buchstabe_breite, buchstabe_hoehe, traeger=()):
    breite = min(NAME_BREITE_FAKTOR * buchstabe_breite,
                 BETT_X - 2 * BETT_RAND)
    glyphen, br, ho, _ = glyphen_setzen(FONT_NAME, name, breite_mm=breite,
                                        spur=NAME_SPUR)
    # an seinen Platz: ueber dem Buchstaben, Mitte auf NAME_MITTE, um
    # NAME_VERSATZ aus der Mitte geschoben (damit der i-Punkt auf dem
    # Mittelbalken aufliegt und ohne Steg auskommt)
    dx = (buchstabe_breite - br) / 2.0 + NAME_VERSATZ
    dy = NAME_MITTE * buchstabe_hoehe - ho / 2.0
    glyphen = [([(x + dx, y + dy) for (x, y) in a],
                [[(x + dx, y + dy) for (x, y) in l] for l in ls])
               for (a, ls) in glyphen]
    stege, abstaende, ruhend = inseln_anbinden(glyphen, traeger)
    schalen = []
    for aussen, loecher in glyphen:
        schalen.append(prisma_mit_loechern(aussen, loecher, 0.0, NAME_DICKE))
    for s in stege:
        schalen.append(prisma(s, 0.0, NAME_DICKE))
    return schalen, glyphen, stege, abstaende, br, ho, (dx, dy), ruhend


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


def rastern(glyphen, stege, h=None, rand=2.0):
    """Material der Schrift in ein Boolean-Raster fuellen (Scanline).

    Je Glyphe gilt die Even-Odd-Regel ueber ihre eigenen Konturen --
    Loecher liegen in ihrer Aussenkontur, das stimmt. Die Vereinigung
    ueber die Glyphen entsteht durch Veroderung der Zeilen.

    h absichtlich nicht mit RASTER als Vorgabewert: Vorgaben werden beim
    Definieren gebunden, ein spaeteres Setzen von RASTER waere wirkungslos
    -- genau das taeuschte erst eine feinere Messung vor, die nie lief
    (drei Schriften lieferten auf 0,01 mm denselben Wert).
    """
    h = RASTER if h is None else h
    teile = [[a] + list(ls) for a, ls in glyphen] + [[s] for s in stege]
    pts = [p for t in teile for k in t for p in k]
    x0 = min(p[0] for p in pts) - rand
    x1 = max(p[0] for p in pts) + rand
    y0 = min(p[1] for p in pts) - rand
    y1 = max(p[1] for p in pts) + rand
    nx = int((x1 - x0) / h) + 1
    ny = int((y1 - y0) / h) + 1
    kanten = []
    for t in teile:
        for k in t:
            n = len(k)
            kanten.append([(k[i], k[(i + 1) % n]) for i in range(n)])
    grid = bytearray(nx * ny)
    for j in range(ny):
        y = y0 + (j + 0.5) * h
        zeile = j * nx
        for kk in kanten:
            xs = []
            for (pa, pb) in kk:
                ya, yb = pa[1], pb[1]
                if (ya <= y) == (yb <= y):
                    continue
                xs.append(pa[0] + (y - ya) * (pb[0] - pa[0]) / (yb - ya))
            if not xs:
                continue
            xs.sort()
            for m in range(0, len(xs) - 1, 2):
                i0 = max(0, int(math.ceil((xs[m] - x0) / h - 0.5)))
                i1 = min(nx - 1, int((xs[m + 1] - x0) / h - 0.5))
                for i in range(i0, i1 + 1):
                    grid[zeile + i] = 1
    return grid, nx, ny, h


def distanzen(grid, nx, ny, h):
    """Chamfer-Distanztransformation: Abstand jeder Materialzelle zum
    naechsten Freiraum, in mm."""
    INF = 1e9
    a, b = 1.0, 1.3507       # Borgefors-Gewichte
    d = [0.0 if not grid[k] else INF for k in range(nx * ny)]
    for j in range(ny):
        z = j * nx
        for i in range(nx):
            k = z + i
            if d[k] == 0.0:
                continue
            v = d[k]
            if i > 0:
                v = min(v, d[k - 1] + a)
            if j > 0:
                v = min(v, d[k - nx] + a)
                if i > 0:
                    v = min(v, d[k - nx - 1] + b)
                if i < nx - 1:
                    v = min(v, d[k - nx + 1] + b)
            d[k] = v
    for j in range(ny - 1, -1, -1):
        z = j * nx
        for i in range(nx - 1, -1, -1):
            k = z + i
            if d[k] == 0.0:
                continue
            v = d[k]
            if i < nx - 1:
                v = min(v, d[k + 1] + a)
            if j < ny - 1:
                v = min(v, d[k + nx] + a)
                if i > 0:
                    v = min(v, d[k + nx - 1] + b)
                if i < nx - 1:
                    v = min(v, d[k + nx + 1] + b)
            d[k] = v
    return [x * h for x in d]


def strichbreiten(glyphen, stege):
    """Breiten entlang der Mittelachse: (duennste robust, absolut duennste,
    mittlere). Mittelachse = Zellen, deren Abstand lokal maximal ist --
    dort passt der groesste Kreis in den Strich, 2*Abstand ist die
    Strichbreite an dieser Stelle."""
    grid, nx, ny, h = rastern(glyphen, stege)
    d = distanzen(grid, nx, ny, h)
    ruecken = []
    for j in range(1, ny - 1):
        z = j * nx
        for i in range(1, nx - 1):
            k = z + i
            v = d[k]
            if v <= 0.0:
                continue
            if (v >= d[k - 1] and v >= d[k + 1] and v >= d[k - nx]
                    and v >= d[k + nx] and v >= d[k - nx - 1]
                    and v >= d[k - nx + 1] and v >= d[k + nx - 1]
                    and v >= d[k + nx + 1]):
                ruecken.append(2.0 * v)
    if not ruecken:
        return 0.0, 0.0, 0.0
    ruecken.sort()
    p2 = ruecken[max(0, int(0.02 * len(ruecken)))]
    return p2, ruecken[0], ruecken[len(ruecken) // 2]


def inkreis(m, teile, max_r=12.0, schritt=0.1, n=32):
    """Radius des groessten Kreises um m, der ganz im Material liegt."""
    if not im_material(m, teile):
        return 0.0
    r = 0.0
    while r + schritt <= max_r:
        rr = r + schritt
        if not all(im_material((m[0] + rr * math.cos(2 * math.pi * k / n),
                                m[1] + rr * math.sin(2 * math.pi * k / n)), teile)
                   for k in range(n)):
            break
        r = rr
    return r


def uebergaenge_pruefen(glyphen, stege):
    """Wie dick ist die duennste Verbindung im Schriftzug?

    Ein Schriftzug aus einem Stueck sagt noch nichts: zwei Buchstaben
    koennen sich auch nur streifen, dann haengen sie an einem Faden von
    einem Millimeter -- duenner als jeder Strich der Schrift und die
    Stelle, an der das Schild bricht. Also wird jede Stelle gemessen, an
    der zwei Teile ueberlappen: Schwerpunkt der Ueberlappung bestimmen
    und dort den groessten Kreis suchen, der noch ganz im Material der
    beiden liegt. Sein Durchmesser ist die Dicke der Verbindung.

    Rueckgabe: Liste (beschreibung, dicke), duennste zuerst.
    """
    teile = list(glyphen) + [(s, []) for s in stege]
    namen = (["Buchstabe %d" % (i + 1) for i in range(len(glyphen))]
             + ["Steg %d" % (i + 1) for i in range(len(stege))])
    ergebnis = []
    for i in range(len(teile)):
        for j in range(i + 1, len(teile)):
            A, B = teile[i], teile[j]
            drin = ([p for p in A[0] if im_material(p, [B])]
                    + [p for p in B[0] if im_material(p, [A])])
            if not drin:
                continue
            c = (sum(p[0] for p in drin) / len(drin),
                 sum(p[1] for p in drin) / len(drin))
            # Bewusst der Schwerpunkt der Ueberlappung und nicht das
            # Maximum ueber alle Ueberlappungspunkte: ein einzelner Punkt
            # kann tief in einem dicken Strich liegen und eine duenne
            # Verbindung schoenrechnen. Nur wenn der Schwerpunkt gar
            # nicht im Material liegt (zwei getrennte Beruehrzonen),
            # zaehlt die dickste der einzelnen Stellen.
            dick = 2 * inkreis(c, [A, B])
            if dick <= 0.0:
                dick = max(2 * inkreis(p, [A, B])
                           for p in drin[::max(1, len(drin) // 8)])
            ergebnis.append(("%s/%s" % (namen[i], namen[j]), dick))
    ergebnis.sort(key=lambda t: t[1])
    return ergebnis


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
    global BUCHSTABE_HOEHE, FONT_NAME, SCHRIFT, NAME_MITTE, GEWICHT, NAME_SPUR
    global NAME_BREITE_FAKTOR, NAME_VERSATZ
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default=NAME)
    ap.add_argument("--buchstabe", default=None,
                    help="grosser Buchstabe (Standard: Anfangsbuchstabe des Namens)")
    ap.add_argument("--hoehe", type=float, default=BUCHSTABE_HOEHE,
                    help="Hoehe des grossen Buchstabens in mm")
    ap.add_argument("--schrift", default=SCHRIFT, choices=sorted(SCHRIFTEN),
                    help="Schreibschrift des Namens (Standard: %(default)s); "
                         "Vergleich: python3 schriftvergleich.py")
    ap.add_argument("--mitte", type=float, default=NAME_MITTE,
                    help="Schriftzugmitte auf dieser Hoehe des Buchstabens "
                         "(0..1, Standard: %(default)s)")
    ap.add_argument("--breite", type=float, default=NAME_BREITE_FAKTOR,
                    help="Schriftzugbreite als Vielfaches der Buchstabenbreite "
                         "(Standard: %(default)s)")
    ap.add_argument("--versatz", type=float, default=NAME_VERSATZ,
                    help="Schriftzug aus der Mitte nach links, mm negativ "
                         "(Standard: %(default)s)")
    ap.add_argument("--staerke", type=float, default=None,
                    help="Schriftgewicht bei Variable Fonts (Dancing Script: "
                         "400 normal bis 700 fett; Standard je Schrift)")
    args = ap.parse_args()
    BUCHSTABE_HOEHE = args.hoehe
    NAME_MITTE = args.mitte
    NAME_BREITE_FAKTOR = args.breite
    NAME_VERSATZ = args.versatz
    SCHRIFT = args.schrift
    FONT_NAME = SCHRIFTEN[SCHRIFT][1]
    GEWICHT = args.staerke if args.staerke is not None else SCHRIFTEN[SCHRIFT][3]
    name = args.name
    zeichen = args.buchstabe or name[0].upper()

    ziel = os.path.join(HIER, "stl")
    os.makedirs(ziel, exist_ok=True)
    for alt in os.listdir(ziel):
        if alt.startswith("tuerschild_") and alt.endswith(".stl"):
            os.remove(os.path.join(ziel, alt))

    b_schalen, b_gl, b_br, b_ho = teil_buchstabe(zeichen)
    # Laufweite: notfalls enger, bis jede Verbindung dick genug ist.
    # Ein Schriftzug "aus einem Stueck" kann an einem 1-mm-Faden
    # haengen; dann helfen nur ueberlappende Buchstaben.
    start_spur = NAME_SPUR
    for versuch in range(13):
        NAME_SPUR = start_spur - 0.005 * versuch
        (n_schalen, n_gl, stege, abst, n_br, n_ho, (dx, dy),
         ruhend) = teil_name(name, b_br, b_ho, b_gl)
        uebergaenge = uebergaenge_pruefen(n_gl, stege)
        duennste = uebergaenge[0][1] if uebergaenge else float("inf")
        if duennste >= UEBERGANG_MIN:
            break
    if NAME_SPUR != start_spur:
        print("Laufweite von %.1f %% auf %.1f %% verengt, damit die Buchstaben "
              "breit genug zusammenwachsen" % (100 * start_spur, 100 * NAME_SPUR))

    print("Tuerschild '%s': Buchstabe %s %.0f mm hoch (%.0f breit, %.0f dick), "
          "Schriftzug %.0f x %.0f mm (%.0f dick) in %s%s"
          % (name, zeichen, b_ho, b_br, BUCHSTABE_DICKE, n_br, n_ho, NAME_DICKE,
             SCHRIFTEN[SCHRIFT][0],
             "" if GEWICHT is None else " (Gewicht %.0f)" % GEWICHT))
    print("Schriftzug ragt %.0f mm links und %.0f mm rechts ueber den "
          "Buchstaben hinaus, Mitte auf %.0f %% der Buchstabenhoehe, "
          "%.0f mm aus der Mitte nach links"
          % (max(0.0, -dx), max(0.0, dx + n_br - b_br), 100 * NAME_MITTE,
             -NAME_VERSATZ))
    if stege:
        print("Inseln angebunden: %d Steg(e) -- %s"
              % (len(stege),
                 ", ".join("%.1f mm Luecke mit %.1f mm breitem Steg" % (d_, b_)
                           for (d_, b_) in abst)))
    else:
        print("Schriftzug haengt von selbst zusammen, keine Stege noetig")
    for k, anteil_ in ruhend:
        print("Insel ohne Steg: liegt zu %.0f %% auf dem Buchstaben auf"
              % (100 * anteil_))
    alle = [a for a, _ in n_gl] + stege
    komp = komponenten(alle)
    lose = [k for k in komp
            if flaechenanteil(_komponente_teile(k, alle, n_gl), b_gl) < STUETZ_MIN]
    if len(lose) != 1:
        raise SystemExit("FEHLER: Schriftzug zerfaellt in %d freie Teile"
                         % len(lose))
    if len(komp) == 1:
        print("Zusammenhang geprueft: ein Stueck")
    else:
        print("Zusammenhang geprueft: ein zusammenhaengendes Hauptstueck, dazu "
              "%d Insel(n), die auf dem Buchstaben ruhen" % (len(komp) - 1))
    if uebergaenge:
        schwach, dick = uebergaenge[0]
        # Gemessen wird nicht gegen eine feste Zahl allein, sondern gegen
        # die Schrift selbst: eine Verbindung darf nicht duenner sein als
        # die duennsten Striche ringsum, sonst ist genau sie die
        # Sollbruchstelle. Bei einer zierlichen Schrift waere eine feste
        # Schwelle sonst unfair, bei einer fetten zu lasch.
        strich, _, _ = strichbreiten(n_gl, ())
        grenze = min(UEBERGANG_MIN, strich)
        print("Duennste Verbindung im Schriftzug: %.1f mm (%s) bei %.1f mm "
              "duennstem Strich, %d Uebergaenge insgesamt"
              % (dick, schwach, strich, len(uebergaenge)))
        if dick < min(UEBERGANG_STOPP, 0.8 * strich):
            raise SystemExit(
                "FEHLER: Verbindung %s nur %.1f mm dick und damit duenner als "
                "die Schrift selbst (%.1f mm) -- das bricht, und engere "
                "Laufweite half nicht. Groesserer Schriftzug (--breite) oder "
                "kraeftigere Schrift (--schrift pacifico) noetig."
                % (schwach, dick, strich))
        if dick < grenze:
            print("  WARNUNG: unter %.1f mm, auch bei %.1f %% Laufweite"
                  % (grenze, 100 * NAME_SPUR))
    anteil = klebeflaeche(n_gl, b_gl)
    print("Klebeflaeche: %.0f %% des Schriftzugs liegen auf dem Buchstaben"
          % (100 * anteil))
    # Ein E besteht ueberwiegend aus Leerraum; der Schriftzug liegt also
    # vor allem ueber den Innenraeumen und trifft Stamm und Balken nur
    # stellenweise. 15 % reichen bei 4 mm steifem Schriftzug voellig.
    # Wichtig: das ist eine Aussage ueber die KLEBEVARIANTE. Beim
    # AMS-Druck steht der Schriftzug ohnehin auf seiner eigenen Unterlage
    # und ist mit ihr verschmolzen -- dort ist die Zahl bedeutungslos.
    # Eine duenne, tief sitzende Schrift darf deshalb nicht den ganzen
    # Lauf abbrechen; erst unter 8 % wird auch Kleben sinnlos.
    if anteil < 0.08:
        raise SystemExit("FEHLER: zu wenig Klebeflaeche")
    if anteil < 0.15:
        print("  WARNUNG: fuer die Klebevariante wenig -- lieber die "
              "AMS-Variante drucken, die ist davon unabhaengig")
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
    sicher = ("".join(c if c.isalnum() else "_" for c in name) + "_" + SCHRIFT
              + ("" if GEWICHT is None else "%.0f" % GEWICHT))
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
    if ruhend:
        print("            Dabei %d Insel(n) einzeln aufkleben -- sie haengen "
              "nicht am Schriftzug, sondern liegen direkt auf dem Buchstaben "
              "(im AMS-Druck verschmelzen sie von selbst)." % len(ruhend))
    print("  AMS    -- nur die beiden ams-Dateien: zusammen laden ("
          "\"mehrteiliges Objekt?\" -> Ja), je Datei ein Filament, ein Druck. "
          "Ein Farbwechsel bei %.0f mm." % BUCHSTABE_DICKE)


if __name__ == "__main__":
    main()
