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

## Generierung 1 — ausgewertet

Video: `higgsfield.ai/s/pjtQvAeeq7c`, 10,08 s, 24 fps, 2206×946. Frames gezogen wie in
`CLAUDE.md` unter „Watch the results" beschrieben.

| Zeit | Bild |
|---|---|
| 0–0,8 s | Zug sauber, Dach zu. Vordergrund-Wischer und Staub funktionieren. |
| 1,0–2,0 s | Ein **waggongroßer grüner Deckel** hebt sich ab und kippt. |
| 2,5 s | Deckel weg, Dach wieder zu und normal. |
| 3,0–5,5 s | **Weiße** geraffte Segeltuchmasse wächst aus dem jetzt offenen Dach. |
| 5,5–6,5 s | Farbe kippt nach dunkelblau, Form streckt sich zum Zeppelin. |
| 6,5–10 s | Endlook korrekt, Seile dran, hält ruhig. **Diese Hälfte ist gut.** |

Vier Ursachen, drei davon am Material nachgewiesen:

1. **Leerer Beat.** Das Dach hatte 3 s ganz allein, ohne Ballon und ohne ein Bild davon,
   wie ein offenes Dach aussieht → der Deckel ist reine Füllerfindung. Ab 3,0 s, als der
   Ballon den Beat trug, öffnete dasselbe Modell das Dach korrekt.
2. **Zu wenige Pixel.** In der Totale ist das Waggondach ein schmaler Streifen; zwei
   schmale Klappen sind darin nicht auflösbar. Framing-Problem, kein Wortproblem.
3. **`@IRON-CLOUD-Inflated` zeigt das Dach geschlossen** — der Lock „Dach bleibt bis
   zum letzten Frame offen" widersprach der Referenz frontal.
4. **Farbumschlag war ein Prompt-Fehler:** der Text sagte „pale folded fabric", die
   Referenz ist dunkelblau. Text besaß die Farbe früh, das Bild spät.

Fix in Generierung 2: kein eigener Dach-Beat mehr — die Hülle drückt das Dach von innen
auf, ein Ereignis. Kein Farbwort im Text, stattdessen Farbbindung an die Referenz
**ab 1,0 s**. Referenzblock schränkt `@IRON-CLOUD-Inflated` auf Hülle und Beschläge ein.
Kamera klettert und fällt durchgehend zurück.

## Was die Referenzen wirklich zeigen (angesehen, nicht geraten)

- **`@IRON-CLOUD-Inflated`** — Studio-Produktfoto auf grauem Seamless, erhöhte
  Dreiviertelansicht, Modell auf Schotterbett. Dunkelblaue Hülle mit Messing-Nasenkappe,
  Messing-Finnen am Heck, Messing-Gantry und Seilen zu Tender und Waggon. Der grüne
  Waggon darunter hat sein **normales geschlossenes Dach** mit Messingknäufen. Weil es
  ein Studiofoto ist, zieht es getaggt in Außenaufnahmen die Kamera Richtung Stillstand
  — im Prompt ausdrücklich auf Hülle und Beschläge einschränken.
- **`@WILDWEST`** — breite Wüsten-Panoramaplatte, Butte links, Mesas rechts, Saguaros und
  Salbei, tiefblauer Himmel. **Kein Gleis**, also keine Blickrichtung, gegen die ein
  Blocking verstoßen könnte. Der frühere Spiegel-Vorbehalt ist damit erledigt.
- Der Zug im `start_image` trägt „IRON CLOUD" in Gold auf Lokflanke und Tender — die
  Beschriftung kommt aus dem ersten Frame und ist kein Textproblem.

## Offene Unbekannte

- Ungeklärt: was `@IRON-CLOUD-FLY` gegenüber `@IRON-CLOUD-Airborne` zeigt, und ob
  `@Cellar-Empty` / `@Cellar-Crowd` / `@Tanzpaar` zu S05 gehören.
- Noch nicht gebaut: ein Element „Zug aufgeblasen **mit offenem Dach**". Solange es
  fehlt, kann kein Shot das offene Dach bis zum Schlussframe halten.

## Vorgeschlagener zweiter Shot — DACH

Halbtotale auf den grünen Waggon, Dach formatfüllend. Erst in dieser Bildgröße ist die
Mechanik überhaupt darstellbar. Noch nicht geschrieben.

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
