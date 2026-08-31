#!/usr/bin/env python3
"""
Transportkoffer fuer das Hot Wheels RC 1:64 (Lamborghini Temerario):
Auto in der Originalbox + Pistolengriff-Controller, so kompakt wie
moeglich, verschliessbar, mit Steck-Tragegriff.

Vier Teile:
  1. WANNE   -- Unterteil mit zwei Faechern (Controller liegend, Auto-Box
                liegend), Klemmrippen, Scharnieraugen hinten, Rastkeilen
                vorn.
  2. DECKEL  -- mit Blattfeder-Boegen (halten den Inhalt nieder),
                Schnappzungen vorn, Scharnieraugen hinten und zwei
                T-Nut-Bloecke aussen am Wandring fuer den Griff.
  3. GRIFF   -- Buegel mit T-Fuessen, wird von unten in die Nuten
                geschoben; beim Tragen ziehen die Fuesse gegen das
                Blindende der Nut (Formschluss).
  4. ACHSSTIFT (2x) -- Scharnierstifte.

Masz-Strategie: Die Originalbox ist gemessen (100 x 50 x 50), der
Controller ist eine begruendete Schaetzung (Pistolengriff der 1:64-Serie,
liegend ca. 115 x 120 x 62). Damit die Schaetzung unkritisch ist, klemmen
in beiden Faechern duenne, federnde Rippen (schlucken +/- 4 mm), und der
Deckel drueckt ueber Federboegen von oben auf den Inhalt. Alle Masze sind
Parameter -- nachmessen, eintragen, neu generieren geht jederzeit.

Mesh-Technik wie in den Nachbarprojekten: mehrere geschlossene,
ueberlappende Prismen je STL; der Slicer vereinigt beim Slicen. Quer
liegende Bohrungen sind Tropfen, quer liegende Bloecke Rauten -- alles
ohne Stuetzen druckbar.

Koordinaten: X = Kofferlaenge, Y = Koffertiefe, Z = Hoehe. Ursprung in
der Mitte des Innenraums am Wannenboden (Innenboden = z 0).
Alle Masse in Millimetern.
"""

import math
import os
import struct

# ---------------------------------------------------------------------------
# Parameter: Inhalt
# ---------------------------------------------------------------------------

AUTOBOX_L  = 100.0    # gemessene Originalbox des Autos
AUTOBOX_B  = 50.0
AUTOBOX_H  = 50.0

# Der Controller hat ZWEI relevante Dicken: das Gehaeuse und das seitlich
# ueberstehende Drehrad. Er wird mit dem Rad NACH OBEN eingelegt -- dann
# liegt das Gehaeuse flach auf, das Rad ragt frei in den Deckelraum.
# Andersherum laege er auf dem Rad und wuerde kippeln. Die Mulde fuehrt
# deshalb nur das Gehaeuse; ihre asymmetrische Pistolenform laesst die
# gespiegelte (falsche) Lage ohnehin nicht zu.
CTRL_GEHAEUSE_D = 42.0    # Gehaeusedicke ohne Rad (gemessen)
CTRL_RAD_UEBER  = 15.0    # Radueberstand ueber die Gehaeuseseite (57 - 42)
CTRL_H = CTRL_GEHAEUSE_D + CTRL_RAD_UEBER    # Gesamthoehe liegend = 57

# Controller-Silhouette (Draufsicht, liegend wie im Original-Tray), aus dem
# Foto des Formfaser-Trays vermessen; Massstab ueber die bekannte 100-mm-
# Auto-Box (474 px). Einheiten mm, y nach unten (wird beim Aufbau
# gespiegelt). Der Radbogen wird programmatisch eingefuegt.
CTRL_KONTUR_ROH = [
    (0.0,  56.0),   # Schnauze vorn-unten
    (8.1,  43.2),   # Schnauze vorn-oben
    "RAD",          # Drehrad: Bogen ueber (RAD_CX, RAD_CY), Radius RAD_R
    (96.7,  9.4),   # hinter dem Rad, oben
    (93.5, 46.3),   # Ruecken / Griffansatz
    (99.0, 118.1),  # Griffruecken
    (100.0, 158.2), # Griffende hinten
    (77.9, 169.8),  # Griffkuppe
    (55.5, 160.3),  # Griffende vorn
    (39.9, 107.5),  # Griff vorn / Trigger
    (35.5,  82.2),  # Triggerbucht
    (27.0,  71.7),  # Unterkante Elektronikbox
]
RAD_CX, RAD_CY, RAD_R = 68.2, 20.0, 20.0
CTRL_FOTO_LAENGE = 169.8   # y-Spanne der Foto-Silhouette (Radkante-Griffende)
CTRL_FOTO_RAD    = 40.0    # Rad-Durchmesser laut Foto
MULDE_LUFT = 4.0           # Offset der Mulde um die Silhouette (Rippenraum)
MULDE_HOEHE = 30.0         # Tiefe der Konturmulde (fuehrt das Gehaeuse)

KLEMMWEG   = 4.0      # was die Rippen je Seite schlucken koennen

# ---------------------------------------------------------------------------
# Parameter: Koffer
# ---------------------------------------------------------------------------

WAND       = 2.8      # Wandstaerke aussen
BODEN      = 3.0
ECKRADIUS  = 12.0     # Aussenecken (smooth!)
TRENNWAND  = 3.0

RIPPE_DICK = 1.1      # Klemmrippen: duenn genug zum Federn
RIPPE_TIEF = 5.0      # wie weit sie ins Fach ragen
RIPPE_BREIT = 8.0     # Auflagebreite pro Rippe

