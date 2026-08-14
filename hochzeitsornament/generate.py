#!/usr/bin/env python3
"""
Ornament zur Goldenen Hochzeit: Herz mit "Ute & Werner" in Schreibschrift
und grosser "50", plus Standsockel fuer den Tisch.

Zwei Teile:
  1. HERZ   -- flache Herzplatte mit erhabenem Rahmen, erhabener Schrift
               und integrierter Oese in der Herzkerbe. Haengt am Baum.
  2. SOCKEL -- Riegel mit geneigter, gekammerter Nut. Das Herz steht darin
               mit der Spitze nach unten, leicht nach hinten geneigt.

Das Ornament wird nach dem Druck lackiert (Metallic-Gold). Deshalb ist
mattes PLA ideal und alle Details sind >= 1.2 mm breit, damit der Lack
nichts zuschwemmt.

Schrift: Great Vibes (SIL Open Font License), Konturen via fontTools.
Buchstaben werden als eigene Prismen auf die Platte gesetzt; Konturen mit
Loechern (e, o, &, 0 ...) werden ueber Bruecken-Triangulierung geschlossen.
Bruecken erzeugen im Deckel/Boden koinzidente Doppelkanten -- der
Kantencheck akzeptiert dort deshalb jede GERADE Anzahl, die Mantelflaechen
entstehen aus den Originalkonturen und bleiben streng zweifach.

Alle Masse in Millimetern.
"""

import math
import os
import struct

from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

# ---------------------------------------------------------------------------
# Parameter
# ---------------------------------------------------------------------------

HERZ_HOEHE      = 165.0   # Herzkoerper ohne Oese
PLATTE_DICKE    = 4.0
RAHMEN_HOEHE    = 3.0     # erhabener Rand oben drauf
RAHMEN_SKALA    = 0.90    # Innenkontur des Rahmens (skaliertes Herz)
SCHRIFT_HOEHE   = 2.6     # Relief der Namen
ZAHL_HOEHE      = 3.0     # Relief der 50
OESE_AUSSEN     = 10.0    # Radius
OESE_LOCH       = 4.0     # Radius (Band/Schnur)

NAMEN           = "Ute & Werner"
NAMEN_BREITE    = 108.0   # Zielbreite des Schriftzugs
ZAHL            = "50"
ZAHL_GROESSE    = 33.0    # Zielhoehe der 50

SOCKEL_LAENGE   = 110.0
SOCKEL_TIEFE    = 46.0
SOCKEL_HOEHE    = 24.0
NUT_BREITE      = 4.4     # Herzdicke 4.0 + Spiel
NUT_TIEFE       = 13.0
NUT_NEIGUNG     = 12.0    # Grad nach hinten
KAMMER_LAENGE   = 30.0    # Nut nur in der Mitte -> Laengsanschlag

FONT_DATEI      = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "GreatVibes-Regular.ttf")
BEZIER_SCHRITTE = 8

# ---------------------------------------------------------------------------
# Polygon- und Mesh-Grundlagen (Technik wie in den Nachbarprojekten)
# ---------------------------------------------------------------------------


