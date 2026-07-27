# Auffahrschutz-Ring fürs Tischbein

Runder Schutzwall, der über den Tischfuß gestülpt wird, damit der Saug-/Wischroboter
nicht mehr darauf auffährt und sich festfährt.

| Maß | Wert |
|---|---|
| Wandstärke | 5 mm |
| Höhe | 50 mm |
| Oberkante | innen und außen mit R2 verrundet |
| Unterkante | scharfkantig, damit der Ring plan aufliegt |

Ein geschlossener Ring ist als Hoop in sich steif — der Hebel ist der ganze
Durchmesser als Standbreite gegen ~40 mm Anstoßhöhe. Da kippt nichts weg, ein
zusätzlicher Bodenflansch ist nicht nötig.

## Welche Datei?

Der einteilige Ring ist die Hauptvariante. Maßgeblich für den Bauraum ist immer
die **kürzere** Bettkante: ein Kreis braucht seinen Durchmesser in beiden Achsen,
Drehen bringt nichts.

| Datei | Außen | Innen (lichte Weite) | Braucht Bettkante |
|---|---|---|---|
| `schutzring_einteilig_335mm.stl` | 335 mm | **325 mm** | ≥ 350 mm |
| `schutzring_einteilig_305mm.stl` | 305 mm | **295 mm** | ≥ 320 mm |
| `schutzring_einteilig_365mm.stl` | 365 mm | 355 mm | ≥ 380 mm — passt auf die H2S **nicht** |

Beide druckbaren Größen lassen 7,5 mm Rand je Seite. Wer einen Brim fahren will,
rechnet dessen Breite nochmal je Seite ab — oder nimmt einen Skirt statt Brim.

**Entscheidend ist die lichte Weite.** Der Tischfuß muss durch die 325 mm bzw.
295 mm passen. Das ist die einzige Zahl, die vorher gemessen sein sollte.

### Warum nicht 365 mm am Stück?

Rein geometrisch:

- Ein Kreis mit 365 mm Durchmesser braucht 365 mm in beiden Achsen. Drehen macht
  ein rundes Teil nicht schmaler.
- Kippen hilft auch nicht: um die Grundfläche unter 350 mm zu drücken, müsste der
  Ring um ≥ 69° gekippt werden. Dann ist er 359 mm hoch und reißt die Z-Grenze
  von 325 mm — abgesehen von den Stützen, die das bräuchte.

Die 365-mm-Datei liegt für einen größeren Drucker trotzdem bei.

### Rückfallvariante, falls der Fuß breiter ist als 325 mm

Dann geht einteilig auf diesem Drucker nicht mehr, und es bleiben die geteilten
Ringe mit vollen 365 mm außen / 355 mm innen. Sie werden über eine senkrechte
Schwalbenschwanz-Verbindung von oben zusammengesteckt.

| Datei | Segmente | Grundfläche je Segment |
|---|---|---|
| `schutzring_2teilig_segment.stl` | 2 × drucken | 321,5 × 321,5 mm bei 44,4° gedreht |
| `schutzring_3teilig_segment.stl` | 3 × drucken | 246 × 246 mm |
| `schutzring_4teilig_segment.stl` | 4 × drucken | 199 × 199 mm |

An jeder Stoßstelle sitzt ein Verbindungsklotz, der die Wand lokal auf 17 mm
verdickt — nur nach **außen**, damit innen überall die vollen 355 mm frei bleiben.
Schwalbenschwanz: Hals 4 mm, Kopf 6,5 mm, Tiefe 9 mm, 0,25 mm Spiel je Flanke,
unten 0,6 mm Einführfase. Gesteckt wird senkrecht von oben — nur so lässt sich
das letzte Segment in beide Nachbarn gleichzeitig einschieben.

## Drucken

- **Material:** PETG. Ein Wischroboter bringt Feuchtigkeit mit, und PETG ist zäher
  gegen die dauernden Stöße. PLA geht auch, ist aber spröder.
- **Lage:** so wie in der STL, also stehend (Z = Wandhöhe). Keine Stützen nötig,
  es gibt keine Überhänge.
- **Haftung:** der geschlossene Ring ist beim Drucken in sich stabil und steht
  auf gut 5000 mm² Fläche. Ein Skirt reicht meist; bei PETG-Neigung zum Lösen
  lieber einen schmalen Brim — dann aber den Platzbedarf beachten.
- **Wände/Infill:** 3 Wandlinien und 15–20 % Infill reichen. Wer es massiv will,
  stellt bei 0,4er Düse 6 Wandlinien und 0 % Infill ein — dann besteht die
  5-mm-Wand komplett aus Perimetern.
- **Schichthöhe:** 0,2–0,28 mm, das Teil hat keine feinen Details.
- **Materialbedarf** (335 mm einteilig): massiv gerechnet 257 cm³. Mit den
  empfohlenen Einstellungen landet man grob bei 140–160 g.

## Ansichten

Im Ordner `stl/`:

- `ansicht_ring_einteilig.svg` — der einteilige Ring
- `ansicht_ring_2teilig.svg` — die geteilte Rückfallvariante
- `ansicht_steckverbindung.svg` — maßstäbliche Detailzeichnung der Stoßstelle
- `vorschau.svg` — Querschnitt der geteilten Varianten

## Maße ändern

Alle Maße stehen als Konstanten oben in `generate.py`, die Durchmesser der
einteiligen Ringe in `EINTEILIG_DURCHMESSER`. Ändern und neu erzeugen:

```bash
python3 generate.py     # schreibt die STL-Dateien nach stl/
python3 vorschau.py     # schreibt die Ansichten nach stl/
```

Beides läuft mit reinem Python 3, ohne Abhängigkeiten und ohne installiertes CAD.

Die Bauteile entstehen als Stapel waagerechter Querschnitte mit identischer
Punktreihenfolge, die zu einem Mesh verbunden werden — keine Boolean-Operationen,
daher keine typischen STL-Fehler. `generate.py` prüft nach dem Erzeugen, dass jede
Kante genau zweimal vorkommt, und bricht ab, wenn ein Mesh nicht geschlossen ist.

Für die geteilte Variante gilt zusätzlich: wird `AUSSEN_DURCHMESSER` oder
`KLOTZ_AUSSEN` geändert, muss der Klotz dick genug bleiben, damit neben der Nut
nach der Kantenverrundung noch Material steht:

```
KLOTZ_AUSSEN / 2 >= VERRUNDUNG + SCHWALBE_KOPF / 2 + SPIEL - WANDSTAERKE / 2 + mindestwand
```

Mit den aktuellen Werten bleiben neben der Nut oben 3,0 mm stehen.
