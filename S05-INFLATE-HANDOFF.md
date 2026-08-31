# IC Prompt Master S05 INFLATE — Session-Handoff

Beim Start dieser Session: **zuerst `CLAUDE.md` lesen** (dort stehen alle hart
erarbeiteten Prompting-Regeln), dann diese Datei. Die Rolle und Arbeitsweise sind
identisch zu `S03-ESTABLISHER-HANDOFF.md` — dort steht sie ausführlich; das Wichtigste:

- User beschreibt auf Deutsch, du lieferst **englische Prompts in Codeblöcken**,
  Video immer über das Skill `higgsfield-seedance-prompt`.
- **Niemals selbst generieren** — der User generiert in der App. API kostet Credits.
- **Eine Änderung pro Generation**, gezielt an der kaputten Stelle nachbessern.
- Niemals Ergebnisse beschreiben, die du nicht sehen kannst. Higgsfield-Medien
  (CDN *und* `higgsfield.ai/s/...`-Share-Links) sind durch die Netzwerk-Policy
  gesperrt — Videos und Bilder sind für dich nicht einsehbar.

## Der Shot

Das Dach des grünen Waggons klappt auf, ein Zeppelin-Ballon entfaltet sich daraus,
bläst sich auf und verbindet sich über Stahlseile mit Lok, Tender und Waggon.
Hintergrund `@WILDWEST`. Zug fährt dabei.

## Was schiefging und warum

Die erste Fassung war ein Vier-Bild-Storyboard (`@image1` geschlossen → `@image2`
aufgeblasen → `@image3` ganzer Zug → `@image4` Endlook) plus ein wieder zuklappendes
Dach im Text. Ergebnis laut User: „das Aufklappen ist da, aber doppelt und komisch."

Drei Ursachen, alle strukturell:

1. **Zeitrollen an Referenzen.** Referenzen tragen Identität, keine Reihenfolge.
   `image1` und `image4` zeigten beide ein geschlossenes Dach → der Zustand lag
   doppelt im Korb → das Dach klappte zweimal auf.
2. **Zwei gegenläufige Dachbewegungen** (auf *und* wieder zu) in einer Generierung —
   ohne Ordnungssignal macht das Modell beide mehrfach.
3. **Aussehen doppelt beschrieben** (Text *und* Bilder): „DB 01 150", „named IRON
   CLOUD", „dark green with polished metallic accents". Verstößt gegen „One owner for
   appearance"; der Name im Text lädt zusätzlich Schriftzüge auf die Maschine ein —
   genau dafür existiert `@LOCO-BASE`.

Die verallgemeinerte Regel steht jetzt in `CLAUDE.md` unter
„References carry identity, not sequence — one direction of change per shot".

## Aktueller Ansatz (Stand: erste Fassung geliefert, Ergebnis steht aus)

Ein einziger durchgehender Take, **eine Bewegungsrichtung**: alles öffnet sich,
nichts kehrt zurück. Das Zuklappen ist gestrichen — unter dem fertigen Ballon
ohnehin kaum sichtbar, notfalls später eigener Insert.

| Slot | Inhalt |
|---|---|
| `start_image` | bisheriges Image 1 (Zug geschlossen, High Noon) |
| Referenz | `@WILDWEST` (Location) |
| Referenz | `@IRON-CLOUD-Inflated` (Endzustand, letztes Frame) |
| entfällt | die bisherigen Image 3 und Image 4 |

Zug-Identität kommt aus dem `start_image`, deshalb **kein** zusätzlicher Lok-Tag.
Der Ballon ist das Einzige, was in Frame 1 noch nicht existiert — dafür genau eine
Referenz. Drei Stufen als *Endzustände* formuliert (Klappen liegen an → Hülle länger
als der Waggon, Unterseite noch schlaff → Hülle prall über dem ganzen Zug, Seile
straff), Größen über Menschenhöhen verankert, nicht in Metern.

**Frame-1-Test:** geschlossenes, ungeteiltes Dach, leerer Himmel darüber, Boden
bereits in Bewegung. Bei Naht oder Ballonansatz in Frame 1 hat `start_image` nicht
gegriffen — dann nicht am Text drehen.

