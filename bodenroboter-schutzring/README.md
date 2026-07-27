# Auffahrschutz-Ring fürs Tischbein

Runder Schutzwall, der um einen Tischfuß gelegt wird, damit der Saug-/Wischroboter
nicht mehr darauf auffährt und sich festfährt.

| Maß | Wert |
|---|---|
| Außendurchmesser | 365 mm |
| Innendurchmesser (lichte Weite für den Fuß) | 355 mm |
| Wandstärke | 5 mm |
| Höhe | 50 mm |
| Oberkante | innen und außen mit R2 verrundet |
| Unterkante | scharfkantig, damit der Ring plan aufliegt |

## Warum geteilt und nicht am Stück?

Zwei unabhängige Gründe:

1. **Bauraum.** 365 mm Außendurchmesser braucht 365 mm in *beide* Richtungen.
   Ein Kreis wird durch Drehen nicht kleiner — auf einem 350 × 350 mm Bett
   fehlen exakt 15 mm. Die Datei `schutzring_einteilig_komplett.stl` liegt
   trotzdem bei, falls sie mal auf einen größeren Drucker soll.
2. **Montage.** Einen geschlossenen Ring bekommt man nicht um ein montiertes
   Tischbein herum, ohne den Tisch zu zerlegen.

Deshalb: identische Kreissegmente mit senkrechter Schwalbenschwanz-Steck­verbindung.
Zusammengesteckt ergeben sie einen geschlossenen Ring, der als Hoop in sich steif
ist — der Hebel ist 365 mm Standbreite gegen ~40 mm Anstoßhöhe, da kippt nichts weg.
Ein zusätzlicher Bodenflansch ist deshalb nicht nötig.

## Welche Datei?

| Datei | Segmente | Grundfläche je Segment | Passt auf 350 × 350 |
|---|---|---|---|
| `schutzring_2teilig_segment.stl` | 2 × drucken | 321,5 × 321,5 mm bei 44,4° gedreht | ja, 28,5 mm Rand |
| `schutzring_3teilig_segment.stl` | 3 × drucken | 246 × 246 mm | ja, reichlich Rand |
| `schutzring_4teilig_segment.stl` | 4 × drucken | 199 × 199 mm | ja |
| `schutzring_einteilig_komplett.stl` | — | 365 × 365 mm | **nein**, 15 mm zu groß |

**Empfehlung: die 2-teilige Variante.** Sie passt diagonal auf ein echtes
350 × 350er Bett und hat nur zwei Stoßstellen. Wenn der nutzbare Bereich in einer
Achse kleiner ist als 322 mm (z. B. 350 × 320), dann die 3-teilige Variante nehmen.
Die Grundflächen oben sind die Lage mit dem größten Randabstand; Bambu Studio
findet mit "Auto-Anordnen" in der Regel selbst eine passende Drehung.

## Steckverbindung

An jeder Stoßstelle sitzt ein Verbindungsklotz, der die Wand lokal von 5 mm auf
17 mm verdickt — nur nach **außen**, damit die Innenfläche ein sauberer Zylinder
bleibt und die volle lichte Weite für den Tischfuß erhalten bleibt. Im Klotz sitzt
ein Schwalbenschwanz: Hals 4 mm, Kopf 6,5 mm, Tiefe 9 mm, 0,25 mm Spiel je Flanke,
unten 0,6 mm Einführfase.

Gesteckt wird **senkrecht von oben**. Dadurch lässt sich das letzte Segment in
beide Nachbarn gleichzeitig einschieben — bei einem geschlossenen Ring geht das
mit tangentialen Verbindungen prinzipiell nicht.

Örtlich ist der Ring an den Klötzen 389 mm im Außendurchmesser statt 365 mm.
Innen bleibt es überall bei 355 mm.

## Drucken

- **Material:** PETG. Ein Wischroboter bringt Feuchtigkeit mit, und PETG ist
  zäher gegen die dauernden Stöße. PLA funktioniert auch, ist aber spröder.
- **Lage:** so wie in der STL, also stehend (Z = Wandhöhe). Keine Stützen nötig,
  es gibt keine Überhänge.
- **Brim:** ja, ~5 mm. Hohe dünne Wand auf schmaler Standfläche.
- **Wände/Infill:** 3 Wandlinien und 15–20 % Infill reichen. Wer es massiv will,
  stellt bei 0,4er Düse 6 Wandlinien und 0 % Infill ein — dann ist die 5-mm-Wand
  komplett aus Perimetern.
- **Schichthöhe:** 0,2–0,28 mm, das Teil hat keine feinen Details.
- **Materialbedarf:** massiv gerechnet 342 cm³ für die 2-teilige Variante
  (~420 g PLA). Mit den empfohlenen Einstellungen landet man grob bei 190–210 g.
  Die 3-teilige Variante braucht wegen der zusätzlichen Stoßstelle etwas mehr.

## Zusammenbau

1. Segment zweimal (bzw. drei-/viermal) drucken.
2. Erstes Segment um den Tischfuß legen.
3. Zweites Segment gerade von oben herunterschieben, bis es plan aufliegt.
   Dafür braucht es etwa 10 cm freie Höhe über dem Boden — unter einem Tisch
   kein Problem.
4. Sitzt es zu stramm: die Zapfenflanken kurz mit Schleifpapier brechen.
   Sitzt es zu locker: ein Tropfen Sekundenkleber in die Nut.

## Ansichten

Im Ordner `stl/`:

- `ansicht_ring_2teilig.svg` — zusammengesteckter Ring
- `ansicht_segment_2teilig.svg` — ein einzelnes Segment
- `ansicht_steckverbindung.svg` — maßstäbliche Detailzeichnung der Stoßstelle
- `vorschau.svg` — Querschnitt der 2- und 3-teiligen Variante

## Maße ändern

Alle Maße stehen als Konstanten oben in `generate.py`. Ändern und neu erzeugen:

```bash
python3 generate.py     # schreibt die STL-Dateien nach stl/
python3 vorschau.py     # schreibt die Ansichten nach stl/
```

Beides läuft mit reinem Python 3, ohne Abhängigkeiten und ohne installiertes CAD.

Die Bauteile entstehen als Stapel waagerechter Querschnitte mit identischer
Punktreihenfolge, die zu einem Mesh verbunden werden — keine Boolean-Operationen,
daher keine typischen STL-Fehler. `generate.py` prüft nach dem Erzeugen, dass jede
Kante genau zweimal vorkommt, und bricht ab, wenn ein Mesh nicht geschlossen ist.

Wenn `AUSSEN_DURCHMESSER` oder `KLOTZ_AUSSEN` geändert wird: der Klotz muss dick
genug bleiben, damit neben der Nut nach der Kantenverrundung noch Material steht.
Die Bedingung lautet

```
KLOTZ_AUSSEN / 2 >= VERRUNDUNG + SCHWALBE_KOPF / 2 + SPIEL - WANDSTAERKE / 2 + mindestwand
```

Mit den aktuellen Werten bleiben neben der Nut oben 3,0 mm stehen.
