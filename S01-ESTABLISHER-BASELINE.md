# S01 Establisher — Baseline (übernommen von S14 „Props Out")

Alle technischen Einstellungen für S01 werden 1:1 von S14 übernommen. Quelle:
Higgsfield-Job `fb980ce3-7c50-47cc-bef3-ae29bc3ab0be` (14.08.2026, 11:38 UTC),
in Dropbox abgelegt als `/IRON CLOUD/AI/VFX_HIGGSFIELD/01_GEN/SEEDANCE25_S14_01.mp4`.

## Generator-Settings (exakt so setzen)

| Parameter | Wert |
|---|---|
| Modell | **Seedance 2.5** (`seedance_2_5`) |
| Auflösung | 1080p (2016 × 864 px) |
| Seitenverhältnis | **21:9** anamorph |
| Dauer | **30 s** |
| Audio generieren | **an** |
| Bitrate | high |
| Genre | auto |
| Speedramp | auto |
| Multi-Shot | **aus** (ein einziger durchgehender Take) |
| Extension Mode | — |
| Prompt-Sprache | en |
| `medias` / `start_image` | **leer** — reiner Text+Referenz-Lauf, keine Startbild-Bindung |

## Reference Elements in S14

Als `reference_elements` getaggt (keine `medias`):

- `@IRON-CLOUD-FLY` — `b8b923b9-b4ee-4fe7-91c8-1fd18299ceaf` (category: character)
- `@JOHN` — `775f494f-ec3f-4131-bb77-399b85cc3f0c`
- `@CHRIS` — `44c8cffa-b44c-4f80-a7c8-64982173f25b`
- `@Schmitzkowsky` — `45b17adc-7bf7-46b9-8bbc-c2f89fcbee87`

Für S01 gilt dieselbe Mechanik, aber die Auswahl richtet sich nach dem Inhalt des
Establishers — Referenzen werden nur getaggt, wenn das Element im Bild ist.

## Prompt-Architektur von S14 (Blockreihenfolge beibehalten)

```
SCENE CONTEXT
ACTIVE REFERENCES          ← Design kommt 100 % aus den Referenzen, Text beschreibt es nicht nach
[Objekt-Locks: z. B. ZEPPELIN ORIENTATION, RIGID BODY RULE]
LOCATION MAP               ← Vordergrund / Mittelgrund / Hintergrund getrennt
ATMOSPHERE AND FOREGROUND OCCLUSION
SCALE                      ← Größen immer gegen sichtbare Dinge im Bild geankert
FIRST FRAME / BLOCKING
FORMAT MODE
OPTICS                     ← pro Zeitsegment ein Sichtfeld, „no drift mid-segment"
CAMERA
ACTION                     ← in Sekundenspannen (0.0s–6.0s, …)
PHYSICS
LIGHTING
COLOR GRADE
AUDIO
STYLE
OUTPUT SETTINGS
POSITIVE LOCKS             ← nur positiv formulierte, prüfbare Bildeigenschaften
```

Feste Werte aus S14, die als Show-Standard weiterlaufen:

- **Optik:** 35 mm anamorphotischer Prime-Charakter, 2.39 Ultra-Widescreen, ovales
  Bokeh, horizontale Flares, Staub auf der Frontlinse; Sichtfeld je Segment
  einzeln gesetzt (84° weit / 63° / 40° nah), kein Drift innerhalb eines Segments.
- **Licht:** harte High-Noon-Sonne senkrecht von oben, kleine Schatten direkt unter
  den Objekten, Hitzeflimmern, **Weißabgleich 5600 K**.
- **Grade:** Spaghetti-Western — ausgebleichtes Ocker, Knochenweiß im Staub,
  Salbeigrün, Rot-Ocker-Fels, harter Kobaltblauhimmel, abgesoffene Schwarzen.
- **Style:** fotoreal live-action, körniges Filmkorn, Gate Weave, natürliche
  Bewegungsunschärfe, „imperfect and lived-in rather than clean".
- **Kamera:** operator-driven, nie rig-perfekt — Tremor, Nachziehen, Überschwingen,
  Horizont kippt leicht und richtet sich wieder auf.

## Zuständigkeit dieser Session

Diese Session ist **ausschließlich für den Establishing Shot S01** zuständig.
Arbeitsregeln aus `CLAUDE.md` und `S03-ESTABLISHER-HANDOFF.md` gelten unverändert —
insbesondere: Generierung erfolgt durch den User in der Higgsfield-App, nie per API.
