"""Statue in vier Farbkoerper fuer die AMS zerlegen.

Vorgehen und warum:

1. FARBE JE DREIECK. Das Netz stammt aus genau den beiden Bildern, seine
   Silhouette deckt sich also mit ihnen. Nach vorne gewandte Dreiecke
   werden im Frontbild nachgeschlagen, nach hinten gewandte im
   Rueckenbild (dort x gespiegelt, man schaut ja von hinten). Was zur
   Seite zeigt, erbt die Farbe des naechsten schon bestimmten Dreiecks.

2. VIER ZIELFARBEN von Hand statt k-Means: ein Clustering wirft Haar und
   Haut zusammen (beide braunstichig) -- das Ergebnis saehe aus wie eine
   Maske. Hemd und Jeans teilen sich dagegen bewusst ein Blau, weil vier
   das Maximum sind.

3. ECHTE TEILUNG DES VOLUMENS, keine sich ueberlappenden Schalen. Die
   Figur wird in Voxel zerlegt, jedes Voxel bekommt die Farbe des
   naechsten Oberflaechendreiecks, danach wird je Farbe eine eigene
   Huelle erzeugt. Damit beruehren sich die vier Koerper, ueberlappen
   sich aber nirgends -- genau das braucht der Slicer fuer ein
   mehrteiliges Objekt.

   Preis dafuer: die Oberflaeche kommt aus dem Voxelraster und nicht
   mehr vom Originalnetz. Bei 0,3 mm Raster liegt die Abweichung unter
   0,15 mm und damit unter dem, was eine 0,4-mm-Duese aufloest.
"""
import os
import sys
import numpy as np
import trimesh
from PIL import Image
from scipy.spatial import cKDTree
from skimage import measure

stl, front_pfad, rueck_pfad, ziel = sys.argv[1:5]
PITCH = float(sys.argv[5]) if len(sys.argv) > 5 else 0.3
os.makedirs(ziel, exist_ok=True)

FARBEN = [
    ("1_braun_haare", (105, 72, 50),  "Haare"),
    ("2_haut",        (228, 171, 133), "Gesicht und Haende"),
    ("3_dunkelblau",  (40, 54, 76),   "Weste, Schuhe, Brille"),
    ("4_mittelblau",  (95, 135, 178), "Hemd und Jeans"),
]
BRAUN, HAUT, NAVY, DENIM = 0, 1, 2, 3


# Hoehen der Kleidungsgrenzen, aus dem Zeilenprofil der Frontansicht
# gemessen (Anteil der Figurhoehe, 0 = Sohle): bis 9 % ist alles Schuh,
# ab 47 % beginnt die Weste. Dazwischen Jeans.
SCHUH_BIS, WESTE_AB = 0.09, 0.47


def klasse_von_rgb(rgb, hoehe):
    """Pixelfarbe und Hoehe -> eine der vier Druckfarben.

    Zwei Messungen stecken hier drin. Erstens die Palette beider Bilder
    (k-Means, sieben Gruppen):

      Jeans 50/78/109 · Weste 40/54/76 · Haut 223/168/132
      Hemd 163/189/215 · Haare 103/74/57 · Grau 127/129/138
      Glanzlicht 204/211/222

    Zweitens das Zeilenprofil der Frontansicht. Das ist noetig, weil
    Weste und Jeans im Bild praktisch denselben Blauton haben --
    Summe 214 gegen 221. Nach Farbe allein landete die ganze Figur in
    einem Blau. Getrennt werden sie deshalb ueber die Hoehe, und das ist
    auch die ehrlichere Regel: es ist eine Aussage ueber das
    Kleidungsstueck, nicht ueber ein paar Pixel.

    Haut und Haare gehen weiter nach Farbe, da ist der Abstand gross.
    """
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    summe = rgb.sum(axis=-1)
    spanne = rgb.max(axis=-1) - rgb.min(axis=-1)
    warm = (r > b) & (spanne >= 30)
    k = np.where(summe > 430, HAUT, BRAUN)            # warme Toene
    # blaue und graue Toene: Hemd ueber die Helligkeit, Rest ueber die Hoehe
    kleidung = np.where(summe > 400, DENIM,
                        np.where(hoehe < SCHUH_BIS, NAVY,
                                 np.where(hoehe < WESTE_AB, DENIM, NAVY)))
    return np.where(warm, k, kleidung).astype(np.int8)


m = trimesh.load(stl, force="mesh")
mb = m.bounds
zentren, normalen = m.triangles_center, m.face_normals
print("Netz: %d Dreiecke, %.1f x %.1f x %.1f mm"
      % (len(m.faces), *(mb[1] - mb[0])))


def bild_laden(p):
    im = np.array(Image.open(p).convert("RGBA"))
    a = im[:, :, 3] > 128
    ys, xs = np.where(a)
    return im, a, xs.min(), xs.max(), ys.min(), ys.max()


