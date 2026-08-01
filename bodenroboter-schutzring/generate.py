#!/usr/bin/env python3
"""
Auffahrschutz-Ring fuer Saug-/Wischroboter um ein Tischbein.

Der Ring liegt auf dem Boden aussen um den Tischfuss herum. Er ist in
identische Kreissegmente geteilt, die an den Stossstellen eine
hinterschnittene Verzahnung tragen. Die haelt ohne Kleber formschluessig:
je Fuge greifen zwei gegenlaeufige Halb-Schwalbenschwaenze ineinander.
Zusammengebaut wird senkrecht von oben -- das Profil ist ein senkrechtes
Prisma, in dieser Richtung ist die Fuge bewusst offen.

Aufbau des Meshes
-----------------
Das Bauteil wird als Stapel waagerechter Querschnitte beschrieben. Alle
Querschnitte haben exakt dieselbe Punktanzahl und -reihenfolge, nur die
Radien aendern sich mit der Hoehe. Dadurch entsteht das Mesh durch einen
simplen Loft (Dreiecksstreifen zwischen benachbarten Profilen) plus je
einer triangulierten Deckflaeche -- ohne CAD-Booleans und damit garantiert
mannigfaltig und dicht.

Ueber diesen Mechanismus entsteht auch die Verrundung oben, umlaufend an
Aussen- und Innenkante. Die Standflaeche unten bleibt scharfkantig, damit
der Ring plan aufliegt und der Roboter keine Kante zum Auffahren findet.

Alle Masse in Millimetern.
"""

import math
import struct
import os

# ---------------------------------------------------------------------------
# Parameter
# ---------------------------------------------------------------------------

# Der Ring liegt auf dem Boden AUSSEN UM den Moebelfuss herum -- der Roboter
# stoesst also an die Ringwand, bevor er den Fuss ueberhaupt erreicht.
# Massgeblich ist damit der Innendurchmesser: er muss ueber den Fuss passen.
#
# Der Fussdurchmesser kommt per Kommandozeile (--fuss), Standard ist der
# Tischfuss. Alle abgeleiteten Radien setzt konfigurieren() weiter unten.
FUSS_DURCHMESSER   = 365.0   # gemessener Durchmesser des Fusses
LUFT               = 5.0     # Spiel zwischen Fuss und Ring, je Seite
WANDSTAERKE        = 5.0     # Dicke der Wand
HOEHE              = 50.0    # Hoehe der Wand

VERRUNDUNG         = 2.0     # Radius der Rundung an der Oberkante

# Verbindungsklotz an den Stossstellen. Er baut ausschliesslich nach AUSSEN
# auf, damit die Innenflaeche des Rings ein sauberer Zylinder bleibt und die
# volle lichte Weite fuer den Tischfuss erhalten bleibt.
KLOTZ_AUSSEN       = 15.0    # zusaetzliches Material nach aussen
KLOTZ_LAENGE       = 18.0    # volle Klotzbreite ab Stossfuge (Bogenlaenge)
KLOTZ_AUSLAUF      = 14.0    # Laenge der Schraege, mit der der Klotz auslaeuft

# Hinterschnittene Verzahnung an der Stossfuge.
#
# Die Stossflaeche wird radial in ZAHN_BAENDER gleich breite Baender geteilt,
# die abwechselnd vorstehen und zurueckspringen. Am einen Ende stehen die
# geraden Baender vor, am anderen die ungeraden -- dadurch passen zwei
# identische Teile zusammen. Aussen und innen bleibt je eine solide Randzone
# stehen, damit die Kantenverrundung oben nicht in die Verzahnung schneidet.
# Die Zaehne sind hinterschnitten, damit die Fuge ohne Kleber formschluessig
# haelt. Der innerste Zahn spreizt zur Ringmitte hin, der aeusserste nach
# aussen -- die beiden Hinterschnitte laufen also gegeneinander. Ein
# tangentiales Auseinanderziehen muesste den einen Zahn radial nach aussen
# und gleichzeitig den anderen nach innen bewegen, was sich gegenseitig
# sperrt. Senkrecht eingeschoben wird trotzdem, weil das ganze Profil ein
# senkrechtes Prisma bleibt.
ZAHN_BAENDER       = 2       # Anzahl der Baender in der Verzahnungszone
ZAHN_TIEFE         = 12.0    # wie weit ein Zahn ueber die Fuge ragt
ZAHN_HINTERSCHNITT = 1.2     # radiale Spreizung des Zahns zum Ende hin
ZAHN_RANDZONE      = 5.0     # solide Randzone der Stossflaeche, je Seite
ZAHN_GRUNDLUFT     = 0.4     # Luft am Grund der Aussparung
SPIEL              = 0.12    # Passungsspiel je Flanke (Schiebesitz)

