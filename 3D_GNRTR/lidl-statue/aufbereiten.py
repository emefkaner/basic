"""GLB aus der Rekonstruktion -> druckbare STL.

    aufbereiten.py <datei.glb> <hoehe_mm> <zielordner>

Macht: zusammenfuegen, aufrichten, auf Zielhoehe skalieren, auf z=0
stellen, Loecher schliessen, Standflaeche pruefen, Kennzahlen ausgeben
und Ansichten von vier Seiten rendern.
"""
import os
import sys
import numpy as np
import trimesh

glb, hoehe_mm, ziel = sys.argv[1], float(sys.argv[2]), sys.argv[3]
os.makedirs(ziel, exist_ok=True)

szene = trimesh.load(glb, force="scene")
m = trimesh.util.concatenate([g for g in szene.dump()]) if hasattr(szene, "dump") \
    else trimesh.load(glb, force="mesh")
print("geladen: %d Ecken, %d Dreiecke" % (len(m.vertices), len(m.faces)))

# --- aufrichten: die laengste Achse ist die Koerperachse -> nach z ---
groesse = m.extents
lang = int(np.argmax(groesse))
print("Ausdehnung roh: %.3f x %.3f x %.3f (laengste Achse: %s)"
      % (*groesse, "xyz"[lang]))
if lang == 1:                      # y-up (GLB-Standard) -> z-up
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
elif lang == 0:
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))

# --- auf Zielhoehe skalieren ---
m.apply_scale(hoehe_mm / m.extents[2])
m.apply_translation(-m.bounds[0] * [0, 0, 1])      # Fuesse auf z = 0
m.apply_translation([-m.centroid[0], -m.centroid[1], 0])

# --- reparieren ---
m.merge_vertices()
m.remove_duplicate_faces() if hasattr(m, "remove_duplicate_faces") else None
m.remove_unreferenced_vertices()
trimesh.repair.fix_normals(m)
dicht_vorher = m.is_watertight
if not dicht_vorher:
    trimesh.repair.fill_holes(m)
print("wasserdicht: vorher %s, nachher %s" % (dicht_vorher, m.is_watertight))
print("Euler-Zahl: %d, Koerper: %d" % (m.euler_number, m.body_count))

b = m.bounds
print("Masse: %.1f x %.1f x %.1f mm" % tuple(b[1] - b[0]))
if m.is_watertight:
    print("Volumen: %.0f cm3 (massiv)" % (m.volume / 1000.0))

# --- Standflaeche: wieviel Material liegt in den untersten 2 mm? ---
unten = m.vertices[m.vertices[:, 2] < b[0][2] + 2.0]
if len(unten) > 2:
    flaeche_x = unten[:, 0].max() - unten[:, 0].min()
    flaeche_y = unten[:, 1].max() - unten[:, 1].min()
    print("Standflaeche in den untersten 2 mm: %.1f x %.1f mm, %d Ecken"
          % (flaeche_x, flaeche_y, len(unten)))
else:
    print("ACHTUNG: fast keine Ecken in den untersten 2 mm -- steht auf einem Punkt")

stl = os.path.join(ziel, "statue_roh_%.0fmm.stl" % hoehe_mm)
m.export(stl)
print("geschrieben:", stl, "%.1f MB" % (os.path.getsize(stl) / 1e6))

# --- Ansichten rendern (Punkt-Splat mit z-Puffer, kein OpenGL noetig) ---
def ansicht(mesh, winkel, breite=420):
    r = trimesh.transformations.rotation_matrix(np.radians(winkel), [0, 0, 1])
    v = trimesh.transform_points(mesh.vertices, r)
    n = trimesh.transform_points(mesh.vertex_normals, r, translate=False)
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    spanne_x = max(x.max() - x.min(), 1e-6)
    spanne_z = max(z.max() - z.min(), 1e-6)
    hoehe_px = int(breite * spanne_z / spanne_x * 1.0)
    px = ((x - x.min()) / spanne_x * (breite - 1)).astype(int)
    py = ((z.max() - z) / spanne_z * (hoehe_px - 1)).astype(int)
    tiefe = np.full((hoehe_px, breite), np.inf)
    bild = np.zeros((hoehe_px, breite), np.float32)
    licht = np.array([0.4, -0.8, 0.45]); licht = licht / np.linalg.norm(licht)
    helligkeit = np.clip(n @ licht, 0.05, 1.0) * 0.85 + 0.15
    # Malerverfahren: von hinten nach vorne, der letzte Schreibzugriff
    # gewinnt. Die Kamera steht bei -y, naeher heisst also kleineres y.
    # (Vorher stand hier ein falscher Tiefenvergleich -- gezeigt wurde
    # dadurch die jeweils ABGEWANDTE Seite.)
    reihenfolge = np.argsort(-y)              # groesstes y zuerst = hinten
    a = py[reihenfolge]; bb = px[reihenfolge]
    bild[a, bb] = helligkeit[reihenfolge]
    return bild

try:
    from PIL import Image
    teile = []
    for w in (0, 90, 180, 270):
        bild = ansicht(m, w)
        leer = bild == 0
        rgb = np.dstack([bild] * 3)
        rgb[leer] = [0.96, 0.94, 0.91]
        teile.append(Image.fromarray((rgb * 255).astype(np.uint8)))
    h = max(t.height for t in teile)
    blatt = Image.new("RGB", (sum(t.width for t in teile) + 30, h), (245, 242, 238))
    x = 0
    for t in teile:
        blatt.paste(t, (x, h - t.height)); x += t.width + 10
    p = os.path.join(ziel, "ansichten.png")
    blatt.save(p)
    print("Ansichten (vorne, rechts, hinten, links):", p)
except Exception as e:
    print("Rendern uebersprungen:", e)
