#!/usr/bin/env python3
"""
Fernrohrhalter fuer ein Kinderfernrohr, zum Anschrauben an ein Brett.

Aufbau (von unten nach oben):

  1. GRUNDPLATTE mit Pfosten -- wird mit 4 Holzschrauben auf das Brett
     (Verandabruestung) geschraubt. Der Pfosten zeigt nach oben.
  2. DREHGABEL -- eine Scheibe mit Huelse, die von oben ueber den Pfosten
     gestuelpt wird und sich frei drehen laesst (schwenken links/rechts).
     Auf der Scheibe stehen zwei Gabelarme mit Lagerbohrungen.
  3. ROHRSCHELLE -- eine C-foermige Klemme, die auf das Fernrohr
     aufgeschnappt wird. Seitlich zwei Lagerboecke.
  4. 2x ACHSSTIFT -- werden von aussen durch die Gabelarme gesteckt und
     in die Lagerboecke der Schelle gepresst (neigen hoch/runter).

Balance: die Schelle wird am SCHWERPUNKT des Fernrohrs festgeklemmt --
vorher das Rohr auf einem Stift ausbalancieren und die Stelle markieren.
Dann bleibt das Fernrohr in jeder Neigung von selbst stehen.

Mesh-Technik wie beim Schutzring-Projekt: jedes Teil besteht aus mehreren
geschlossenen, sich ueberlappenden Prismen ("Schalen") in einer STL-Datei.
Der Slicer vereinigt ueberlappende Schalen beim Slicen -- so kommen wir
ohne CAD-Booleans aus, und jede Schale ist beweisbar wasserdicht.
Bohrungen liegen immer in Extrusionsrichtung (Prisma mit Loch), Zapfen
und Loecher quer zur Druckrichtung sind tropfen- bzw. rautenfoermig,
damit ohne Stuetzen gedruckt werden kann.

Alle Masse in Millimetern.
"""

import math
import struct
import os

# ---------------------------------------------------------------------------
# Parameter
# ---------------------------------------------------------------------------

ROHR_D          = 50.0    # Aussendurchmesser des Fernrohrs (--rohr!)
ROHR_SPIEL      = 0.4     # Luft der Schelle zum Rohr (Klemmung kommt vom C)

SCHELLE_WAND    = 4.0     # Wandstaerke der C-Schelle
SCHELLE_LAENGE  = 40.0    # Laenge der Schelle entlang des Rohrs
SCHELLE_OEFFNUNG = 100.0  # Oeffnungswinkel des C in Grad (zum Aufschnappen)

BOSS_BREITE     = 22.0    # Lagerbock: Raute ueber Eck gemessen
BOSS_LAENGE     = 8.0     # Lagerbock: Laenge entlang der Achse
LOCH_BOSS       = 9.5     # Bohrung im Lagerbock (Presssitz fuer den Stift)
LOCH_ARM        = 9.9     # Bohrung im Gabelarm (Drehsitz)
ACHSE_D         = 9.7     # Achsstift-Durchmesser
ACHSE_KOPF_D    = 16.0    # Kopf des Achsstifts
ACHSE_KOPF_H    = 4.0

PLATTE          = 110.0   # Kantenlaenge der Grundplatte
PLATTE_H        = 8.0
ECKRADIUS       = 12.0
SCHLITZ_B       = 5.2     # offene Schraubschlitze (4.5er Holzschraube)
SCHLITZ_T       = 14.0    # Schlitztiefe vom Rand

PFOSTEN_D       = 25.0
HUELSE_SPIEL    = 0.7     # Drehspiel Gabel/Pfosten (Durchmesser)

SCHEIBE_H       = 8.0     # Bodenscheibe der Drehgabel
KRAGEN_D        = 42.0    # Huelse auf der Scheibe
KRAGEN_H        = 20.0

ARM_DICKE       = 8.0
ARM_BREITE      = 30.0
ARM_BOSS_LUFT   = 1.0     # axiales Spiel Gabelarm <-> Lagerbock
KIPP_FREIRAUM   = 5.0     # Luft zwischen Schellenunterkante und Kragen

SEGMENTE        = 96      # Aufloesung runder Konturen