BOGEN_SCHRITT_GRAD = 1.0     # Aufloesung der Rundungen in der Draufsicht
VERRUNDUNG_STUFEN  = 8       # Aufloesung der Kantenverrundung in der Hoehe

DRUCKBETT = (350.0, 350.0)   # angenommener nutzbarer Bauraum X/Y


# ---------------------------------------------------------------------------
# 2D-Hilfsfunktionen
# ---------------------------------------------------------------------------

def pol(winkel, radius):
    return (radius * math.cos(winkel), radius * math.sin(winkel))


def bogen(punkte, w_von, w_bis, radius, schritte):
    """Diskretisierter Kreisbogen mit fest vorgegebener Schrittzahl.

    Die Schrittzahl wird von aussen vorgegeben (nicht aus dem Radius
    abgeleitet), damit alle Profile eines Bauteils punktweise
    korrespondieren -- Voraussetzung fuer den Loft.
    """
    for i in range(1, schritte + 1):
        punkte.append(pol(w_von + (w_bis - w_von) * i / schritte, radius))


def flaeche_signiert(poly):
    s = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return s / 2.0


def _kreuz(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _punkt_in_dreieck(p, a, b, c):
    d1 = _kreuz(a, b, p)
    d2 = _kreuz(b, c, p)
    d3 = _kreuz(c, a, p)
    neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
    return not (neg and pos)


def triangulieren(poly):
    """Ear-Clipping fuer ein einfaches (lochfreies) Polygon -> Indextripel."""
    idx = list(range(len(poly)))
    if flaeche_signiert(poly) < 0:
        idx.reverse()
        gedreht = True
    else:
        gedreht = False
    dreiecke = []
    grenze = 20 * len(poly)
    schutz = 0
    while len(idx) > 3 and schutz < grenze:
        schutz += 1
        n = len(idx)
        gefunden = False
        for i in range(n):
            ia, ib, ic = idx[(i - 1) % n], idx[i], idx[(i + 1) % n]
            a, b, c = poly[ia], poly[ib], poly[ic]
            if _kreuz(a, b, c) <= 1e-9:
                continue                       # konkav oder entartet
            frei = True
            for j in idx:
                if j in (ia, ib, ic):
                    continue
                if _punkt_in_dreieck(poly[j], a, b, c):
                    frei = False
                    break
            if frei:
                dreiecke.append((ia, ib, ic))
                del idx[i]
                gefunden = True
                break
        if not gefunden:
            raise RuntimeError("Triangulierung steckengeblieben")
    if len(idx) == 3:
        dreiecke.append(tuple(idx))
    if gedreht:                                 # Indizes beziehen sich auf poly
        dreiecke = [(a, b, c) for (a, b, c) in dreiecke]
    return dreiecke


# ---------------------------------------------------------------------------
# Querschnitt eines Segments
# ---------------------------------------------------------------------------

def konfigurieren(fuss=None, luft=None):
    """Setzt den Fussdurchmesser und rechnet alle abgeleiteten Radien neu.

    Beim Import laeuft das einmal mit den Standardwerten; main() ruft es
    erneut auf, wenn --fuss/--luft uebergeben wurden. Alle Profilfunktionen
    lesen die Modul-Globals zur Laufzeit, deshalb genuegt das Umsetzen hier.

    Die Grenzen der Verzahnungszone sind bewusst feste Radien und NICHT vom
    Einzug der Kantenverrundung abgeleitet: die Verzahnung muss ueber die
    ganze Hoehe identisch bleiben, sonst passen die Segmente oben nicht mehr.
    """
    global FUSS_DURCHMESSER, LUFT, INNEN_DURCHMESSER, AUSSEN_DURCHMESSER
    global R_AUSSEN, R_INNEN, R_KLOTZ, R_BOGEN
    global R_ZONE_INNEN, R_ZONE_AUSSEN, ZAHN_BANDBREITE

    if fuss is not None:
        FUSS_DURCHMESSER = float(fuss)
    if luft is not None:
        LUFT = float(luft)

    INNEN_DURCHMESSER = FUSS_DURCHMESSER + 2 * LUFT
    AUSSEN_DURCHMESSER = INNEN_DURCHMESSER + 2 * WANDSTAERKE

    R_AUSSEN = AUSSEN_DURCHMESSER / 2.0
    R_INNEN = R_AUSSEN - WANDSTAERKE
    R_KLOTZ = R_AUSSEN + KLOTZ_AUSSEN
    R_BOGEN = (R_AUSSEN + R_INNEN) / 2.0        # Referenz fuer Bogenlaengen

    R_ZONE_INNEN = R_INNEN + ZAHN_RANDZONE
    R_ZONE_AUSSEN = R_KLOTZ - ZAHN_RANDZONE
    ZAHN_BANDBREITE = (R_ZONE_AUSSEN - R_ZONE_INNEN) / ZAHN_BAENDER


konfigurieren()


def _band(k):
    """Radiale Grenzen (innen, aussen) des k-ten Bandes der Verzahnung."""
    return (R_ZONE_INNEN + k * ZAHN_BANDBREITE,
            R_ZONE_INNEN + (k + 1) * ZAHN_BANDBREITE)


def _hinterschnitt(k):
    """Richtung, in die sich Band k zum Zahnende hin aufweitet.

    -1 = zur Ringmitte, +1 = nach aussen, 0 = gerade. Nur die beiden
    aeusseren Baender werden hinterschnitten; sie weiten sich in die
    solide Randzone hinein auf, nicht in das Nachbarband. Andernfalls
    wuerde die Aussparung des einen Bandes den Zahnfuss des anderen
    wegschneiden.
    """
    if k == 0:
        return -1.0
    if k == ZAHN_BAENDER - 1:
        return 1.0
    return 0.0


def _zahn_radien(k):
    """(Fuss innen, Fuss aussen, Ende innen, Ende aussen) eines Zahns."""
    lo, hi = _band(k)
    ri = _hinterschnitt(k)
    fuss_lo, fuss_hi = lo + SPIEL, hi - SPIEL
    ende_lo = fuss_lo - (ZAHN_HINTERSCHNITT if ri < 0 else 0.0)
    ende_hi = fuss_hi + (ZAHN_HINTERSCHNITT if ri > 0 else 0.0)
    return fuss_lo, fuss_hi, ende_lo, ende_hi


def _nut_radien(k):
    """(Mund innen, Mund aussen, Grund innen, Grund aussen) einer Aussparung."""
    lo, hi = _band(k)
    ri = _hinterschnitt(k)
    grund_lo = lo - (ZAHN_HINTERSCHNITT if ri < 0 else 0.0)
    grund_hi = hi + (ZAHN_HINTERSCHNITT if ri > 0 else 0.0)
    return lo, hi, grund_lo, grund_hi


def _bogen_schritte(w_spanne):
    return max(1, int(math.ceil(abs(w_spanne) / math.radians(BOGEN_SCHRITT_GRAD))))


def segment_profil(anzahl_segmente, einzug=0.0):
    """Waagerechter Querschnitt eines Segments als geschlossenes Polygon.

    einzug -- radiales Zuruecksetzen der Aussenhaut (Kantenverrundung).
              Aussen- und Klotzradius wandern nach innen, der Innenradius
              nach aussen. Die Stossflaechen und die gesamte Verzahnung
              bleiben davon unberuehrt, sonst wuerden die Haelften oben
              nicht mehr passen.

    Am Ende phi stehen die geraden Baender der Verzahnung vor, am Anfang 0
    die ungeraden. Dadurch passen zwei identische Teile zusammen.
    """
    r_aussen = R_AUSSEN - einzug
    r_innen = R_INNEN + einzug
    r_klotz = R_KLOTZ - einzug

    phi = 2.0 * math.pi / anzahl_segmente

    # Bogenlaengen -> Winkel (durchgaengig ueber denselben Referenzradius,
    # damit Zahn und Aussparung exakt zueinander passen)
    a_klotz = KLOTZ_LAENGE / R_BOGEN
    a_auslauf = (KLOTZ_LAENGE + KLOTZ_AUSLAUF) / R_BOGEN
    a_zahn = ZAHN_TIEFE / R_BOGEN
    a_nut = (ZAHN_TIEFE + ZAHN_GRUNDLUFT) / R_BOGEN

    s_klotz = _bogen_schritte(a_klotz)
    s_wand = _bogen_schritte(phi - 2 * a_auslauf)

    p = []

    # --- Aussenkontur, Winkel steigend von 0 nach phi ----------------------
    p.append(pol(0.0, r_klotz))
    bogen(p, 0.0, a_klotz, r_klotz, s_klotz)
    p.append(pol(a_auslauf, r_aussen))                    # Auslaufschraege
    bogen(p, a_auslauf, phi - a_auslauf, r_aussen, s_wand)
    p.append(pol(phi - a_klotz, r_klotz))                 # Auslaufschraege
    bogen(p, phi - a_klotz, phi, r_klotz, s_klotz)

    # --- Stossflaeche am Ende phi, von aussen nach innen -------------------
    # Zaehne ragen nach +phi in den Nachbarn hinein, Aussparungen nach -phi.
    p.append(pol(phi, R_ZONE_AUSSEN))                     # solide Randzone
    for k in range(ZAHN_BAENDER - 1, -1, -1):
        lo, hi = _band(k)
        if k % 2 == 0:                                    # Zahn
            fuss_lo, fuss_hi, ende_lo, ende_hi = _zahn_radien(k)
            p.append(pol(phi, fuss_hi))
            p.append(pol(phi + a_zahn, ende_hi))
            p.append(pol(phi + a_zahn, ende_lo))
            p.append(pol(phi, fuss_lo))
            p.append(pol(phi, lo))
        else:                                             # Aussparung
            _, _, grund_lo, grund_hi = _nut_radien(k)
            p.append(pol(phi - a_nut, grund_hi))
            p.append(pol(phi - a_nut, grund_lo))
            p.append(pol(phi, lo))
    p.append(pol(phi, r_innen))                           # solide Randzone

    # --- Innenkontur, Winkel fallend von phi nach 0 ------------------------
    bogen(p, phi, phi - a_klotz, r_innen, s_klotz)
    p.append(pol(phi - a_auslauf, r_innen))
    bogen(p, phi - a_auslauf, a_auslauf, r_innen, s_wand)
    p.append(pol(a_klotz, r_innen))
    bogen(p, a_klotz, 0.0, r_innen, s_klotz)

    # --- Stossflaeche am Anfang 0, von innen nach aussen -------------------
    # Hier ist das Muster genau umgekehrt: ungerade Baender ragen vor.
    p.append(pol(0.0, R_ZONE_INNEN))                      # solide Randzone
    for k in range(ZAHN_BAENDER):
        lo, hi = _band(k)
        if k % 2 == 1:                                    # Zahn
            fuss_lo, fuss_hi, ende_lo, ende_hi = _zahn_radien(k)
            p.append(pol(0.0, fuss_lo))
            p.append(pol(-a_zahn, ende_lo))
            p.append(pol(-a_zahn, ende_hi))
            p.append(pol(0.0, fuss_hi))
            p.append(pol(0.0, hi))
        else:                                             # Aussparung
            _, _, grund_lo, grund_hi = _nut_radien(k)
            p.append(pol(a_nut, grund_lo))
            p.append(pol(a_nut, grund_hi))
            p.append(pol(0.0, hi))
    # Der Umlauf schliesst sich ueber p[0] = (0, r_klotz). Dieser Punkt darf
    # hier nicht erneut angehaengt werden, sonst entsteht eine Kante der
    # Laenge 0 und das Ear-Clipping findet kein Ohr mehr.

    return p


def ring_profil(d_aussen, einzug=0.0):
    """Querschnitt des ungeteilten Rings: Aussen- und Innenkreis.

    Der einteilige Ring braucht keine Verbindungsklotze, ist also ein
    schlichter Kreisring. Der Durchmesser wird hier explizit uebergeben,
    weil der einteilige Ring auf den Bauraum heruntergerechnet werden muss.
    """
    r_a = d_aussen / 2.0
    r_i = r_a - WANDSTAERKE
    n = int(round(360.0 / BOGEN_SCHRITT_GRAD))
    aussen = [pol(2 * math.pi * i / n, r_a - einzug) for i in range(n)]
    innen = [pol(2 * math.pi * i / n, r_i + einzug) for i in range(n)]
    return aussen, innen


# ---------------------------------------------------------------------------
# Hoehenprofil: welche Querschnitte liegen auf welcher Hoehe
# ---------------------------------------------------------------------------

def hoehen_stufen():
    """Liste (z, einzug) von unten nach oben.

    Die Verzahnung wird waagerecht zusammengeschoben und braucht daher
    keine Einfuehrfase am unteren Ende -- das Profil ist ueber die ganze
    Hoehe konstant, bis oben die Kantenverrundung einsetzt.
    """
    # gerader Bereich bis zum Beginn der Kantenverrundung
    stufen = [(0.0, 0.0), (HOEHE - VERRUNDUNG, 0.0)]

    # Viertelkreis-Verrundung an der Oberkante
    for i in range(1, VERRUNDUNG_STUFEN + 1):
        t = i / VERRUNDUNG_STUFEN
        winkel = math.pi / 2.0 * t
        z = HOEHE - VERRUNDUNG + VERRUNDUNG * math.sin(winkel)
        einzug = VERRUNDUNG * (1.0 - math.cos(winkel))
        stufen.append((z, einzug))

    return stufen


# ---------------------------------------------------------------------------
# Querschnitt-Stapel -> Mesh
# ---------------------------------------------------------------------------

def loften(profile, hoehen):
    """Profile gleicher Punktzahl zu einem geschlossenen Mesh verbinden."""
    n = len(profile[0])
    for p in profile:
        assert len(p) == n, "Profile muessen punktweise korrespondieren"

    dreiecke = []

    # Boden (Normale nach unten)
    unten = profile[0]
    for (a, b, c) in triangulieren(unten):
        pa, pb, pc = unten[a], unten[b], unten[c]
        dreiecke.append(((pa[0], pa[1], hoehen[0]),
                         (pc[0], pc[1], hoehen[0]),
                         (pb[0], pb[1], hoehen[0])))

    # Deckel (Normale nach oben)
    oben = profile[-1]
    for (a, b, c) in triangulieren(oben):
        pa, pb, pc = oben[a], oben[b], oben[c]
        dreiecke.append(((pa[0], pa[1], hoehen[-1]),
                         (pb[0], pb[1], hoehen[-1]),
                         (pc[0], pc[1], hoehen[-1])))

    # Mantel
    for k in range(len(profile) - 1):
        pu, po = profile[k], profile[k + 1]
        zu, zo = hoehen[k], hoehen[k + 1]
        if abs(zo - zu) < 1e-12:
            continue
        for i in range(n):
            j = (i + 1) % n
            a = (pu[i][0], pu[i][1], zu)
            b = (pu[j][0], pu[j][1], zu)
            c = (po[j][0], po[j][1], zo)
            d = (po[i][0], po[i][1], zo)
            dreiecke.append((a, b, c))
            dreiecke.append((a, c, d))

    return dreiecke


def segment_mesh(anzahl_segmente):
    stufen = hoehen_stufen()
    profile = [segment_profil(anzahl_segmente, einzug) for (_, einzug) in stufen]
    hoehen = [z for (z, _) in stufen]
    return loften(profile, hoehen)


def ring_mesh(d_aussen):
    """Ungeteilter Ring mit derselben Oberkanten-Verrundung."""
    entpackt = hoehen_stufen()

    dreiecke = []
    profile = [ring_profil(d_aussen, e) for (_, e) in entpackt]
    hoehen = [z for (z, _) in entpackt]
    n = len(profile[0][0])

    # Boden
    a0, i0 = profile[0]
    for i in range(n):
        j = (i + 1) % n
        ao, bo, ai, bi = a0[i], a0[j], i0[i], i0[j]
        dreiecke.append(((ao[0], ao[1], 0.0), (ai[0], ai[1], 0.0), (bi[0], bi[1], 0.0)))
        dreiecke.append(((ao[0], ao[1], 0.0), (bi[0], bi[1], 0.0), (bo[0], bo[1], 0.0)))
    # Deckel
    aT, iT = profile[-1]
    zT = hoehen[-1]
    for i in range(n):
        j = (i + 1) % n
        ao, bo, ai, bi = aT[i], aT[j], iT[i], iT[j]
        dreiecke.append(((ao[0], ao[1], zT), (bo[0], bo[1], zT), (bi[0], bi[1], zT)))
        dreiecke.append(((ao[0], ao[1], zT), (bi[0], bi[1], zT), (ai[0], ai[1], zT)))
    # Mantel
    for k in range(len(profile) - 1):
        (au, iu), (ao_, io_) = profile[k], profile[k + 1]
        zu, zo = hoehen[k], hoehen[k + 1]
        for i in range(n):
            j = (i + 1) % n
            # aussen
            a = (au[i][0], au[i][1], zu)
            b = (au[j][0], au[j][1], zu)
            c = (ao_[j][0], ao_[j][1], zo)
            d = (ao_[i][0], ao_[i][1], zo)
            dreiecke.append((a, b, c))
            dreiecke.append((a, c, d))
            # innen (umgekehrter Umlauf)
            a = (iu[i][0], iu[i][1], zu)
            b = (iu[j][0], iu[j][1], zu)
            c = (io_[j][0], io_[j][1], zo)
            d = (io_[i][0], io_[i][1], zo)
            dreiecke.append((a, c, b))
            dreiecke.append((a, d, c))

    return dreiecke


# ---------------------------------------------------------------------------
# STL-Ausgabe und Pruefungen
# ---------------------------------------------------------------------------

def stl_schreiben(pfad, dreiecke, name="schutzring"):
    with open(pfad, "wb") as f:
        kopf = ("Auffahrschutz-Ring - " + name).encode("ascii", "replace")
        f.write(kopf.ljust(80, b" ")[:80])
        f.write(struct.pack("<I", len(dreiecke)))
        for (a, b, c) in dreiecke:
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz = ux * vy - uy * vx
            laenge = math.sqrt(nx * nx + ny * ny + nz * nz)
            if laenge > 1e-12:
                nx, ny, nz = nx / laenge, ny / laenge, nz / laenge
            else:
                nx = ny = nz = 0.0
            f.write(struct.pack("<12fH", nx, ny, nz,
                                a[0], a[1], a[2], b[0], b[1], b[2],
                                c[0], c[1], c[2], 0))


def volumen(dreiecke):
    v = 0.0
    for (a, b, c) in dreiecke:
        v += (a[0] * (b[1] * c[2] - c[1] * b[2])
              - a[1] * (b[0] * c[2] - c[0] * b[2])
              + a[2] * (b[0] * c[1] - c[0] * b[1])) / 6.0
    return abs(v)


def offene_kanten(dreiecke):
    """Jede Kante muss genau zweimal auftreten -- sonst ist das Mesh offen."""
    zaehler = {}
    for (a, b, c) in dreiecke:
        for p, q in ((a, b), (b, c), (c, a)):
            kp = tuple(round(w, 5) for w in p)
            kq = tuple(round(w, 5) for w in q)
            s = (kp, kq) if kp < kq else (kq, kp)
            zaehler[s] = zaehler.get(s, 0) + 1
    return sum(1 for n in zaehler.values() if n != 2)


def _punkt_in_polygon(p, poly):
    """Ray-Casting: liegt p innerhalb von poly?"""
    x, y = p
    drin = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xs = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xs > x:
                drin = not drin
    return drin


def _abstand_zu_rand(p, poly):
    """Kuerzester Abstand von p zum Polygonrand."""
    x, y = p
    best = float("inf")
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0.0 else max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / L2))
        best = min(best, math.hypot(x - (x1 + t * dx), y - (y1 + t * dy)))
    return best


