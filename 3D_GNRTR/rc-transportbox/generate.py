#!/usr/bin/env python3
"""
Transportkoffer fuer das Hot Wheels RC 1:64 (Lamborghini Temerario):
Auto in der Originalbox + Pistolengriff-Controller, so kompakt wie
moeglich, verschliessbar; Steck-Tragegriff optional (--mit-griff).

Drei Teile (vier mit Griff):
  1. WANNE   -- Unterteil mit zwei Faechern (Controller liegend, Auto-Box
                liegend), Klemmrippen, Scharnieraugen hinten, Rastkeilen
                vorn.
  2. DECKEL  -- mit Blattfeder-Boegen (halten den Inhalt nieder),
                Schnappzungen vorn, Scharnieraugen hinten -- aussen
                glatt. Nur mit --mit-griff kommen zwei T-Nut-Bloecke
                an den Wandring.
  3. ACHSSTIFT (2x) -- Scharnierstifte.
  4. GRIFF (optional) -- Buegel mit T-Fuessen, wird von unten in die
                Nuten geschoben; beim Tragen ziehen die Fuesse gegen
                das Blindende der Nut (Formschluss).

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

import argparse
import math
import re
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
# Das Rad steht (Controller von hinten gesehen) nach RECHTS ueber -- liegend
# mit Rad oben liegt er also auf seiner linken Gehaeuseseite. Durchmesser
# und Laengsposition sind bis zur Messung aus dem Foto geschaetzt; sie
# steuern nur, wo im Deckel Freiraum bleiben muss.
RAD_D = 45.0              # Durchmesser des Drehrads (gemessen)
RAD_RAND_LINKS = 77.0     # Radkante von links in der Breitenachse (gemessen)
RAD_FREI = 4.0            # Sicherheitsabstand der Federn zum Radrand

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
# Radgeometrie in Rohkoordinaten, ruecklaufend aus der Messung bestimmt:
# Raddurchmesser 45 mm, Raender in der 131er Achse 77 mm / 10 mm. Die
# Summe 77+45+10 = 132 gegen 131 gemessene Breite zeigt ~1 mm Messstreuung,
# die Werte liegen deshalb mittig dazwischen (ergibt 76.4 / 9.6).
RAD_CX, RAD_CY, RAD_R = 75.5, 20.0, 17.2
CTRL_FOTO_LAENGE = 169.8   # y-Spanne der Foto-Silhouette (Radkante-Griffende)
CTRL_FOTO_RAD    = 40.0    # Rad-Durchmesser laut Foto
MULDE_LUFT = 4.0           # Offset der Mulde um die Silhouette (Rippenraum)
MULDE_HOEHE = 30.0         # Tiefe der Konturmulde (fuehrt das Gehaeuse)

KLEMMWEG   = 4.0      # was die Rippen je Seite schlucken koennen

# ---------------------------------------------------------------------------
# Parameter: Koffer
# ---------------------------------------------------------------------------

# Wandstaerke: 4.0 statt der sonst ueblichen 2.8, weil der Stufenfalz die
# Wand oben teilt -- 2.0 mm bleiben an der Wanne stehen, 1.5 mm bekommt die
# Deckellippe, dazwischen 0.5 mm Spiel.
WAND       = 4.0      # Wandstaerke aussen
BODEN      = 3.0
ECKRADIUS  = 12.0     # Aussenecken (smooth!)
TRENNWAND  = 3.0

RIPPE_DICK = 1.1      # Klemmrippen: duenn genug zum Federn
RIPPE_TIEF = 5.0      # wie weit sie ins Fach ragen
RIPPE_BREIT = 8.0     # Auflagebreite pro Rippe

# Stufenfalz: der Deckel traegt eine umlaufende Lippe, die in eine
# Aussparung an der Wanneninnenkante greift. Aussen bleibt die Fuge eine
# saubere Linie (beide Waende buendig), innen ist der Deckel gefuehrt,
# kann nicht seitlich verrutschen und die Fuge ist staubdicht.
FALZ_H     = 9.0      # wie tief die Lippe in die Wanne greift
FALZ_T     = 2.0      # Ruecksprung der Wanneninnenkante (Falzbreite)
FALZ_SP    = 0.25     # Spiel je Seite zwischen Lippe und Falz

# Der Controller ragt jetzt weniger in den Deckel (die Wanne ist um die
# Falzzone hoeher), der Deckel darf also flacher werden.
DECKEL_INNEN = 21.0   # lichte Hoehe im Deckel
KANTE_R    = 3.0      # Verrundung der Deckeloberkante (Loft-Einzug)

# Deckellogo: SVG (bevorzugt) oder Bilddatei neben generate.py. Das Logo
# wird als eigenes Bauteil buendig in die Deckelaussenflaeche eingelassen
# -- gleiche Hoehe, andere Farbe. Deckel und Logo kommen als zwei STLs
# mit identischem Ursprung: in Bambu Studio beide laden, die Frage nach
# dem mehrteiligen Objekt mit JA beantworten, dem Logoteil Filament 2
# zuweisen. Auf texturierter Platte bekommen beide dasselbe Muster.
LOGO_DATEI  = "logo.png"
LOGO_BREITE = 130.0   # mm ueber die Deckelmitte
LOGO_TIEFE  = 0.6     # 3 Lagen bei 0,2 mm -- deckt sauber in Farbe 2

CTRL_FED_DICK = 1.4   # Laengsfeder am Kopfende der Controllermulde
CTRL_FED_HUB  = 15.0  # Hub -- deckt den unbekannten Radueberstand ab

FEDER_DICK = 1.0      # Blattfeder-Boegen im Deckel
FEDER_HUB  = 18.0     # wie weit sie unter die Deckeldecke ragen

# Scharnier: durchgehendes Klavierband ueber die ganze Rueckseite statt
# zweier kurzer Augen. Zwei 12-mm-Nasen trugen den Deckel auf 24 mm
# Gesamtbreite -- zu wenig, wenn der volle Koffer am Deckel haengt. Jetzt
# tragen vier Wannensegmente auf rund 100 mm, und der Stift ist dicker.
SCHARNIER_AUGE = 11.0     # Augen-Aussenmass (Raute)
SCHARNIER_SEG  = 7        # Segmente ueber die Breite (Wanne 4, Deckel 3)
SCHARNIER_BAND = 180.0    # Gesamtbreite des Bands
SCHARNIER_LUFT = 0.5      # Luft zwischen Wannen- und Deckelsegment

# Achse: ein Stueck ROHES FILAMENT (1,75 mm) statt eines gedruckten
# Stifts. Es ist gezogen und homogen, hat eine glatte runde Oberflaeche
# (bessere Achse als jeder Druck) und kostet nichts. Tragfaehig ist es,
# weil das Band vielfach gelagert ist: frei biegen kann sich die Achse
# nur ueber die Segmentspalte von SCHARNIER_LUFT, die Last laeuft als
# Scherung durch die Uebergaenge.
FILAMENT_D  = 1.75
LOCH_ACHSE  = 2.2         # Drehsitz fuer 1,75er Filament (liegend gedruckt)
SENKUNG_D   = 4.0         # Ansenkung am Eintritt: dort versinkt der
SENKUNG_T   = 2.5         # verschmolzene Filamentkopf
SACK_T      = 3.0         # Restwand am Blindende (haelt die Achse)

# Alternative, nur mit --gedruckter-stift:
GEDRUCKTER_STIFT = False
STIFT_D    = 5.0
LOCH_DREH  = 5.3          # Wannenauge (drehbar)
LOCH_PRESS = 4.8          # Deckelauge (Presssitz)

ZUNGE_BREIT = 26.0    # Schnappzungen vorn (tragen den Deckel)
ZUNGE_DICK  = 1.4
ZUNGE_LANG  = 16.0
HAKEN       = 1.8   # ergibt 1.4 mm Rasteingriff

# Tragegriff: standardmaessig AUS. Die T-Nut-Bloecke stehen aussen am
# Deckelring vor und machen den Koffer 18 mm tiefer -- der geschlossene
# Koffer ist mit 213 x 212 x 66 mm und rund 0,8 kg bequem an den Seiten
# zu greifen. Mit --mit-griff werden Nuten und Buegel wieder erzeugt.
MIT_GRIFF = False
GRIFF_BREIT = 90.0    # lichte Grifflaenge
GRIFF_HOCH  = 24.0
GRIFF_PROFIL = 12.0   # Querschnitt des Buegels
SCHWALBE_SP = 0.25    # Spiel der Griff-Schwalbe

# Zusatzfaecher fuer lose Hot Wheels 1:64. Ausgelegt auf das laengste
# Auto des Nutzers (gemessen 88 x 35 x 30); kuerzere Autos haelt die
# Stirnfeder, schmalere die Klemmrippen.
HW_L, HW_B, HW_H = 88.0, 35.0, 30.0
HW_LUFT   = 1.5     # je Seite -> lichtes Fach = Auto + 2 x Luft
HW_WAND   = 2.5     # Fachwand
HW_ECKE   = 5.0     # Eckradius der Faecher (rund, wie gewuenscht)
HW_FEDER  = 1.2     # Stirn-Blattfeder: Dicke
HW_FED_HUB = 8.0    # Hub der Stirnfeder -> haelt auch 80-mm-Autos

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
    pts = [((x - min(xs)) * sx, (ymax - y) * sy) for (x, y) in pts]
    return kopf_glaetten(pts)


def kopf_glaetten(pts, bis=16):
    """Kopfbereich (Gehaeusekopf + Drehrad) durch seine konvexe Huelle
    ersetzen.

    Aus dem Tray-Foto abgenommen hatte die Kontur zwischen Radbogen und
    Gehaeusekopf eine Taille -- das Rad stand als Nase ab. Auf den Fotos
    des Controllers sitzt es buendig am Kopf. Die Huelle trifft das
    besser als eine geratene Einschnuerung und macht die Mulde dort nur
    weiter, nie enger. Die Kerbe zwischen Rad und Griff bleibt
    unangetastet -- dort liegt das Hot-Wheels-Fach.
    """
    kopf, rest = pts[:bis + 1], pts[bis + 1:]

    def kreuz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    kette = []
    for q in sorted(kopf):
        while len(kette) >= 2 and kreuz(kette[-2], kette[-1], q) >= 0:
            kette.pop()
        kette.append(q)
    # obere Kette, von links nach rechts = Umlaufrichtung der Kontur
    if kette[0] != kopf[0]:
        kette = kette[::-1]
    return kette + rest


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
    # Bezugspunkte ueber ihre LAGE bestimmen, nicht ueber Konturindizes:
    # das Glaetten des Kopfes aendert die Punktzahl, Indizes waeren still
    # falsch geworden.
    k = g["kontur"]
    kx = [x for (x, _) in k]
    ky = [y for (_, y) in k]
    x0k, y0k = min(kx), min(ky)
    # Radmitte aus den GEMESSENEN Werten: Radrand 77 mm von links, 10 mm
    # von rechts, Durchmesser 45; in der Laengsachse gibt das Rad das
    # Ende vor (die 190 wurden ab Radkante gemessen).
    g["rad_pos"] = (x0k + RAD_RAND_LINKS + RAD_D / 2.0,
                    y0k + CTRL_LAENGE - RAD_D / 2.0)
    griffpts = [q for q in k if q[1] < y0k + 0.16 * CTRL_LAENGE]
    g["griff_pos"] = (sum(x for x, _ in griffpts) / len(griffpts),
                      sum(y for _, y in griffpts) / len(griffpts))
    schnauzpts = [q for q in k if q[0] < x0k + 0.22 * CTRL_BREITE]
    g["schnauz_pos"] = (sum(x for x, _ in schnauzpts) / len(schnauzpts),
                        sum(y for _, y in schnauzpts) / len(schnauzpts))
    # Klemmrippen: an allen Konturpunkten AUSSER im Radbereich. Das Rad
    # reicht von z=12 bis 57 -- eine Rippe wuerde dort auf das Drehrad
    # druecken statt auf das Gehaeuse.
    g["rippen_idx"] = [i for i, q in enumerate(k)
                       if q[1] < y0k + 0.78 * CTRL_LAENGE]
    g["fachC_l"] = max(xs) - min(xs) + 2 * steg
    g["fachC_t"] = max(ys) - min(ys) + 2 * steg
    g["fachA_l"] = AUTOBOX_B + zuschlag          # Box liegt quer: B in X
    g["fachA_t"] = AUTOBOX_L + zuschlag

    g["innen_x"] = g["fachC_l"] + TRENNWAND + g["fachA_l"]
    g["innen_y"] = max(g["fachC_t"], g["fachA_t"])
    # Die Wanne besteht innen aus zwei Zonen: unten die Muldenzone (dort
    # sitzen Fuellschale, Trennwand, Bloecke und Rippen), darueber die
    # Falzzone, die vollstaendig frei bleiben MUSS -- dort greift die
    # Deckellippe ein. Wuerde ein Innenteil in die Falzzone ragen, liesse
    # sich der Deckel nicht schliessen.
    g["wanne_innen_h"] = MULDE_HOEHE + FALZ_H
    g["z_fach"] = MULDE_HOEHE
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

    # Die Auto-Box sitzt nicht mehr mittig, sondern ganz HINTEN im rechten
    # Fach. Damit wird aus den zwei ungenutzten Streifen (je 48 mm) vorn
    # ein Stueck von 96 mm -- gerade genug fuer ein Hot-Wheels-Fach.
    g["fachA_y1"] = g["innen_y"] / 2.0
    g["fachA_y0"] = g["fachA_y1"] - g["fachA_t"]

    # Zusatzfaecher fuer lose Hot Wheels (LICHTE Masze).
    hb, hl = HW_B + 2 * HW_LUFT, HW_L + 2 * HW_LUFT
    ix, iy = g["innen_x"] / 2.0, g["innen_y"] / 2.0
    # Fach A: in den Keil zwischen Rad- und Griffkontur, vorn links.
    ax0 = -ix + HW_WAND
    ay0 = -iy + HW_WAND
    # Fach B: vorn im rechten Fach, vor der Auto-Box, in x mittig.
    bxm = (g["fachA_x0"] + g["fachA_x1"]) / 2.0
    by1 = g["fachA_y0"] - HW_WAND
    g["hw"] = [(ax0, ax0 + hb, ay0, ay0 + hl),
               (bxm - hb / 2.0, bxm + hb / 2.0, by1 - hl, by1)]
    g["hw_licht"] = (hb, hl)

    # Scharnierband: SCHARNIER_SEG gleich breite Segmente, abwechselnd
    # Wanne / Deckel. Wanne bekommt die geraden Indizes (aussen 0 und
    # SEG-1, damit die Bandenden an der Wanne sitzen und der Deckel
    # dazwischen gefuehrt wird).
    sb = (SCHARNIER_BAND - (SCHARNIER_SEG - 1) * SCHARNIER_LUFT) / SCHARNIER_SEG
    g["schar_breite"] = sb
    g["schar_wanne"], g["schar_deckel"] = [], []
    for i in range(SCHARNIER_SEG):
        x0 = -SCHARNIER_BAND / 2.0 + i * (sb + SCHARNIER_LUFT)
        (g["schar_wanne"] if i % 2 == 0 else g["schar_deckel"]).append(x0)
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

def hw_feder(x0, x1, y_wand, s, z1):
    """Blattfeder quer im Hot-Wheels-Fach: Fuesse in der Stirnwand,
    Scheitel ragt HW_FED_HUB ins Fach. s = +1/-1 (Richtung ins Fach).
    Die Biegung liegt in der Lagenebene -- Zug in XY, nicht ueber die
    Lagenhaftung."""
    n = 20
    vorn, hint = [], []
    for i in range(n + 1):
        t = i / n
        vorn.append((x0 + (x1 - x0) * t,
                     y_wand + s * math.sin(math.pi * t) * HW_FED_HUB))
    for i in range(n + 1):
        t = 1.0 - i / n
        hint.append((x0 + (x1 - x0) * t,
                     y_wand - s * HW_FEDER
                     + s * math.sin(math.pi * t) * HW_FED_HUB))
    return prisma(vorn + hint, 0.0, z1)


def _svg_pfad_punkte(d, feinheit=0.35):
    """SVG-Pfaddaten in Punktlisten wandeln (eine je Subpath).

    Unterstuetzt M/L/H/V/C/S/Q/T/Z in Gross- und Kleinschreibung. Beziers
    werden abgetastet; `feinheit` ist der Zielabstand der Stuetzpunkte in
    Nutzereinheiten. Bogenbefehle (A) kommen in Logos praktisch nicht vor
    und werden als Gerade genaehert -- der Aufrufer bekommt eine Warnung.
    """
    import re
    zahlen = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
    befehle = re.findall(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)",
                         d)
    pfade, akt = [], []
    x = y = 0.0
    start = (0.0, 0.0)
    letzter_c = letzter_q = None
    warnung = [False]

    def bez(p0, p1, p2, p3):
        laenge = (math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3))
        n = max(4, min(80, int(laenge / max(feinheit, 0.05))))
        for i in range(1, n + 1):
            t = i / n
            u = 1.0 - t
            akt.append((u * u * u * p0[0] + 3 * u * u * t * p1[0]
                        + 3 * u * t * t * p2[0] + t * t * t * p3[0],
                        u * u * u * p0[1] + 3 * u * u * t * p1[1]
                        + 3 * u * t * t * p2[1] + t * t * t * p3[1]))

    for kmd, rest in befehle:
        w = [float(v) for v in zahlen.findall(rest)]
        rel = kmd.islower()
        k = kmd.upper()
        if k == "Z":
            if len(akt) > 2:
                pfade.append(akt)
            akt = []
            x, y = start
            continue
        i = 0
        while i < len(w) or (k == "M" and i == 0 and not w):
            if k == "M":
                nx, ny = w[i] + (x if rel else 0.0), w[i + 1] + (y if rel else 0.0)
                if len(akt) > 2:
                    pfade.append(akt)
                akt = [(nx, ny)]
                x, y, start = nx, ny, (nx, ny)
                i += 2
                k = "L"           # weitere Paare nach M sind Linien
            elif k == "L":
                x, y = w[i] + (x if rel else 0.0), w[i + 1] + (y if rel else 0.0)
                akt.append((x, y))
                i += 2
            elif k == "H":
                x = w[i] + (x if rel else 0.0)
                akt.append((x, y))
                i += 1
            elif k == "V":
                y = w[i] + (y if rel else 0.0)
                akt.append((x, y))
                i += 1
            elif k in ("C", "S"):
                if k == "C":
                    p1 = (w[i] + (x if rel else 0.0), w[i + 1] + (y if rel else 0.0))
                    p2 = (w[i + 2] + (x if rel else 0.0), w[i + 3] + (y if rel else 0.0))
                    p3 = (w[i + 4] + (x if rel else 0.0), w[i + 5] + (y if rel else 0.0))
                    i += 6
                else:
                    p1 = (2 * x - letzter_c[0], 2 * y - letzter_c[1]) \
                        if letzter_c else (x, y)
                    p2 = (w[i] + (x if rel else 0.0), w[i + 1] + (y if rel else 0.0))
                    p3 = (w[i + 2] + (x if rel else 0.0), w[i + 3] + (y if rel else 0.0))
                    i += 4
                bez((x, y), p1, p2, p3)
                letzter_c, letzter_q = p2, None
                x, y = p3
            elif k in ("Q", "T"):
                if k == "Q":
                    q = (w[i] + (x if rel else 0.0), w[i + 1] + (y if rel else 0.0))
                    p3 = (w[i + 2] + (x if rel else 0.0), w[i + 3] + (y if rel else 0.0))
                    i += 4
                else:
                    q = (2 * x - letzter_q[0], 2 * y - letzter_q[1]) \
                        if letzter_q else (x, y)
                    p3 = (w[i] + (x if rel else 0.0), w[i + 1] + (y if rel else 0.0))
                    i += 2
                # quadratisch -> kubisch
                bez((x, y), (x + 2.0 / 3 * (q[0] - x), y + 2.0 / 3 * (q[1] - y)),
                    (p3[0] + 2.0 / 3 * (q[0] - p3[0]),
                     p3[1] + 2.0 / 3 * (q[1] - p3[1])), p3)
                letzter_q, letzter_c = q, None
                x, y = p3
            elif k == "A":
                warnung[0] = True
                x, y = w[i + 5] + (x if rel else 0.0), w[i + 6] + (y if rel else 0.0)
                akt.append((x, y))
                i += 7
            else:
                break
    if len(akt) > 2:
        pfade.append(akt)
    if warnung[0]:
        print("  Hinweis: Bogenbefehle (A) im SVG wurden als Gerade "
              "genaehert -- Kontur pruefen.")
    return pfade


def _svg_fuellfarbe(el, ns):
    """Fuellfarbe eines Elements: fill-Attribut oder style="fill:..."."""
    f = (el.get("fill") or "").strip().lower()
    if not f:
        stil = el.get("style") or ""
        tref = re.search(r"fill\s*:\s*([^;]+)", stil)
        f = tref.group(1).strip().lower() if tref else ""
    if f in ("", "none", "currentcolor"):
        return None
    return f


def svg_farbgruppen(pfad, breite_mm, mitte=(0.0, 0.0)):
    """SVG -> Bauteile je Fuellfarbe, fuer den AMS-Druck.

    Jeder Pfad behaelt seine Farbe. Innerhalb eines Pfades trennen die
    Subpaths ueber ihre Verschachtelung Flaeche und Loch. Zwischen
    Pfaden gilt die Zeichenreihenfolge: was spaeter kommt, liegt oben --
    seine Flaechen werden deshalb aus den frueheren Farben
    HERAUSGESTANZT. Sonst lagen zwei Koerper im selben Raum und der
    Slicer muesste raten, welche Farbe gewinnt.

    Rueckgabe: Liste von (farbe, [(flaeche, [loecher]), ...]) in
    Zeichenreihenfolge.
    """
    import xml.etree.ElementTree as ET

    baum = ET.parse(pfad)
    ns = "{http://www.w3.org/2000/svg}"
    gruppen = []          # (farbe, [subpath, ...]) in Zeichenreihenfolge
    for el in baum.getroot().iter():
        tag = el.tag.replace(ns, "")
        teile = []
        if tag == "path" and el.get("d"):
            teile = _svg_pfad_punkte(el.get("d"))
        elif tag == "polygon" and el.get("points"):
            zahlen = [float(v) for v in
                      re.findall(r"[-+]?(?:\d*\.\d+|\d+\.?)", el.get("points"))]
            teile = [list(zip(zahlen[0::2], zahlen[1::2]))]
        elif tag == "rect":
            x0 = float(el.get("x", 0)); y0 = float(el.get("y", 0))
            b = float(el.get("width", 0)); h = float(el.get("height", 0))
            teile = [[(x0, y0), (x0 + b, y0), (x0 + b, y0 + h), (x0, y0 + h)]]
        if teile:
            gruppen.append((_svg_fuellfarbe(el, ns) or "#000000", teile))
    if not gruppen:
        raise SystemExit("FEHLER: keine Pfade in %s" % pfad)

    alle = [p for (_, t) in gruppen for p in t]
    xs = [q[0] for k in alle for q in k]
    ys = [q[1] for k in alle for q in k]
    skala = breite_mm / (max(xs) - min(xs))
    cx, cy = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0

    def um(k):
        p = [((x - cx) * skala + mitte[0], (cy - y) * skala + mitte[1])
             for (x, y) in k]
        if len(p) > 2 and math.dist(p[0], p[-1]) < 0.05:
            p = p[:-1]
        return p if len(p) > 2 and abs(flaeche_signiert(p)) >= 2.0 else None

    # Schritt 1: je Farbgruppe Flaechen und eigene Loecher
    roh = []
    for farbe, teile in gruppen:
        polys = [q for q in (um(k) for k in teile) if q]
        flaechen, loecher = [], []
        for i, q in enumerate(polys):
            tiefe = sum(1 for j, r in enumerate(polys)
                        if j != i and punkt_in_polygon(q[0], r))
            (loecher if tiefe % 2 else flaechen).append(q)
        if flaechen:
            roh.append((farbe, flaechen, loecher))

    # Schritt 2: spaetere Farben aus frueheren stanzen
    ergebnis = []
    for i, (farbe, flaechen, loecher) in enumerate(roh):
        spaeter = [f for (_, fs, _) in roh[i + 1:] for f in fs]
        teile = []
        for f in flaechen:
            drin = [h for h in loecher if punkt_in_polygon(h[0], f)]
            drin += [sp for sp in spaeter if punkt_in_polygon(sp[0], f)]
            teile.append((f, drin))
        ergebnis.append((farbe, teile))
    return ergebnis


def svg_konturen(pfad, breite_mm, mitte=(0.0, 0.0)):
    """Die Aussparung fuer den Deckel: aeussere Umrisse und echte Loecher.

    Ausgespart wird die Silhouette des ganzen Logos -- also nur die
    Konturen, die in keiner anderen Flaeche liegen. Eine zweite Farbe
    liegt IN der ersten und darf hier nicht als eigenes Loch auftauchen,
    sonst muesste die Brueckentriangulierung ein Loch im Loch bauen.
    Stehen bleibt Deckelmaterial nur in Loechern, die keine Farbe fuellt
    -- etwa im O von HOT.
    """
    gruppen = svg_farbgruppen(pfad, breite_mm, mitte)
    alle = [f for (_, teile) in gruppen for (f, _) in teile]
    aussen = [f for f in alle
              if not any(punkt_in_polygon(f[0], q) for q in alle if q is not f)]
    inseln = []
    for (_, teile) in gruppen:
        for (f, loecher) in teile:
            for h in loecher:
                if any(h is q for q in alle):
                    continue                     # das ist eine andere Farbe
                if not any(punkt_in_polygon(q[0], h) for q in alle if q is not f):
                    inseln.append(h)
    return aussen, inseln


_LOGO_CACHE = []


def logo_flaechen(g):
    """Logokonturen fuer den Deckel, oder None wenn keine Datei da ist.

    Die Bilddatei liegt neben generate.py (LOGO_DATEI). Fehlt sie, wird
    der Deckel schlicht glatt -- der Generator laeuft trotzdem durch."""
    if _LOGO_CACHE:
        return _LOGO_CACHE[0]
    ordner = os.path.dirname(os.path.abspath(__file__))
    treffer = None
    for name in (LOGO_DATEI, "logo.svg", "logo.png", "logo.jpg"):
        pfad = os.path.join(ordner, name)
        if os.path.exists(pfad):
            if pfad.lower().endswith(".svg"):
                g["logo_gruppen"] = svg_farbgruppen(pfad, LOGO_BREITE)
                treffer = svg_konturen(pfad, LOGO_BREITE)
            else:
                treffer = logo_konturen(pfad, LOGO_BREITE)
                g["logo_gruppen"] = [("#000000",
                                      [(f, [h for h in treffer[1]
                                            if punkt_in_polygon(h[0], f)])
                                       for f in treffer[0]])]
            g["logo_datei"] = os.path.basename(pfad)
            break
    _LOGO_CACHE.append(treffer)
    return treffer


def logo_konturen(pfad, breite_mm, mitte=(0.0, 0.0), glaettung=0.9):
    """Bilddatei -> Polygone fuer das eingebrannte Deckellogo.

    Alles, was nicht (nahezu) weiss ist, gilt als Logo. Die Konturen
    kommen aus einer Marching-Squares-Extraktion und werden per
    Douglas-Peucker vereinfacht -- sonst haette jede Pixelkante einen
    Punkt und die STL Hunderttausende Dreiecke.

    Rueckgabe: (flaechen, inseln). `flaechen` sind die Umrisse der
    Logoteile (sie werden in die erste Schicht des Deckels als
    Aussparung gestanzt), `inseln` die Loecher darin -- etwa im O von
    HOT --, die als eigene Prismen wieder aufgefuellt werden.
    """
    from PIL import Image
    import numpy as np
    from skimage import measure

    bild = Image.open(pfad).convert("L")
    a = np.asarray(bild, dtype=float)
    maske = (a < 235).astype(float)          # nicht-weiss = Logo
    if maske.sum() < 50:
        raise SystemExit("FEHLER: %s enthaelt kaum dunkle Pixel" % pfad)
    roh = measure.find_contours(maske, 0.5)
    hoehe, breite = maske.shape
    skala = breite_mm / float(breite)
    polys = []
    for k in roh:
        k = measure.approximate_polygon(k, tolerance=glaettung)
        if len(k) < 4:
            continue
        # (Zeile, Spalte) -> (x, y), y nach oben, um die Mitte zentriert
        poly = [((c - breite / 2.0) * skala + mitte[0],
                 (hoehe / 2.0 - r) * skala + mitte[1]) for (r, c) in k]
        if poly[0] == poly[-1]:
            poly = poly[:-1]
        if abs(flaeche_signiert(poly)) < 4.0:      # Rauschen
            continue
        polys.append(poly)
    # Aussen oder Insel ueber die VERSCHACHTELUNG bestimmen, nicht ueber
    # das Vorzeichen der Flaeche: die Bildkoordinaten werden in y
    # gespiegelt, damit kippt jede Orientierung.
    flaechen, inseln = [], []
    for i, p in enumerate(polys):
        tiefe = sum(1 for j, q in enumerate(polys)
                    if j != i and punkt_in_polygon(p[0], q))
        (inseln if tiefe % 2 else flaechen).append(p)
    if not flaechen:
        raise SystemExit("FEHLER: keine Logokontur in %s gefunden" % pfad)
    return flaechen, inseln


def sehnenfeder(pa, pb, richtpunkt, hub, dick, z0, z1):
    """Blattfeder als Bogen ueber der Sehne pa->pb, Scheitel um `hub` in
    Richtung `richtpunkt` ausgelenkt. Die Fuesse liegen `dick` tief in der
    Wand, damit sie angebunden sind. Biegung in der Lagenebene."""
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    mx, my = (pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0
    if (richtpunkt[0] - mx) * nx + (richtpunkt[1] - my) * ny < 0:
        nx, ny = -nx, -ny
    n = 24
    vorn, hint = [], []
    for i in range(n + 1):
        t = i / n
        b = math.sin(math.pi * t) * hub
        vorn.append((pa[0] + dx * t + nx * b, pa[1] + dy * t + ny * b))
    for i in range(n + 1):
        t = 1.0 - i / n
        b = math.sin(math.pi * t) * hub - dick
        hint.append((pa[0] + dx * t + nx * b, pa[1] + dy * t + ny * b))
    return prisma(vorn + hint, z0, z1)


def ctrl_feder(g, z1, mx0=None, my0=None):
    """Laengsfeder am Kopfende der Controllermulde.

    Das Drehrad sitzt OBEN auf dem Gehaeuse (z = 42..57) und ragt in
    Laengsrichtung ueber die Gehaeusekante hinaus. In der Muldenzone
    (z = 0..30) ist dort also nur Gehaeuse -- die Mulde reicht aber bis
    zur Radkante, der Controller koennte um den Radueberstand nach vorn
    wandern. Wie weit das Rad genau uebersteht, ist aus Fotos nicht
    sicher zu messen; statt es zu raten, drueckt diese Feder den
    Controller gegen die Wand am Griffende. Die ist eine echte
    Gehaeusekante -- damit ist die Laengslage definiert, egal wie der
    Radueberstand ausfaellt."""
    if mx0 is None:
        mx0, my0 = g["fachC_x0"], -g["fachC_t"] / 2.0
    mulde = [(x + mx0, y + my0) for (x, y) in g["mulde"]]
    ys = [p[1] for p in mulde]
    grenze = min(ys) + 0.80 * (max(ys) - min(ys))
    kopf = [p for p in mulde if p[1] > grenze]
    if len(kopf) < 2:
        return []
    pa = min(kopf, key=lambda p: p[0])
    pb = max(kopf, key=lambda p: p[0])
    mitte = (sum(p[0] for p in mulde) / len(mulde),
             sum(p[1] for p in mulde) / len(mulde))
    L = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
    dehnung = 3.0 * CTRL_FED_DICK * CTRL_FED_HUB / (2.0 * L * L)
    if dehnung > 0.04:
        raise SystemExit("FEHLER: Controllerfeder %.1f %% Randdehnung "
                         "(max 4) -- Hub verkleinern oder Sehne verlaengern"
                         % (100 * dehnung))
    return [sehnenfeder(pa, pb, mitte, CTRL_FED_HUB, CTRL_FED_DICK,
                        0.0, z1)]


def hw_kontur(x0, x1, y0, y1):
    """Lichte Fachkontur (Rundrechteck) an ihrer Einbaustelle."""
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    return [(px + cx, py + cy)
            for px, py in rundrechteck(x1 - x0, y1 - y0, HW_ECKE)]


def hw_fach(x0, x1, y0, y1, z1, feder_vorn=True, rahmen=True):
    """Ein Einzelfach fuer ein loses Hot Wheels (x0..x1, y0..y1 = LICHTE
    Masze): zwei Klemmrippen je Laengsseite und eine Stirnfeder, die auch
    kuerzere Autos gegen die Gegenseite drueckt.

    rahmen=True baut die Fachwand als eigenen Ring -- richtig, wo das Fach
    frei im Kofferinneren steht. rahmen=False, wenn das Fach als LOCH in
    einer Fuellschale sitzt: dort liefert die Fuellung das Material
    rundum, ein zusaetzlicher Ring waere nicht nur ueberfluessig, das
    Fachinnere bliebe massiv."""
    schalen = []
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    bx, by = x1 - x0, y1 - y0
    if rahmen:
        innen = hw_kontur(x0, x1, y0, y1)
        aussen = [(px + cx, py + cy) for px, py in
                  rundrechteck(bx + 2 * HW_WAND, by + 2 * HW_WAND,
                               HW_ECKE + HW_WAND)]
        schalen.append(loch_prisma(aussen, innen, 0.0, z1))
    for dy in (-by * 0.26, by * 0.26):
        schalen.append(rippe(x0, cy + dy, "+x", 0.0, z1))
        schalen.append(rippe(x1, cy + dy, "-x", 0.0, z1))
    if feder_vorn:
        schalen.append(hw_feder(x0 + 4.0, x1 - 4.0, y0, +1.0, z1))
    else:
        schalen.append(hw_feder(x0 + 4.0, x1 - 4.0, y1, -1.0, z1))
    return schalen


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


def scharnier_auge(loch_d, laenge, sack=0.0, senkung=0.0):
    """Auge des Scharnierbands: Raute aussen, Tropfenloch innen, Achse
    entlang X, x = 0..laenge. Gibt eine LISTE von Schalen zurueck.

    sack > 0: die letzten `sack` mm bleiben massiv -- ein Blindende, gegen
    das die Achse laeuft, damit sie nicht durchrutschen kann.
    senkung > 0: die ersten `senkung` mm haben ein aufgeweitetes Loch;
    dort versinkt der verschmolzene Kopf des Filaments, aussen bleibt die
    Flaeche buendig."""
    a = raute(SCHARNIER_AUGE / 2.0)
    teile = []
    x0 = 0.0
    if senkung > 0.0:
        teile.append(loch_prisma(a, tropfen(SENKUNG_D / 2.0), 0.0, senkung))
        x0 = senkung
    teile.append(loch_prisma(a, tropfen(loch_d / 2.0), x0, laenge - sack))
    if sack > 0.0:
        teile.append(prisma(a, laenge - sack, laenge))
    return [dreh_z90(dreh_x90(t)) for t in teile]


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
    # Wandring, zweiteilig: unten volle Wandstaerke, oben die Falzstufe.
    # In der Stufe (die obersten FALZ_H mm) springt die Innenkante um
    # FALZ_T nach aussen -- genau dort sitzt spaeter die Deckellippe.
    r_i = max(2.0, ECKRADIUS - WAND)
    innen_falz = rundrechteck(g["innen_x"] + 2 * FALZ_T,
                              g["innen_y"] + 2 * FALZ_T, r_i + FALZ_T)
    schalen.append(loch_prisma(aussen, innen, 0.0, g["z_fach"]))
    schalen.append(loch_prisma(aussen, innen_falz,
                               g["z_fach"], g["wanne_innen_h"]))

    # Trennwand
    tw = [(g["fachC_x1"], -g["innen_y"] / 2), (g["fachC_x1"] + TRENNWAND, -g["innen_y"] / 2),
          (g["fachC_x1"] + TRENNWAND, g["innen_y"] / 2), (g["fachC_x1"], g["innen_y"] / 2)]
    schalen.append(prisma(tw, 0.0, g["z_fach"]))

    z1 = g["z_fach"]          # Oberkante aller Innenteile
    z_rand = g["wanne_innen_h"]   # Oberkante der Wannenwand

    # Die Auto-Box liegt hinten im rechten Fach; davor sitzt das
    # Hot-Wheels-Fach B. Ein Fuellblock ist nicht mehr noetig -- die
    # Rueckwand von Fach B ist zugleich der Anschlag der Box.

    # Zusatzfaecher fuer lose Hot Wheels
    for i, (hx0, hx1, hy0, hy1) in enumerate(g["hw"]):
        schalen.extend(hw_fach(hx0, hx1, hy0, hy1, z1, feder_vorn=(i == 0),
                               rahmen=(hx1 > g["fachC_x1"])))

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
    # Loecher der Fuellschale: die Controllermulde -- und jedes
    # Hot-Wheels-Fach, das im Controllerfach liegt. Ohne dieses zweite
    # Loch stuende die Fachwand zwar da, das Fach waere aber bis oben
    # massiv gefuellt (der Fehler, der beim Durchsehen der Ansicht auffiel).
    loecher = [mulde_pos]
    for (hx0, hx1, hy0, hy1) in g["hw"]:
        if hx1 <= g["fachC_x1"]:
            loecher.append(hw_kontur(hx0, hx1, hy0, hy1))
    schalen.append((prisma_mit_loechern(fachrect, loecher,
                                        0.0, MULDE_HOEHE), True))
    g["fuellung"] = (fachrect, loecher)

    # Laengsfeder am Kopfende: drueckt den Controller gegen die Wand am
    # Griffende, damit die Laengslage vom Radueberstand unabhaengig ist.
    schalen.extend(ctrl_feder(g, MULDE_HOEHE))

    # Rippen: Muldenwand -> Richtung Originalkontur (dort sitzt das Teil).
    # Nicht am Radbogen -- dort wuerde die Rippe das Drehrad klemmen.
    for idx in g["rippen_idx"]:
        px, py = mulde_pos[idx]
        qx, qy = kontur_pos[idx]
        schalen.append(rippe_frei(px, py, qx - px, qy - py, 0.0, MULDE_HOEHE))

    # Klemmrippen Autofach (Box sitzt jetzt hinten: fachA_y0..fachA_y1)
    ax = (g["fachA_x0"] + g["fachA_x1"]) / 2.0
    aym = (g["fachA_y0"] + g["fachA_y1"]) / 2.0
    for dy in (-g["fachA_t"] * 0.25, g["fachA_t"] * 0.25):
        schalen.append(rippe(g["fachA_x0"] + TRENNWAND, aym + dy, "+x", 0.0, z1))
        schalen.append(rippe(g["fachA_x1"], aym + dy, "-x", 0.0, z1))
    for dx in (-g["fachA_l"] * 0.22, g["fachA_l"] * 0.22):
        schalen.append(rippe(ax + dx, g["fachA_y0"], "+y", 0.0, z1))
        schalen.append(rippe(ax + dx, g["fachA_y1"], "-y", 0.0, z1))

    # Scharnieraugen hinten aussen (Achse X, Lochmitte 4 ueber Randkante)
    z_achse = z_rand + SCHARNIER_AUGE / 2.0 - 2.0
    y_auge = g["aussen_y"] / 2.0 + SCHARNIER_AUGE / 2.0 - 1.5
    sb = g["schar_breite"]
    loch_w = LOCH_ACHSE if not GEDRUCKTER_STIFT else LOCH_DREH
    for nr, x0 in enumerate(g["schar_wanne"]):
        # Das linke Aussensegment bekommt die Ansenkung (dort wird die
        # Achse eingeschoben), das rechte das Blindende.
        erstes = (nr == 0)
        letztes = (nr == len(g["schar_wanne"]) - 1)
        auge = scharnier_auge(
            loch_w, sb,
            sack=SACK_T if (letztes and not GEDRUCKTER_STIFT) else 0.0,
            senkung=SENKUNG_T if (erstes and not GEDRUCKTER_STIFT) else 0.0)
        for teil in auge:
            schalen.append(verschieben(teil, x0, y_auge, z_achse))
        # Stuetzsteg vom Auge zur Rueckwand, ueber die volle Segmentbreite
        steg = [(x0, g["aussen_y"] / 2.0 - 1.0), (x0 + sb, g["aussen_y"] / 2.0 - 1.0),
                (x0 + sb, y_auge), (x0, y_auge)]
        schalen.append(prisma(steg, z_rand - 8.0, z_achse))

    # Rastkeile vorn (halbe Raute quer): Zunge des Deckels schnappt darunter
    y_front = -g["aussen_y"] / 2.0
    for xm in (-g["aussen_x"] * 0.25, g["aussen_x"] * 0.25):
        keil_profil = [(y_front, z_rand - 6.0),
                       (y_front - HAKEN, z_rand - 6.0 + HAKEN),
                       (y_front, z_rand - 6.0 + 2 * HAKEN)]
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

    logo = logo_flaechen(g)
    if logo:
        # Logotasche: die unterste Scheibe bekommt das Logo als Loch.
        # Gefuellt wird sie vom eigenen Bauteil (teil_logo) in Farbe 2 --
        # buendig, kein Absatz, keine Stufe.
        flaechen, inseln = logo
        schalen.append((prisma_mit_loechern(profile[0], flaechen,
                                            0.0, LOGO_TIEFE), True))
        for insel in inseln:
            schalen.append(prisma(insel, 0.0, LOGO_TIEFE))
        rest_profile = [profile[0]] + profile[1:]
        rest_hoehen = [LOGO_TIEFE] + [max(h, LOGO_TIEFE) for h in hoehen[1:]]
        schalen.append(loften(rest_profile, rest_hoehen))
    else:
        schalen.append(loften(profile, hoehen))

    # Wandring des Deckels
    schalen.append(loch_prisma(aussen, innen, BODEN, BODEN + DECKEL_INNEN))

    # Stufenfalz-Lippe: ragt im Druck nach oben (im Gebrauch nach unten in
    # die Wanne) und fuellt die Falzstufe. Aussen FALZ_SP Luft zur
    # Wannenstufe, innen FALZ_SP zur Wanneninnenkontur -- damit zentriert
    # sie den Deckel, ohne zu klemmen. Da sie im Druck senkrecht aufragt,
    # entsteht kein Ueberhang.
    r_i = max(2.0, ECKRADIUS - WAND)
    lippe_a = rundrechteck(g["innen_x"] + 2 * (FALZ_T - FALZ_SP),
                           g["innen_y"] + 2 * (FALZ_T - FALZ_SP),
                           r_i + FALZ_T - FALZ_SP)
    lippe_i = rundrechteck(g["innen_x"] + 2 * FALZ_SP,
                           g["innen_y"] + 2 * FALZ_SP, r_i + FALZ_SP)
    z_lippe = BODEN + DECKEL_INNEN
    # 0.5 mm kuerzer als die Falzstufe tief ist: sonst koennte die Lippe am
    # Stufengrund aufsetzen, bevor die Aussenfuge geschlossen ist -- der
    # Deckel muss auf der Wannenwand aufliegen, nicht auf der Lippe.
    schalen.append(loch_prisma(lippe_a, lippe_i, z_lippe - 1.0,
                               z_lippe + FALZ_H - 0.5))

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
             (-(g["fachA_x0"] + g["fachA_x1"]) / 2.0,
              (g["fachA_y0"] + g["fachA_y1"]) / 2.0 - g["fachA_t"] * 0.22,
              g["fachA_l"] * 0.8, hub_box),
             (-(g["fachA_x0"] + g["fachA_x1"]) / 2.0,
              (g["fachA_y0"] + g["fachA_y1"]) / 2.0 + g["fachA_t"] * 0.22,
              g["fachA_l"] * 0.8, hub_box)]
    for cx, y, spann, hub in ziele:
        profil = feder(cx, spann, hub)
        t = prisma(profil, y - 5.0, y + 5.0)
        t = [tuple((x, z, y_) for (x, y_, z) in tri) for tri in t]
        schalen.append(t)

    # Kontrolle 1: das Rad muss in der Hoehe frei bleiben
    if ueber_rad > DECKEL_INNEN - 1.0:
        raise SystemExit("FEHLER: Drehrad ragt %.1f mm in den Deckel, dort "
                         "sind nur %.1f mm -- DECKEL_INNEN erhoehen"
                         % (ueber_rad, DECKEL_INNEN))

    # Kontrolle 2: keine Feder darf ueber dem Rad stehen -- sie wuerde es
    # klemmen statt den Controller zu halten. Rechteck der Feder gegen den
    # Radkreis pruefen.
    rad_x = -(mx0 + g["rad_pos"][0])
    rad_y = my0 + g["rad_pos"][1]
    grenze = RAD_D / 2.0 + RAD_FREI
    for cx, y, spann, hub in ziele[:2]:
        dy = abs(y - rad_y) - 5.0
        dx = abs(cx - rad_x) - spann / 2.0
        if max(dx, dy) < grenze:
            raise SystemExit(
                "FEHLER: Deckelfeder bei x=%.0f y=%.0f steht ueber dem "
                "Drehrad (Radmitte x=%.0f y=%.0f, D=%.0f) -- Federposition "
                "oder Spannweite anpassen" % (cx, y, rad_x, rad_y, RAD_D))

    # Scharnieraugen (versetzt zu denen der Wanne, Presssitz)
    z_rand = BODEN + DECKEL_INNEN
    y_auge = g["aussen_y"] / 2.0 + SCHARNIER_AUGE / 2.0 - 1.5
    sb = g["schar_breite"]
    # ACHTUNG Spiegelung: der Deckel wird um Y gespiegelt gedruckt
    # ((x,y,z)->(-x,y,z_top-z)). Ein Segment, das im GEBRAUCH bei
    # [a, a+sb] sitzen soll, muss hier also bei [-(a+sb), -a] stehen.
    # Ohne diese Umrechnung landen Deckel- und Wannensegmente
    # uebereinander statt ineinander -- der Deckel liesse sich nicht
    # anscharnieren.
    loch_d_ = LOCH_ACHSE if not GEDRUCKTER_STIFT else LOCH_PRESS
    for a in g["schar_deckel"]:
        x0 = -(a + sb)
        for teil in scharnier_auge(loch_d_, sb):
            schalen.append(verschieben(teil, x0, y_auge,
                                       z_rand - SCHARNIER_AUGE / 2.0 + 2.0))
        steg = [(x0, g["aussen_y"] / 2.0 - 1.0), (x0 + sb, g["aussen_y"] / 2.0 - 1.0),
                (x0 + sb, y_auge), (x0, y_auge)]
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
    keil_unter = g["wanne_innen_h"] - 6.0            # Gebrauch (Wannenoberkante)
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

    if not MIT_GRIFF:
        return schalen

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


def teil_logo(g):
    """Das Logo als Bauteile je Farbe -- fuer den AMS-Druck in einem Zug.

    Keine Tasche, kein Einleger: die Koerper liegen buendig in der
    Deckelflaeche, exakt in deren Aussparung, und sind genauso hoch.
    Gedruckt wird alles zusammen, der Wechsel passiert in der Ebene.
    Ueberlappungen gibt es nicht -- eine spaeter gezeichnete Farbe ist
    aus den frueheren herausgestanzt.

    Rueckgabe: Liste von (farbe, schalen), Reihenfolge = Filament 2, 3, ...
    """
    if logo_flaechen(g) is None:
        return []
    teile = []
    for farbe, flaechen in g["logo_gruppen"]:
        schalen = []
        for (f, loecher) in flaechen:
            if loecher:
                schalen.append((prisma_mit_loechern(f, loecher,
                                                    0.0, LOGO_TIEFE), True))
            else:
                schalen.append(prisma(f, 0.0, LOGO_TIEFE))
        if schalen:
            teile.append((farbe, schalen))
    return teile


def teil_lehre(g):
    """Passlehre: der Muldenquerschnitt als flache Platte mit Klemmrippen.

    Zuerst drucken (rund 40 Minuten statt der halben Nacht fuer die
    Wanne), Controller einlegen, Passung pruefen. Die Silhouette stammt
    aus Fotos -- eine Lehre ist billiger als ein Fehldruck. Passt sie
    nicht, misst man den Restspalt und korrigiert CTRL_BREITE /
    CTRL_LAENGE / MULDE_LUFT."""
    h = 8.0
    platte = [(0.0, 0.0), (g["fachC_l"], 0.0),
              (g["fachC_l"], g["fachC_t"]), (0.0, g["fachC_t"])]
    schalen = [(prisma_mit_loechern(platte, [g["mulde"]], 0.0, h), True)]
    schalen.extend(ctrl_feder(g, h, 0.0, 0.0))
    for idx in g["rippen_idx"]:
        px, py = g["mulde"][idx]
        qx, qy = g["kontur"][idx]
        schalen.append(rippe_frei(px, py, qx - px, qy - py, 0.0, h))
    return schalen


def teil_stift(g):
    """Achsstift fuer das Scharnierband. Zwei Stueck: von links und von
    rechts eingeschoben, sie treffen sich im mittleren Segment. Je Stift
    also knapp die halbe Bandbreite."""
    kopf_r, kopf_h = 4.5, 3.0
    laenge = SCHARNIER_BAND / 2.0 - 1.0
    schalen = []
    schalen.append(prisma(kreis(kopf_r), 0.0, kopf_h))
    schalen.append(prisma(kreis(STIFT_D / 2.0), kopf_h - 1.0,
                          kopf_h + laenge - 1.5))
    schalen.append(loften([kreis(STIFT_D / 2.0), kreis(STIFT_D / 2.0 - 1.0)],
                          [kopf_h + laenge - 1.51, kopf_h + laenge]))
    return schalen


# ---------------------------------------------------------------------------

def hw_faecher_pruefen(g):
    """Jedes Hot-Wheels-Fach muss vollstaendig frei liegen: die Aussenkante
    seines Rahmens darf weder in die Controller-Mulde noch in die Auto-Box
    noch aus der Wanne ragen. Geprueft wird der Rahmenrand Punkt fuer
    Punkt -- die Mulde ist konkav, ein Test nur der Ecken uebersaehe die
    Kerbe zwischen Rad- und Griffkontur."""
    mx0, my0 = g["fachC_x0"], -g["fachC_t"] / 2.0
    mulde = [(x + mx0, y + my0) for (x, y) in g["mulde"]]
    ix, iy = g["innen_x"] / 2.0, g["innen_y"] / 2.0
    box = (g["fachA_x0"], g["fachA_x1"], g["fachA_y0"], g["fachA_y1"])
    fehler = []
    # Liegt ein Fach in einer Fuellschale, MUSS es dort als Loch stehen --
    # sonst ist es bis oben massiv und man sieht es der STL nicht an.
    fuell_a, fuell_l = g.get("fuellung", (None, []))
    for nr, (x0, x1, y0, y1) in enumerate(g["hw"], 1):
        if fuell_a is None:
            break
        mitte = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
        if punkt_in_polygon(mitte, fuell_a) and not any(
                punkt_in_polygon(mitte, loch) for loch in fuell_l):
            fehler.append("Fach %d liegt in der Fuellschale, ist dort aber "
                          "kein Loch -- es waere massiv zugefuellt" % nr)
    for nr, (x0, x1, y0, y1) in enumerate(g["hw"], 1):
        ax0, ax1 = x0 - HW_WAND, x1 + HW_WAND
        ay0, ay1 = y0 - HW_WAND, y1 + HW_WAND
        rand = []
        for t in [i / 40.0 for i in range(41)]:
            rand += [(ax0 + (ax1 - ax0) * t, ay0),
                     (ax0 + (ax1 - ax0) * t, ay1),
                     (ax0, ay0 + (ay1 - ay0) * t),
                     (ax1, ay0 + (ay1 - ay0) * t)]
        for p in rand:
            if punkt_in_polygon(p, mulde):
                fehler.append("Fach %d ragt in die Controllermulde" % nr)
                break
            if (box[0] < p[0] < box[1] and box[2] < p[1] < box[3]):
                fehler.append("Fach %d ragt in das Auto-Box-Fach" % nr)
                break
            if not (-ix - WAND + 1.0 <= p[0] <= ix + WAND - 1.0
                    and -iy - WAND + 1.0 <= p[1] <= iy + WAND - 1.0):
                fehler.append("Fach %d ragt aus der Wanne" % nr)
                break
    return sorted(set(fehler))


def scharnier_pruefen(g):
    """Die Segmente von Wanne und Deckel muessen im GEBRAUCH ineinander
    greifen, nicht uebereinander liegen. Geprueft werden die Intervalle
    entlang der Achse -- der Deckel wird gespiegelt gedruckt, ein
    Vorzeichenfehler faellt in der STL sonst niemandem auf."""
    sb = g["schar_breite"]
    w = [(a, a + sb) for a in g["schar_wanne"]]
    d = [(a, a + sb) for a in g["schar_deckel"]]
    fehler = []
    for (w0, w1) in w:
        for (d0, d1) in d:
            ueber = min(w1, d1) - max(w0, d0)
            if ueber > 0:
                fehler.append("Wannensegment %.0f..%.0f und Deckelsegment "
                              "%.0f..%.0f ueberlappen %.1f mm"
                              % (w0, w1, d0, d1, ueber))
    alle = sorted(w + d)
    for (a0, a1), (b0, b1) in zip(alle, alle[1:]):
        if b0 - a1 < SCHARNIER_LUFT - 0.01:
            fehler.append("Segmentspalt nur %.2f mm (soll %.2f)"
                          % (b0 - a1, SCHARNIER_LUFT))
    tragend = sum(x1 - x0 for (x0, x1) in w)
    return fehler, tragend


def hw_hohlraum_pruefen(g, schalen):
    """Beweist, dass die Hot-Wheels-Faecher wirklich leer sind.

    Ein Fach kann fehlerfrei modelliert und trotzdem massiv zugefuellt
    sein, wenn eine andere Schale (hier die Fuellschale der Konturmulde)
    darueber liegt -- die STL sieht dabei voellig unauffaellig aus. Der
    Test schickt senkrechte Strahlen durch das Fachinnere und meldet jede
    Flaeche oberhalb des Bodens."""
    tris = [t for sch in schalen
            for t in (sch[0] if isinstance(sch, tuple) else sch)]
    treffer = []
    for nr, (x0, x1, y0, y1) in enumerate(g["hw"], 1):
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        proben = [(cx, cy)]
        for fx, fy in ((0.3, 0.3), (0.7, 0.3), (0.3, 0.7), (0.7, 0.7)):
            proben.append((x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy))
        for (px, py) in proben:
            hoch = []
            for (p1, p2, p3) in tris:
                (ax, ay, az), (bx, by, bz), (cx3, cy3, cz) = p1, p2, p3
                d1 = (bx - ax) * (py - ay) - (by - ay) * (px - ax)
                d2 = (cx3 - bx) * (py - by) - (cy3 - by) * (px - bx)
                d3 = (ax - cx3) * (py - cy3) - (ay - cy3) * (px - cx3)
                if not ((d1 >= 0 and d2 >= 0 and d3 >= 0)
                        or (d1 <= 0 and d2 <= 0 and d3 <= 0)):
                    continue
                A = (by - ay) * (cz - az) - (bz - az) * (cy3 - ay)
                B = (bz - az) * (cx3 - ax) - (bx - ax) * (cz - az)
                C = (bx - ax) * (cy3 - ay) - (by - ay) * (cx3 - ax)
                if abs(C) < 1e-9:
                    continue
                z = az + (A * (ax - px) + B * (ay - py)) / C
                if z > 1.0:
                    hoch.append(z)
            if hoch:
                treffer.append("Fach %d: Material bis z=%.1f bei (%.0f, %.0f)"
                               % (nr, max(hoch), px, py))
                break
    return treffer


def falzzone_pruefen(g, schalen):
    """Die Falzzone der Wanne muss frei bleiben.

    Zwischen z_fach und der Wannenoberkante sitzt spaeter die Deckellippe.
    Ragt dort ein Innenteil (Fuellschale, Trennwand, Block, Rippe) in den
    Lippenquerschnitt, laesst sich der Deckel nicht schliessen -- und man
    saehe es der STL nicht an. Deshalb hier gepruefte Geometrie statt
    Vertrauen: jeder Eckpunkt in der Falzhoehe wird gegen die
    Lippenaussenkontur getestet.
    """
    r_i = max(2.0, ECKRADIUS - WAND)
    lippe_a = rundrechteck(g["innen_x"] + 2 * (FALZ_T - FALZ_SP),
                           g["innen_y"] + 2 * (FALZ_T - FALZ_SP),
                           r_i + FALZ_T - FALZ_SP)
    z0 = g["z_fach"] + 0.1
    z1 = g["wanne_innen_h"] - 0.1
    # Nicht die Eckpunkte pruefen, sondern die z-INTERVALLE der Dreiecke:
    # ein Prisma, das die Falzzone durchquert, hat dort gar keinen
    # Eckpunkt und wuerde einem Punkt-Test entgehen.
    treffer = 0
    for eintrag in schalen:
        sch = eintrag[0] if isinstance(eintrag, tuple) else eintrag
        for tri in sch:
            zs = [v[2] for v in tri]
            if max(zs) <= z0 or min(zs) >= z1:
                continue
            if any(punkt_in_polygon((v[0], v[1]), lippe_a) for v in tri):
                treffer += 1
    return treffer


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
    global MIT_GRIFF
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--gedruckter-stift", action="store_true",
                    help="Scharnierstifte drucken statt rohes 1,75er "
                         "Filament als Achse zu verwenden")
    ap.add_argument("--mit-griff", action="store_true",
                    help="Steck-Tragegriff und die T-Nut-Bloecke am Deckel "
                         "mit erzeugen (Standard: ohne, saubere Aussenflaeche)")
    global GEDRUCKTER_STIFT
    args = ap.parse_args()
    MIT_GRIFF = args.mit_griff
    GEDRUCKTER_STIFT = args.gedruckter_stift

    g = abgeleitet()
    ziel = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
    os.makedirs(ziel, exist_ok=True)

    print("Griff: %s" % ("Buegel + T-Nuten" if MIT_GRIFF
                         else "keiner (Aussenflaeche glatt)"))
    print("Koffer aussen: %.0f x %.0f x %.0f mm (ohne Griff), innen %.0f x %.0f x %.0f"
          % (g["aussen_x"], g["aussen_y"],
             BODEN + g["wanne_innen_h"] + DECKEL_INNEN + BODEN,
             g["innen_x"], g["innen_y"], g["innen_h"]))
    print("Fach Controller: %.0f x %.0f | Fach Auto-Box: %.0f x %.0f "
          "(Rippen schlucken +/- %.0f mm)\n"
          % (g["fachC_l"], g["fachC_t"], g["fachA_l"], g["fachA_t"], KLEMMWEG))

    fehler = 0
    wanne = teil_wanne(g)          # setzt g["fuellung"] fuer die Pruefung
    hw_fehler = hw_faecher_pruefen(g)
    if hw_fehler:
        raise SystemExit("FEHLER: " + "; ".join(hw_fehler))
    sfehler, tragend = scharnier_pruefen(g)
    if sfehler:
        raise SystemExit("FEHLER Scharnier: " + "; ".join(sfehler))
    achse = "gedruckter Stift %.1f mm" % STIFT_D if GEDRUCKTER_STIFT \
        else "Rohfilament %.2f mm" % FILAMENT_D
    print("Scharnierband: %d Segmente a %.0f mm (Wanne %d / Deckel %d), "
          "tragende Breite %.0f mm, Achse: %s"
          % (SCHARNIER_SEG, g["schar_breite"], len(g["schar_wanne"]),
             len(g["schar_deckel"]), tragend, achse))

    voll = hw_hohlraum_pruefen(g, wanne)
    if voll:
        raise SystemExit("FEHLER: Fach zugefuellt -- " + "; ".join(voll))
    hb, hl = g["hw_licht"]
    print("Hot-Wheels-Faecher: %d Stueck (Strahltest: innen frei), "
          "licht %.0f x %.0f x %.0f mm "
          "(Auto bis %.0f x %.0f x %.0f, Stirnfeder %.0f mm)"
          % (len(g["hw"]), hb, hl, MULDE_HOEHE, HW_B, HW_L, HW_H, HW_FED_HUB))

    frei = falzzone_pruefen(g, wanne)
    if frei:
        raise SystemExit("FEHLER: %d Punkte der Wanne ragen in die Falzzone "
                         "-- der Deckel liesse sich nicht schliessen" % frei)
    print("Falzzone frei (Lippe %.1f mm tief, %.1f mm dick, %.2f mm Spiel)"
          % (FALZ_H, FALZ_T - 2 * FALZ_SP, FALZ_SP))
    fehler += bauen(ziel, "rcbox_0_passlehre_zuerst_drucken.stl",
                    teil_lehre(g))
    fehler += bauen(ziel, "rcbox_1_wanne_1x_drucken.stl", wanne)
    fehler += bauen(ziel, "rcbox_2_deckel_1x_drucken.stl", teil_deckel(g))
    for alt_nr in range(2, 6):
        alt_pfad = os.path.join(
            ziel, "rcbox_2%s_deckellogo_filament%d_1x_drucken.stl"
            % ("bcde"[alt_nr - 2], alt_nr))
        if os.path.exists(alt_pfad):
            os.remove(alt_pfad)
    logo_teile = teil_logo(g)
    for nr, (farbe, schalen) in enumerate(logo_teile, start=2):
        name = ("rcbox_2%s_deckellogo_filament%d_1x_drucken.stl"
                % ("bcde"[nr - 2], nr))
        fehler += bauen(ziel, name, schalen)
        print("   Farbe %s -> Filament %d" % (farbe, nr))
    if logo_teile:
        print("Logo: %s, %.0f mm breit, %.1f mm hoch, %d Farbteile. In Bambu "
              "Studio ALLE Deckel-STLs zusammen laden ('mehrteiliges "
              "Objekt?' -> Ja), dann je Teil das Filament setzen."
              % (g.get("logo_datei", LOGO_DATEI), LOGO_BREITE, LOGO_TIEFE,
                 len(logo_teile)))
    griff_datei = os.path.join(ziel, "rcbox_3_griff_1x_drucken.stl")
    if MIT_GRIFF:
        griff = teil_griff(g)
        # flach legen: Buegelebene (YZ) aufs Bett -> (x,y,z) -> (y, z, x+8)
        griff_flach = [[tuple((y_, z_, x_ + 8.0) for (x_, y_, z_) in tri)
                        for tri in s_] for s_ in griff]
        fehler += bauen(ziel, "rcbox_3_griff_1x_drucken.stl", griff_flach)
    elif os.path.exists(griff_datei):
        # Keine Alternativ-Variante im Ordner liegen lassen -- sonst wird
        # im Slicer ein Teil gedruckt, das nirgends hineinpasst.
        os.remove(griff_datei)
        print("Griff-Variante aus: alte %s geloescht"
              % os.path.basename(griff_datei))
    stift_datei = os.path.join(ziel, "rcbox_4_achsstift_2x_drucken.stl")
    if GEDRUCKTER_STIFT:
        # Stehend gedruckt laegen alle Lagen quer zur Achse; flach legen:
        # (x,y,z) -> (z, x, y) plus Hub, damit die Fasern laengs laufen.
        stift_flach = [[tuple((z_, x_, y_ + 5.0) for (x_, y_, z_) in tri)
                        for tri in s_] for s_ in teil_stift(g)]
        fehler += bauen(ziel, "rcbox_4_achsstift_2x_drucken.stl", stift_flach)
    else:
        if os.path.exists(stift_datei):
            os.remove(stift_datei)
        # Nutzbare Bohrung: vom Bandanfang bis zum Grund des Blindendes
        x_a = g["schar_wanne"][0]
        x_e = g["schar_wanne"][-1] + g["schar_breite"] - SACK_T
        print("Achse: %.2f mm Rohfilament. Bohrung %.0f mm lang -- %.0f mm "
              "ablaengen, einschieben, den Ueberstand in der Senkung "
              "(%.1f mm tief) zum Kopf verschmelzen."
              % (FILAMENT_D, x_e - x_a, x_e - x_a + 2.0, SENKUNG_T))

    if fehler:
        raise SystemExit("FEHLER: %d offene Kanten" % fehler)
    print("\nAlle Schalen wasserdicht.")


if __name__ == "__main__":
    main()
