# Ornament zur Goldenen Hochzeit — Ute & Werner

Herz-Ornament (165 mm) mit „Ute & Werner" in Schreibschrift und großer „50",
zum Hängen an den Geschenkbaum und zum Aufstellen auf den Tisch. Wird nach
dem Druck mit Metallic-Goldlack lackiert.

## Dateien

| Teil | Datei | Drucken |
|---|---|---|
| Herz | `ornament_herz_1x_drucken.stl` | 1 × |
| Sockel | `ornament_sockel_1x_drucken.stl` | 1 × |

- **Herz:** 165 mm hoch, 4 mm Platte, erhabener Rahmen (3 mm), Schrift als
  Relief (2,6–3 mm). Die Öse sitzt geschützt in der Herzkerbe — das Band
  läuft zwischen den Herzbögen nach oben.
- **Sockel:** Riegel 110 × 46 × 24 mm mit geneigter Nut (12° nach hinten).
  Das Herz steht mit der Spitze in der Nut; die Nut ist nur in der Mitte
  30 mm lang ausgespart, die Kammerenden sind der seitliche Anschlag.

Hängen: Band durch die Öse. Stellen: Spitze in die Sockelnut. Kein
Umbau, keine Teile wechseln.

## Drucken & Lackieren

- **Material:** mattes PLA, Farbe egal (wird lackiert). Mattes PLA ist der
  beste Lackträger; Silk wäre kontraproduktiv.
- **Lage:** beide Teile liegen druckfertig — Herz flach mit Schrift nach
  oben, Sockel auf der Unterseite. Keine Stützen.
- **Schichthöhe:** 0,12–0,16 mm — die Schriftkanten danken es.
- **Infill:** 15 %, 3 Wandlinien. Herz ~35 g, Sockel ~45 g.
- **Lackieren:** 1× Kunststoff-Haftgrund, dann 2 dünne Schichten
  Metallic-Gold. Dünn sprühen — die Schriftkanten sollen scharf bleiben.
  Wer mag, tupft danach die Reliefflächen mit dunkler Patina/Antikwachs
  und wischt sie ab: hebt die Schrift deutlich hervor.

## Technik

- Schrift: **Great Vibes** (SIL Open Font License, siehe `OFL.txt`),
  Konturen via fontTools direkt aus der TTF, Bézier-Kurven abgeflacht.
  Buchstaben mit Löchern (e, o, &, 0 …) werden über Brücken-Triangulierung
  geschlossen; die Mantelflächen entstehen aus den Originalkonturen.
- Eine **Sicherheitsprüfung** stellt sicher, dass jede Schriftkontur samt
  Schwüngen innerhalb der Herzfläche liegt — beim ersten Wurf ragte die
  Schleife der „5" über den Rand und wäre in der Luft gedruckt worden;
  genau das fängt der Check jetzt automatisch ab.
- Text, Größen und Herzmaß sind Konstanten oben in `generate.py`
  (`NAMEN`, `ZAHL`, `HERZ_HOEHE` …). Nach Änderung:

```bash
python3 generate.py     # STLs nach stl/
python3 vorschau.py     # Ansichten nach stl/
```

Benötigt `fontTools` (`pip install fonttools`) und die beiliegende
`GreatVibes-Regular.ttf`.

Ansichten: `stl/ansicht_herz_front.svg`, `stl/ansicht_aufgestellt.svg`.
