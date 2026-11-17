"""Die vier Farbkoerper gemeinsam rendern -- so sieht der Druck aus."""
import sys
import glob
import numpy as np
import trimesh
from PIL import Image

ordner, ziel = sys.argv[1], sys.argv[2]
FARBEN = {"1_braun_haare": (120, 78, 48), "2_haut": (238, 190, 155),
          "3_dunkelblau": (40, 54, 76), "4_mittelblau": (95, 135, 178)}

punkte, farben, normalen = [], [], []
for pfad in sorted(glob.glob(ordner + "/statue_ams_*.stl")):
    name = pfad.split("statue_ams_")[1][:-4]
    m = trimesh.load(pfad, force="mesh")
    n = max(120_000, int(m.area * 90))   # ~0,1 Punkt je mm2 reicht fuer 430 px
    p, fid = trimesh.sample.sample_surface(m, n)
    punkte.append(p); normalen.append(m.face_normals[fid])
    farben.append(np.tile(np.array(FARBEN[name], float) / 255, (len(p), 1)))
    print("%-14s %d Punkte" % (name, len(p)))
punkte = np.vstack(punkte); normalen = np.vstack(normalen); farben = np.vstack(farben)

licht = np.array([0.45, -0.75, 0.5]); licht /= np.linalg.norm(licht)
teile = []
for winkel in (0, 90, 180, 270):
    r = trimesh.transformations.rotation_matrix(np.radians(winkel), [0, 0, 1])
    v = trimesh.transform_points(punkte, r)
    nn = trimesh.transform_points(normalen, r, translate=False)
    x, y, z = v[:, 0], v[:, 1], v[:, 2]
    breite = 430
    sx = x.max() - x.min(); sz = z.max() - z.min()
    hoehe = int(breite * sz / sx)
    px = np.clip(((x - x.min()) / sx * (breite - 1)).astype(int), 0, breite - 1)
    py = np.clip(((z.max() - z) / sz * (hoehe - 1)).astype(int), 0, hoehe - 1)
    hell = (np.clip(nn @ licht, 0, 1) * 0.65 + 0.35)[:, None]
    bild = np.zeros((hoehe, breite, 3), np.float32)
    belegt = np.zeros((hoehe, breite), bool)
    o = np.argsort(-y)
    bild[py[o], px[o]] = farben[o] * hell[o]
    belegt[py[o], px[o]] = True
    bild[~belegt] = [0.96, 0.94, 0.91]
    teile.append(Image.fromarray((np.clip(bild, 0, 1) * 255).astype(np.uint8)))

h = max(t.height for t in teile)
blatt = Image.new("RGB", (sum(t.width for t in teile) + 42, h + 20), (245, 242, 238))
x = 0
for t in teile:
    blatt.paste(t, (x, 20 + h - t.height)); x += t.width + 14
blatt.save(ziel)
print("geschrieben:", ziel)
