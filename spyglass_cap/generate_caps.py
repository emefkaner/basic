#!/usr/bin/env python3
"""
Erzeugt zwei druckfertige Kappen (STL) fuer das abgebrochene Piraten-Fernrohr.

Deine Masse:
  - 7,0 cm  Aussenmass  -> 70 mm
  - 2,5 cm  Innenmass    -> 25 mm

Weil aus "Aussenmass / Innenmass" zwei verschiedene Bauformen moeglich sind,
werden BEIDE erzeugt. Nimm die, die auf dein Rohr passt:

  Variante A  "Ueberstuelp-Kappe" (slip-over)
      Die Kappe wird wie ein Flaschendeckel ueber das Rohrende gestuelpt.
      -> passend, wenn 70 mm der AUSSENdurchmesser des Rohrs ist.

  Variante B  "Deckel mit Zapfen" (top-hat)
      Flacher Deckel (70 mm) liegt auf dem Rohrende, ein Zapfen (25 mm)
      steckt zentrierend in die mittige Oeffnung und klemmt.
      -> passend, wenn 70 mm der Aussenrand und 25 mm das Loch/die Bohrung ist.

Alle Masse stehen unten als Variablen -> einfach aendern und neu ausfuehren.
"""

import math
import numpy as np
from stl import mesh

SEG = 220  # Winkel-Aufloesung (hoeher = runder)


def revolve(profile, seg=SEG):
    """Dreht ein geschlossenes 2D-Profil [(r, z), ...] um die Z-Achse
    und liefert eine wasserdichte Dreiecksliste (Solid of Revolution)."""
    eps = 1e-9
    tris = []
    n = len(profile)
    for i in range(n):
        r0, z0 = profile[i]
        r1, z1 = profile[(i + 1) % n]
        if r0 <= eps and r1 <= eps:
            continue  # Kante liegt komplett auf der Achse -> keine Flaeche
        for j in range(seg):
            a0 = 2 * math.pi * j / seg
            a1 = 2 * math.pi * (j + 1) / seg
            v00 = (r0 * math.cos(a0), r0 * math.sin(a0), z0)
            v01 = (r0 * math.cos(a1), r0 * math.sin(a1), z0)
            v10 = (r1 * math.cos(a0), r1 * math.sin(a0), z1)
            v11 = (r1 * math.cos(a1), r1 * math.sin(a1), z1)
            if r0 > eps and r1 > eps:
                tris.append((v00, v10, v11))   # Quad -> zwei Dreiecke
                tris.append((v00, v11, v01))
            elif r0 <= eps:
                tris.append((v00, v10, v11))   # Faecher von der Achsenspitze unten
            else:
                tris.append((v10, v01, v00))   # Faecher zur Achsenspitze oben
    return tris


