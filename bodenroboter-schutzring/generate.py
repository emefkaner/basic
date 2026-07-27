#!/usr/bin/env python3
"""
Auffahrschutz-Ring fuer Saug-/Wischroboter um ein Tischbein.

Erzeugt STL-Dateien fuer einen runden Schutzwall, der in identische
Kreissegmente geteilt ist. Die Segmente werden mit einer senkrechten
Schwalbenschwanz-Verbindung von oben ineinander geschoben und ergeben
zusammengesteckt einen geschlossenen, in sich steifen Ring.

Aufbau des Meshes
-----------------
Das Bauteil wird als Stapel waagerechter Querschnitte beschrieben. Alle
Querschnitte haben exakt dieselbe Punktanzahl und -reihenfolge, nur die
Radien aendern sich mit der Hoehe. Dadurch entsteht das Mesh durch einen
simplen Loft (Dreiecksstreifen zwischen benachbarten Profilen) plus je
einer triangulierten Deckflaeche -- ohne CAD-Booleans und damit garantiert
mannigfaltig und dicht.

Ueber diesen Mechanismus entstehen auch die beiden Verrundungen:
  * oben umlaufend eine Rundung an Aussen- und Innenkante (Optik)
  * unten eine kleine Einfuehrfase am Schwalbenschwanz-Zapfen (Montage)
Die Standflaeche unten bleibt scharfkantig, damit der Ring plan aufliegt
und der Roboter keine Kante zum Auffahren findet.

Alle Masse in Millimetern.
"""

import math
import struct
import os

# ---------------------------------------------------------------------------
# Parameter
# ---------------------------------------------------------------------------

AUSSEN_DURCHMESSER = 365.0   # Aussendurchmesser des fertigen Rings
WANDSTAERKE        = 5.0     # Dicke der Wand
HOEHE              = 50.0    # Hoehe der Wand

VERRUNDUNG         = 2.0     # Radius der Rundung an der Oberkante

# Verbindungsklotz an den Stossstellen. Er baut ausschliesslich nach AUSSEN
# auf, damit die Innenflaeche des Rings ein sauberer Zylinder bleibt und die
# volle lichte Weite fuer den Tischfuss erhalten bleibt.
KLOTZ_AUSSEN       = 12.0    # zusaetzliches Material nach aussen
KLOTZ_LAENGE       = 18.0    # volle Klotzbreite ab Stossfuge (Bogenlaenge)
KLOTZ_AUSLAUF      = 14.0    # Laenge der Schraege, mit der der Klotz auslaeuft

# Schwalbenschwanz. Der Querschnitt liegt waagerecht, gesteckt wird senkrecht.
SCHWALBE_HALS      = 4.0     # radiale Breite an der Stossfuge (schmal)
SCHWALBE_KOPF      = 6.5     # radiale Breite am Ende (breit -> haelt)
SCHWALBE_TIEFE     = 9.0     # wie weit der Zapfen ueber die Fuge ragt
SPIEL              = 0.25    # Passungsspiel je Flanke (Schiebesitz)
EINFUEHRFASE       = 0.6     # Verjuengung des Zapfens am unteren Ende
EINFUEHRFASE_HOEHE = 1.5     # ueber welche Hoehe die Fase auslaeuft

BOGEN_SCHRITT_GRAD = 1.0     # Aufloesung der Rundungen in der Draufsicht
VERRUNDUNG_STUFEN  = 8       # Aufloesung der Kantenverrundung in der Hoehe

DRUCKBETT = (350.0, 350.0)   # angenommener nutzbarer Bauraum X/Y

# Einteilige Ringe. Ein Kreis braucht seinen Durchmesser in BEIDEN Achsen --
# der massgebliche Wert ist also immer die kuerzere Bettkante. 365 mm passen
# auf kein Bett dieser Groessenordnung, deshalb zusaetzlich die groessten
# Durchmesser, die auf die beiden plausiblen H2S-Bauraeume passen:
#   350 mm Kante - 2 x 7.5 mm Sicherheitsabstand -> 335 mm
#   320 mm Kante - 2 x 7.5 mm Sicherheitsabstand -> 305 mm
# Wer zusaetzlich einen Brim fahren will, rechnet dessen Breite (~5 mm)
# nochmal je Seite ab und geht 10 mm kleiner.
EINTEILIG_DURCHMESSER = (365.0, 335.0, 305.0)


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