def passung_pruefen(anzahl_segmente, toleranz=0.01):
    """Prueft, ob zwei benachbarte Segmente kollisionsfrei zusammenpassen.

    Baut die Querschnitte zweier benachbarter Segmente in Einbaulage und
    sucht Punkte, die deutlich im jeweils anderen Teil liegen. So faellt
    ein falsch herum laufendes Zahnmuster sofort auf und nicht erst nach
    Stunden Druckzeit.

    Rueckgabe: (anzahl_kollisionen, groesste_ueberdeckung_mm)
    """
    phi = 2.0 * math.pi / anzahl_segmente
    cw, sw = math.cos(phi), math.sin(phi)
    a = segment_profil(anzahl_segmente)
    b = [(x * cw - y * sw, x * sw + y * cw) for x, y in a]

    treffer, tiefste = 0, 0.0
    for quelle, ziel in ((a, b), (b, a)):
        for punkt in quelle:
            if _punkt_in_polygon(punkt, ziel):
                tiefe = _abstand_zu_rand(punkt, ziel)
                if tiefe > toleranz:
                    treffer += 1
                    tiefste = max(tiefste, tiefe)
    return treffer, tiefste


def formschluss_pruefen(anzahl_segmente, max_bogen=25.0, schritt=0.1):
    """Prueft, ob die Fuge ohne Kleber formschluessig ist.

    Die Verzahnung ist in Polarkoordinaten aufgebaut, ihre Freigabe-
    bewegung in der Ebene ist deshalb eine DREHUNG um die Ringmitte, keine
    Geradfahrt. Der Test dreht ein Segment aus der Fuge heraus und schaut,
    ob und wann es anschlaegt.

    Gerade Zaehne loesen sich dabei vollstaendig -- sie sperren nur radial
    und braeuchten Kleber. Hinterschnittene Zaehne fangen sich nach kurzem
    Weg, weil die beiden gegenlaeufigen Hinterschnitte sich blockieren.

    Senkrecht laesst sich ein Segment in jedem Fall herausziehen; das ist
    die Montagerichtung und bleibt bewusst offen.

    Rueckgabe: (formschluessig, weg_bis_zum_anschlag_mm)
    """
    phi = 2.0 * math.pi / anzahl_segmente
    a = segment_profil(anzahl_segmente)

    def gedreht(poly, w):
        cw, sw = math.cos(w), math.sin(w)
        return [(x * cw - y * sw, x * sw + y * cw) for x, y in poly]

    b = gedreht(a, phi)
    bogen = schritt
    while bogen <= max_bogen:
        verdreht = gedreht(b, bogen / R_BOGEN)
        for quelle, ziel in ((a, verdreht), (verdreht, a)):
            for punkt in quelle:
                if (_punkt_in_polygon(punkt, ziel)
                        and _abstand_zu_rand(punkt, ziel) > 0.01):
                    return True, bogen
        bogen += schritt
    return False, max_bogen