def orient_outward(tris):
    """Vereinheitlicht die Umlaufrichtung aller Dreiecke (BFS ueber gemeinsame
    Kanten) und dreht die Normalen so, dass sie nach aussen zeigen."""
    def key(v):
        return tuple(round(x, 4) for x in v)
    faces = [[key(a), key(b), key(c)] for a, b, c in tris]
    edge_faces = {}
    for fi, f in enumerate(faces):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            edge_faces.setdefault(tuple(sorted((f[a], f[b]))), []).append(fi)
    visited = [False] * len(faces)
    for start in range(len(faces)):
        if visited[start]:
            continue
        stack = [start]
        visited[start] = True
        while stack:
            fi = stack.pop()
            f = faces[fi]
            fedges = {(f[a], f[b]) for a, b in ((0, 1), (1, 2), (2, 0))}
            for a, b in ((0, 1), (1, 2), (2, 0)):
                for nb in edge_faces[tuple(sorted((f[a], f[b])))]:
                    if nb == fi or visited[nb]:
                        continue
                    nf = faces[nb]
                    nedges = {(nf[i], nf[j]) for i, j in ((0, 1), (1, 2), (2, 0))}
                    # gemeinsame Kante muss in beiden Dreiecken GEGENlaeufig sein
                    if fedges & nedges:
                        nf.reverse()
                    visited[nb] = True
                    stack.append(nb)
    tris = [(f[0], f[1], f[2]) for f in faces]
    # Signiertes Volumen; bei negativ alles spiegeln -> Normalen nach aussen
    vol = 0.0
    for a, b, c in tris:
        vol += (a[0]*(b[1]*c[2]-b[2]*c[1])
                - a[1]*(b[0]*c[2]-b[2]*c[0])
                + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6.0
    if vol < 0:
        tris = [(a, c, b) for a, b, c in tris]
    return tris


def save_stl(tris, path):
    tris = orient_outward(tris)
    data = np.zeros(len(tris), dtype=mesh.Mesh.dtype)
    for k, (a, b, c) in enumerate(tris):
        data["vectors"][k] = np.array([a, b, c])
    m = mesh.Mesh(data)
    m.save(path)
    mins = m.vectors.reshape(-1, 3).min(axis=0)
    maxs = m.vectors.reshape(-1, 3).max(axis=0)
    size = maxs - mins
    print(f"  -> {path}")
    print(f"     Dreiecke: {len(tris)}  |  Bauraum X/Y/Z: "
          f"{size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")


# ---------------------------------------------------------------------------
# Gemeinsame Einstellungen
# ---------------------------------------------------------------------------
CLEARANCE = 0.4   # Spiel fuer Passung (diametral). Sitzt zu stramm? -> groesser.
                  # Sitzt zu locker? -> kleiner (z.B. 0.2).

# ---------------------------------------------------------------------------
# Variante A: Ueberstuelp-Kappe
# ---------------------------------------------------------------------------
A_TUBE_OUTER_D = 70.0     # gemessener AUSSENdurchmesser des Rohrs
A_WALL         = 3.0      # Wandstaerke der Kappe
A_SKIRT_H      = 20.0     # wie weit die Kappe ueber das Rohr greift
A_TOP_TH       = 3.0      # Dicke des geschlossenen Deckels

def make_slip_over():
    inner_r = (A_TUBE_OUTER_D + CLEARANCE) / 2.0
    outer_r = inner_r + A_WALL
    z_rim   = 0.0
    z_floor = A_SKIRT_H            # Unterkante Deckel / Oberkante Bohrung
    z_top   = A_SKIRT_H + A_TOP_TH
    profile = [
        (0.0,     z_floor),
        (inner_r, z_floor),
        (inner_r, z_rim),
        (outer_r, z_rim),
        (outer_r, z_top),
        (0.0,     z_top),
    ]
    print("Variante A  Ueberstuelp-Kappe:")
    print(f"     Innen-Oe (Rohr passt rein): {2*inner_r:.1f} mm")
    print(f"     Aussen-Oe der Kappe:        {2*outer_r:.1f} mm")
    print(f"     Hoehe gesamt:               {z_top:.1f} mm")
    return revolve(profile)


# ---------------------------------------------------------------------------
# Variante B: Deckel mit Zapfen (top-hat)
# ---------------------------------------------------------------------------
B_LID_D    = 70.0    # Aussendurchmesser des Deckels (deckt das Rohrende ab)
B_LID_TH   = 3.0     # Dicke des Deckels
B_HOLE_D   = 25.0    # Durchmesser der Oeffnung/Bohrung, in die der Zapfen steckt
B_PLUG_LEN = 16.0    # Laenge des Zapfens
B_CHAMFER  = 1.5     # kleine Einfuehr-Fase am Zapfen

def make_top_hat():
    lid_r  = B_LID_D / 2.0
    plug_r = (B_HOLE_D - CLEARANCE) / 2.0
    z0     = 0.0                 # Zapfenspitze (unten)
    z_lidb = B_PLUG_LEN          # Unterkante Deckel
    z_lidt = B_PLUG_LEN + B_LID_TH
    profile = [
        (0.0,             z0),
        (plug_r - B_CHAMFER, z0),
        (plug_r,          z0 + B_CHAMFER),
        (plug_r,          z_lidb),
        (lid_r,           z_lidb),
        (lid_r,           z_lidt),
        (0.0,             z_lidt),
    ]
    print("Variante B  Deckel mit Zapfen:")
    print(f"     Deckel-Oe:                  {2*lid_r:.1f} mm")
    print(f"     Zapfen-Oe (steckt ins Loch):{2*plug_r:.1f} mm")
    print(f"     Hoehe gesamt:               {z_lidt:.1f} mm")
    return revolve(profile)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    save_stl(make_slip_over(), os.path.join(here, "kappe_A_ueberstuelp.stl"))
    save_stl(make_top_hat(),   os.path.join(here, "kappe_B_deckel_zapfen.stl"))
    print("\nFertig. Zum Aendern der Masse einfach die Variablen oben anpassen "
          "und erneut ausfuehren:  python3 generate_caps.py")