R_AUSSEN = AUSSEN_DURCHMESSER / 2.0
R_INNEN = R_AUSSEN - WANDSTAERKE
R_KLOTZ = R_AUSSEN + KLOTZ_AUSSEN
R_SCHWALBE = (R_INNEN + R_KLOTZ) / 2.0          # Mitte des Verbindungsklotzes
R_BOGEN = (R_AUSSEN + R_INNEN) / 2.0            # Referenz fuer Bogenlaengen


def _bogen_schritte(w_spanne):
    return max(1, int(math.ceil(abs(w_spanne) / math.radians(BOGEN_SCHRITT_GRAD))))


def segment_profil(anzahl_segmente, einzug=0.0, zapfen_fase=0.0):
    """Waagerechter Querschnitt eines Segments als geschlossenes Polygon.

    einzug       -- radiales Zuruecksetzen der Aussenhaut (Kantenverrundung).
                    Aussen- und Klotzradius wandern nach innen, der
                    Innenradius nach aussen.
    zapfen_fase  -- radiale Verjuengung des Schwalbenschwanz-Zapfens je
                    Flanke (Einfuehrfase am unteren Ende).

    Winkel 0   -> Schwalbenschwanz-NUT (Aufnahme)
    Winkel phi -> Schwalbenschwanz-ZAPFEN (ragt in den Nachbarn)
    Damit sind alle Segmente eines Rings identisch.

    Die Stossfugen (Winkel 0 und phi) und die gesamte Nut bleiben vom
    Einzug unberuehrt -- sonst wuerden die Segmente oben nicht mehr passen.
    """
    r_aussen = R_AUSSEN - einzug
    r_innen = R_INNEN + einzug
    r_klotz = R_KLOTZ - einzug

    phi = 2.0 * math.pi / anzahl_segmente

    # Bogenlaengen -> Winkel (durchgaengig ueber denselben Referenzradius)
    a_klotz = KLOTZ_LAENGE / R_BOGEN
    a_auslauf = (KLOTZ_LAENGE + KLOTZ_AUSLAUF) / R_BOGEN
    a_zapfen = SCHWALBE_TIEFE / R_BOGEN
    a_nut = (SCHWALBE_TIEFE + 0.5) / R_BOGEN     # 0.5 mm Luft am Nutgrund

    # Radien der Schwalbenschwanz-Flanken
    z_hals_a = R_SCHWALBE + SCHWALBE_HALS / 2.0 - zapfen_fase
    z_hals_i = R_SCHWALBE - SCHWALBE_HALS / 2.0 + zapfen_fase
    z_kopf_a = R_SCHWALBE + SCHWALBE_KOPF / 2.0 - zapfen_fase
    z_kopf_i = R_SCHWALBE - SCHWALBE_KOPF / 2.0 + zapfen_fase

    n_hals_a = R_SCHWALBE + SCHWALBE_HALS / 2.0 + SPIEL
    n_hals_i = R_SCHWALBE - SCHWALBE_HALS / 2.0 - SPIEL
    n_kopf_a = R_SCHWALBE + SCHWALBE_KOPF / 2.0 + SPIEL
    n_kopf_i = R_SCHWALBE - SCHWALBE_KOPF / 2.0 - SPIEL

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

    # --- Schwalbenschwanz-Zapfen am Ende phi -------------------------------
    p.append(pol(phi, z_hals_a))                          # Stirnflaeche aussen
    p.append(pol(phi + a_zapfen, z_kopf_a))               # aeussere Flanke
    p.append(pol(phi + a_zapfen, z_kopf_i))               # Kopfflaeche
    p.append(pol(phi, z_hals_i))                          # innere Flanke
    p.append(pol(phi, r_innen))                           # Stirnflaeche innen

    # --- Innenkontur, Winkel fallend von phi nach 0 ------------------------
    bogen(p, phi, phi - a_klotz, r_innen, s_klotz)
    p.append(pol(phi - a_auslauf, r_innen))
    bogen(p, phi - a_auslauf, a_auslauf, r_innen, s_wand)
    p.append(pol(a_klotz, r_innen))
    bogen(p, a_klotz, 0.0, r_innen, s_klotz)

    # --- Schwalbenschwanz-Nut am Anfang 0 ----------------------------------
    p.append(pol(0.0, n_hals_i))                          # Stirnflaeche innen
    p.append(pol(a_nut, n_kopf_i))                        # innere Flanke
    p.append(pol(a_nut, n_kopf_a))                        # Nutgrund
    p.append(pol(0.0, n_hals_a))                          # aeussere Flanke
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
    """Liste (z, einzug, zapfen_fase) von unten nach oben."""
    stufen = [(0.0, 0.0, EINFUEHRFASE)]

    # Einfuehrfase am Zapfen auslaufen lassen
    for i in range(1, VERRUNDUNG_STUFEN + 1):
        z = EINFUEHRFASE_HOEHE * i / VERRUNDUNG_STUFEN
        rest = EINFUEHRFASE * (1.0 - i / VERRUNDUNG_STUFEN) ** 2
        stufen.append((z, 0.0, rest))

    # gerader Bereich bis zum Beginn der Kantenverrundung
    stufen.append((HOEHE - VERRUNDUNG, 0.0, 0.0))

    # Viertelkreis-Verrundung an der Oberkante
    for i in range(1, VERRUNDUNG_STUFEN + 1):
        t = i / VERRUNDUNG_STUFEN
        winkel = math.pi / 2.0 * t
        z = HOEHE - VERRUNDUNG + VERRUNDUNG * math.sin(winkel)
        einzug = VERRUNDUNG * (1.0 - math.cos(winkel))
        stufen.append((z, einzug, 0.0))

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
    profile = [segment_profil(anzahl_segmente, einzug, fase)
               for (_, einzug, fase) in stufen]
    hoehen = [z for (z, _, _) in stufen]
    return loften(profile, hoehen)


