# IC Promt Master S03 Establisher — Session-Handoff

Diese Datei macht aus einem frischen Chat eine Kopie des ursprünglichen
IRON-CLOUD-Prompt-Master-Chats. Beim Start dieser Session: **zuerst `CLAUDE.md`
lesen** (dort stehen alle hart erarbeiteten Prompting-Regeln), dann diese Datei.

## Rolle & Arbeitsweise

- Der User beschreibt Shots auf Deutsch; du lieferst fertige **englische Prompts
  in Codeblöcken**. Für Videos immer das Skill `higgsfield-seedance-prompt`
  benutzen (Blockstruktur: SCENE CONTEXT → ACTIVE REFERENCES → … → POSITIVE LOCKS).
- Der User generiert **selbst in der Higgsfield-App** (Unlimited-Modus, kostenlos).
  **Niemals eigenständig über die API generieren** — das kostet Credits. Nur nach
  ausdrücklicher Freigabe.
- Nach jedem Ergebnis meldet der User zurück; dann **gezielt an der kaputten
  Stelle nachbessern**, nicht alles neu schreiben. **EINE Änderung pro Generation.**
- Wenn Prompt-Tuning ausgereizt ist: ehrlich sagen und strukturelle Wege
  vorschlagen (neues Asset bauen, `start_image`, Zwei-Pass-Compositing).
- Bei Unklarheit zu Blickrichtung, Brennweite, Distanz oder Tageszeit: **fragen.**
- Niemals Ergebnisse beschreiben, die du nicht wirklich sehen kannst.

## Tag-Registry

**Diese Liste ist nur eine Momentaufnahme.** Vor jedem Prompt die Elements per
`show_reference_elements` (action `list`) abfragen — kostenlos, und die Namen dort
sind die Wahrheit. Stand 2026-08-05:

Figuren: `@EISENSTEIN` · `@PINKERTON` (Allan Pinkerton, **mit Hut und Mantel**) ·
`@PINKERTON2` (**mit Hut, ohne Mantel**) · `@OHarris` · `@VILLAIN` (**mit Kapuze** —
das ist die Standardvariante) · `@VILLAIN-NOHOOD` · `@Young` · `@Schmitzkowsky` (Hero) ·
`@SchmitzkowskyGoggle` · `@CHRIS` und `@JOHN` (**die beiden Heizer auf der
Führerkanzel** — in den meisten Shots vernachlässigbar)

Die fünf Wartenden des S03-Establishers sind damit durch Ausschluss festgelegt:
`@EISENSTEIN`, `@Young`, `@VILLAIN`, `@PINKERTON`, `@OHarris`.

Zug & Requisiten: `@IRON-CLOUD-Normal` · `@IRON-CLOUD-Inflated` ·
`@IRON-CLOUD-Airborne` · `@VILLAINs-Eye`

`@LOK-FRONT`, `@LOK-LEFT` und `@LOK-BACK` sind **Innenaufnahmen der Führerkanzel**
(Blick nach vorn, nach links, nach achtern) — nicht die Lok von außen. Für jede
Außeneinstellung der stehenden Lok in Nähe gibt es noch kein Element; das wäre neu
zu bauen.

Locations: `@TRAIN-STATION-NORTH-HIGH` · `@TRAIN-STATION-NORTH-LOW` ·
`@TRAIN-STATION-SOUTH-2` · `@TRAIN-STATION-SOUTH-LOW` · `@IRON-CLOUD-STAIRS` ·
`@WILDWEST`

Korrekturen gegenüber der alten Liste: es heißt **NORTH**, nicht `NORD`; ein blankes
`@TRAIN-STATION-SOUTH` existiert nicht (es gibt `-2` und `-LOW`); `@WAGON-STEPS-BOKEH`
ist im Account nicht mehr vorhanden.

### Location-Geometrie (aus den Element-Beschreibungen)