**Fallback, falls es weiter doppelt:** Split in zwei Generierungen, Schnitt wenn die
Dachklappen unten liegen. Shot A endet auf offenem Dach; Shot B nimmt dessen letztes
Frame als `start_image`.

## Offene Unbekannte

- `@WILDWEST` hat **keine Beschreibung** im Account und das Bild ist nicht einsehbar.
  Falls es eine feste Blickrichtung oder Gleisseite vorgibt, die gegen die aktuelle
  Blocking-Annahme steht (Zug fährt nach screen-left, Kamera 25 m rechts vom Gleis),
  kommt der Shot gespiegelt — dann die **Kameraseite im Prompt** drehen, nicht das
  Element bekämpfen. Beschreibung am Element nachtragen, sobald bekannt.
- `@IRON-CLOUD-Inflated`: unbekannt, ob Totale oder engere Ansicht. Eine
  Weitwinkel-Totale zieht die Framing-Distanz mit.
- Ungeklärt: was `@IRON-CLOUD-FLY` gegenüber `@IRON-CLOUD-Airborne` zeigt, und ob
  `@Cellar-Empty` / `@Cellar-Crowd` / `@Tanzpaar` zu S05 gehören.

## Tag-Registry — Stand 2026-08-31 (frisch aus dem Account)

Gegenüber der Liste in `S03-ESTABLISHER-HANDOFF.md` sind **fünf Elemente neu**:

| Element | Kategorie | Beschreibung im Account |
|---|---|---|
| `@IRON-CLOUD-FLY` | character | — |
| `@Cellar-Empty` | environment | — |
| `@Cellar-Crowd` | environment | — |
| `@Tanzpaar` | character | — |
| `@LOCO-BASE` | prop | neutral benannter Zwilling von `@IRON-CLOUD-Normal`, damit der Elementname keine Wörter enthält, die als Schriftzug auf die Maschine gemalt werden |

`@LOCO-BASE` und `@IRON-CLOUD-Normal` zeigen **dasselbe Bild** (identische media-id).

Vollständig, wie im Account benannt:

- **Figuren:** `@EISENSTEIN` · `@PINKERTON` (mit Hut und Mantel) · `@PINKERTON2`
  (mit Hut, ohne Mantel) · `@OHarris` · `@VILLAIN` (mit Kapuze, Standardvariante) ·
  `@VILLAIN-NOHOOD` · `@Young` · `@Schmitzkowsky` (Hero) · `@SchmitzkowskyGoggle` ·
  `@CHRIS` · `@JOHN` (Heizer) · `@Tanzpaar`
- **Zug & Requisiten:** `@IRON-CLOUD-Normal` · `@LOCO-BASE` · `@IRON-CLOUD-Inflated` ·
  `@IRON-CLOUD-Airborne` · `@IRON-CLOUD-FLY` · `@VILLAINs-Eye`
- **Führerkanzel (innen!):** `@LOK-FRONT` · `@LOK-LEFT` · `@LOK-BACK`
- **Locations:** `@TRAIN-STATION-NORTH-HIGH` · `@TRAIN-STATION-NORTH-LOW` ·
  `@TRAIN-STATION-SOUTH-2` · `@TRAIN-STATION-SOUTH-LOW` · `@IRON-CLOUD-STAIRS` ·
  `@WILDWEST` · `@Cellar-Empty` · `@Cellar-Crowd`

Die Location-Geometrie-Tabelle der vier Bahnhofs-Elemente steht in
`S03-ESTABLISHER-HANDOFF.md` und gilt unverändert.

## Film-Grunddaten

Spaghetti-Western „IRON CLOUD", 1860er. Konsist-Lock: **schwarze Lok – schwarzer
Tender – grüner Waggon**, der Zug endet an der Rückwand des grünen Waggons.
Standardwetter: High Noon, „cloudless deep hot blue sky, hard crisp shadows"
(nie „bleached white sky" — das erzeugt Bewölkung). Bahnhofsschild: **YOUNG & CO.**

## Starter-Prompt für diese Session

> Lies CLAUDE.md und S05-INFLATE-HANDOFF.md. Du bist mein Prompt Master für
> IRON CLOUD, Fokus S05 INFLATE. Übernimm alle Regeln und den dortigen Arbeitsstand
> und melde dich kurz, wenn du bereit bist.
