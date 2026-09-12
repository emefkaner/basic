# Türschild „Elsie" — großer Buchstabe, Name in Schreibschrift

Vorbild: das klassische zweilagige Kinderzimmer-Türschild — ein großer
Serifen-Anfangsbuchstabe (rosa), quer darüber der Name in Schreibschrift
(creme), der links und rechts über den Buchstaben hinausragt.

| | |
|---|---|
| **Buchstabe E** | 158 × 240 mm, 6 mm dick, Liberation Serif Bold, auf 72 % gestaucht |
| **Schriftzug Elsie** | 269 × 123 mm, 4 mm dick, Dancing Script im fetten Schnitt (Gewicht 700) |
| **Lage** | Schriftzug mittig über dem Buchstaben, Mitte auf 32 % der Höhe (unteres Drittel, auf dem unteren Balken), ragt je 55 mm über |
| **Stege** | 2 (13,6 und 1,0 mm), 2,5 mm breit — der Schriftzug ist **ein** Stück |
| **Klebefläche** | 24 % des Schriftzugs liegen auf dem Buchstaben |
| **Strichbreite** | im Mittel 10,3 mm, dünnste Stelle 4,1 mm |

Die Höhe des Schriftzugs steuert `NAME_MITTE` in `generate.py`: 0,32
heißt Mitte auf 32 % der Buchstabenhöhe. Tiefer als 0,27 läuft er unten
über den Buchstaben hinaus.

## Zwei Wege zum selben Schild

Der Generator schreibt beide Varianten. Von vorn sehen sie gleich aus.

### A — AMS: ein Druck, zwei Filamente (empfohlen)

| Datei | Filament | z |
|---|---|---|
| `tuerschild_Elsie_dancingscript700_ams_filament1_rosa_1x_drucken.stl` | rosa | 0 – 6 mm |
| `tuerschild_Elsie_dancingscript700_ams_filament2_creme_1x_drucken.stl` | creme | 6 – 10 mm |

Die Farben liegen **übereinander** und berühren sich in einer Ebene bei
6 mm — im Druck verschmelzen sie zu einem Stück. Kein Kleber, nichts
kann verrutschen, genau **ein** Farbwechsel über die ganze Höhe.

Farbe 1 ist nicht nur der Buchstabe, sondern der Buchstabe **plus der
Umriss des Schriftzugs**: der Schriftzug ragt je 55 mm über den
Buchstaben hinaus und hätte dort sonst nichts unter sich. So steht jeder
Punkt der oberen Farbe auf Material — nichts schwebt, keine Stützen.

Laden: beide Dateien zusammen auswählen, beim Dialog *„mehrteiliges
Objekt?"* → **Ja**, dann je Teil das Filament zuweisen. Grundfläche
269 × 240 mm, 10 mm hoch, ~190 cm³.

### B — Kleben: zwei einfarbige Drucke

| Datei | Farbe | Drucken |
|---|---|---|
| `tuerschild_Elsie_dancingscript700_1_buchstabe_E_1x_drucken.stl` | rosa | flach, Vorderseite oben |
| `tuerschild_Elsie_dancingscript700_2_name_1x_drucken.stl` | creme | flach, Vorderseite oben |

Auch hier teilen beide STLs den Ursprung; zusammen geladen sieht man die
Lage. Ohne AMS nacheinander drucken, mit AMS als zwei Objekte
nebeneinander auf einer Platte (hochkant 297 × 269 mm, passt auf die
H2S). Braucht weniger Material (~138 cm³), weil der Schriftzug keine
Unterlage hat.

**Zusammenbau:** Schriftzug auf die Vorderseite des Buchstabens kleben
(Sekundenkleber oder Klebepads). Die überhängenden Enden tragen sich bei
4 mm PLA selbst.

An die Tür kommt bei beiden Varianten Klebepad auf die Rückseite — die
ist plan, ohne Löcher.

## Schriftart wählen

    python3 schriftvergleich.py

schreibt `stl/schriftvergleich.svg` und `.png`: alle Kandidatinnen
untereinander, jede in Originalgröße über dem großen Buchstaben. Dazu
eine Tabelle mit der **dünnsten Stelle** im Schriftzug (über Raster und
Distanztransformation auf der Mittelachse gemessen, nicht geschätzt) und
der Zahl nötiger Stege.

