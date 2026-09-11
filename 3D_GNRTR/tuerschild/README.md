# Türschild „Elsie" — großer Buchstabe, Name in Schreibschrift

Vorbild: das klassische zweilagige Kinderzimmer-Türschild — ein großer
Serifen-Anfangsbuchstabe (rosa), quer darüber der Name in Schreibschrift
(creme), der links und rechts über den Buchstaben hinausragt.

| | |
|---|---|
| **Buchstabe E** | 158 × 240 mm, 6 mm dick, Liberation Serif Bold, auf 72 % gestaucht |
| **Schriftzug Elsie** | 269 × 129 mm, 4 mm dick, Great Vibes |
| **Lage** | Schriftzug mittig über dem Buchstaben, Mitte auf 52 % der Buchstabenhöhe, ragt je 55 mm über |
| **Stege** | 2 (i-Punkt 4,7 mm, E→l 9,7 mm), 2,5 mm breit — der Schriftzug ist **ein** Stück |
| **Klebefläche** | 20 % des Schriftzugs liegen auf dem Buchstaben |

## Teile

| Datei | Farbe | Drucken |
|---|---|---|
| `tuerschild_Elsie_1_buchstabe_E_1x_drucken.stl` | rosa | flach, Vorderseite oben |
| `tuerschild_Elsie_2_name_1x_drucken.stl` | creme | flach, Vorderseite oben |

Beide STLs teilen den Ursprung: zusammen in den Slicer geladen sieht man
die Lage; gedruckt werden sie einzeln (zwei Farben) oder als zwei Objekte
mit AMS auf einer Platte (Buchstabe + Schriftzug hochkant nebeneinander:
297 × 269 mm, passt auf die H2S).

**Zusammenbau:** Schriftzug auf die Vorderseite des Buchstabens kleben
(Sekundenkleber oder Klebepads). Die überhängenden Enden tragen sich bei
4 mm PLA selbst. An die Tür mit Klebepads auf der Rückseite des
Buchstabens — die Rückseite ist plan, ohne Löcher.

## Andere Namen

    python3 generate.py --name Emilia
    python3 generate.py --name Noah --hoehe 200

Der große Buchstabe ist der Anfangsbuchstabe (`--buchstabe` überschreibt).
Der Generator prüft: Dichtheit, Zusammenhang des Schriftzugs (alle Inseln
über Stege angebunden), Klebefläche ≥ 15 %, Bauraum.

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
