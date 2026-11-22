# Kappe für den Lightning-Stecker des Backbone One

Kleine Kappe, die auf die Lightning-Zunge des Backbone One gesteckt wird.
Das Telefon liegt dann an einer glatten, breiteren Kunststofffläche an
statt an der Metallzunge.

| | |
|---|---|
| **Maße** | 12 / 13 / 14 × 6 × 4,7 mm |
| **Aufnahme** | Schlitz für die Zunge 6,7 × 1,5 mm plus Spiel, 3,5 mm tief |
| **Material** | alle drei zusammen unter 1 g |

## Drei Varianten, an der Länge zu erkennen

| Länge | Spiel je Seite | Sitz |
|---|---|---|
| 12 mm | 0,10 mm | am strammsten |
| 13 mm | 0,15 mm | mittel |
| 14 mm | 0,20 mm | am lockersten |

Alle drei drucken und die behalten, die sich mit etwas Druck aufstecken
lässt und dann von selbst hält. Das Spiel einer Steckpassung hängt am
Drucker und am Filament, nicht an der Zeichnung.

## Drucken

Anlagefläche nach unten, Schlitz nach oben, ohne Stützen. Die Fläche,
die am Telefon anliegt, ist damit die glatte Bettseite; die Fase daran
verhindert Elefantenfuß und Kratzkanten. PLA oder PETG genügt. Mit TPU
hält sie besser und ist weicher zum Telefon, dann aber die stramme
Variante nehmen.

## Was gemessen ist und was nicht

**Belegt:** Die Lightning-Zunge ist 6,7 × 1,5 mm (Wikipedia, ein
USPTO-Dokument und mehrere Herstellerseiten stimmen überein).

**Nicht gemessen:**
- Wie weit die Zunge beim Backbone aus dem Gehäuse ragt. Deshalb greift
  die Kappe nur auf die vorderen 3,5 mm. Ragt sie weniger heraus, sitzt
  die Kappe auf dem Gehäuse auf — das ist sogar besser, dann trägt das
  Gehäuse die Klemmkraft statt der Zunge.
- Wie breit die Wiege ist, in der das Telefon sitzt. Die Kappe ist in
  dieser Richtung 6 mm und damit schmaler als jedes Telefon, das hineinpasst.

## Wichtig vor dem Benutzen

**Die Kappe deckt den Stecker ab, die Verbindung läuft übers Kabel.**
Der Backbone One Lightning hat weder Bluetooth noch Akku, er spricht nur
über den Stecker mit dem Telefon (Herstellerseite, Sony-Support, iFixit).
Mit einem Kabel zwischen Backbone und dem iPhone Duo (USB-C) funktioniert
er: Das wurde am Gerät getestet.

**Das iPhone Duo ist zugeklappt 11,3 mm dick** (aufgeklappt 5,2 mm). Ob
das zugeklappt in die Wiege des Backbone passt, ist ungeprüft.

## Dateien

| Datei | Inhalt |
|---|---|
| `projekt/backbone_lightning_kappe_3varianten.3mf` | **für Bambu Studio:** drei getrennte, benannte Objekte, mittig auf der Platte der H2S |
| `stl/backbone_lightning_kappe_3varianten.stl` | dieselben drei Kappen als ein STL-Objekt |

In der 3MF ist jede Kappe ein eigenes Objekt mit Namen, etwa „Kappe 1 -
0.10 mm Spiel - stramm (12 mm lang)“. So lässt sich im Slicer eine
einzelne Kappe abwählen oder nachdrucken. Jede Kappe ist vorher zu einem
dichten Körper vereinigt; die strenge Prüfung von lib3mf meldet keine
Warnung, und alle drei Objekte sind geschlossen und richtig orientiert.

Beim Öffnen sagt Bambu Studio, die Datei stamme nicht aus Bambu Studio,
und lädt nur die Geometrie. Das ist so gewollt: Drucker, Filament und
Schichthöhe kommen aus deinen eigenen Profilen. Danach einmal speichern,
dann ist es ein richtiges Bambu-Projekt.

    python3 generate.py                 # STL
    <venv>/bin/python bambu_projekt.py  # 3MF, braucht trimesh, manifold3d, lxml