def flaeche_signiert(poly):
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def _kreuz(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _in_dreieck(p, a, b, c):
    d1, d2, d3 = _kreuz(a, b, p), _kreuz(b, c, p), _kreuz(c, a, p)
    return not (((d1 < 0) or (d2 < 0) or (d3 < 0))
                and ((d1 > 0) or (d2 > 0) or (d3 > 0)))


def punkt_in_polygon(p, poly):
    x, y = p
    drin = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            drin = not drin
    return drin


def triangulieren(poly):
    idx = list(range(len(poly)))
    if flaeche_signiert(poly) < 0:
        idx.reverse()
    out = []
    schutz = 0
    while len(idx) > 3 and schutz < 60 * len(poly):
        schutz += 1
        n = len(idx)
        ok = False
        for i in range(n):
            ia, ib, ic = idx[(i - 1) % n], idx[i], idx[(i + 1) % n]
            a, b, c = poly[ia], poly[ib], poly[ic]
            if _kreuz(a, b, c) <= 1e-9:
                continue
            if any(_in_dreieck(poly[j], a, b, c)
                   for j in idx if j not in (ia, ib, ic)
                   and poly[j] != a and poly[j] != b and poly[j] != c):
                continue
            out.append((ia, ib, ic))
            del idx[i]
            ok = True
            break
        if not ok:
            raise RuntimeError("Triangulierung steckengeblieben")
    if len(idx) == 3:
        out.append(tuple(idx))
    return out


def _bruecke_einbauen(aussen, loch):
    """Loch ueber eine Bruecke in die Aussenkontur einschneiden.

    Klassisches Verfahren: naechstgelegenes Punktpaar verbinden; falls das
    ein unbrauchbares Polygon ergibt, die naechsten Kandidaten probieren.
    Ergebnis ist ein einfaches Polygon mit doppelt durchlaufener Bruecke.
    """
    paare = sorted(((ax - lx) ** 2 + (ay - ly) ** 2, i, j)
                   for i, (ax, ay) in enumerate(aussen)
                   for j, (lx, ly) in enumerate(loch))
    for _, i, j in paare[:40]:
        loch_um = loch[j:] + loch[:j]
        kombi = (aussen[:i + 1] + loch_um + [loch_um[0]] + aussen[i:])
        try:
            triangulieren(kombi)
            return kombi
        except RuntimeError:
            continue
    raise RuntimeError("keine brauchbare Bruecke gefunden")


def prisma_mit_loechern(aussen, loecher, z0, z1):
    """Prisma eines Polygons mit beliebigen Loechern.

    Deckel und Boden entstehen aus der Bruecken-Triangulierung, die
    Mantelflaechen aus den unveraenderten Originalkonturen (aussen CCW,
    Loecher CW) -- so bleiben die Waende sauber zweifach vernetzt.
    """
    if flaeche_signiert(aussen) < 0:
        aussen = aussen[::-1]
    loecher = [l[::-1] if flaeche_signiert(l) > 0 else l for l in loecher]

    kombi = aussen
    for l in loecher:
        kombi = _bruecke_einbauen(kombi, l)
    caps = triangulieren(kombi)

    t = []
    for (a, b, c) in caps:
        pa, pb, pc = kombi[a], kombi[b], kombi[c]
        t.append(((pa[0], pa[1], z0), (pc[0], pc[1], z0), (pb[0], pb[1], z0)))
        t.append(((pa[0], pa[1], z1), (pb[0], pb[1], z1), (pc[0], pc[1], z1)))
    for kontur in [aussen] + loecher:
        n = len(kontur)
        for i in range(n):
            x1, y1 = kontur[i]
            x2, y2 = kontur[(i + 1) % n]
            t.append(((x1, y1, z0), (x2, y2, z0), (x2, y2, z1)))
            t.append(((x1, y1, z0), (x2, y2, z1), (x1, y1, z1)))
    return t


def prisma(poly, z0, z1):
    return prisma_mit_loechern(poly, [], z0, z1)


def kreis(r, cx=0.0, cy=0.0, seg=64):
    return [(cx + r * math.cos(2 * math.pi * i / seg),
             cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


def verschieben(t, dx=0.0, dy=0.0, dz=0.0):
    return [tuple((x + dx, y + dy, z + dz) for (x, y, z) in tri) for tri in t]


def kanten_pruefen(t, gerade_erlaubt=False):
    """0 = sauber. Mit gerade_erlaubt akzeptiert der Check koinzidente
    Doppelkanten aus der Bruecken-Triangulierung (jede gerade Anzahl)."""
    z = {}
    for (a, b, c) in t:
        for p, q in ((a, b), (b, c), (c, a)):
            kp = tuple(round(w, 5) for w in p)
            kq = tuple(round(w, 5) for w in q)
            s = (kp, kq) if kp < kq else (kq, kp)
            z[s] = z.get(s, 0) + 1
    if gerade_erlaubt:
        return sum(1 for n in z.values() if n % 2 != 0)
    return sum(1 for n in z.values() if n != 2)


def volumen(t):
    v = 0.0
    for (a, b, c) in t:
        v += (a[0] * (b[1] * c[2] - c[1] * b[2])
              - a[1] * (b[0] * c[2] - c[0] * b[2])
              + a[2] * (b[0] * c[1] - c[0] * b[1])) / 6.0
    return abs(v)


def stl_schreiben(pfad, dreiecke, name):
    with open(pfad, "wb") as f:
        f.write(("Goldene Hochzeit - " + name).encode("ascii", "replace")
                .ljust(80, b" ")[:80])
        f.write(struct.pack("<I", len(dreiecke)))
        for (a, b, c) in dreiecke:
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz,
                          ux * vy - uy * vx)
            l = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(struct.pack("<12fH", nx / l, ny / l, nz / l,
                                a[0], a[1], a[2], b[0], b[1], b[2],
                                c[0], c[1], c[2], 0))


# ---------------------------------------------------------------------------
# Schrift -> Konturen
# ---------------------------------------------------------------------------

_font = None


def font():
    global _font
    if _font is None:
        _font = TTFont(FONT_DATEI)
    return _font


def _quad(p0, p1, p2, schritte=BEZIER_SCHRITTE):
    pts = []
    for k in range(1, schritte + 1):
        t = k / schritte
        u = 1.0 - t
        pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return pts


def glyph_konturen(zeichen):
    """Konturen eines Zeichens in Font-Einheiten, Beziers abgeflacht."""
    f = font()
    name = f.getBestCmap()[ord(zeichen)]
    pen = RecordingPen()
    f.getGlyphSet()[name].draw(pen)

    konturen = []
    aktuelle = []
    letzter = None
    for op, args in pen.value:
        if op == "moveTo":
            aktuelle = [args[0]]
            letzter = args[0]
        elif op == "lineTo":
            aktuelle.append(args[0])
            letzter = args[0]
        elif op == "qCurveTo":
            # TrueType: beliebig viele Off-Curve-Punkte, implizite
            # On-Curve-Mittelpunkte dazwischen; letzter Punkt ist on-curve.
            punkte = list(args)
            ziel = punkte[-1]
            offs = punkte[:-1]
            start = letzter
            if ziel is None:                      # geschlossene Quad-Kette
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
        elif op == "curveTo":                     # kubisch (kommt kaum vor)
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
                # doppelte Endpunkte vermeiden
                if (abs(aktuelle[0][0] - aktuelle[-1][0]) < 1e-9
                        and abs(aktuelle[0][1] - aktuelle[-1][1]) < 1e-9):
                    aktuelle.pop()
                konturen.append(aktuelle)
            aktuelle = []
    breite = f["hmtx"][name][0]
    return konturen, breite


def text_konturen(text, hoehe_mm=None, breite_mm=None):
    """Text setzen -> Liste (aussen, [loecher]) in mm, Ursprung unten links.

    Skaliert ueber hoehe_mm (Versalhoehe des gesetzten Textes) ODER
    breite_mm (Gesamtbreite).
    """
    f = font()
    upm = f["head"].unitsPerEm
    x = 0.0
    alle = []
    for z in text:
        if z == " ":
            x += 0.30 * upm
            continue
        konturen, adv = glyph_konturen(z)
        for k in konturen:
            alle.append([(px + x, py) for (px, py) in k])
        x += adv

    xs = [p[0] for k in alle for p in k]
    ys = [p[1] for k in alle for p in k]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    if breite_mm:
        s = breite_mm / (maxx - minx)
    else:
        s = hoehe_mm / (maxy - miny)
    alle = [[((px - minx) * s, (py - miny) * s) for (px, py) in k]
            for k in alle]

    # Aussenkonturen von Loechern trennen: eine Kontur ist ein Loch, wenn
    # ihr erster Punkt in einer ungeraden Zahl ANDERER Konturen liegt.
    gruppen = []
    for i, k in enumerate(alle):
        tiefe = sum(1 for j, other in enumerate(alle)
                    if j != i and punkt_in_polygon(k[0], other))
        gruppen.append((tiefe, k))
    aussen = [(i, k) for i, (t, k) in enumerate(gruppen) if t % 2 == 0]
    ergebnis = []
    for i, a in aussen:
        loecher = [k for j, (t, k) in enumerate(gruppen)
                   if t % 2 == 1 and punkt_in_polygon(k[0], a)]
        ergebnis.append((a, loecher))
    br = (maxx - minx) * s
    ho = (maxy - miny) * s
    return ergebnis, br, ho


# ---------------------------------------------------------------------------
# Herzkontur
# ---------------------------------------------------------------------------

def herz_kontur(hoehe, seg=240):
    """Klassische parametrische Herzkurve, auf Zielhoehe skaliert,
    Zentrum (0,0) in der Mitte der Bounding Box."""
    roh = []
    for i in range(seg):
        t = 2 * math.pi * i / seg
        x = 16 * math.sin(t) ** 3
        y = (13 * math.cos(t) - 5 * math.cos(2 * t)
             - 2 * math.cos(3 * t) - math.cos(4 * t))
        roh.append((x, y))
    ys = [p[1] for p in roh]
    s = hoehe / (max(ys) - min(ys))
    cy = (max(ys) + min(ys)) / 2.0
    return [(x * s, (y - cy) * s) for (x, y) in roh]


def skaliert_um(poly, faktor, cx=0.0, cy=0.0):
    return [((x - cx) * faktor + cx, (y - cy) * faktor + cy) for (x, y) in poly]


# ---------------------------------------------------------------------------
# Bauteile
# ---------------------------------------------------------------------------

def teil_herz():
    herz = herz_kontur(HERZ_HOEHE)
    ys = [p[1] for p in herz]
    y_kerbe = max(y for (x, y) in herz if abs(x) < 1.0)   # Kerbenmitte oben
    y_top = max(ys)

    schalen = []       # (dreiecke, gerade_erlaubt)
    schalen.append((prisma(herz, 0.0, PLATTE_DICKE), False))

    # Rahmen: Band zwischen Originalkontur und skalierter Kontur
    innen = skaliert_um(herz, RAHMEN_SKALA)
    schalen.append((prisma_mit_loechern(herz, [innen], PLATTE_DICKE - 1.0,
                                        PLATTE_DICKE + RAHMEN_HOEHE), True))

    # Oese in der Kerbe: Ring, der beide Herzbuckel ueberlappt
    oese_y = y_kerbe + OESE_AUSSEN * 0.55
    ring_aussen = kreis(OESE_AUSSEN, 0.0, oese_y)
    ring_loch = kreis(OESE_LOCH, 0.0, oese_y)
    schalen.append((prisma_mit_loechern(ring_aussen, [ring_loch],
                                        0.0, PLATTE_DICKE), True))
    hoehe_gesamt = oese_y + OESE_AUSSEN - min(ys)

    # Sicherheitszone fuer die Schrift: alles muss innerhalb der
    # Rahmen-Innenkante liegen, mit etwas Abstand -- sonst wuerde Relief
    # ueber die Platte hinaus in der Luft gedruckt.
    zone = skaliert_um(herz, RAHMEN_SKALA - 0.03)

    def schrift_pruefen(konturen, dx, dy, was):
        draussen = 0
        for aussen, loecher in konturen:
            for (x, y) in aussen:
                if not punkt_in_polygon((x + dx, y + dy), zone):
                    draussen += 1
        if draussen:
            raise SystemExit("FEHLER: %s ragt mit %d Konturpunkten ueber "
                             "die Herzflaeche hinaus -- Position/Groesse "
                             "anpassen" % (was, draussen))

    # Schriftzug
    namen, n_br, n_ho = text_konturen(NAMEN, breite_mm=NAMEN_BREITE)
    n_y = 6.0                                    # Grundlinie ueber Herzmitte
    schrift_pruefen(namen, -n_br / 2.0, n_y, "Namenszug")
    for aussen, loecher in namen:
        t = prisma_mit_loechern(aussen, loecher,
                                PLATTE_DICKE - 0.5,
                                PLATTE_DICKE + SCHRIFT_HOEHE)
        schalen.append((verschieben(t, -n_br / 2.0, n_y), True))

    # Grosse 50
    zahl, z_br, z_ho = text_konturen(ZAHL, hoehe_mm=ZAHL_GROESSE)
    z_y = n_y - 8.0 - z_ho
    schrift_pruefen(zahl, -z_br / 2.0, z_y, "Zahl 50")
    for aussen, loecher in zahl:
        t = prisma_mit_loechern(aussen, loecher,
                                PLATTE_DICKE - 0.5,
                                PLATTE_DICKE + ZAHL_HOEHE)
        schalen.append((verschieben(t, -z_br / 2.0, z_y), True))

    return schalen, hoehe_gesamt


def teil_sockel():
    """Riegel mit geneigter Nut, Nut nur in der mittleren Kammer.

    Aufbau als Extrusion des Querschnitts entlang X: zwei volle Endbloecke
    und die Kammer mit Nut dazwischen. Querschnitt in (y, z):
    Trapez mit Fase, Nut von oben, um NUT_NEIGUNG nach hinten gekippt.
    """
    fase = 5.0
    t2, h = SOCKEL_TIEFE / 2.0, SOCKEL_HOEHE

    def profil(mit_nut):
        """Querschnitt (y, z), gegen den Uhrzeigersinn ab unten links.

        Die Nut ist ein von oben eingeschnittenes Parallelogramm: ihre
        Bodenkante ist gegenueber der Oeffnung um tan(neigung)*tiefe nach
        hinten (-y) versetzt -- das Herz lehnt dadurch nach hinten.
        """
        p = [(-t2, 0.0), (t2, 0.0), (t2, h - fase), (t2 - fase, h)]
        if mit_nut:
            nb = NUT_BREITE / 2.0
            versatz = math.tan(math.radians(NUT_NEIGUNG)) * NUT_TIEFE
            p.append((nb, h))
            p.append((nb - versatz, h - NUT_TIEFE))
            p.append((-nb - versatz, h - NUT_TIEFE))
            p.append((-nb, h))
        p.append((-(t2 - fase), h))
        p.append((-t2, h - fase))
        return p

    def extrudieren_x(poly_yz, x0, x1):
        """Querschnitt (y,z) entlang X extrudieren."""
        t = prisma(poly_yz, x0, x1)               # erst als (y,z)-Prisma in Z
        return [tuple((z, x, y) for (x, y, z) in tri) for tri in t]

    l2 = SOCKEL_LAENGE / 2.0
    k2 = KAMMER_LAENGE / 2.0
    schalen = [
        (extrudieren_x(profil(False), -l2, -k2 + 1.0), False),
        (extrudieren_x(profil(True), -k2, k2), False),
        (extrudieren_x(profil(False), k2 - 1.0, l2), False),
    ]
    return schalen


# ---------------------------------------------------------------------------

def bauen(ziel, name, schalen):
    fehler = 0
    alle = []
    for s, gerade in schalen:
        fehler += kanten_pruefen(s, gerade_erlaubt=gerade)
        alle.extend(s)
    stl_schreiben(os.path.join(ziel, name), alle, name)
    vol = sum(volumen(s) for s, _ in schalen)
    print("%-40s %3d Schalen %6d Dreiecke  ~%5.1f cm3  Kantenfehler: %d"
          % (name, len(schalen), len(alle), vol / 1000.0, fehler))
    return fehler


def main():
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    os.makedirs(ziel, exist_ok=True)

    herz, hoehe = teil_herz()
    print("Herz: %.0f mm hoch (mit Oese %.0f mm), Platte %.1f mm, "
          "Schrift +%.1f mm Relief\n" % (HERZ_HOEHE, hoehe, PLATTE_DICKE,
                                         SCHRIFT_HOEHE))
    fehler = 0
    fehler += bauen(ziel, "ornament_herz_1x_drucken.stl", herz)
    fehler += bauen(ziel, "ornament_sockel_1x_drucken.stl", teil_sockel())

    if fehler:
        raise SystemExit("FEHLER: %d Kantenfehler" % fehler)
    print("\nAlle Meshes geschlossen. Herz flach drucken, Schrift nach oben.")


if __name__ == "__main__":
    main()
