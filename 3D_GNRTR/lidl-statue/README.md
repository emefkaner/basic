# Statue aus einem Comicbild — vierfarbig für die AMS

Aus einer einzelnen Zeichnung wird eine stehende Figur, 150 mm hoch,
zerlegt in vier Farbkörper für den Mehrfarbdruck.

| | |
|---|---|
| **Höhe** | 150 mm (skalierbar, siehe unten) |
| **Grundfläche** | 53 × 30 mm, Standfläche 30 × 20 mm |
| **Volumen** | 69 cm³ massiv, verteilt auf vier Körper |
| **Dateien** | vier STL mit gemeinsamem Ursprung, alle wasserdicht |

## Die vier Farben

| Datei | Region | Volumen |
|---|---|---|
| `statue_ams_1_braun_haare.stl` | Haare | 11,4 cm³ |
| `statue_ams_2_haut.stl` | Gesicht und Hände | 4,6 cm³ |
| `statue_ams_3_dunkelblau.stl` | Weste, Schuhe, Brille | 25,6 cm³ |
| `statue_ams_4_mittelblau.stl` | Hemd und Jeans | 27,3 cm³ |

In Bambu Studio alle vier zusammen auswählen, beim Dialog
*„mehrteiliges Objekt?"* → **Ja**, dann je Teil das Filament zuweisen.
Die Körper teilen sich das Volumen überschneidungsfrei, sie überlappen
nirgends.

## Ablauf, in der Reihenfolge der Skripte

1. **`freistellen.py`** — Hintergrund per Flutfüllung vom Rand weg. Kein
   globaler Farbschlüssel: Jeans und Hemd sind selbst blau, ein
   Schlüssel hätte sie mitgelöscht.
2. **Rückansicht erzeugen.** Ein Modell, das nur die Front kennt, muss
   den Hinterkopf erfinden — beim ersten Versuch kam ein glatter Lappen
   statt Haaren heraus. Deshalb wird aus der Front ein Rückenbild
   erzeugt (`bilder/rueckansicht_roh.png`) und beides zusammen
   rekonstruiert.
3. **`paaren.py`** — beide Ansichten auf dieselbe Figurhöhe bringen.
   Mehransichts-Rekonstruktion setzt gleiche Größe voraus.
4. **Rekonstruktion** zu `quelle/figur_front_rueck.glb` (Hunyuan3D v3,
   nur Geometrie, 500 000 Flächen).
5. **`aufbereiten.py`** — GLB → STL: aufrichten, auf Zielhöhe skalieren,
   auf z = 0 stellen, Dichtheit und Standfläche prüfen.

       python3 aufbereiten.py quelle/figur_front_rueck.glb 150 stl

6. **`ams_teilen.py`** — die Vierfarb-Zerlegung.

       python3 ams_teilen.py stl/statue_roh_150mm.stl \
           bilder/ansicht_front.png bilder/ansicht_rueck.png stl 0.3

7. **`rendern.py`** / **`farbansicht.py`** — Ansichten von vier Seiten,
   grau beziehungsweise in den vier Druckfarben.

Gebraucht werden `trimesh`, `numpy`, `scipy`, `scikit-image`, `pillow`.

## Warum die Farbzuordnung so aussieht

**Gemessen statt geschätzt.** Die Palette beider Bilder wurde per
k-Means bestimmt: Jeans 50/78/109, Weste 40/54/76, Haut 223/168/132,
Hemd 163/189/215, Haare 103/74/57, Grau 127/129/138, Glanzlicht
204/211/222.

**Weste und Jeans lassen sich nicht über die Farbe trennen** — Summe 214
gegen 221, das ist dasselbe Blau. Nach Farbe allein wurde die ganze
Figur einfarbig blau. Getrennt wird deshalb über die Höhe, abgelesen am
Zeilenprofil der Frontansicht: bis 9 % der Figurhöhe Schuhe, bis 47 %
Jeans, darüber Weste. Haut und Haare laufen weiter über die Farbe, da
ist der Abstand groß genug.

**Verdeckte Flächen bekommen keine Farbe aus dem Bild.** Eine reine
Projektion gab der Brust hinter dem angewinkelten Arm die Farbe des
Ärmels — die Seitenansichten waren übersät mit Flecken. Jetzt entscheidet
ein Tiefenpuffer in Bildauflösung, ob ein Dreieck überhaupt zu sehen ist.

**Abgetastet wird ein 5×5-Fenster, gewertet die häufigste Klasse.** Ein
einzelnes Pixel trifft an der Silhouette fast immer die schwarze
Outline, die färbte sonst jede Körperkante dunkelblau.

**Das Farbrauschen wird gefiltert.** Punktweise Zuordnung ist fleckig;
ungefiltert zerfiel allein die Haut in 344 Inseln, jede wäre ein eigener
Materialwechsel. Zwei Durchgänge Mehrheitsfilter im 3×3×3-Fenster, danach
fallen Inseln unter 2 mm³ weg und erben die Farbe des Nachbarn. Übrig
bleiben 5 bis 16 Körper je Farbe.