def abgeleitet():
    """Alle Folgemasse aus den Parametern."""
    g = {}
    g["schelle_innen_r"] = (ROHR_D + ROHR_SPIEL) / 2.0
    g["schelle_aussen_r"] = g["schelle_innen_r"] + SCHELLE_WAND
    # Gabelweite: Schelle + beidseitig Lagerbock + Luft
    g["arm_innen_y"] = g["schelle_aussen_r"] + BOSS_LAENGE + ARM_BOSS_LUFT
    g["arm_aussen_y"] = g["arm_innen_y"] + ARM_DICKE
    # Drehachse so hoch, dass die Schelle den Kragen frei ueberschwenkt
    g["pivot_z"] = SCHEIBE_H + KRAGEN_H + KIPP_FREIRAUM + g["schelle_aussen_r"]
    g["scheibe_r"] = math.hypot(ARM_BREITE / 2.0, g["arm_aussen_y"]) + 2.0
    g["achse_len"] = ARM_DICKE + ARM_BOSS_LUFT + BOSS_LAENGE + 0.5
    g["pfosten_h"] = SCHEIBE_H + KRAGEN_H - 1.0    # 1 mm Luft am Grund
    return g


# ---------------------------------------------------------------------------
# 2D- und Mesh-Grundlagen
# ---------------------------------------------------------------------------

def pol(w, r, cx=0.0, cy=0.0):
    return (cx + r * math.cos(w), cy + r * math.sin(w))


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


def triangulieren(poly):
    """Ear-Clipping fuer einfache (lochfreie) Polygone."""
    idx = list(range(len(poly)))
    if flaeche_signiert(poly) < 0:
        idx.reverse()
    out = []
    schutz = 0
    while len(idx) > 3 and schutz < 30 * len(poly):
        schutz += 1
        n = len(idx)
        ok = False
        for i in range(n):
            ia, ib, ic = idx[(i - 1) % n], idx[i], idx[(i + 1) % n]
            a, b, c = poly[ia], poly[ib], poly[ic]
            if _kreuz(a, b, c) <= 1e-9:
                continue
            if any(_in_dreieck(poly[j], a, b, c)
                   for j in idx if j not in (ia, ib, ic)):
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


def prisma(poly, z0, z1):
    """Einfaches Polygon -> geschlossenes Prisma entlang Z."""
    if flaeche_signiert(poly) < 0:
        poly = poly[::-1]
    n = len(poly)
    t = []
    for (a, b, c) in triangulieren(poly):
        pa, pb, pc = poly[a], poly[b], poly[c]
        t.append(((pa[0], pa[1], z0), (pc[0], pc[1], z0), (pb[0], pb[1], z0)))
        t.append(((pa[0], pa[1], z1), (pb[0], pb[1], z1), (pc[0], pc[1], z1)))
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        t.append(((x1, y1, z0), (x2, y2, z0), (x2, y2, z1)))
        t.append(((x1, y1, z0), (x2, y2, z1), (x1, y1, z1)))
    return t


def loch_prisma(aussen, innen, z0, z1):
    """Prisma mit einem Loch. aussen/innen: gleiche Punktzahl, gleiche
    Umlaufrichtung, punktweise radial korrespondierend (beide star-shaped
    um dasselbe Zentrum). Deckel/Boden entstehen als Streifen dazwischen."""
    if flaeche_signiert(aussen) < 0:
        aussen = aussen[::-1]
    if flaeche_signiert(innen) < 0:
        innen = innen[::-1]
    n = len(aussen)
    assert len(innen) == n
    t = []
    for i in range(n):
        j = (i + 1) % n
        ao, bo, ai, bi = aussen[i], aussen[j], innen[i], innen[j]
        # Boden
        t.append(((ao[0], ao[1], z0), (ai[0], ai[1], z0), (bi[0], bi[1], z0)))
        t.append(((ao[0], ao[1], z0), (bi[0], bi[1], z0), (bo[0], bo[1], z0)))
        # Deckel
        t.append(((ao[0], ao[1], z1), (bo[0], bo[1], z1), (bi[0], bi[1], z1)))
        t.append(((ao[0], ao[1], z1), (bi[0], bi[1], z1), (ai[0], ai[1], z1)))
        # Aussenmantel
        t.append(((ao[0], ao[1], z0), (bo[0], bo[1], z0), (bo[0], bo[1], z1)))
        t.append(((ao[0], ao[1], z0), (bo[0], bo[1], z1), (ao[0], ao[1], z1)))
        # Innenmantel
        t.append(((ai[0], ai[1], z0), (ai[0], ai[1], z1), (bi[0], bi[1], z1)))
        t.append(((ai[0], ai[1], z0), (bi[0], bi[1], z1), (bi[0], bi[1], z0)))
    return t