| Element | Höhe | Blick | Gleis im Bild |
|---|---|---|---|
| `@TRAIN-STATION-NORTH-HIGH` | erhöht | die Hauptstraße entlang | mittig in der Straße, Falschfassaden links, Koppel rechts |
| `@TRAIN-STATION-NORTH-LOW` | 1,7 m, Kamera **links** vom Gleis | nach **Süden** | **rechte** Bildhälfte, Boardwalk links |
| `@TRAIN-STATION-SOUTH-2` | ~25 m | nach **Norden** die Hauptstraße hinauf | mittig, Wasserturm, Poststation „YOUNG & Co." rechts |
| `@TRAIN-STATION-SOUTH-LOW` | 1,6 m, Kamera ~3 m **rechts** vom Gleis | nach **Norden** | diagonal in der **linken** Bildhälfte, Poststation nah rechts, Wasserturm dahinter |

Ein Kran-Abstieg braucht ein Paar mit gleicher Blickrichtung und gleicher Gleisseite.
`SOUTH-2` → `SOUTH-LOW` ist ein solches Paar (beide nach Norden, ~25 m auf Augenhöhe).
`NORTH-HIGH` → `NORTH-LOW` blickt nach Süden mit dem Gleis rechts.

Das Gleis liegt **in der Hauptstraße**, nicht in einem Bahnhofsgelände: kein
Schotterbett, keine Bahnsteigkante. Prompts, die Schotter, Bahnsteig oder Güterschuppen
beschreiben, reden gegen die Bilder.

## Film-Grunddaten

Spaghetti-Western „IRON CLOUD", 1860er, Wüste/Western-Stadt mit Bahnhof.
Die Iron Cloud: Steampunk-Lok (schwarz) + Tender (schwarz) + grüner Waggon,
darüber Zeppelin. Konsist-Lock: „black–black–green", Zug endet an der Rückwand
des grünen Waggons. Standard-Wetter: High Noon, „cloudless deep hot blue sky,
hard crisp shadows" (nie „bleached white sky" — das erzeugt Bewölkung).
Bahnhofsschild: **YOUNG & CO.**

## Aktueller Stand der offenen Shots (S03)

1. **Transformations-Shot** (Lok wird flugfähig: Frontkappe löst sich wie ein
   Druckventil, extrudiert nach vorn, Luftleitbleche fächern zu Rotoren auf,
   Kappe fährt bündig zurück, Spin-up): Letzte Version nutzt den Block
   „DESIGN COMES FROM THE IMAGES — the one unbreakable rule" — alles Aussehen
   kommt aus @image1 (vor der Verwandlung) und @image2 (Propeller ausgefahren),
   Text beschreibt NUR Bewegung. Checkable Frame-1-Test: Leitbleche sichtbar,
   keine Schriftzug-Klappe. **Ergebnis der Generierung steht noch aus.**
   Fallback bei Fehlschlag: vereinfachter Split (Blech → zwei Blätter statt vier).
2. **Kran-Ankunfts-Shot** (Full-AI, 15 s: Start auf 25 m Kranhöhe → endet auf
   Augenhöhe bei den fünf Männern, Zug fährt ein): Die letzte gute Basisversion
   ist wiederhergestellt; die Kameraseite spiegelt weiterhin unzuverlässig.
   Möglicher nächster Schritt: die Bewegung auf zwei Generierungen aufteilen.
3. **Ruhend:** Zug-Austausch per `start_image`-Zweischritt (Prompts geliefert,
   auf Eis); Tender-Schriftzug über Insert-Stills.

## Verifiziert & wiederverwendbar

- Das **Plate-Compositing-Template** steht komplett in `CLAUDE.md`
  („Working template — plate compositing"). Es ist auf IRON CLOUD verifiziert —
  Blockreihenfolge und Gewichtung (KEEP lang und emphatisch) beibehalten.
- Over-Shoulder-Plates brauchen ihren eigenen KEEP-Absatz („partially in frame
  by design") — steht ebenfalls in `CLAUDE.md`.

## Starter-Prompt für diese Session

> Lies CLAUDE.md und S03-ESTABLISHER-HANDOFF.md. Du bist mein Prompt Master für
> IRON CLOUD, Fokus S03-Establisher. Übernimm alle Regeln und den dortigen
> Arbeitsstand und melde dich kurz, wenn du bereit bist.
