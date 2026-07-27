# Auffahrschutz-Ring fürs Tischbein

Runder Schutzwall, der auf dem Boden **außen um den Tischfuß** liegt. Der
Saug-/Wischroboter stößt an die Ringwand, bevor er den Fuß überhaupt erreicht,
und kann sich damit nicht mehr daraufsetzen.

| Maß | Wert |
|---|---|
| Tischfuß (gemessen) | 365 mm |
| Luft zum Fuß | 5 mm je Seite |
| **Innendurchmesser** | **375 mm** |
| Außendurchmesser | 385 mm |
| Wandstärke | 5 mm |
| Höhe | 50 mm |
| Oberkante | innen und außen mit R2 verrundet |
| Unterkante | scharfkantig, damit der Ring plan aufliegt |

Ausgeführt als **zwei identische Hälften**, die an den Stoßstellen ineinander
verzahnt und verklebt werden. Verklebt ist der Ring ein geschlossener Hoop und
damit in sich steif — der Hebel ist der ganze Durchmesser als Standbreite gegen
~40 mm Anstoßhöhe, da kippt nichts weg.

## Dateien

| Datei | Stück | Grundfläche je Teil |
|---|---|---|
| `schutzring_2teilig_385mm_segment.stl` | **2 × drucken** | 341,2 × 341,3 mm bei 135,8° gedreht |
| `schutzring_3teilig_385mm_segment.stl` | 3 × drucken | 265 × 265 mm |
| `schutzring_4teilig_385mm_segment.stl` | 4 × drucken | 217 × 217 mm |
| `schutzring_einteilig_385mm.stl` | — | 385 × 385 mm, braucht ein Bett ≥ 400 mm |

Alle Teile eines Rings sind identisch — an einem Ende stehen die geraden Bänder
der Verzahnung vor, am anderen die ungeraden, dadurch passt jedes Teil auf jedes.

### Achtung beim Bauraum

Die zweiteilige Variante braucht **350 × 350 mm** und lässt dann nur 8,7 mm Rand.
Das reicht für einen Skirt, aber nicht für einen Brim.

Wenn der nutzbare Bereich der H2S in einer Achse nur 320 mm ist — laut
Spezifikation ist der Bauraum 350 × 320 × 325 mm — dann geht die zweiteilige
Variante **nicht**. Eine Halbschale dieses Durchmessers passt in kein Quadrat
unter ~329 mm, das ist eine harte geometrische Grenze. In dem Fall die
dreiteilige Datei nehmen, die passt mit 85 mm Rand.

Am schnellsten geklärt: die STL in Bambu Studio laden und schauen, ob die Platte
meckert.

## Verzahnung

Bei genau zwei Hälften liegen beide Stoßflächen in **derselben** Ebene. Die
Hälften lassen sich deshalb geradlinig zusammenschieben, beide Fugen schließen
gleichzeitig. Darum gerade Zähne und bewusst *kein* Schwalbenschwanz: den
müsstest du über die vollen 50 mm senkrecht einfädeln und würdest dabei den
Kleber abstreifen.

Die Stoßfläche ist an der Fuge auf 17 mm verdickt — nur nach **außen**, damit
innen die vollen 375 mm für den Fuß frei bleiben. Sie ist radial aufgeteilt in:

- 3,5 mm solide Randzone innen
- zwei Bänder à 5 mm, die abwechselnd 12 mm vorstehen bzw. zurückspringen
- 3,5 mm solide Randzone außen

Die Randzonen stehen da, damit die Kantenverrundung oben nicht in die Verzahnung
schneidet. Klebespalt 0,15 mm je Flanke.

Klebefläche pro Stoßstelle: rund 3250 mm². Eine glatte Stoßfuge auf der 5-mm-Wand
hätte 250 mm² — also gut das Dreizehnfache.

Örtlich ist der Ring an den beiden Stoßstellen außen 409 mm statt 385 mm. Innen
bleibt es überall bei 375 mm.