DECKEL_INNEN = 30.0   # lichte Hoehe im Deckel
KANTE_R    = 3.0      # Verrundung der Deckeloberkante (Loft-Einzug)

FEDER_DICK = 1.0      # Blattfeder-Boegen im Deckel
FEDER_HUB  = 18.0     # wie weit sie unter die Deckeldecke ragen

SCHARNIER_AUGE = 13.0     # Augen-Aussenmass (Raute)
STIFT_D    = 4.0
LOCH_DREH  = 4.3          # Wannenauge (drehbar)
LOCH_PRESS = 3.8          # Deckelauge (Presssitz)

ZUNGE_BREIT = 18.0    # Schnappzungen vorn
ZUNGE_DICK  = 1.4
ZUNGE_LANG  = 16.0
HAKEN       = 1.8   # ergibt 1.4 mm Rasteingriff

GRIFF_BREIT = 90.0    # lichte Grifflaenge
GRIFF_HOCH  = 24.0
GRIFF_PROFIL = 12.0   # Querschnitt des Buegels
SCHWALBE_SP = 0.25    # Spiel der Griff-Schwalbe

SEG = 64

# Vom Nutzer GEMESSEN (Messschieber): Controller liegend 190 lang (Radkante
# bis Griffende), 131 breit (Schnauze bis Griffruecken), 50 dick. Die
# Foto-Silhouette wird darauf anisotrop skaliert -- die Foto-Skala war
# wegen Parallaxe (Referenzbox liegt hoeher als die Controller-Kontur)
# in beiden Achsen unterschiedlich zu klein.
CTRL_LAENGE = 190.0
CTRL_BREITE = 131.0


# ---------------------------------------------------------------------------
# Abgeleitete Masze
# ---------------------------------------------------------------------------

def ctrl_kontur():
    """Silhouette als geschlossenes Polygon in mm, y nach oben, auf die
    gemessenen Werte skaliert, Ursprung = linke untere BBox-Ecke."""
    pts = []
    for eintrag in CTRL_KONTUR_ROH:
        if eintrag == "RAD":
            # Bogen ueber das Rad, von links (180 Grad) bis -30 Grad
            for i in range(13):
                w = math.radians(180.0 - 210.0 * i / 12.0)
                pts.append((RAD_CX + RAD_R * math.cos(w),
                            RAD_CY - RAD_R * math.sin(w)))
        else:
            pts.append(eintrag)
    xs = [x for (x, _) in pts]
    ys = [y for (_, y) in pts]
    sx = CTRL_BREITE / (max(xs) - min(xs))
    sy = CTRL_LAENGE / (max(ys) - min(ys))
    ymax = max(ys)
    return [((x - min(xs)) * sx, (ymax - y) * sy) for (x, y) in pts]


def offset_polygon(poly, d):
    """Polygon um d nach aussen versetzen (Vertex-Normalen-Verfahren --
    fuer kleine d an handgezaehlten Konturen ausreichend)."""
    if flaeche_signiert(poly) < 0:
        poly = poly[::-1]
    n = len(poly)
    out = []
    for i in range(n):
        x0, y0 = poly[(i - 1) % n]
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        # Kantennormalen (aussen = rechts der Laufrichtung bei CCW)
        def norm(ax, ay, bx, by):
            dx, dy = bx - ax, by - ay
            l = math.hypot(dx, dy) or 1.0
            return (dy / l, -dx / l)
        n1 = norm(x0, y0, x1, y1)
        n2 = norm(x1, y1, x2, y2)
        mx, my = n1[0] + n2[0], n1[1] + n2[1]
        l = math.hypot(mx, my) or 1.0
        # Miter-Begrenzung: nicht weiter als 2*d hinaus
        f = min(2.0, 2.0 / l)
        out.append((x1 + mx / l * d * f / (f if f else 1) * 1.0,
                    y1 + my / l * d * f / (f if f else 1) * 1.0))
    return out


def abgeleitet():
    g = {}
    zuschlag = 2.0 * (RIPPE_TIEF - 1.0)
    kontur = ctrl_kontur()
    mulde = offset_polygon(kontur, MULDE_LUFT)
    xs = [x for (x, _) in mulde]
    ys = [y for (_, y) in mulde]
    # 3 mm Randsteg rundum, damit die Fuellschale um die Mulde herum
    # ueberall Material hat (Loch darf die Fachwand nicht beruehren)
    steg = 3.0
    g["mulde"] = [(x - min(xs) + steg, y - min(ys) + steg) for (x, y) in mulde]
    g["kontur"] = [(x - min(xs) + steg, y - min(ys) + steg) for (x, y) in kontur]
    radpts = g["kontur"][2:15]                   # Radbogen-Punkte
    griffpts = g["kontur"][17:21]                # Griffende
    g["rad_pos"] = (sum(x for x, _ in radpts) / len(radpts),
                    sum(y for _, y in radpts) / len(radpts))
    g["griff_pos"] = (sum(x for x, _ in griffpts) / len(griffpts),
                      sum(y for _, y in griffpts) / len(griffpts))
    schnauzpts = [g["kontur"][0], g["kontur"][1], g["kontur"][-1]]
    g["schnauz_pos"] = (sum(x for x, _ in schnauzpts) / len(schnauzpts),
                        sum(y for _, y in schnauzpts) / len(schnauzpts))
    g["fachC_l"] = max(xs) - min(xs) + 2 * steg
    g["fachC_t"] = max(ys) - min(ys) + 2 * steg
    g["fachA_l"] = AUTOBOX_B + zuschlag          # Box liegt quer: B in X
    g["fachA_t"] = AUTOBOX_L + zuschlag

    g["innen_x"] = g["fachC_l"] + TRENNWAND + g["fachA_l"]
    g["innen_y"] = max(g["fachC_t"], g["fachA_t"])
    # Die Fuellschale fuellt die Wanne buendig aus -> Wanneninnenhoehe ist
    # die Muldentiefe. Was darueber hinausragt, faengt der Deckel.
    g["wanne_innen_h"] = MULDE_HOEHE
    g["innen_h"] = g["wanne_innen_h"] + DECKEL_INNEN

    g["aussen_x"] = g["innen_x"] + 2 * WAND
    g["aussen_y"] = g["innen_y"] + 2 * WAND
    g["wanne_h"] = BODEN + g["wanne_innen_h"]
    g["deckel_h"] = DECKEL_INNEN + BODEN

    # Fachmitten (X): Controller links, Auto rechts
    g["fachC_x0"] = -g["innen_x"] / 2.0
    g["fachC_x1"] = g["fachC_x0"] + g["fachC_l"]
    g["fachA_x1"] = g["innen_x"] / 2.0
    g["fachA_x0"] = g["fachA_x1"] - g["fachA_l"]
    return g