## Was an dieser Statue nicht aus dem Bild stammt

- **Die Seiten.** Vorder- und Rückansicht sind belegt, die Körperseiten
  nur über die Silhouettenränder. Dort mischen sich Weste und Hemd
  stellenweise. Von vorn und hinten stimmt es.
- **Alles Räumliche.** Zwei Ansichten sagen nichts über die Tiefe. Die
  Figur ist 30 mm tief bei 53 mm Breite, das ist eine Annahme des
  Modells, keine Messung.
- **Das Logo auf der Weste** ist in vier Farben nicht darstellbar und
  fällt weg.

## Oberfläche: Voxel, nicht Originalnetz

Die vier Körper entstehen aus einem Voxelraster von 0,3 mm, nicht aus dem
Originalnetz. Nur so teilen sie sich das Volumen garantiert
überschneidungsfrei — und das braucht der Slicer für ein mehrteiliges
Objekt. Der Preis: die Oberfläche weicht um bis zu 0,15 mm vom Original
ab. Das liegt unter dem, was eine 0,4-mm-Düse auflöst.

Nebeneffekt: die Summe der vier Körper ist mit 68,9 cm³ um 4,6 % größer
als das Original (65,9 cm³). Die Füllung legt eine halbe Voxelschale um
die Figur.

## Andere Höhe, feineres Raster

    python3 aufbereiten.py quelle/figur_front_rueck.glb 200 stl   # 200 mm
    python3 ams_teilen.py ... stl 0.2                             # feiner

Feineres Raster heißt glattere Oberfläche und deutlich größere Dateien;
bei 0,3 mm sind die vier STL zusammen rund 57 MB. Deshalb liegen sie
**nicht** im Repo — die beiden Befehle oben erzeugen sie neu.

## Drucken

Stehend, ohne Stützen geht es nicht: der angewinkelte Arm und die Haare
hängen über. Mit Stützen nur unter dem Arm kommt man hin. Alternativ in
der Mitte teilen und stehend ohne Überhang drucken.

Rechtliches: Das Logo ist Marke des Unternehmens. Die Figur ist für den
Eigengebrauch gedacht, nicht zum Verkauf.

## Vorschau im Browser: `web/`

Drehbare Ansicht mit Metallic-Gold, für `www.emefka.com/lina`. Zwei
Dateien, sonst nichts:

| Datei | Inhalt |
|---|---|
| `web/index.html` | Seite mit three.js 0.187 vom CDN jsdelivr |
| `web/lina.glb` | die Figur, auf 150 000 Dreiecke reduziert, 3,6 MB |

Das Gold ist ein physikalisch basiertes Material: Metallic 1, darüber
eine Klarlackschicht, und ein Studioraum (`RoomEnvironment`) zum
Spiegeln — ohne Umgebung sähe Metall flach braun aus. Der Regler unten
rechts stellt den Lack von matt bis hochglänzend ein, das hilft bei der
Wahl des Sprühlacks. Tonemapping ist `Neutral` statt `ACES`, weil ACES
Gold in den Lichtern ins Weißgelbe zieht.

Die Seite trägt `noindex`, Suchmaschinen nehmen sie also nicht auf.

**Hochladen** geht nur vom eigenen Rechner aus: Strato nimmt Dateien nur
per SFTP auf Port 22 an, und der ist in der Cloud-Sitzung gesperrt
(geprüft). Ziel auf dem Webspace ist `/neu/lina/` — `/neu` ist das
Wurzelverzeichnis von emefka.com, nicht der oberste Ordner. Beide Dateien
zusätzlich nach `Dropbox/_CLAUDE/WEB_emefka.com/lina/` legen, damit das
Webprojekt sie kennt. Für zwei Dateien einzeln per paramiko hochladen,
nicht das ganze Projekt neu (2,4 GB). Zugangsdaten liest das Werkzeug
selbst aus `WEB_emefka.com/tools/.deploy-credentials`; das Passwort nie
ausgeben. Prüfen mit Cache-Brecher, Strato hat einen Zwischenspeicher:

    curl -s -o /dev/null -w "%{http_code}\n" "https://www.emefka.com/lina/?cb=$RANDOM"

`emefka.com/lina` leitet auf `www.emefka.com/lina` weiter und nimmt den
Pfad mit (geprüft).

**Geprüft** in Chromium per Playwright: lädt in 1280 × 800 und in
400 × 820, dreht sich beim Ziehen, Lackregler wirkt, keine
Konsolenfehler. Nicht geprüft: Safari auf dem iPhone.

Das Web-Netz ist nur für die Ansicht reduziert. Gedruckt wird die volle
Auflösung aus `aufbereiten.py`.
