#!/usr/bin/env python3
"""Kappe fuer den Lightning-Stecker des Backbone One.

Die Kappe steckt auf dem Stecker und gibt dem Telefon eine glatte,
breitere Anlageflaeche statt der Metallzunge. Gedruckt wird sie mit der
Anlageflaeche nach unten, die Aufnahme fuer den Stecker zeigt nach oben
-- so braucht sie keine Stuetzen, und die Flaeche, die am Telefon
anliegt, ist die glatte Bettseite.

Gemessen ist hier nur, was belegt ist: der Lightning-Stecker ist
6,7 x 1,5 mm (Wikipedia, USPTO-Dokument, mehrere Hersteller). Wie weit er
beim Backbone aus dem Gehaeuse ragt, ist NICHT gemessen. Deshalb greift
die Kappe nur auf den vorderen 3,5 mm der Zunge -- ragt der Stecker
weniger heraus, sitzt die Kappe eben auf dem Gehaeuse auf.

Das Spiel einer Steckpassung haengt am Drucker, nicht an der Zeichnung.
Darum gibt es drei Kappen mit 0,10 / 0,15 / 0,20 mm Spiel je Seite. Man
erkennt sie an der Laenge: die kuerzeste (12 mm) sitzt am strammsten,
die laengste (14 mm) am lockersten. Alle drei drucken, die behalten, die
haelt ohne zu klemmen.

    python3 generate.py
"""
import importlib.util
import math
import os
import struct

HIER = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "hochzeitsornament_generate",
    os.path.join(HIER, "..", "hochzeitsornament", "generate.py"))
_ho = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ho)
prisma = _ho.prisma
prisma_mit_loechern = _ho.prisma_mit_loechern
kanten_pruefen = _ho.kanten_pruefen
volumen = _ho.volumen

# --- Lightning-Stecker (belegt) ---
STECKER_B = 6.7          # Breite der Zunge
STECKER_T = 1.5          # Dicke der Zunge

# --- Kappe ---
GRIFF = 3.5              # so tief schiebt sich die Zunge hinein
BODEN = 1.2              # Wand zwischen Zunge und Telefon
TIEFE = 6.0              # Mass in Telefondicke-Richtung (passt in die Wiege)
FASE = 0.5               # Fase an der Anlageflaeche: kein Elefantenfuss, keine Kratzkante
ECKE = 1.5               # Eckenradius aussen
VARIANTEN = [            # (Spiel je Seite, Laenge der Kappe)
    (0.10, 12.0),
    (0.15, 13.0),
    (0.20, 14.0),
]
ABSTAND = 20.0           # Abstand der drei Kappen auf dem Bett


def rundrechteck(b, t, r, n=8):
    """Gerundetes Rechteck um den Ursprung, gegen den Uhrzeigersinn."""
    r = min(r, b / 2 - 1e-3, t / 2 - 1e-3)
    pts = []
    for cx, cy, w0 in ((b / 2 - r, t / 2 - r, 0), (-b / 2 + r, t / 2 - r, 90),
                       (-b / 2 + r, -t / 2 + r, 180), (b / 2 - r, -t / 2 + r, 270)):
        for k in range(n + 1):
            w = math.radians(w0 + 90 * k / n)
            pts.append((cx + r * math.cos(w), cy + r * math.sin(w)))
    return pts


def loft(unten, oben, z0, z1):
    """Geschlossener Koerper zwischen zwei Umrissen gleicher Punktzahl."""
    n = len(unten)
    tris = []
    for i in range(n):
        j = (i + 1) % n
        a, b = (*unten[i], z0), (*unten[j], z0)
        c, d = (*oben[j], z1), (*oben[i], z1)
        tris += [(a, b, c), (a, c, d)]
    mu = (sum(p[0] for p in unten) / n, sum(p[1] for p in unten) / n, z0)
    mo = (sum(p[0] for p in oben) / n, sum(p[1] for p in oben) / n, z1)
    for i in range(n):
        j = (i + 1) % n
        tris.append((mu, (*unten[j], z0), (*unten[i], z0)))   # Boden nach unten
        tris.append((mo, (*oben[i], z1), (*oben[j], z1)))     # Deckel nach oben
    return tris


def kappe(spiel, laenge, dx):
    h = BODEN + GRIFF
    aussen = [(x + dx, y) for x, y in rundrechteck(laenge, TIEFE, ECKE)]
    innen = [(x + dx, y) for x, y in
             rundrechteck(laenge - 2 * FASE, TIEFE - 2 * FASE, ECKE - FASE)]
    sb, st = STECKER_B + 2 * spiel, STECKER_T + 2 * spiel
    schlitz = [(dx - sb / 2, -st / 2), (dx + sb / 2, -st / 2),
               (dx + sb / 2, st / 2), (dx - sb / 2, st / 2)]
    return [
        loft(innen, aussen, 0.0, FASE),                        # Fase an der Anlageflaeche
        prisma(aussen, FASE - 0.02, BODEN + 0.02),             # Boden
        prisma_mit_loechern(aussen, [schlitz], BODEN, h),      # Wand mit Schlitz
    ], (sb, st, h)


def stl_schreiben(pfad, schalen, kopf):
    tris = [t for s in schalen for t in s]
    with open(pfad, "wb") as f:
        f.write(kopf.encode("ascii", "replace").ljust(80, b" ")[:80])
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
            vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
            nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            l = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
            f.write(struct.pack("<12fH", nx / l, ny / l, nz / l, *a, *b, *c, 0))
    return len(tris)


def main():
    ziel = os.path.join(HIER, "stl")
    os.makedirs(ziel, exist_ok=True)
    alle, offen = [], 0
    print("Lightning-Zunge %.1f x %.1f mm, Griff %.1f mm, Boden %.1f mm"
          % (STECKER_B, STECKER_T, GRIFF, BODEN))
    for i, (spiel, laenge) in enumerate(VARIANTEN):
        schalen, (sb, st, h) = kappe(spiel, laenge, i * ABSTAND)
        dicht = sum(kanten_pruefen(s, gerade_erlaubt=True) for s in schalen)
        offen += dicht
        # Wand neben dem Schlitz muss druckbar bleiben (zwei Bahnen a 0,42)
        wand_t = (TIEFE - st) / 2
        wand_b = (laenge - sb) / 2
        print("  Kappe %d: %4.1f x %.1f x %.1f mm, Schlitz %.2f x %.2f mm "
              "(Spiel %.2f je Seite), Wand %.2f / %.2f mm, offene Kanten %d"
              % (i + 1, laenge, TIEFE, h, sb, st, spiel, wand_b, wand_t, dicht))
        if min(wand_t, wand_b) < 0.84:
            raise SystemExit("FEHLER: Wand neben dem Schlitz unter zwei Druckbahnen")
        alle += schalen
    if offen:
        raise SystemExit("FEHLER: %d offene Kanten" % offen)
    p = os.path.join(ziel, "backbone_lightning_kappe_3varianten.stl")
    n = stl_schreiben(p, alle, "Backbone Lightning-Kappe, 3 Varianten")
    vol = sum(volumen(s) for s in alle) / 1000.0
    print("\n%s: %d Dreiecke, ~%.2f cm3 fuer alle drei (Ueberlappung der "
          "Teilkoerper mitgezaehlt)" % (os.path.basename(p), n, vol))
    print("Drucken: Anlageflaeche nach unten, Schlitz nach oben, ohne Stuetzen.")


if __name__ == "__main__":
    main()
