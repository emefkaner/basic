#!/usr/bin/env python3
"""Ausmalbild (PNG/JPG) in ein sauberes SVG fuer die Lernkarten verwandeln.

    python3 lernkarten/vektorisieren.py bild.png lernkarten/motive/pooh.svg

Was passiert:
1. Bild in Graustufen, 4x hochgerechnet (weichere Kanten fuer potrace).
2. Schwellwert: alles unter --schwelle wird schwarz, der Rest weiss. Damit
   verschwinden helle Hintergruende (Holzmaserung, Papierton, Raster).
3. Auf den Inhalt zugeschnitten, damit das Motiv die Karte spaeter fuellt.
4. potrace erzeugt daraus Kurven -> SVG, beliebig gross druckbar.

Braucht: Pillow und potrace.
    pip install pillow          /  apt-get install -y potrace
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow fehlt:  pip install pillow")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("quelle")
    p.add_argument("ziel")
    p.add_argument("--schwelle", type=int, default=128,
                   help="0-255. Hoeher = mehr wird als Linie erkannt (Standard 128)")
    p.add_argument("--rand", type=int, default=8, help="Rand in Pixeln um das Motiv")
    p.add_argument("--flusen", type=int, default=8,
                   help="potrace --turdsize: Flecken bis zu dieser Groesse wegwerfen")
    a = p.parse_args()

    im = Image.open(a.quelle).convert("L")
    im = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)

    # Schwarzweiss und auf den Inhalt zuschneiden
    sw = im.point(lambda v: 0 if v < a.schwelle else 255, mode="L")
    kasten = sw.point(lambda v: 255 if v == 0 else 0).getbbox()
    if not kasten:
        sys.exit("Kein dunkler Inhalt gefunden - Schwelle anpassen (--schwelle).")
    links, oben, rechts, unten = kasten
    sw = sw.crop((max(0, links - a.rand), max(0, oben - a.rand),
                  min(sw.width, rechts + a.rand), min(sw.height, unten + a.rand)))

    with tempfile.TemporaryDirectory() as tmp:
        pbm = Path(tmp) / "motiv.pbm"
        sw.convert("1").save(pbm)
        Path(a.ziel).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["potrace", "-s", "-o", a.ziel, "--turdsize", str(a.flusen),
             "--alphamax", "1.0", "--opttolerance", "0.2", str(pbm)],
            check=True)

    print(f"geschrieben: {a.ziel}  ({sw.width}x{sw.height} Pixel Vorlage)")


if __name__ == "__main__":
    main()
