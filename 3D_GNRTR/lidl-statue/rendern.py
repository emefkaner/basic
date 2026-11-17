"""Ansichten einer STL rendern -- ohne OpenGL.

Nicht die Eckpunkte splatten: bei 250k Ecken auf 420 px bleiben Luecken,
durch die die Rueckseite durchscheint. Deshalb werden Punkte GLEICHMAESSIG
AUF DEN FLAECHEN abgetastet (3 Mio.), mit der Flaechennormalen schattiert
und im Malerverfahren von hinten nach vorne gezeichnet.
"""
import sys
import numpy as np
import trimesh
from PIL import Image

stl, ziel = sys.argv[1], sys.argv[2]
titel = sys.argv[3].split(",") if len(sys.argv) > 3 else ["vorne", "rechts", "hinten", "links"]
m = trimesh.load(stl, force="mesh")
punkte, fid = trimesh.sample.sample_surface(m, 3_000_000)
normalen = m.face_normals[fid]

licht = np.array([0.45, -0.75, 0.5]); licht /= np.linalg.norm(licht)


def ansicht(winkel, breite=430):
    r = trimesh.transformations.rotation_matrix(np.radians(winkel), [0, 0, 1])
    v = trimesh.transform_points(punkte, r)
    n = trimesh.transform_points(normalen, r, translate=False)
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    sx = max(x.max() - x.min(), 1e-6); sz = max(z.max() - z.min(), 1e-6)
    hoehe = int(breite * sz / sx)
    px = np.clip(((x - x.min()) / sx * (breite - 1)).astype(int), 0, breite - 1)
    py = np.clip(((z.max() - z) / sz * (hoehe - 1)).astype(int), 0, hoehe - 1)
    hell = np.clip(n @ licht, 0.0, 1.0) * 0.8 + 0.2
    bild = np.zeros((hoehe, breite), np.float32)
    o = np.argsort(-y)                 # hinten zuerst, vorne gewinnt
    bild[py[o], px[o]] = hell[o]
    return bild


teile = []
for w in (0, 90, 180, 270):
    b = ansicht(w)
    rgb = np.dstack([b] * 3)
    rgb[b == 0] = [0.96, 0.94, 0.91]
    teile.append(Image.fromarray((rgb * 255).astype(np.uint8)))

h = max(t.height for t in teile)
rand, lücke = 26, 14
blatt = Image.new("RGB", (sum(t.width for t in teile) + 3 * lücke, h + rand),
                  (245, 242, 238))
x = 0
for t in teile:
    blatt.paste(t, (x, rand + h - t.height)); x += t.width + lücke
blatt.save(ziel)
print("geschrieben:", ziel, blatt.size, "Reihenfolge:", ", ".join(titel))