| Schrift | Charakter | dünnste Stelle | Stege |
|---|---|---|---|
| Great Vibes | festlich, starker Strichkontrast | 2,4 mm | 2 |
| Parisienne | zierlich und ruhig, gut lesbar | 3,2 mm | 1 |
| Alex Brush | flott, schräg, gleichmäßig dünn | 2,4 mm | 2 |
| Sacramento | monolinear, modern, fast ohne Kontrast | 4,9 mm | 2 |
| **Dancing Script 700** | **verspielt, freundlich, kindgerecht (Standard)** | **4,1 mm** | **2** |
| Kaushan Script | kräftiger Pinsel, sehr präsent | 4,1 mm | 5 |
| Pacifico | dick und rund, Retro, am robustesten | 10,5 mm | 1 |

Gewählte Schrift drucken:

    python3 generate.py --schrift pacifico

Alle sieben sind bei dieser Größe druckbar — kritisch wird es erst unter
etwa 1,2 mm, dort bleiben bei 0,4 mm Düse nur zwei Wandlinien ohne Kern.
Die Dateinamen tragen die Schrift, so lassen sich mehrere nebeneinander
aufheben. Fonts und ihre Lizenzen liegen in `schriften/` (alle SIL OFL).

### Strichstärke

Dancing Script ist eine Variable Font mit Gewichtsachse 400 bis 700.
`--staerke` legt sie fest, Standard ist 700, also der fetteste Schnitt:

    python3 generate.py --staerke 550      # halbfett, falls 700 zu wuchtig ist

Das ist kein nachträgliches Aufdicken, sondern die echte fette Zeichnung
des Entwerfers — `instantiateVariableFont` backt die Achse in die
Umrisse ein. Ein Offset würde auch die Rundungen aufblähen und enge
Punzen zuschmieren. Wirkung: mittlere Strichbreite 7,6 → 10,3 mm,
dünnste Stelle 2,4 → 4,1 mm, Cremefilament 25 → 35 cm³.

## Andere Namen

    python3 generate.py --name Emilia
    python3 generate.py --name Noah --hoehe 200
    python3 generate.py --name Mia --schrift parisienne --mitte 0.40

Der große Buchstabe ist der Anfangsbuchstabe (`--buchstabe` überschreibt).
Der Generator prüft: Dichtheit, Zusammenhang des Schriftzugs (alle Inseln
über Stege angebunden), Bauraum, Klebefläche (unter 15 % eine Warnung
für die Klebevariante, unter 8 % Abbruch) — und für die
AMS-Variante zusätzlich, dass die beiden Farbkörper sich in z nicht
überlappen, dass jeder Rasterpunkt der oberen Farbe auf der unteren steht
und dass die untere Farbe ein einziges zusammenhängendes Stück ist.

`python3 vorschau.py` schreibt `stl/ansicht_vorne.svg` (so hängt es an
der Tür) und `stl/ansicht_ams_schnitt.svg` (Schnitt durch den Farbstapel).

## Drei Fallen bei Schreibschrift, alle im Generator abgefangen

1. **Zusammengesetzte Glyphen.** Das „i" in Great Vibes besteht aus
   Strich und Punkt als *Komponenten*. Der normale `RecordingPen` liefert
   dafür keine Kontur — der Buchstabe fehlte, „Elsie" las sich als
   „Else". Erst beim Zählen der Glyphen aufgefallen. Deshalb
   `DecomposingRecordingPen`.
2. **Löcher je Glyphe bestimmen, nicht global.** Schreibschrift
   überlappt Nachbarbuchstaben; eine globale Zählung „liegt in einer
   ungeraden Zahl anderer Konturen" hält dann Außenkonturen für Löcher.
3. **Inseln.** i-Punkt und oft der Anfangsbuchstabe hängen nicht am
   Rest. Ein Schriftzug aus drei Teilen lässt sich nicht gerade
   aufkleben. Jede Insel wird über einen schmalen Steg an den nächsten
   Nachbarn angebunden, und der Zusammenhang wird danach geprüft.

Laufweite bleibt bei 100 %: die Schreibschriften sind so gezeichnet,
dass die Verbindungsstriche genau dort treffen. Enger gesetzt
kollidieren l, s und i.

Fonts: Great Vibes (SIL OFL, `OFL.txt`), Liberation Serif (SIL OFL,
`LICENSE-LiberationSerif.txt`), die sechs Schreibschriften in
`schriften/` (alle SIL OFL, Lizenz je Familie daneben).