def kegelstumpf(cx, cy, r0, r1, z0, z1, seg=SEGMENTE):
    """Zylinder bzw. Kegelstumpf entlang Z (fuer Pfosten und Achsstift)."""
    unten = [pol(2 * math.pi * i / seg, r0, cx, cy) for i in range(seg)]
    oben = [pol(2 * math.pi * i / seg, r1, cx, cy) for i in range(seg)]
    t = []
    for (a, b, c) in triangulieren(unten):
        pa, pb, pc = unten[a], unten[b], unten[c]
        t.append(((pa[0], pa[1], z0), (pc[0], pc[1], z0), (pb[0], pb[1], z0)))
    for (a, b, c) in triangulieren(oben):
        pa, pb, pc = oben[a], oben[b], oben[c]
        t.append(((pa[0], pa[1], z1), (pb[0], pb[1], z1), (pc[0], pc[1], z1)))
    for i in range(seg):
        j = (i + 1) % seg
        a = (unten[i][0], unten[i][1], z0)
        b = (unten[j][0], unten[j][1], z0)
        c = (oben[j][0], oben[j][1], z1)
        d = (oben[i][0], oben[i][1], z1)
        t.append((a, b, c))
        t.append((a, c, d))
    return t


def verschieben(t, dx=0.0, dy=0.0, dz=0.0):
    return [tuple((x + dx, y + dy, z + dz) for (x, y, z) in tri) for tri in t]


def dreh_x90(t):
    """+90 Grad um die X-Achse: Z-Extrusion wird zur Y-Extrusion."""
    return [tuple((x, -z, y) for (x, y, z) in tri) for tri in t]


def dreh_y90(t):
    """+90 Grad um die Y-Achse: Z-Extrusion wird zur X-Extrusion."""
    return [tuple((z, y, -x) for (x, y, z) in tri) for tri in t]