def bester_bauraum(dreiecke):
    """Guenstigste Platzierung auf dem Druckbett.

    Durchsucht alle Drehwinkel und liefert die Lage mit dem groessten
    Randabstand -- also die robusteste Platzierung, nicht die knappste.
    Ist der Randabstand negativ, passt das Teil in keiner Lage; der Betrag
    zeigt dann, wie viel fehlt.

    Rueckgabe: (passt, bx, by, winkel_grad, rand_mm)
    """
    punkte = sorted(set((round(v[0], 3), round(v[1], 3)) for t in dreiecke for v in t))
    bett_lang, bett_kurz = max(DRUCKBETT), min(DRUCKBETT)

    bestes = None
    for grad10 in range(0, 1800):
        w = math.radians(grad10 / 10.0)
        cw, sw = math.cos(w), math.sin(w)
        xs = [x * cw - y * sw for (x, y) in punkte]
        ys = [x * sw + y * cw for (x, y) in punkte]
        bx, by = max(xs) - min(xs), max(ys) - min(ys)
        lang, kurz = max(bx, by), min(bx, by)
        rand = min(bett_lang - lang, bett_kurz - kurz)
        if bestes is None or rand > bestes[0]:
            bestes = (rand, bx, by, grad10 / 10.0)

    rand, bx, by, winkel = bestes
    return (rand >= 0.0, bx, by, winkel, rand)