# ---------------------------------------------------------------------------
# Mesh-Grundlagen (erprobter Baukasten der Nachbarprojekte)
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


def prisma(poly, z0, z1):
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


def loften(profile, hoehen):
    """Profile gleicher Punktzahl zu einem geschlossenen Koerper verbinden
    (Boden = erstes, Deckel = letztes Profil)."""
    n = len(profile[0])
    t = []
    unten = profile[0]
    for (a, b, c) in triangulieren(unten):
        pa, pb, pc = unten[a], unten[b], unten[c]
        t.append(((pa[0], pa[1], hoehen[0]), (pc[0], pc[1], hoehen[0]),
                  (pb[0], pb[1], hoehen[0])))
    oben = profile[-1]
    for (a, b, c) in triangulieren(oben):
        pa, pb, pc = oben[a], oben[b], oben[c]
        t.append(((pa[0], pa[1], hoehen[-1]), (pb[0], pb[1], hoehen[-1]),
                  (pc[0], pc[1], hoehen[-1])))
    for k in range(len(profile) - 1):
        pu, po = profile[k], profile[k + 1]
        zu, zo = hoehen[k], hoehen[k + 1]
        for i in range(n):
            j = (i + 1) % n
            a = (pu[i][0], pu[i][1], zu)
            b = (pu[j][0], pu[j][1], zu)
            c = (po[j][0], po[j][1], zo)
            d = (po[i][0], po[i][1], zo)
            t.append((a, b, c))
            t.append((a, c, d))
    return t


def loch_prisma(aussen, innen, z0, z1):
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
        t.append(((ao[0], ao[1], z0), (ai[0], ai[1], z0), (bi[0], bi[1], z0)))
        t.append(((ao[0], ao[1], z0), (bi[0], bi[1], z0), (bo[0], bo[1], z0)))
        t.append(((ao[0], ao[1], z1), (bo[0], bo[1], z1), (bi[0], bi[1], z1)))
        t.append(((ao[0], ao[1], z1), (bi[0], bi[1], z1), (ai[0], ai[1], z1)))
        t.append(((ao[0], ao[1], z0), (bo[0], bo[1], z0), (bo[0], bo[1], z1)))
        t.append(((ao[0], ao[1], z0), (bo[0], bo[1], z1), (ao[0], ao[1], z1)))
        t.append(((ai[0], ai[1], z0), (ai[0], ai[1], z1), (bi[0], bi[1], z1)))
        t.append(((ai[0], ai[1], z0), (bi[0], bi[1], z1), (bi[0], bi[1], z0)))
    return t


def punkt_in_polygon(pt, poly):
    x, y = pt
    drin = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            drin = not drin
    return drin


def _bruecke_einbauen(aussen, loch):
    """Loch ueber eine Bruecke in die Aussenkontur einschneiden (Technik
    aus dem Hochzeitsornament-Projekt)."""
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
    """Prisma mit beliebigen Loechern: Deckel/Boden aus der Bruecken-
    Triangulierung, Mantel aus den Originalkonturen. Bruecken erzeugen in
    den Deckflaechen koinzidente Doppelkanten -> Kantencheck dort mit
    gerade_erlaubt fahren."""
    if flaeche_signiert(aussen) < 0:
        aussen = aussen[::-1]
    loecher = [l[::-1] if flaeche_signiert(l) > 0 else l for l in loecher]
    kombi = aussen
    for l in loecher:
        kombi = _bruecke_einbauen(kombi, l)
    t = []
    for (a, b, c) in triangulieren(kombi):
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


def verschieben(t, dx=0.0, dy=0.0, dz=0.0):
    return [tuple((x + dx, y + dy, z + dz) for (x, y, z) in tri) for tri in t]


def dreh_x90(t):
    """+90 um X: Z-Richtung -> Y-Richtung."""
    return [tuple((x, -z, y) for (x, y, z) in tri) for tri in t]


def dreh_z90(t):
    """+90 um Z: X -> Y."""
    return [tuple((-y, x, z) for (x, y, z) in tri) for tri in t]