def nachschlagen(bild_daten, x_mm, z_mm, spiegeln):
    im, a, x0, x1, y0, y1 = bild_daten
    bx = (x_mm - mb[0][0]) / (mb[1][0] - mb[0][0])
    if spiegeln:
        bx = 1.0 - bx
    px = np.clip((x0 + bx * (x1 - x0)).astype(int), 0, im.shape[1] - 1)
    bz = (z_mm - mb[0][2]) / (mb[1][2] - mb[0][2])
    py = np.clip((y1 - bz * (y1 - y0)).astype(int), 0, im.shape[0] - 1)
    return im[py, px, :3].astype(float), a[py, px]


front, rueck = bild_laden(front_pfad), bild_laden(rueck_pfad)
klasse = np.full(len(zentren), -1, np.int8)

# Eine reine Projektion gibt auch Flaechen eine Farbe, die im Bild gar
# nicht zu sehen sind -- die Brust hinter dem angewinkelten Arm bekam so
# die Farbe des Aermels, die Beinseiten die der Haare. Ergebnis waren
# wilde Flecken an den Seiten. Deshalb ein Tiefenpuffer in
# Bildaufloesung: ein Dreieck wird nur nachgeschlagen, wenn an seinem
# Bildpunkt nichts naeher an der Kamera liegt.
TOLERANZ = 1.5          # mm


def sichtbar(bild_daten, spiegeln, nach_vorne):
    """Sichtbare Dreiecke bestimmen und ihre Farbklasse abstimmen lassen.

    Zwei Feinheiten:

    Der Normalenschwellwert ist mit 0,05 bewusst niedrig. Flaechen, die
    fast quer zur Kamera stehen, liegen genau an der Silhouette -- und
    dort zeigt das Bild das aeusserste Kleidungsstueck, also die
    richtige Farbe fuer die Koerperseite. Mit einem strengen Schwellwert
    blieben die Seiten ohne Daten und mussten geraten werden; genau da
    war das Ergebnis vorher fleckig.

    Abgetastet wird nicht ein Pixel, sondern ein 5x5-Fenster, und
    gewertet wird die haeufigste Klasse darin. Ein einzelnes Pixel
    traefe an der Silhouette fast immer die schwarze Outline, und die
    faerbte dann jede Koerperkante dunkelblau.
    """
    im, a, x0, x1, y0, y1 = bild_daten
    bx = (zentren[:, 0] - mb[0][0]) / (mb[1][0] - mb[0][0])
    if spiegeln:
        bx = 1.0 - bx
    px = np.clip((x0 + bx * (x1 - x0)).astype(int), 0, im.shape[1] - 1)
    bz = (zentren[:, 2] - mb[0][2]) / (mb[1][2] - mb[0][2])
    py = np.clip((y1 - bz * (y1 - y0)).astype(int), 0, im.shape[0] - 1)

    tiefe = zentren[:, 1] if nach_vorne else -zentren[:, 1]
    puffer = np.full(im.shape[:2], np.inf)
    np.minimum.at(puffer, (py, px), tiefe)
    frei = tiefe <= puffer[py, px] + TOLERANZ
    passt = (normalen[:, 1] < -0.05) if nach_vorne else (normalen[:, 1] > 0.05)
    gueltig = frei & passt

    stimmen = np.zeros((len(zentren), len(FARBEN)), np.int16)
    rel_h = (zentren[:, 2] - mb[0][2]) / (mb[1][2] - mb[0][2])
    for dy in (-4, -2, 0, 2, 4):
        for dx in (-4, -2, 0, 2, 4):
            qy = np.clip(py + dy, 0, im.shape[0] - 1)
            qx = np.clip(px + dx, 0, im.shape[1] - 1)
            rgb = im[qy, qx, :3].astype(float)
            ok = a[qy, qx] & (rgb.sum(axis=-1) > 120)      # keine Outline
            k = klasse_von_rgb(rgb, rel_h)
            np.add.at(stimmen, (np.where(ok)[0], k[ok]), 1)
    hat_stimmen = stimmen.sum(axis=1) > 0
    return gueltig & hat_stimmen, np.argmax(stimmen, axis=1).astype(np.int8)


for daten, spiegel, vorne_hin, name in ((front, False, True, "vorne"),
                                        (rueck, True, False, "hinten")):
    gueltig, k = sichtbar(daten, spiegel, vorne_hin)
    klasse[gueltig] = k[gueltig]
    print("  aus %-7s belegt: %6d Dreiecke (%.0f %%)"
          % (name, gueltig.sum(), 100 * gueltig.mean()))

offen = klasse < 0
if offen.any():
    baum = cKDTree(zentren[~offen])
    klasse[offen] = klasse[~offen][baum.query(zentren[offen], k=1)[1]]
print("  per Nachbar ergaenzt: %d Dreiecke (%.0f %%)" % (offen.sum(), 100 * offen.mean()))

# --- Volumen in Voxel zerlegen ---
print("\nVoxel mit %.2f mm Raster ..." % PITCH)
vox = m.voxelized(pitch=PITCH).fill()
gefuellt = np.array(vox.sparse_indices)
punkte = vox.indices_to_points(gefuellt)
print("  %d gefuellte Voxel = %.1f cm3" % (len(punkte), len(punkte) * PITCH**3 / 1000))