def ring_mesh(d_aussen):
    """Ungeteilter Ring mit derselben Oberkanten-Verrundung."""
    stufen = [(z, e, f) for (z, e, f) in hoehen_stufen() if f == 0.0]
    # doppelte Hoehen (aus der Fasen-Stufe) entfernen
    entpackt = []
    for eintrag in stufen:
        if not entpackt or abs(eintrag[0] - entpackt[-1][0]) > 1e-9:
            entpackt.append(eintrag)
    entpackt[0] = (0.0, 0.0, 0.0)

    dreiecke = []
    profile = [ring_profil(d_aussen, e) for (_, e, _) in entpackt]
    hoehen = [z for (z, _, _) in entpackt]
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

def main():
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    os.makedirs(ziel, exist_ok=True)

    print("Ring: aussen %.1f / innen %.1f / Wand %.1f / Hoehe %.1f mm, "
          "Oberkante R%.1f verrundet"
          % (AUSSEN_DURCHMESSER, AUSSEN_DURCHMESSER - 2 * WANDSTAERKE,
             WANDSTAERKE, HOEHE, VERRUNDUNG))
    print("Angenommener Bauraum: %.0f x %.0f mm\n" % DRUCKBETT)

    fehler = 0
    for n in (2, 3, 4):
        d = segment_mesh(n)
        offen = offene_kanten(d)
        fehler += offen
        name = "schutzring_%dteilig_segment.stl" % n
        stl_schreiben(os.path.join(ziel, name), d, name)
        passt, bx, by, winkel, rand = bester_bauraum(d)
        print("%-34s %5d Dr. | %6.1f cm3 je Segment (%dx = %6.1f cm3) | "
              "%5.1f x %5.1f mm @ %5.1f Grad, Rand %+6.1f mm -> %-11s | offene Kanten %d"
              % (name, len(d), volumen(d) / 1000.0, n, n * volumen(d) / 1000.0,
                 bx, by, winkel, rand, "passt" if passt else "PASST NICHT", offen))

    print()
    for d_aussen in EINTEILIG_DURCHMESSER:
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

    svg_schreiben(os.path.join(ziel, "vorschau.svg"), [2, 3])
    print("\nvorschau.svg geschrieben")

    if fehler:
        raise SystemExit("FEHLER: %d offene Kanten -- Mesh nicht dicht" % fehler)
    print("Alle Meshes sind geschlossen (wasserdicht).")


if __name__ == "__main__":
    main()
