# Türschild „Elsie" — großer Buchstabe, Name in Schreibschrift

Vorbild: das klassische zweilagige Kinderzimmer-Türschild — ein großer
Serifen-Anfangsbuchstabe (rosa), quer darüber der Name in Schreibschrift
(creme), der links und rechts über den Buchstaben hinausragt.

| | |
|---|---|
| **Buchstabe E** | 158 × 240 mm, 6 mm dick, Liberation Serif Bold, auf 72 % gestaucht |
| **Schriftzug Elsie** | 269 × 129 mm, 4 mm dick, Great Vibes |
| **Lage** | Schriftzug mittig über dem Buchstaben, Mitte auf 32 % der Höhe (unteres Drittel, auf dem unteren Balken), ragt je 55 mm über |
| **Stege** | 2 (i-Punkt 4,7 mm, E→l 9,7 mm), 2,5 mm breit — der Schriftzug ist **ein** Stück |
| **Klebefläche** | 22 % des Schriftzugs liegen auf dem Buchstaben |

Die Höhe des Schriftzugs steuert `NAME_MITTE` in `generate.py`: 0,32
heißt Mitte auf 32 % der Buchstabenhöhe. Tiefer als 0,27 läuft er unten
über den Buchstaben hinaus.

## Zwei Wege zum selben Schild

Der Generator schreibt beide Varianten. Von vorn sehen sie gleich aus.

### A — AMS: ein Druck, zwei Filamente (empfohlen)

| Datei | Filament | z |
|---|---|---|
| `tuerschild_Elsie_ams_filament1_rosa_1x_drucken.stl` | rosa | 0 – 6 mm |
| `tuerschild_Elsie_ams_filament2_creme_1x_drucken.stl` | creme | 6 – 10 mm |

Die Farben liegen **übereinander** und berühren sich in einer Ebene bei
6 mm — im Druck verschmelzen sie zu einem Stück. Kein Kleber, nichts
kann verrutschen, genau **ein** Farbwechsel über die ganze Höhe.

Farbe 1 ist nicht nur der Buchstabe, sondern der Buchstabe **plus der
Umriss des Schriftzugs**: der Schriftzug ragt je 55 mm über den
Buchstaben hinaus und hätte dort sonst nichts unter sich. So steht jeder
Punkt der oberen Farbe auf Material — nichts schwebt, keine Stützen.

Laden: beide Dateien zusammen auswählen, beim Dialog *„mehrteiliges
Objekt?"* → **Ja**, dann je Teil das Filament zuweisen. Grundfläche
269 × 240 mm, 10 mm hoch, ~165 cm³.

### B — Kleben: zwei einfarbige Drucke

| Datei | Farbe | Drucken |
|---|---|---|
| `tuerschild_Elsie_1_buchstabe_E_1x_drucken.stl` | rosa | flach, Vorderseite oben |
| `tuerschild_Elsie_2_name_1x_drucken.stl` | creme | flach, Vorderseite oben |

Auch hier teilen beide STLs den Ursprung; zusammen geladen sieht man die
Lage. Ohne AMS nacheinander drucken, mit AMS als zwei Objekte
nebeneinander auf einer Platte (hochkant 297 × 269 mm, passt auf die
H2S). Braucht weniger Material (~128 cm³), weil der Schriftzug keine
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
| Great Vibes | festlich, starker Strichkontrast (Standard) | 2,4 mm | 2 |
| Parisienne | zierlich und ruhig, gut lesbar | 3,2 mm | 1 |
| Alex Brush | flott, schräg, gleichmäßig dünn | 2,4 mm | 2 |
| Sacramento | monolinear, modern, fast ohne Kontrast | 4,9 mm | 2 |
| Dancing Script | verspielt, freundlich, kindgerecht | 2,4 mm | 2 |
| Kaushan Script | kräftiger Pinsel, sehr präsent | 4,1 mm | 5 |
| Pacifico | dick und rund, Retro, am robustesten | 10,5 mm | 1 |

Gewählte Schrift drucken:

    python3 generate.py --schrift pacifico

Alle sieben sind bei dieser Größe druckbar — kritisch wird es erst unter
etwa 1,2 mm, dort bleiben bei 0,4 mm Düse nur zwei Wandlinien ohne Kern.
Die Dateinamen tragen die Schrift, so lassen sich mehrere nebeneinander
aufheben. Fonts und ihre Lizenzen liegen in `schriften/` (alle SIL OFL).

## Andere Namen

    python3 generate.py --name Emilia
    python3 generate.py --name Noah --hoehe 200
    python3 generate.py --name Mia --schrift parisienne --mitte 0.40

Der große Buchstabe ist der Anfangsbuchstabe (`--buchstabe` überschreibt).
Der Generator prüft: Dichtheit, Zusammenhang des Schriftzugs (alle Inseln
über Stege angebunden), Klebefläche ≥ 15 %, Bauraum — und für die
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

Laufweite bleibt bei 100 %: Great Vibes ist so gezeichnet, dass die
Verbindungsstriche genau dort treffen. Enger gesetzt kollidieren l, s
und i.

Fonts: Great Vibes (SIL OFL, `OFL.txt`), Liberation Serif (SIL OFL,
`LICENSE-LiberationSerif.txt`).