## Drucken

- **Material:** PETG. Ein Wischroboter bringt Feuchtigkeit mit, und PETG ist
  zäher gegen die dauernden Stöße. PLA geht auch, ist aber spröder.
- **Lage:** so wie in der STL, also stehend (Z = Wandhöhe). Keine Stützen nötig,
  es gibt keine Überhänge — das ganze Teil ist ein senkrechtes Prisma, bis oben
  die Verrundung einsetzt.
- **Haftung:** Skirt. Für einen Brim ist bei der zweiteiligen Variante kein
  Platz (siehe oben).
- **Wände/Infill:** 3 Wandlinien und 15–20 % Infill reichen. Wer es massiv will,
  stellt bei 0,4er Düse 6 Wandlinien und 0 % Infill ein — dann besteht die
  5-mm-Wand komplett aus Perimetern.
- **Schichthöhe:** 0,2–0,28 mm, das Teil hat keine feinen Details.
- **Materialbedarf:** massiv gerechnet 357 cm³ für den ganzen Ring. Mit den
  empfohlenen Einstellungen landet man grob bei 190–220 g.

## Zusammenbau

1. Beide Hälften trocken zusammenstecken und prüfen, ob die Verzahnung
   spielfrei aufeinandergeht. Falls sie klemmt: die Zahnflanken kurz mit
   Schleifpapier brechen.
2. Kleber auf die Zahnflanken und die Randzonen beider Stoßflächen.
   **Zweikomponenten-Epoxid** ist hier richtig — der Klebespalt beträgt 0,15 mm
   je Flanke, und Epoxid füllt Spalte, während Sekundenkleber einen Pressitz
   bräuchte. Falls es Sekundenkleber sein soll, dann Gel.
3. Beide Hälften auf dem Boden um den Fuß legen und geradlinig
   zusammenschieben. Beide Fugen schließen gleichzeitig.
4. Auf einer ebenen Fläche aushärten lassen, damit der Ring plan bleibt.

## Ansichten

Im Ordner `stl/`:

- `ansicht_ring_2teilig.svg` — der fertig verklebte Ring
- `ansicht_haelfte.svg` — eine Hälfte, wie sie gedruckt wird
- `ansicht_verzahnung.svg` — maßstäbliche Detailzeichnung der Stoßfuge
- `vorschau.svg` — Querschnitt der Varianten

## Maße ändern

Alle Maße stehen als Konstanten oben in `generate.py`. Der Ring wird aus
`FUSS_DURCHMESSER` und `LUFT` abgeleitet — wenn der Fuß doch anders gemessen
wird, reicht es, diese eine Zahl zu ändern:

```bash
python3 generate.py     # schreibt die STL-Dateien nach stl/
python3 vorschau.py     # schreibt die Ansichten nach stl/
```

Beides läuft mit reinem Python 3, ohne Abhängigkeiten und ohne installiertes CAD.

Die Bauteile entstehen als Stapel waagerechter Querschnitte mit identischer
Punktreihenfolge, die zu einem Mesh verbunden werden — keine Boolean-Operationen,
daher keine typischen STL-Fehler.

`generate.py` prüft nach dem Erzeugen zweierlei und bricht bei Verstoß ab:

- **Dichtheit:** jede Kante muss genau zweimal vorkommen.
- **Passung:** die Querschnitte zweier benachbarter Segmente werden in Einbaulage
  gegeneinander gelegt und auf Überdeckung geprüft. Ein falsch herum laufendes
  Zahnmuster oder ein zu klein gewähltes `SPIEL` fällt damit sofort auf und
  nicht erst nach Stunden Druckzeit.

Wird `KLOTZ_AUSSEN` verkleinert oder `VERRUNDUNG` vergrößert, muss `ZAHN_RANDZONE`
größer bleiben als `VERRUNDUNG`, sonst schneidet die Kantenverrundung oben in die
Verzahnung.