def offene_kanten(t):
    z = {}
    for (a, b, c) in t:
        for p, q in ((a, b), (b, c), (c, a)):
            kp = tuple(round(w, 5) for w in p)
            kq = tuple(round(w, 5) for w in q)
            s = (kp, kq) if kp < kq else (kq, kp)
            z[s] = z.get(s, 0) + 1
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
        f.write(("Fernrohrhalter - " + name).encode("ascii", "replace")
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
# Sonderkonturen
# ---------------------------------------------------------------------------

def kreis(r, cx=0.0, cy=0.0, seg=SEGMENTE):
    return [pol(2 * math.pi * i / seg, r, cx, cy) for i in range(seg)]


def raute(halbe_diagonale, seg=SEGMENTE):
    """Raute (45-Grad-Quadrat) als Polarkontur -- druckbar ohne Stuetzen,
    weil Ober- und Unterseite unter 45 Grad laufen."""
    pts = []
    for i in range(seg):
        w = 2 * math.pi * i / seg
        r = halbe_diagonale / (abs(math.cos(w)) + abs(math.sin(w)))
        pts.append(pol(w, r))
    return pts


def tropfen(r, seg=SEGMENTE):
    """Tropfenkontur: Kreis mit 45-Grad-Spitze oben. Als liegende Bohrung
    ohne Stuetzen druckbar, weil die Decke keine Rundung hat."""
    apex = r / math.sin(math.pi / 4.0)          # Spitze bei (0, r*sqrt2)
    pts = []
    for i in range(seg):
        w = 2 * math.pi * i / seg
        grad = math.degrees(w) % 360.0
        if 45.0 <= grad <= 135.0:
            # Ersatz der Kreisdecke durch zwei Geraden zur Spitze
            if grad <= 90.0:
                t = (grad - 45.0) / 45.0
                a = pol(math.radians(45.0), r)
                b = (0.0, apex)
            else:
                t = (grad - 90.0) / 45.0
                a = (0.0, apex)
                b = pol(math.radians(135.0), r)
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        else:
            pts.append(pol(w, r))
    return pts


def stadion_um_loch(breite, fuss_z, seg=SEGMENTE):
    """Gabelarm-Silhouette: Rechteck mit halbrundem Kopf, Zentrum im
    Bohrungsmittelpunkt (0, 0). fuss_z ist negativ (Unterkante).
    Star-shaped um den Ursprung -> radial paarbar mit der Bohrung."""
    hb = breite / 2.0
    pts = []
    for i in range(seg):
        w = 2 * math.pi * i / seg
        dx, dz = math.cos(w), math.sin(w)
        if dz >= 0:
            r = hb                                   # halbrunder Kopf
        else:
            kand = [abs(fuss_z) / -dz] if dz < 0 else []
            if abs(dx) > 1e-9:
                kand.append(hb / abs(dx))
            r = min(kand)
        pts.append((r * dx, r * dz))
    return pts


def platte_kontur():
    """Grundplatte: abgerundetes Quadrat mit 4 offenen Schraubschlitzen
    in den Kantenmitten. Ein einziges einfaches Polygon."""
    h = PLATTE / 2.0
    r = ECKRADIUS
    sb = SCHLITZ_B / 2.0
    st = SCHLITZ_T
    seite = []                                       # rechte Kante, y steigend
    seite.append((h, -(h - r)))
    seite.append((h, -sb))
    seite.append((h - st, -sb))                      # Schlitz hinein
    seite.append((h - st, sb))
    seite.append((h, sb))                            # und wieder heraus
    seite.append((h, h - r))
    for i in range(1, 9):                            # Eckenrundung
        w = math.radians(i * 10.0)
        seite.append((h - r + r * math.cos(w), h - r + r * math.sin(w)))
    pts = []
    for k in range(4):                               # 4x um 90 Grad drehen
        cw = math.cos(math.pi / 2 * k)
        sw = math.sin(math.pi / 2 * k)
        pts.extend((x * cw - y * sw, x * sw + y * cw) for (x, y) in seite)
    return pts


def c_schelle_kontur(g):
    """C-foermige Schelle als ein einfaches Polygon (Ring mit Sektorluecke).

    Die Oeffnung zeigt nach +X -- um 90 Grad versetzt zu den Lagerboecken
    auf der Y-Achse, sonst saesse ein Bock mitten in der Luecke. Im
    zusammengebauten Zustand zeigt die Oeffnung nach oben: das Fernrohr
    wird von oben eingeschnappt."""
    ri, ra = g["schelle_innen_r"], g["schelle_aussen_r"]
    halb = math.radians(SCHELLE_OEFFNUNG / 2.0)
    w0, w1 = halb, 2 * math.pi - halb
    n = SEGMENTE
    pts = [pol(w0 + (w1 - w0) * i / n, ra) for i in range(n + 1)]
    pts += [pol(w1 - (w1 - w0) * i / n, ri) for i in range(n + 1)]
    return pts


# ---------------------------------------------------------------------------
# Bauteile
# ---------------------------------------------------------------------------

def teil_grundplatte(g):
    schalen = [prisma(platte_kontur(), 0.0, PLATTE_H)]
    schalen.append(kegelstumpf(0, 0, PFOSTEN_D / 2, PFOSTEN_D / 2,
                               PLATTE_H - 1.0, PLATTE_H + g["pfosten_h"]))
    # Einfuehrfase am Pfostenkopf
    schalen.append(kegelstumpf(0, 0, PFOSTEN_D / 2, PFOSTEN_D / 2 - 1.5,
                               PLATTE_H + g["pfosten_h"] - 0.01,
                               PLATTE_H + g["pfosten_h"] + 2.0))
    return schalen


def teil_drehgabel(g):
    loch_r = (PFOSTEN_D + HUELSE_SPIEL) / 2.0
    schalen = []
    # Bodenscheibe mit Pfostenbohrung
    schalen.append(loch_prisma(kreis(g["scheibe_r"]), kreis(loch_r),
                               0.0, SCHEIBE_H))
    # Kragen (fuehrt den Pfosten, verhindert Wackeln)
    schalen.append(loch_prisma(kreis(KRAGEN_D / 2.0), kreis(loch_r),
                               SCHEIBE_H - 1.0, SCHEIBE_H + KRAGEN_H))
    # Zwei Gabelarme mit Lagerbohrung, Silhouette in XZ, Dicke entlang Y
    fuss_z = SCHEIBE_H - 1.0
    sil_aussen = stadion_um_loch(ARM_BREITE, fuss_z - g["pivot_z"])
    sil_loch = kreis(LOCH_ARM / 2.0)
    for seite in (-1.0, +1.0):
        arm = loch_prisma(sil_aussen, sil_loch, 0.0, ARM_DICKE)
        arm = dreh_x90(arm)                          # Dicke jetzt entlang Y
        y0 = seite * g["arm_innen_y"]
        if seite > 0:
            arm = verschieben(arm, 0, y0 + ARM_DICKE, g["pivot_z"])
        else:
            arm = verschieben(arm, 0, y0, g["pivot_z"])
        schalen.append(arm)
    return schalen


def teil_rohrschelle(g):
    schalen = [prisma(c_schelle_kontur(g), 0.0, SCHELLE_LAENGE)]
    # Lagerboecke: Raute aussen, Tropfenbohrung innen, Achse entlang Y.
    # Gedruckt wird die Schelle mit Rohrachse senkrecht; die Tropfenspitze
    # zeigt dann nach oben (+Z im Bauteil), die Raute traegt sich selbst.
    mitte_z = SCHELLE_LAENGE / 2.0
    aussen = raute(BOSS_BREITE / 2.0)
    innen = tropfen(LOCH_BOSS / 2.0)
    for seite in (-1.0, +1.0):
        # Bohrung entlang Y: Silhouette in XZ zeichnen, dann kippen.
        # dreh_x90 legt das Z-Intervall [0, L] auf Y = [-L, 0]; der Bock
        # soll aussen bei schelle_aussen_r + BOSS_LAENGE enden und 2 mm
        # in die Schelenwand hineinragen.
        boss = loch_prisma(aussen, innen, 0.0, BOSS_LAENGE + 2.0)
        boss = dreh_x90(boss)                        # Achse entlang Y
        aussen_y = seite * (g["schelle_aussen_r"] + BOSS_LAENGE)
        if seite > 0:
            boss = verschieben(boss, 0, aussen_y, mitte_z)
        else:
            boss = verschieben(boss, 0, aussen_y + (BOSS_LAENGE + 2.0), mitte_z)
        schalen.append(boss)
    return schalen


def teil_achsstift(g):
    schalen = [kegelstumpf(0, 0, ACHSE_KOPF_D / 2, ACHSE_KOPF_D / 2,
                           0.0, ACHSE_KOPF_H)]
    schaft_l = g["achse_len"]
    schalen.append(kegelstumpf(0, 0, ACHSE_D / 2, ACHSE_D / 2,
                               ACHSE_KOPF_H - 1.0,
                               ACHSE_KOPF_H + schaft_l - 1.5))
    # Einfuehrfase an der Spitze
    schalen.append(kegelstumpf(0, 0, ACHSE_D / 2, ACHSE_D / 2 - 1.2,
                               ACHSE_KOPF_H + schaft_l - 1.51,
                               ACHSE_KOPF_H + schaft_l))
    return schalen


# ---------------------------------------------------------------------------

def bauen_und_schreiben(ziel, name, schalen):
    fehler = 0
    alle = []
    for s in schalen:
        fehler += offene_kanten(s)
        alle.extend(s)
    pfad = os.path.join(ziel, name)
    stl_schreiben(pfad, alle, name)
    vol = sum(volumen(s) for s in schalen)           # Ueberlappung: leicht zu hoch
    print("%-44s %2d Schalen %6d Dreiecke  ~%6.1f cm3  offene Kanten: %d"
          % (name, len(schalen), len(alle), vol / 1000.0, fehler))
    return fehler


def main():
    import argparse
    global ROHR_D
    parser = argparse.ArgumentParser(description="Fernrohrhalter-Generator")
    parser.add_argument("--rohr", type=float, default=None,
                        help="Aussendurchmesser des Fernrohrs in mm "
                             "(Standard %.0f)" % ROHR_D)
    args = parser.parse_args()
    if args.rohr:
        ROHR_D = float(args.rohr)

    g = abgeleitet()
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    os.makedirs(ziel, exist_ok=True)

    print("Fernrohr-Durchmesser %.1f mm -> Schelle innen %.1f / aussen %.1f mm"
          % (ROHR_D, 2 * g["schelle_innen_r"], 2 * g["schelle_aussen_r"]))
    print("Gabelweite innen %.1f mm, Drehachse %.1f mm ueber der Scheibe\n"
          % (2 * g["arm_innen_y"], g["pivot_z"]))

    fehler = 0
    fehler += bauen_und_schreiben(ziel, "fernrohrhalter_1_grundplatte_1x_drucken.stl",
                                  teil_grundplatte(g))
    fehler += bauen_und_schreiben(ziel, "fernrohrhalter_2_drehgabel_1x_drucken.stl",
                                  teil_drehgabel(g))
    fehler += bauen_und_schreiben(ziel, "fernrohrhalter_3_rohrschelle_1x_drucken.stl",
                                  teil_rohrschelle(g))
    fehler += bauen_und_schreiben(ziel, "fernrohrhalter_4_achsstift_2x_drucken.stl",
                                  teil_achsstift(g))

    if fehler:
        raise SystemExit("FEHLER: %d offene Kanten" % fehler)
    print("\nAlle Schalen wasserdicht. Dateinamen sagen die Stueckzahl.")


if __name__ == "__main__":
    main()
