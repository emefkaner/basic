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


def fillet(profile, radius, steps=10, skip=frozenset()):
    """Rundet die Ecken eines 2D-Profils [(r, z), ...] ab, indem jede Ecke
    durch einen tangentialen Kreisbogen ersetzt wird. Indizes in 'skip'
    bleiben scharf (z.B. verdeckte Innenecken)."""
    if radius <= 0:
        return profile
    n = len(profile)
    out = []
    for i in range(n):
        p0 = profile[(i - 1) % n]
        p = profile[i]
        p1 = profile[(i + 1) % n]
        if i in skip:
            out.append(p)
            continue
        v1 = (p0[0] - p[0], p0[1] - p[1])
        v2 = (p1[0] - p[0], p1[1] - p[1])
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)
        if l1 < 1e-9 or l2 < 1e-9:
            out.append(p)
            continue
        u1 = (v1[0] / l1, v1[1] / l1)
        u2 = (v2[0] / l2, v2[1] / l2)
        half = math.acos(max(-1.0, min(1.0, u1[0]*u2[0] + u1[1]*u2[1]))) / 2.0
        if half < 1e-4 or math.pi/2 - half < 1e-4:
            out.append(p)
            continue
        d = min(radius / math.tan(half), l1 * 0.49, l2 * 0.49)
        r_eff = d * math.tan(half)
        t1 = (p[0] + u1[0]*d, p[1] + u1[1]*d)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        bl = math.hypot(*bis)
        ub = (bis[0]/bl, bis[1]/bl)
        c = (p[0] + ub[0]*(r_eff/math.sin(half)),
             p[1] + ub[1]*(r_eff/math.sin(half)))
        a1 = math.atan2(t1[1]-c[1], t1[0]-c[0])
        t2 = (p[0] + u2[0]*d, p[1] + u2[1]*d)
        a2 = math.atan2(t2[1]-c[1], t2[0]-c[0])
        da = a2 - a1
        while da > math.pi:  da -= 2*math.pi
        while da < -math.pi: da += 2*math.pi
        for s in range(steps + 1):
            a = a1 + da * s / steps
            out.append((c[0] + r_eff*math.cos(a), c[1] + r_eff*math.sin(a)))
    return out


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


# ---------------------------------------------------------------------------
# Variante C: HALTERING mit Guckloch  (das ist, was du brauchst)
# ---------------------------------------------------------------------------
# Kein geschlossener Deckel: haelt die ausfahrbaren Teile im Rohr, laesst
# aber in der Mitte ein Guckloch frei. Wird ueber das Rohrende gestuelpt.
R_TUBE_OUTER_D = 70.0    # AUSSENdurchmesser des Rohrs (worauf der Ring greift)
R_VIEW_HOLE_D  = 35.0    # Guckloch in der Mitte (3,5 cm)
R_WALL         = 3.5     # Wandstaerke der Schuerze (die ueber das Rohr greift)
R_SKIRT_H      = 20.0    # wie weit der Ring ueber das Rohr greift
R_FACE_TH      = 3.5     # Dicke der vorderen Halte-Flaeche (mit Guckloch)
R_ROUND        = 1.5     # Kantenradius (Abrundung) fuer den Original-Look

def make_retaining_ring():
    inner_r = (R_TUBE_OUTER_D + CLEARANCE) / 2.0   # Schuerze innen (Rohr passt rein)
    outer_r = inner_r + R_WALL                      # Schuerze aussen
    hole_r  = R_VIEW_HOLE_D / 2.0                    # Guckloch
    z0 = 0.0                       # offene Kante (wird ueber das Rohr geschoben)
    z1 = R_SKIRT_H                 # Unterseite der Halte-Flaeche (Rohr stoesst an)
    z2 = R_SKIRT_H + R_FACE_TH     # Vorderseite
    profile = [
        (hole_r,  z1),   # innere Kante der Halte-Nase, unten
        (hole_r,  z2),   # innere Kante, vorne (Guckloch-Rand)
        (outer_r, z2),   # vorne aussen
        (outer_r, z0),   # Schuerze aussen, unten
        (inner_r, z0),   # Schuerze innen, unten (offen fuers Rohr)
        (inner_r, z1),   # Schuerze innen, oben (trifft Halte-Nase)
    ]
    ledge = inner_r - hole_r
    print("Variante C  HALTERING mit Guckloch:")
    print(f"     Guckloch:                   {2*hole_r:.1f} mm")
    print(f"     Innen-Oe (Rohr Ø{R_TUBE_OUTER_D:.0f}+Spiel):  {2*inner_r:.1f} mm")
    print(f"     Aussen-Oe des Rings:        {2*outer_r:.1f} mm")
    print(f"     Halte-Nase (Ueberlappung):  {ledge:.1f} mm ringsum")
    print(f"     Hoehe gesamt:               {z2:.1f} mm")
    print(f"     Kanten abgerundet mit R:    {R_ROUND:.1f} mm")
    # Sichtbare Kanten abrunden (Guckloch-Rand, Aussenkante vorne/hinten,
    # Mundkante). Die verdeckten Innenecken auf Hoehe z1 bleiben scharf,
    # damit Sitzflaeche und Halte-Nase voll erhalten bleiben.
    profile = fillet(profile, R_ROUND, skip={0, 5})
    return revolve(profile)


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    save_stl(make_retaining_ring(), os.path.join(here, "kappe_C_haltering.stl"))
    save_stl(make_slip_over(), os.path.join(here, "kappe_A_ueberstuelp.stl"))
    save_stl(make_top_hat(),   os.path.join(here, "kappe_B_deckel_zapfen.stl"))
    print("\nFertig. Zum Aendern der Masse einfach die Variablen oben anpassen "
          "und erneut ausfuehren:  python3 generate_caps.py")