# ---------------------------------------------------------------------------
# SVG-Vorschau
# ---------------------------------------------------------------------------

def svg_schreiben(pfad, varianten):
    breite_je = 380.0
    zeilen = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.0f 430" width="%.0f">'
              % (breite_je * len(varianten), 340 * len(varianten)),
              '<rect width="100%" height="100%" fill="#ffffff"/>']
    farben = ["#2f6fb5", "#3f9a55", "#c46a1f", "#8a4fbf"]

    for spalte, n in enumerate(varianten):
        cx = breite_je * spalte + breite_je / 2.0
        cy = 215.0
        s = 0.46                                   # mm -> SVG-Einheiten
        phi = 2.0 * math.pi / n
        zeilen.append('<g transform="translate(%.1f,%.1f) scale(%.4f)">' % (cx, cy, s))
        for k in range(n):
            dreh = k * phi
            poly = segment_profil(n)
            gedreht = [(x * math.cos(dreh) - y * math.sin(dreh),
                        x * math.sin(dreh) + y * math.cos(dreh)) for x, y in poly]
            pts = " ".join("%.2f,%.2f" % (x, y) for x, y in gedreht)
            zeilen.append('<polygon points="%s" fill="%s" fill-opacity="0.8" '
                          'stroke="#111" stroke-width="1.2"/>' % (pts, farben[k % len(farben)]))
        zeilen.append('</g>')
        zeilen.append('<text x="%.1f" y="30" font-family="sans-serif" font-size="17" '
                      'font-weight="600" text-anchor="middle">%d Segmente</text>' % (cx, n))
        zeilen.append('<text x="%.1f" y="410" font-family="sans-serif" font-size="13" '
                      'text-anchor="middle" fill="#444">'
                      'aussen %.0f / innen %.0f / Wand %.0f / Hoehe %.0f mm</text>'
                      % (cx, AUSSEN_DURCHMESSER, AUSSEN_DURCHMESSER - 2 * WANDSTAERKE,
                         WANDSTAERKE, HOEHE))
    zeilen.append('</svg>')
    with open(pfad, "w") as f:
        f.write("\n".join(zeilen))


