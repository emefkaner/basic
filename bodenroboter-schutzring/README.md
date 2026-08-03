# Auffahrschutz-Ringe für Möbelfüße

Runde Schutzwälle, die auf dem Boden **außen um einen Möbelfuß** liegen. Der
Saug-/Wischroboter stößt an die Ringwand, bevor er den Fuß überhaupt erreicht,
und kann sich damit nicht mehr daraufsetzen.

Zwei Größen sind fertig generiert:

| | Tisch | Relaxstuhl |
|---|---|---|
| Fuß (gemessen) | 365 mm | 635 mm |
| Luft zum Fuß | 5 mm je Seite | 5 mm je Seite |
| **Innendurchmesser** | **375 mm** | **645 mm** |
| Außendurchmesser | 385 mm | 655 mm |
| Segmente (empfohlen) | 3 | 5 |

Gemeinsam: Wand 5 mm, Höhe 50 mm, Oberkante innen und außen mit R2 verrundet,
Unterkante scharfkantig, damit der Ring plan aufliegt.

Die Segmente werden **nur gesteckt, nicht geklebt**. Die Verzahnung ist
hinterschnitten und hält formschlüssig.

## Welche Datei?

**Eine Datei pro Größe, der Dateiname sagt, wie oft gedruckt wird:**

| Ring | Datei | Drucken |
|---|---|---|
| Tisch | `schutzring_385mm_1_segment_3x_drucken.stl` | **genau 3 ×** |
| Relaxstuhl | `schutzring_655mm_1_segment_5x_drucken.stl` | **genau 5 ×** |

Jede Datei enthält **ein** Segment. Die angegebene Stückzahl ergibt exakt 360° —
ein Segment mehr ist Ausschuss, eins weniger schließt den Ring nicht. Alle
Segmente eines Rings sind identisch — an einem Ende steht das innere Zahnband
vor, am anderen das äußere, dadurch passt jedes auf jedes.

Der Generator schreibt bewusst nur noch diese eine empfohlene Datei je Größe.
Früher lagen hier auch 2-/4-/6-/7-teilige Alternativen — wer davon im Slicer
die falsche erwischte, druckte zwangsläufig die falsche Stückzahl. Alternativen
gibt es weiterhin über `--segmente`, den ungeteilten Referenzring über
`--einteilig`; beide landen dann mit ihrer eigenen Stückzahl im Dateinamen.
Die Segmentzahl wählt der Generator als kleinstes n, dessen Segment mit
mindestens 20 mm Rand (Platz für Brim) aufs Bett passt.

## Verzahnung

Die Stoßfläche ist an der Fuge auf 20 mm verdickt — nur nach **außen**, damit
innen die volle lichte Weite für den Fuß frei bleibt. Sie ist radial
aufgeteilt in:

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

Örtlich ist der Ring an den Stoßstellen außen 30 mm größer als der
Nenndurchmesser. Innen bleibt es überall bei der vollen lichten Weite.

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
- **Materialbedarf** (massiv gerechnet / grob real mit den empfohlenen
  Einstellungen): Tisch 3-teilig 412 cm³ / 210–240 g, Relaxstuhl 5-teilig
  696 cm³ / 350–400 g.

## Zusammenbau

Wegen des Hinterschnitts geht nur noch **senkrecht von oben** — seitliches
Zusammenschieben ist jetzt gesperrt, das ist ja der Sinn der Sache.

1. Erstes Segment um den Fuß legen.
2. Weitere Segmente nacheinander von oben absenken, bis sie plan aufliegen.
3. Das letzte Segment von oben in beide Nachbarn gleichzeitig absenken. Das
   geht, weil alle Fugen senkrecht sind.
4. Fertig. Du brauchst etwa 10 cm freie Höhe über dem Boden.

Falls ein Segment klemmt: die Zahnflanken kurz mit Schleifpapier brechen. Nicht
mit Gewalt drücken, der Zahn ist am Fuß am schmalsten.

## Ansichten

Im Ordner `stl/`, je Größe:

- `ansicht_ring_<aussen>mm_<n>teilig.svg` — zusammengesteckter Ring
- `ansicht_segment_<aussen>mm_<n>teilig.svg` — ein Segment, wie es gedruckt wird
- `ansicht_verzahnung_<aussen>mm.svg` — maßstäbliche Detailzeichnung der Stoßfuge
- `vorschau_<aussen>mm.svg` — Querschnitt der Varianten

## Andere Größe erzeugen

Der Fußdurchmesser kommt per Kommandozeile, alles andere rechnet sich daraus.
Der Generator wählt die Segmentzahl automatisch und schreibt genau eine Datei,
benannt nach Außendurchmesser und Stückzahl:

```bash
python3 generate.py                    # Tisch (Standard: Fuss 365 mm)
python3 generate.py --fuss 635         # Relaxstuhl
python3 generate.py --fuss 500 --luft 8
python3 vorschau.py --fuss 635 --teile 5   # Ansichten dazu
```

**Vor dem Generieren richtig messen:** bei gewölbten Tellerfüßen misst ein
über die Wölbung gelegtes Maßband die Bogenlänge, nicht den Durchmesser —
das Ergebnis ist dann 2–3 cm zu groß. Entweder mit zwei Anschlägen (Bücher
links und rechts an den Teller, Abstand messen) oder, wenn schon ein Ring
gedruckt ist: Ring an den Fuß anschieben, Restspalt messen, echter Fuß =
Innendurchmesser − Spalt.

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