baum = cKDTree(zentren)
_, naechstes = baum.query(punkte, k=1, workers=-1)
vox_klasse = klasse[naechstes]

gitter = np.zeros(vox.shape, np.int8)
gitter[tuple(gefuellt.T)] = vox_klasse + 1          # 0 = leer

# --- Farbrauschen entfernen ---------------------------------------------
# Die Zuordnung aus dem Bild ist punktweise und deshalb fleckig: einzelne
# helle Pixel auf dem Hemd landen bei "Haut", Schattenkanten bei "braun".
# Ungefiltert zerfiel allein die Haut in 344 Inseln -- unbrauchbar, jede
# Insel waere ein eigener Materialwechsel. Zwei Schritte dagegen:
#   1. Mehrheitsfilter im 3x3x3-Fenster, zweimal. Jedes Voxel bekommt die
#      Farbe, die in seiner Nachbarschaft ueberwiegt.
#   2. Was dann noch an Inseln unter MIN_VOXEL uebrig ist, wird freigegeben
#      und erbt die Farbe des naechsten verbliebenen Voxels.
from scipy import ndimage
MIN_VOXEL = int(round(2.0 / PITCH ** 3))        # alles unter ~2 mm3 faellt weg
voll = gitter > 0
for runde in range(2):
    zaehler = np.stack([ndimage.uniform_filter((gitter == i + 1).astype(np.float32),
                                               size=3)
                        for i in range(len(FARBEN))])
    neu_gitter = np.argmax(zaehler, axis=0).astype(np.int8) + 1
    gitter = np.where(voll, neu_gitter, 0).astype(np.int8)

inseln_weg = 0
for i in range(len(FARBEN)):
    komp, n = ndimage.label(gitter == i + 1)
    if n == 0:
        continue
    groesse = np.bincount(komp.ravel())
    klein = np.where(groesse < MIN_VOXEL)[0]
    klein = klein[klein > 0]
    if len(klein):
        weg = np.isin(komp, klein)
        gitter[weg] = 0
        inseln_weg += len(klein)
frei = voll & (gitter == 0)
if frei.any():
    belegt_idx = np.argwhere(gitter > 0)
    baum2 = cKDTree(belegt_idx)
    offen_idx = np.argwhere(frei)
    _, nn = baum2.query(offen_idx, k=1, workers=-1)
    gitter[tuple(offen_idx.T)] = gitter[tuple(belegt_idx[nn].T)]
print("  Rauschen entfernt: %d Kleinstinseln aufgeloest, %d Voxel neu vergeben"
      % (inseln_weg, frei.sum()))

# --- je Farbe eine Huelle ---
gesamt_vol = 0.0
teile = []
for i, (name, rgb, was) in enumerate(FARBEN):
    maske = (gitter == i + 1)
    if maske.sum() == 0:
        print("  %s: leer, uebersprungen" % name)
        continue
    pad = np.pad(maske.astype(np.float32), 1)
    ecken, flaechen, _, _ = measure.marching_cubes(pad, level=0.5)
    ecken = (ecken - 1) * PITCH + vox.indices_to_points(np.zeros((1, 3), int))[0]
    teil = trimesh.Trimesh(vertices=ecken, faces=flaechen, process=True)
    teil.merge_vertices()
    trimesh.repair.fix_normals(teil)
    if teil.volume < 0:          # marching_cubes liefert die Wicklung
        teil.invert()            # andersherum als trimesh erwartet
    teil.fix_normals()
    p = os.path.join(ziel, "statue_ams_%s.stl" % name)
    teil.export(p)
    gesamt_vol += teil.volume
    teile.append((name, teil, was))
    print("  %-14s %7d Dreiecke, %5.1f cm3, dicht: %s -> %s"
          % (name, len(teil.faces), teil.volume / 1000, teil.is_watertight,
             os.path.basename(p)))
    print("                 %d Einzelkoerper, %d offene Kanten"
          % (teil.body_count,
             len(teil.edges_sorted)
             - 2 * len(trimesh.grouping.group_rows(teil.edges_sorted,
                                                   require_count=2))))

# --- Gegenproben ---
print("\nPruefungen")
print("  Summe der vier Koerper: %.1f cm3, Original: %.1f cm3, Abweichung %.1f %%"
      % (gesamt_vol / 1000, m.volume / 1000,
         100 * abs(gesamt_vol - m.volume) / m.volume))
belegt = (gitter > 0).sum()
print("  jedes gefuellte Voxel genau einer Farbe zugeordnet: %s"
      % (belegt == len(punkte)))
ecken_min = np.array([t.bounds[0] for _, t, _ in teile]).min(axis=0)
ecken_max = np.array([t.bounds[1] for _, t, _ in teile]).max(axis=0)
print("  gemeinsamer Ursprung, Gesamtmass: %.1f x %.1f x %.1f mm"
      % tuple(ecken_max - ecken_min))
np.save(os.path.join(ziel, "klassen.npy"), klasse)
