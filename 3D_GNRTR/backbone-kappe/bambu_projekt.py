#!/usr/bin/env python3
"""Alle drei Lightning-Kappen als ein 3MF-Projekt fuer Bambu Studio.

    <venv>/bin/python bambu_projekt.py

Schreibt projekt/backbone_lightning_kappe_3varianten.3mf: drei getrennte,
benannte Objekte, mittig auf der Platte der H2S (340 x 320 mm).

Warum nicht einfach die STL: In der STL sind die drei Kappen EIN Objekt,
und jede Kappe besteht aus drei sich ueberlappenden Teilkoerpern. Fuer
den Slicer ist das ein Netz, das sich selbst schneidet. Hier wird jede
Kappe vorher zu einem dichten Koerper vereinigt (manifold3d), und jede
Kappe ist ein eigenes Objekt. So laesst sich im Slicer eine einzelne
Kappe abwaehlen, drehen oder nachdrucken.

Braucht trimesh und manifold3d (pip install trimesh manifold3d).
"""
import os
import zipfile
from xml.sax.saxutils import quoteattr

import manifold3d
import numpy as np
import trimesh

import generate as g

HIER = os.path.dirname(os.path.abspath(__file__))
ZIEL = os.path.join(HIER, "projekt",
                    "backbone_lightning_kappe_3varianten.3mf")

PLATTE = (340.0, 320.0)           # H2S laut Hersteller
NAMEN = ("stramm", "mittel", "locker")


def schale_zu_manifold(tris):
    v = np.array([p for t in tris for p in t], dtype=np.float64)
    m = trimesh.Trimesh(vertices=v, faces=np.arange(len(v)).reshape(-1, 3),
                        process=True)          # gleiche Punkte verschmelzen
    if not m.is_watertight:
        raise SystemExit("FEHLER: Teilkoerper nicht dicht")
    return manifold3d.Manifold(manifold3d.Mesh(
        vert_properties=m.vertices.astype(np.float32),
        tri_verts=m.faces.astype(np.uint32)))


def kappe_vereint(spiel, laenge):
    schalen, masse = g.kappe(spiel, laenge, 0.0)
    teile = [schale_zu_manifold(s) for s in schalen]
    ganz = teile[0]
    for t in teile[1:]:
        ganz = ganz + t                          # Vereinigung
    mesh = ganz.to_mesh()
    m = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                        faces=np.asarray(mesh.tri_verts), process=True)
    return m, masse


def modell_xml(objekte):
    """objekte: Liste (name, trimesh, (x, y))"""
    z = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<model unit="millimeter" xml:lang="de-DE" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
         ' <metadata name="Title">Backbone Lightning-Kappe, 3 Varianten</metadata>',
         ' <metadata name="Designer">3D_GNRTR</metadata>',
         ' <resources>']
    for i, (name, m, _) in enumerate(objekte, start=1):
        z.append('  <object id="%d" type="model" name=%s>' % (i, quoteattr(name)))
        z.append('   <mesh>')
        z.append('    <vertices>')
        z += ['     <vertex x="%.5f" y="%.5f" z="%.5f"/>' % tuple(p)
              for p in m.vertices]
        z.append('    </vertices>')
        z.append('    <triangles>')
        z += ['     <triangle v1="%d" v2="%d" v3="%d"/>' % tuple(f)
              for f in m.faces]
        z.append('    </triangles>')
        z.append('   </mesh>')
        z.append('  </object>')
    z.append(' </resources>')
    z.append(' <build>')
    for i, (_, _, (x, y)) in enumerate(objekte, start=1):
        z.append('  <item objectid="%d" transform="1 0 0 0 1 0 0 0 1 %.3f %.3f 0"/>'
                 % (i, x, y))
    z.append(' </build>')
    z.append('</model>')
    return "\n".join(z) + "\n"


INHALT = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
"""
BEZUEGE = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""


def main():
    objekte = []
    n = len(g.VARIANTEN)
    for i, ((spiel, laenge), wort) in enumerate(zip(g.VARIANTEN, NAMEN)):
        m, (sb, st, h) = kappe_vereint(spiel, laenge)
        if not m.is_watertight or not m.is_winding_consistent or m.volume <= 0:
            raise SystemExit("FEHLER: Kappe %d nicht dicht" % (i + 1))
        name = "Kappe %d - %.2f mm Spiel - %s (%.0f mm lang)" % (
            i + 1, spiel, wort, laenge)
        x = PLATTE[0] / 2 + (i - (n - 1) / 2) * g.ABSTAND
        objekte.append((name, m, (x, PLATTE[1] / 2)))
        print("  %-44s %4d Dreiecke, %.0f mm3, Schlitz %.2f x %.2f mm"
              % (name, len(m.faces), m.volume, sb, st))

    os.makedirs(os.path.dirname(ZIEL), exist_ok=True)
    with zipfile.ZipFile(ZIEL, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", INHALT)
        zf.writestr("_rels/.rels", BEZUEGE)
        zf.writestr("3D/3dmodel.model", modell_xml(objekte))

    # Gegenprobe: Datei wieder einlesen, wie ein fremdes Programm sie sieht
    szene = trimesh.load(ZIEL, force="scene")
    geladen = list(szene.geometry.values())
    if len(geladen) != n or not all(m.is_watertight for m in geladen):
        raise SystemExit("FEHLER: Gegenprobe der 3MF fehlgeschlagen")
    lo, hi = szene.bounds
    print("\n%s: %d Objekte, alle dicht, auf der Platte x %.1f..%.1f, "
          "y %.1f..%.1f, z %.1f..%.1f mm"
          % (os.path.relpath(ZIEL, HIER), len(geladen),
             lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))


if __name__ == "__main__":
    main()