# ---------------------------------------------------------------------------

def segmentzahlen_waehlen():
    """Sinnvolle Segmentzahlen fuer den aktuellen Ring bestimmen.

    Gesucht wird das kleinste n, dessen Segment auf das Druckbett passt
    (weniger Fugen = steifer und weniger Montage), dazu die naechsten
    beiden als Alternativen. Der Fit wird billig ueber die Sehnenlaenge
    des Klotzkreises vorabgeschaetzt und dann exakt ueber das Mesh
    verifiziert -- die teure Drehwinkelsuche laeuft so nur fuer
    Kandidaten, nicht fuer offensichtlich zu grosse Segmente.
    """
    diagonale = math.hypot(*DRUCKBETT)
    kandidaten = []
    n = 2
    while len(kandidaten) < 3 and n <= 12:
        sehne = 2.0 * R_KLOTZ * math.sin(math.pi / n)
        if sehne < diagonale:                    # grobe Vorauswahl
            passt, _, _, _, _ = bester_bauraum(segment_mesh(n))
            if passt:
                kandidaten.append(n)
        n += 1
    return kandidaten


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="STL-Generator fuer den Auffahrschutz-Ring")
    parser.add_argument("--fuss", type=float, default=None,
                        help="Durchmesser des Moebelfusses in mm "
                             "(Standard: %.0f)" % FUSS_DURCHMESSER)
    parser.add_argument("--luft", type=float, default=None,
                        help="Spiel zwischen Fuss und Ring je Seite in mm "
                             "(Standard: %.0f)" % LUFT)
    parser.add_argument("--segmente", type=str, default=None,
                        help="Kommagetrennte Segmentzahlen, z.B. 5,6,7 "
                             "(Standard: automatisch)")
    args = parser.parse_args()
    konfigurieren(fuss=args.fuss, luft=args.luft)

    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    os.makedirs(ziel, exist_ok=True)

    print("Moebelfuss %.1f mm + %.1f mm Luft je Seite"
          % (FUSS_DURCHMESSER, LUFT))
    print("Ring: innen %.1f / aussen %.1f / Wand %.1f / Hoehe %.1f mm, "
          "Oberkante R%.1f verrundet"
          % (INNEN_DURCHMESSER, AUSSEN_DURCHMESSER, WANDSTAERKE, HOEHE, VERRUNDUNG))
    print("Angenommener Bauraum: %.0f x %.0f mm\n" % DRUCKBETT)

    if args.segmente:
        zahlen = [int(t) for t in args.segmente.split(",")]
    else:
        zahlen = segmentzahlen_waehlen()

    fehler = 0
    for n in zahlen:
        d = segment_mesh(n)
        offen = offene_kanten(d)
        fehler += offen
        name = "schutzring_%dteilig_%.0fmm_segment.stl" % (n, AUSSEN_DURCHMESSER)
        stl_schreiben(os.path.join(ziel, name), d, name)
        passt, bx, by, winkel, rand = bester_bauraum(d)
        kollisionen, tiefe = passung_pruefen(n)
        fehler += kollisionen
        haelt, weg = formschluss_pruefen(n)
        print("%-36s %5d Dr. | %6.1f cm3 je Segment (%dx = %6.1f cm3) | "
              "%5.1f x %5.1f mm, Rand %+6.1f mm -> %-11s | Kanten %s | "
              "Passung %s | Formschluss %s"
              % (name, len(d), volumen(d) / 1000.0, n, n * volumen(d) / 1000.0,
                 bx, by, rand, "passt" if passt else "PASST NICHT",
                 "dicht" if offen == 0 else "OFFEN(%d)" % offen,
                 "ok" if kollisionen == 0 else "KOLLISION %.2f mm" % tiefe,
                 "sperrt nach %.1f mm" % weg if haelt else "FEHLT"))

    # Einteiliger Ring als Referenz fuer einen groesseren Drucker. Ein Kreis
    # braucht seinen Durchmesser in BEIDEN Achsen, massgeblich ist also
    # immer die kuerzere Bettkante.
    print()
    d_aussen = AUSSEN_DURCHMESSER
    d = ring_mesh(d_aussen)
    offen = offene_kanten(d)
    fehler += offen
    name = "schutzring_einteilig_%.0fmm.stl" % d_aussen
    stl_schreiben(os.path.join(ziel, name), d, name)
    passt, bx, by, winkel, rand = bester_bauraum(d)
    print("%-34s %5d Dr. | %6.1f cm3 gesamt, innen %5.1f mm  | "
          "%5.1f x %5.1f mm, Rand %+6.1f mm -> %-11s | offene Kanten %d"
          % (name, len(d), volumen(d) / 1000.0, d_aussen - 2 * WANDSTAERKE,
             bx, by, rand, "passt" if passt else "PASST NICHT", offen))

    svg_schreiben(os.path.join(ziel, "vorschau_%.0fmm.svg" % AUSSEN_DURCHMESSER),
                  zahlen[:2])
    print("\nvorschau_%.0fmm.svg geschrieben" % AUSSEN_DURCHMESSER)

    if fehler:
        raise SystemExit("FEHLER: %d offene Kanten -- Mesh nicht dicht" % fehler)
    print("Alle Meshes sind geschlossen (wasserdicht).")


if __name__ == "__main__":
    main()