def kanten_pruefen(t, gerade_erlaubt=False):
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
        f.write(("RC-Transportbox - " + name).encode("ascii", "replace")
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
# Konturen
# ---------------------------------------------------------------------------

def rundrechteck(bx, by, r, seg_ecke=12):
    """Rechteck bx x by um (0,0) mit Eckradius r."""
    hx, hy = bx / 2.0, by / 2.0
    pts = []
    ecken = [(hx - r, hy - r, 0.0), (-(hx - r), hy - r, 90.0),
             (-(hx - r), -(hy - r), 180.0), (hx - r, -(hy - r), 270.0)]
    for cx, cy, start in ecken:
        for i in range(seg_ecke + 1):
            w = math.radians(start + 90.0 * i / seg_ecke)
            pts.append((cx + r * math.cos(w), cy + r * math.sin(w)))
    return pts


def kreis(r, cx=0.0, cy=0.0, seg=SEG):
    return [(cx + r * math.cos(2 * math.pi * i / seg),
             cy + r * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


def raute(halb, seg=SEG):
    pts = []
    for i in range(seg):
        w = 2 * math.pi * i / seg
        r = halb / (abs(math.cos(w)) + abs(math.sin(w)))
        pts.append((r * math.cos(w), r * math.sin(w)))
    return pts


def tropfen(r, seg=SEG):
    apex = r * math.sqrt(2.0)
    pts = []
    for i in range(seg):
        w = 2 * math.pi * i / seg
        grad = math.degrees(w) % 360.0
        if 45.0 <= grad <= 135.0:
            if grad <= 90.0:
                t = (grad - 45.0) / 45.0
                a = (r * math.cos(math.radians(45)), r * math.sin(math.radians(45)))
                b = (0.0, apex)
            else:
                t = (grad - 90.0) / 45.0
                a = (0.0, apex)
                b = (r * math.cos(math.radians(135)), r * math.sin(math.radians(135)))
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        else:
            pts.append((r * math.cos(w), r * math.sin(w)))
    return pts


# ---------------------------------------------------------------------------
# Wiederkehrende Baugruppen
# ---------------------------------------------------------------------------

def rippe(x, y, richtung, z0, z1):
    """Eine Klemmrippe: duenner Steg, der senkrecht von einer Fachwand
    absteht. richtung: '+x','-x','+y','-y' = wohin sie ins Fach ragt.
    Am freien Ende 1 mm Anlauffase (Loft), damit der Inhalt sie beim
    Einlegen niederdrueckt statt hakt."""
    if richtung in ("+x", "-x"):
        s = 1.0 if richtung == "+x" else -1.0
        voll = [(x, y - RIPPE_BREIT / 2), (x + s * RIPPE_TIEF, y - RIPPE_BREIT / 2),
                (x + s * RIPPE_TIEF, y + RIPPE_BREIT / 2), (x, y + RIPPE_BREIT / 2)]
        kurz = [(x, y - RIPPE_BREIT / 2), (x + s * (RIPPE_TIEF - 1.5), y - RIPPE_BREIT / 2),
                (x + s * (RIPPE_TIEF - 1.5), y + RIPPE_BREIT / 2), (x, y + RIPPE_BREIT / 2)]
    else:
        s = 1.0 if richtung == "+y" else -1.0
        voll = [(x - RIPPE_BREIT / 2, y), (x + RIPPE_BREIT / 2, y),
                (x + RIPPE_BREIT / 2, y + s * RIPPE_TIEF), (x - RIPPE_BREIT / 2, y + s * RIPPE_TIEF)]
        kurz = [(x - RIPPE_BREIT / 2, y), (x + RIPPE_BREIT / 2, y),
                (x + RIPPE_BREIT / 2, y + s * (RIPPE_TIEF - 1.5)),
                (x - RIPPE_BREIT / 2, y + s * (RIPPE_TIEF - 1.5))]
    # Fase oben: obere 3 mm laufen auf die kurze Kontur zu
    return loften([voll, voll, kurz], [z0, z1 - 3.0, z1])


def rippe_frei(px, py, nx, ny, z0, z1):
    """Klemmrippe an einer Konturwand: steht bei (px,py), ragt in Richtung
    der Normalen (nx,ny) ins Fach, mit Anlauffase oben."""
    l = math.hypot(nx, ny) or 1.0
    nx, ny = nx / l, ny / l
    tx, ty = -ny, nx
    b = RIPPE_BREIT / 2.0

    def quer(tief):
        return [(px - tx * b, py - ty * b),
                (px + tx * b, py + ty * b),
                (px + tx * b + nx * tief, py + ty * b + ny * tief),
                (px - tx * b + nx * tief, py - ty * b + ny * tief)]

    return loften([quer(RIPPE_TIEF), quer(RIPPE_TIEF), quer(RIPPE_TIEF - 1.5)],
                  [z0, z1 - 3.0, z1])


def scharnier_auge(loch_d, laenge):
    """Auge: Raute aussen, Tropfenloch innen, Achse entlang X,
    Zentrum (0,0,0), erstreckt sich x = 0..laenge."""
    a = raute(SCHARNIER_AUGE / 2.0)
    i = tropfen(loch_d / 2.0)
    t = loch_prisma(a, i, 0.0, laenge)            # Achse erst entlang Z
    t = dreh_x90(t)                               # -> entlang -Y
    t = dreh_z90(t)                               # -> entlang +X
    return t


# ---------------------------------------------------------------------------
# Teil 1: Wanne
# ---------------------------------------------------------------------------

def teil_wanne(g):
    schalen = []
    aussen = rundrechteck(g["aussen_x"], g["aussen_y"], ECKRADIUS)
    innen = rundrechteck(g["innen_x"], g["innen_y"], max(2.0, ECKRADIUS - WAND))

    # Boden mit Fusskante (unten 1.5 mm eingezogen = kleine Fase)
    boden_klein = rundrechteck(g["aussen_x"] - 3.0, g["aussen_y"] - 3.0,
                               ECKRADIUS)
    schalen.append(loften([boden_klein, aussen, aussen],
                          [-BODEN, -BODEN + 1.5, 0.5]))
    # Wandring
    schalen.append(loch_prisma(aussen, innen, 0.0, g["wanne_innen_h"]))

    # Trennwand
    tw = [(g["fachC_x1"], -g["innen_y"] / 2), (g["fachC_x1"] + TRENNWAND, -g["innen_y"] / 2),
          (g["fachC_x1"] + TRENNWAND, g["innen_y"] / 2), (g["fachC_x1"], g["innen_y"] / 2)]
    schalen.append(prisma(tw, 0.0, g["wanne_innen_h"]))

    z1 = g["wanne_innen_h"]

    # Fuellbloecke im Autofach (verkuerzen die Tiefe auf Boxmass + Rippenraum)
    fach_a_frei = g["fachA_t"]
    if g["innen_y"] > fach_a_frei + 0.5:
        blockt = (g["innen_y"] - fach_a_frei) / 2.0
        for s in (+1, -1):
            y_innen = s * (g["innen_y"] / 2.0 - blockt)
            y_aussen = s * g["innen_y"] / 2.0
            bl = [(g["fachA_x0"], min(y_innen, y_aussen)),
                  (g["fachA_x1"], min(y_innen, y_aussen)),
                  (g["fachA_x1"], max(y_innen, y_aussen)),
                  (g["fachA_x0"], max(y_innen, y_aussen))]
            schalen.append(prisma(bl, 0.0, z1))

    # Controllerfach: Konturmulde nach dem Vorbild des Original-Trays.
    # Eine Fuellschale mit pistolenfoermigem Loch (Bruecken-Triangulierung)
    # bildet die Mulde; Klemmrippen an markanten Konturpunkten uebernehmen
    # die Toleranz. Die Mulde ist MULDE_HOEHE tief -- darueber haelt der
    # Federbogen des Deckels.
    mx0 = g["fachC_x0"]
    my0 = -g["fachC_t"] / 2.0
    mulde_pos = [(x + mx0, y + my0) for (x, y) in g["mulde"]]
    kontur_pos = [(x + mx0, y + my0) for (x, y) in g["kontur"]]
    fachrect = [(g["fachC_x0"], -g["innen_y"] / 2.0),
                (g["fachC_x1"], -g["innen_y"] / 2.0),
                (g["fachC_x1"], g["innen_y"] / 2.0),
                (g["fachC_x0"], g["innen_y"] / 2.0)]
    schalen.append((prisma_mit_loechern(fachrect, [mulde_pos],
                                        0.0, MULDE_HOEHE), True))

    # Rippen: Muldenwand -> Richtung Originalkontur (dort sitzt das Teil)
    for idx in (0, 7, 15, 17, 18, 19, 20, 22):
        px, py = mulde_pos[idx]
        qx, qy = kontur_pos[idx]
        schalen.append(rippe_frei(px, py, qx - px, qy - py, 0.0, MULDE_HOEHE))

    # Klemmrippen Autofach
    ax = (g["fachA_x0"] + g["fachA_x1"]) / 2.0
    ay = fach_a_frei / 2.0
    for dy in (-g["fachA_t"] * 0.25, g["fachA_t"] * 0.25):
        schalen.append(rippe(g["fachA_x0"] + TRENNWAND, dy, "+x", 0.0, z1))
        schalen.append(rippe(g["fachA_x1"], dy, "-x", 0.0, z1))
    for dx in (-g["fachA_l"] * 0.22, g["fachA_l"] * 0.22):
        schalen.append(rippe(ax + dx, -ay, "+y", 0.0, z1))
        schalen.append(rippe(ax + dx, ay, "-y", 0.0, z1))

    # Scharnieraugen hinten aussen (Achse X, Lochmitte 4 ueber Randkante)
    z_achse = z1 + SCHARNIER_AUGE / 2.0 - 2.0
    y_auge = g["aussen_y"] / 2.0 + SCHARNIER_AUGE / 2.0 - 1.5
    for x0 in (-58.0, 46.0):
        auge = scharnier_auge(LOCH_DREH, 12.0)
        schalen.append(verschieben(auge, x0, y_auge, z_achse))
        # Stuetzsteg vom Auge zur Rueckwand
        steg = [(x0, g["aussen_y"] / 2.0 - 1.0), (x0 + 12.0, g["aussen_y"] / 2.0 - 1.0),
                (x0 + 12.0, y_auge), (x0, y_auge)]
        schalen.append(prisma(steg, z1 - 8.0, z_achse))

    # Rastkeile vorn (halbe Raute quer): Zunge des Deckels schnappt darunter
    y_front = -g["aussen_y"] / 2.0
    for xm in (-g["aussen_x"] * 0.25, g["aussen_x"] * 0.25):
        keil_profil = [(y_front, z1 - 6.0), (y_front - HAKEN, z1 - 6.0 + HAKEN),
                       (y_front, z1 - 6.0 + 2 * HAKEN)]
        # Profil liegt in (y,z); entlang X extrudieren
        t = prisma(keil_profil, xm - ZUNGE_BREIT / 2.0, xm + ZUNGE_BREIT / 2.0)
        t = [tuple((z, x, y) for (x, y, z) in tri) for tri in t]
        schalen.append(t)

    return schalen


# ---------------------------------------------------------------------------
# Teil 2: Deckel  (gedruckt mit der Innenseite nach OBEN)
# ---------------------------------------------------------------------------

def teil_deckel(g):
    """Der Deckel wird verkehrt herum konstruiert, so wie er gedruckt wird:
    Aussenflaeche unten (z=0), Innenseite oben. Die Verrundung der (im
    Gebrauch) Oberkante liegt damit am Druckbett -- Loft mit Einzug."""
    schalen = []
    aussen = rundrechteck(g["aussen_x"], g["aussen_y"], ECKRADIUS)
    innen = rundrechteck(g["innen_x"], g["innen_y"], max(2.0, ECKRADIUS - WAND))

    # Deckelplatte mit verrundeter Kante (im Druck unten)
    profile, hoehen = [], []
    stufen = 5
    for i in range(stufen + 1):
        w = math.radians(90.0 * i / stufen)
        einzug = KANTE_R * (1.0 - math.sin(w))
        z = KANTE_R * (1.0 - math.cos(w))
        profile.append(rundrechteck(g["aussen_x"] - 2 * einzug,
                                    g["aussen_y"] - 2 * einzug, ECKRADIUS))
        hoehen.append(z)
    profile.append(profile[-1])
    hoehen.append(BODEN + 0.5)
    schalen.append(loften(profile, hoehen))

    # Wandring des Deckels
    schalen.append(loch_prisma(aussen, innen, BODEN, BODEN + DECKEL_INNEN))

    # Blattfeder-Boegen: flache Boegen quer ueber jedes Fach, Fusspunkte
    # auf der Deckelplatte, Scheitel ragt FEDER_HUB in den Innenraum.
    def feder(cx, spann, hub=FEDER_HUB):
        n = 24
        aussen_pts, innen_pts = [], []
        for i in range(n + 1):
            t = i / n
            x = cx - spann / 2.0 + spann * t
            z = BODEN + math.sin(math.pi * t) * hub
            aussen_pts.append((x, z))
        for i in range(n + 1):
            t = 1.0 - i / n
            x = cx - spann / 2.0 + spann * t
            z = BODEN + math.sin(math.pi * t) * hub - FEDER_DICK
            innen_pts.append((x, max(BODEN - 0.5, z)))
        profil = aussen_pts + innen_pts
        return profil

    # Federn gezielt ueber Drehrad und Griffende des Controllers sowie
    # ueber der Auto-Box. ACHTUNG: der Deckel wird beim Schliessen um die
    # X-Achse... nein: um Y gespiegelt ((x,y,z)->(-x,y,z_top-z)), die
    # x-Positionen der Wanne erscheinen im Deckel daher negiert.
    mx0 = g["fachC_x0"]
    my0 = -g["fachC_t"] / 2.0

    # Wie weit ragt der jeweilige Inhalt in den Deckel? Daraus folgt der
    # noetige Federhub. Ueber dem Drehrad darf KEINE Feder stehen -- das
    # Rad ragt am hoechsten und wuerde geklemmt statt gehalten.
    ueber_gehaeuse = CTRL_GEHAEUSE_D - g["wanne_innen_h"]
    ueber_rad = CTRL_H - g["wanne_innen_h"]
    ueber_box = AUTOBOX_H - g["wanne_innen_h"]
    hub_ctrl = max(3.0, DECKEL_INNEN - ueber_gehaeuse - 1.0)
    hub_box = max(3.0, DECKEL_INNEN - ueber_box - 1.0)

    ziele = [(-(mx0 + g["schnauz_pos"][0]), my0 + g["schnauz_pos"][1],
              48.0, hub_ctrl),
             (-(mx0 + g["griff_pos"][0]), my0 + g["griff_pos"][1],
              48.0, hub_ctrl),
             (-(g["fachA_x0"] + g["fachA_x1"]) / 2.0, -g["fachA_t"] * 0.22,
              g["fachA_l"] * 0.8, hub_box),
             (-(g["fachA_x0"] + g["fachA_x1"]) / 2.0, g["fachA_t"] * 0.22,
              g["fachA_l"] * 0.8, hub_box)]
    for cx, y, spann, hub in ziele:
        profil = feder(cx, spann, hub)
        t = prisma(profil, y - 5.0, y + 5.0)
        t = [tuple((x, z, y_) for (x, y_, z) in tri) for tri in t]
        schalen.append(t)

    # Kontrolle: das Rad muss im Deckel frei bleiben
    if ueber_rad > DECKEL_INNEN - 1.0:
        raise SystemExit("FEHLER: Drehrad ragt %.1f mm in den Deckel, dort "
                         "sind nur %.1f mm -- DECKEL_INNEN erhoehen"
                         % (ueber_rad, DECKEL_INNEN))

    # Scharnieraugen (versetzt zu denen der Wanne, Presssitz)
    z_rand = BODEN + DECKEL_INNEN
    y_auge = g["aussen_y"] / 2.0 + SCHARNIER_AUGE / 2.0 - 1.5
    for x0 in (-46.0, 58.0 - 12.0):
        auge = scharnier_auge(LOCH_PRESS, 12.0)
        schalen.append(verschieben(auge, x0, y_auge,
                                   z_rand - SCHARNIER_AUGE / 2.0 + 2.0))
        steg = [(x0, g["aussen_y"] / 2.0 - 1.0), (x0 + 12.0, g["aussen_y"] / 2.0 - 1.0),
                (x0 + 12.0, y_auge), (x0, y_auge)]
        schalen.append(prisma(steg, z_rand - 10.0,
                              z_rand - SCHARNIER_AUGE / 2.0 + 2.0))

    # Schnappzungen vorn. Geometrie im GEBRAUCH: der Rastkeil der Wanne
    # sitzt aussen auf der Frontwand (Unterkante wanne_innen_h - 6, Spitze
    # 2.2 vor der Wand). Die Zunge muss also 0.4 mm VOR der Keilspitze
    # herabhaengen und ihr Haken nach innen unter den Keil schnappen --
    # nicht an der Wand anliegen. Anbindung an den Deckel ueber einen
    # Ausleger, der oberhalb des Keils ueber die Wannenkante greift.
    def gz(z_gebrauch):
        """Gebrauchs-z -> Druck-z des Deckels (gespiegelt)."""
        return (g["wanne_innen_h"] + DECKEL_INNEN + BODEN) - z_gebrauch
    y_wand = -g["aussen_y"] / 2.0
    keil_unter = g["wanne_innen_h"] - 6.0            # Gebrauch
    y_zunge_i = y_wand - HAKEN - 0.4                 # Innenflaeche der Zunge
    for xm in (-g["aussen_x"] * 0.25, g["aussen_x"] * 0.25):
        x0, x1 = xm - ZUNGE_BREIT / 2.0, xm + ZUNGE_BREIT / 2.0
        # Ausleger: vom Wandring ueber die Wannenkante nach aussen
        ausleger = [(y_zunge_i - ZUNGE_DICK, z_rand - 3.0),
                    (y_wand + 2.0, z_rand - 3.0),
                    (y_wand + 2.0, z_rand),
                    (y_zunge_i - ZUNGE_DICK, z_rand)]
        # Zungensteg: steht im Druck nach oben, aussen am Ausleger
        steg = [(y_zunge_i - ZUNGE_DICK, z_rand - 3.0),
                (y_zunge_i, z_rand - 3.0),
                (y_zunge_i, gz(keil_unter) + 2.5),
                (y_zunge_i - ZUNGE_DICK, gz(keil_unter) + 2.5)]
        # Rautenhaken auf Keilhoehe (45/45: schnappt beim Schliessen ueber
        # den Keil und rastet unter seiner Unterkante ein)
        haken = [(y_zunge_i, gz(keil_unter) - 2.2),
                 (y_zunge_i + HAKEN, gz(keil_unter)),
                 (y_zunge_i, gz(keil_unter) + 2.2)]
        for profil in (ausleger, steg, haken):
            t = prisma(profil, x0, x1)
            t = [tuple((z, x, y) for (x, y, z) in tri) for tri in t]
            schalen.append(t)

    # Griff-Taschen: zwei Nutbloecke aussen am Wandring, an den
    # Langseiten mittig (x=0). Vertikale T-Nut, deren Hals die
    # Blockaussenseite schlitzt; oben (im Druck) 3 mm Blindende.
    # Im Gebrauch haengt der Koffer am Griff -> die Fuesse ziehen gegen
    # das Blindende, der Formschluss traegt die Last.
    hals, kopf, nut_tief = 6.4, 11.4, 4.0
    block_b, block_t = 22.0, 7.0
    z0b, z1b = BODEN + 2.0, BODEN + DECKEL_INNEN
    for sy in (-1.0, +1.0):
        yw = sy * g["aussen_y"] / 2.0
        ya = yw + sy * block_t

        def q(x0, x1, yi, yo):
            lo, hi = min(yi, yo), max(yi, yo)
            return [(x0, lo), (x1, lo), (x1, hi), (x0, hi)]

        # Blockquerschnitt mit T-Ausschnitt von der Aussenkante her,
        # als drei Teilprismen (links, rechts, Ruecksteg am Kofferkoerper)
        xk, xh = kopf / 2.0, hals / 2.0
        links = q(-block_b / 2.0, -xk, yw - 1.0, ya)
        rechts = q(xk, block_b / 2.0, yw - 1.0, ya)
        for teil in (links, rechts):
            schalen.append(prisma(teil, z0b + 2.9, z1b))
        # Halsleisten: decken den wandseitigen Kopfraum nach aussen ab,
        # dazwischen bleibt der vertikale Halsschlitz frei
        y_kopf_aussen = yw + sy * (block_t - nut_tief + 2.0)
        schalen.append(prisma(q(-xk, -xh, y_kopf_aussen, ya), z0b + 2.9, z1b))
        schalen.append(prisma(q(xh, xk, y_kopf_aussen, ya), z0b + 2.9, z1b))
        # Blindende: voller Querschnitt am druck-unteren Blockende --
        # das ist im Gebrauch OBEN, dort ziehen die Grifffuesse dagegen
        schalen.append(prisma(q(-block_b / 2.0, block_b / 2.0, yw - 1.0, ya),
                              z0b, z0b + 3.0))

    return schalen


# ---------------------------------------------------------------------------
# Teil 3: Griff, Teil 4: Achsstift
# ---------------------------------------------------------------------------

def teil_griff(g):
    """Buegelgriff im Gebrauchs-Koordinatensystem des geschlossenen
    Koffers (z=0 = Deckelaussenflaeche, Fuesse nach unten). Fuer den
    Druck wird das Teil in main() flach gelegt.

    Je Seite: Buegelschenkel aussen, daran Hals (durch den Schlitz) und
    T-Kopf (im Kopfraum). Eingeschoben wird von unten; beim Tragen
    ziehen die Koepfe gegen die Blindenden der Nuten.
    """
    hals = 6.4 - 2 * SCHWALBE_SP
    kopf = 11.4 - 2 * SCHWALBE_SP
    block_t, nut_tief = 7.0, 4.0
    schalen = []

    yw = g["aussen_y"] / 2.0
    ya = yw + block_t
    ye = ya + 6.0                       # Aussenkante der Buegelschenkel

    # Buegel-Silhouette in (y, z), Dicke entlang X
    # Aussenkontur: Schenkel bei +/-ye, Bogen darueber. Innenkontur: der
    # gleiche Bogen, um die Profilhoehe abgesenkt und nur zwischen den
    # Schenkel-INNENkanten (+/-(ye-6)) gespannt -- sonst schnitte sie die
    # Aussenkontur an den Schenkeln.
    n = 28
    yi = ye - 6.0
    aussen_pts = [(-ye, -9.0)]
    for i in range(n + 1):
        t = i / n
        y = -ye + 2 * ye * t
        aussen_pts.append((y, 6.0 + GRIFF_HOCH * math.sin(math.pi * t) ** 0.75))
    aussen_pts.append((ye, -9.0))
    innen_pts = [(yi, -9.0)]
    for i in range(n + 1):
        t = 1.0 - i / n
        y = -yi + 2 * yi * t
        innen_pts.append((y, GRIFF_HOCH * math.sin(math.pi * t) ** 0.75))
    innen_pts.append((-yi, -9.0))
    silhouette = aussen_pts + innen_pts
    b = prisma(silhouette, -8.0, 8.0)
    # prisma extrudiert die Silhouette in Z; wir brauchen sie in YZ mit
    # Dicke entlang X -> Achsentausch (x,y,z) -> (z,x,y)
    schalen.append([tuple((z_, x_, y_) for (x_, y_, z_) in tri) for tri in b])

    for sy in (-1.0, +1.0):
        y_kopf_aussen = sy * (yw + block_t - nut_tief + 2.0)
        # Hals: durch den Schlitz
        lo = min(sy * (yw + 1.0), sy * (ya + 2.0))
        hi = max(sy * (yw + 1.0), sy * (ya + 2.0))
        halsq = [(-hals / 2.0, lo), (hals / 2.0, lo),
                 (hals / 2.0, hi), (-hals / 2.0, hi)]
        schalen.append(prisma(halsq, -28.0, -9.0))
        # T-Kopf: im Kopfraum
        lo = min(sy * (yw + 0.4), sy * (y_kopf_aussen - sy * 0.3))
        hi = max(sy * (yw + 0.4), sy * (y_kopf_aussen - sy * 0.3))
        kopfq = [(-kopf / 2.0, lo), (kopf / 2.0, lo),
                 (kopf / 2.0, hi), (-kopf / 2.0, hi)]
        schalen.append(prisma(kopfq, -28.0, -9.0))
    return schalen


def teil_stift(g):
    kopf_r, kopf_h = 4.5, 3.0
    laenge = 12.0 + 2.0 + 12.0 + 1.0
    schalen = []
    schalen.append(prisma(kreis(kopf_r), 0.0, kopf_h))
    schalen.append(prisma(kreis(STIFT_D / 2.0), kopf_h - 1.0,
                          kopf_h + laenge - 1.5))
    schalen.append(loften([kreis(STIFT_D / 2.0), kreis(STIFT_D / 2.0 - 1.0)],
                          [kopf_h + laenge - 1.51, kopf_h + laenge]))
    return schalen


# ---------------------------------------------------------------------------

def bauen(ziel, name, schalen):
    fehler = 0
    alle = []
    for eintrag in schalen:
        if isinstance(eintrag, tuple):
            sch, gerade = eintrag
        else:
            sch, gerade = eintrag, False
        fehler += kanten_pruefen(sch, gerade_erlaubt=gerade)
        alle.extend(sch)
    stl_schreiben(os.path.join(ziel, name), alle, name)
    vol = sum(volumen(e[0] if isinstance(e, tuple) else e)
              for e in schalen)
    print("%-36s %3d Schalen %6d Dreiecke  ~%6.1f cm3  offene Kanten: %d"
          % (name, len(schalen), len(alle), vol / 1000.0, fehler))
    return fehler


def main():
    g = abgeleitet()
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    os.makedirs(ziel, exist_ok=True)

    print("Koffer aussen: %.0f x %.0f x %.0f mm (ohne Griff), innen %.0f x %.0f x %.0f"
          % (g["aussen_x"], g["aussen_y"],
             BODEN + g["wanne_innen_h"] + DECKEL_INNEN + BODEN,
             g["innen_x"], g["innen_y"], g["innen_h"]))
    print("Fach Controller: %.0f x %.0f | Fach Auto-Box: %.0f x %.0f "
          "(Rippen schlucken +/- %.0f mm)\n"
          % (g["fachC_l"], g["fachC_t"], g["fachA_l"], g["fachA_t"], KLEMMWEG))

    fehler = 0
    fehler += bauen(ziel, "rcbox_1_wanne_1x_drucken.stl", teil_wanne(g))
    fehler += bauen(ziel, "rcbox_2_deckel_1x_drucken.stl", teil_deckel(g))
    griff = teil_griff(g)
    # flach legen: Buegelebene (YZ) aufs Bett -> (x,y,z) -> (y, z, x+8)
    griff_flach = [[tuple((y_, z_, x_ + 8.0) for (x_, y_, z_) in tri)
                    for tri in s_] for s_ in griff]
    fehler += bauen(ziel, "rcbox_3_griff_1x_drucken.stl", griff_flach)
    fehler += bauen(ziel, "rcbox_4_achsstift_2x_drucken.stl", teil_stift(g))

    if fehler:
        raise SystemExit("FEHLER: %d offene Kanten" % fehler)
    print("\nAlle Schalen wasserdicht.")


if __name__ == "__main__":
    main()
