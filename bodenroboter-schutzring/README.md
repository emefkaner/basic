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

Die Segmente werden **nur gesteckt, nicht geklebt**. Die Verzahnung ist
hinterschnitten und hält formschlüssig.

## Welche Datei?

**`schutzring_3teilig_385mm_segment.stl`, 3 × drucken.** Alle Segmente sind
identisch — an einem Ende steht das innere Zahnband vor, am anderen das äußere,
dadurch passt jedes auf jedes.

| Datei | Stück | Grundfläche je Teil | Bett |
|---|---|---|---|
| `schutzring_3teilig_385mm_segment.stl` | 3 × | 268,4 × 268,8 mm | 81 mm Rand |
| `schutzring_2teilig_385mm_segment.stl` | 2 × | 342,8 × 342,9 mm | braucht echte 350 × 350 |
| `schutzring_4teilig_385mm_segment.stl` | 4 × | 220,0 × 220,3 mm | 130 mm Rand |
| `schutzring_einteilig_385mm.stl` | — | 385 × 385 mm | braucht ein Bett ≥ 400 mm |

## Verzahnung

Die Stoßfläche ist an der Fuge auf 20 mm verdickt — nur nach **außen**, damit
innen die vollen 375 mm für den Fuß frei bleiben. Sie ist radial aufgeteilt in:

- 5 mm solide Randzone innen
- zwei Zahnbänder à 5 mm, die abwechselnd 12 mm vorstehen bzw. zurückspringen
- 5 mm solide Randzone außen

Beide Zähne sind **hinterschnitten**, also am Ende 1,2 mm breiter als am Fuß:
der innere spreizt zur Ringmitte, der äußere nach außen. Die beiden
Hinterschnitte laufen damit gegeneinander — ein Auseinanderziehen müsste den
einen Zahn nach außen und gleichzeitig den anderen nach innen bewegen, was sich
gegenseitig sperrt. Spiel 0,12 mm je Flanke (Schiebesitz).

Die Randzonen stehen da, damit die Kantenverrundung oben nicht in die Verzahnung
schneidet, und damit der Hinterschnitt sich in massives Material aufweiten kann.

Örtlich ist der Ring an den Stoßstellen außen 415 mm statt 385 mm. Innen bleibt
es überall bei 375 mm.

### Was der Formschluss leistet — und was nicht

In der Ebene ist die Fuge dicht: gedreht sperrt sie nach 0,7 mm, radial sperren
die Zähne sofort. **Senkrecht ist sie bewusst offen** — genau darüber wird
montiert, und ein Segment lässt sich entsprechend auch wieder nach oben
herausziehen. Im Betrieb passiert das nicht, der Ring liegt auf dem Boden und
wird nur waagerecht angestupst.

Die 0,7 mm Weg bis zum Anschlag bedeuten etwas Spiel je Fuge. Der Ring ist also
nicht bretthart, sondern atmet minimal. Für einen Bodenring ohne Belang — wenn
der Roboter dagegenfährt, geht die Fuge auf Druck und schließt sich ohnehin.

Wenn du es doch bombenfest willst: die Verzahnung hat rund 3800 mm² Fläche je
Stoß, ein Tropfen 2K-Epoxid auf die Zahnflanken macht es unlösbar.

## Drucken

- **Material:** PETG. Ein Wischroboter bringt Feuchtigkeit mit, und PETG ist
  zäher gegen die dauernden Stöße. PLA geht auch, ist aber spröder — und beim
  Hinterschnitt willst du eher Zähigkeit als Härte.
- **Lage:** so wie in der STL, also stehend (Z = Wandhöhe). Keine Stützen nötig,
  es gibt keine Überhänge — das ganze Teil ist ein senkrechtes Prisma, bis oben
  die Verrundung einsetzt. Auch der Hinterschnitt ist senkrecht ausgeführt und
  damit unkritisch.
- **Haftung:** Brim, bei der dreiteiligen Variante ist reichlich Platz.
- **Wände/Infill:** 3 Wandlinien und 15–20 % Infill reichen.
- **Maßhaltigkeit:** die Zähne entscheiden über die Passung. Wenn dein Drucker
  bekanntermaßen Löcher zu eng druckt, lieber `SPIEL` auf 0,15 setzen und neu
  erzeugen, statt hinterher zu schleifen.
- **Materialbedarf:** massiv gerechnet 412 cm³ für den ganzen Ring. Mit den
  empfohlenen Einstellungen grob 210–240 g.

## Zusammenbau

Wegen des Hinterschnitts geht nur noch **senkrecht von oben** — seitliches
Zusammenschieben ist jetzt gesperrt, das ist ja der Sinn der Sache.

1. Erstes Segment um den Fuß legen.
2. Zweites Segment von oben absenken, bis es plan aufliegt.
3. Drittes Segment von oben in beide Nachbarn gleichzeitig absenken. Das geht,
   weil beide Fugen senkrecht sind.
4. Fertig. Du brauchst etwa 10 cm freie Höhe über dem Boden.

Falls ein Segment klemmt: die Zahnflanken kurz mit Schleifpapier brechen. Nicht
mit Gewalt drücken, der Zahn ist am Fuß am schmalsten.

## Ansichten

Im Ordner `stl/`:

- `ansicht_ring_2teilig.svg` — zusammengesteckter Ring
- `ansicht_haelfte.svg` — ein Segment, wie es gedruckt wird
- `ansicht_verzahnung.svg` — maßstäbliche Detailzeichnung der Stoßfuge
- `vorschau.svg` — Querschnitt der Varianten

## Maße ändern

Alle Maße stehen als Konstanten oben in `generate.py`. Der Ring wird aus
`FUSS_DURCHMESSER` und `LUFT` abgeleitet:

```bash
python3 generate.py     # schreibt die STL-Dateien nach stl/
python3 vorschau.py     # schreibt die Ansichten nach stl/
```

Beides läuft mit reinem Python 3, ohne Abhängigkeiten und ohne installiertes CAD.

Die Bauteile entstehen als Stapel waagerechter Querschnitte mit identischer
Punktreihenfolge, die zu einem Mesh verbunden werden — keine Boolean-Operationen,
daher keine typischen STL-Fehler.

`generate.py` prüft nach dem Erzeugen drei Dinge:

- **Dichtheit:** jede Kante muss genau zweimal vorkommen. Bricht bei Verstoß ab.
- **Passung:** die Querschnitte zweier benachbarter Segmente werden in Einbaulage
  gegeneinander gelegt und auf Überdeckung geprüft. Ein falsch herum laufendes
  Zahnmuster oder ein zu klein gewähltes `SPIEL` fällt damit sofort auf und nicht
  erst nach Stunden Druckzeit. Bricht bei Verstoß ab.
- **Formschluss:** ein Segment wird aus der Fuge herausgedreht und geprüft, ob es
  anschlägt. Die Verzahnung ist in Polarkoordinaten aufgebaut, ihre
  Freigabebewegung in der Ebene ist deshalb eine Drehung um die Ringmitte, keine
  Geradfahrt. Mit `ZAHN_HINTERSCHNITT = 0` meldet der Test korrekt „FEHLT" —
  das ist dann die Variante zum Verkleben.

Wird `KLOTZ_AUSSEN` verkleinert oder `VERRUNDUNG` vergrößert, muss
`ZAHN_RANDZONE` größer bleiben als `VERRUNDUNG + ZAHN_HINTERSCHNITT`, sonst
schneidet die Kantenverrundung oben in die Verzahnung.
