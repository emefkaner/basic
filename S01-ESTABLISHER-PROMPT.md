# S01 Establisher — Arbeitsstand

## Ergebnisse bisher

**30-s-Lauf (Seedance 2.5) — unbrauchbar.** Kamerafahrt zu schnell, danach
~7 s Stillstand, und der Zug kam von vorn und drehte beim Überfahren die
Richtung. Lehre: drei Änderungen in einem Lauf gebündelt; Länge allein macht
aus einem haltenden Shot keine 30 s.

**15-s-Lauf, Job `346838e5`, 15.09. 23:22 (Seedance 2.5).** Frame-geprüft:

- ✅ **Richtung stimmt.** Bei 11,75 s kommt der Zug von der unteren Bildkante
  (also von hinten), 11,75–13,5 s Unterseiten über der Linse, ab 13,5 s
  entfernt er sich rauchend die Gerade hinunter. Der Dreher war ein reines
  30-s-Problem.
- ✅ Sonnenöffnung mit Anamorphot-Flares und Geiern, 0–3 s.
- ✅ Die Abfahrt aufs Gleis und die bodennahe Perspektive sitzen.
- ❌ **Die Kamera steht mitten in der Stadt.** Ab Sekunde 3 flankieren
  „LAND OFFICE" links und „YOUNG & Co." rechts das Gleis, Wasserturm rechts,
  bis zum letzten Frame. Keine Mesas, keine Saguaros, keine leere Ebene.
- ❌ **~6,5 s bis ~11,5 s ist praktisch ein Standbild** — fünf tote Sekunden,
  ein Drittel des Shots.

## Ursache des Stadt-Fehlers

Getaggt war `@TRAIN-STATION-SOUTH-2` (`15d96ecf-…`). Dieses Element **ist** eine
Aufnahme von innerhalb der Stadt: Gleis mittig in der Hauptstraße, Land Office
links, Young & Co. rechts, Wasserturm rechts. Das Modell hat diese Fotografie
samt Geometrie reproduziert. Der `TOWN DISTANCE`-Block im Text kann dagegen
nichts ausrichten — „das Bild schlägt den Text". Zusätzlich hatte die Landschaft
gar keinen eigenen Eigentümer, also hat das Stadt-Foto sie mitbesetzt.

## Lösung: eigenes Element für die ferne Stadt

Nach der Regel „Build purpose-made reference elements": die Perspektive einmal
als Still lösen und als eigenes Element taggen, statt sie im Video zu erbitten.

Entscheidend war, die Entfernung **nicht** als absolute Zahl zu fordern
(„eineinhalb Kilometer" scheitert zuverlässig), sondern als prüfbare
Bildeigenschaft: *die beiden Schienen laufen optisch zusammen, und der Punkt,
an dem sie sich berühren, liegt bei der Stadt.* Dazu die Stadt auf maximal ein
Zehntel der Bildbreite und zwölf Telegrafenmasten zwischen Kamera und erstem
Gebäude als Tiefenstaffel.

Erzeugt mit Nano Banana (1 Credit), Job `d9b760b0-4dd7-4fb2-a25e-eece5ea9abe8`,
Referenz: `@TRAIN-STATION-SOUTH-2` nur als Quelle der Architektur, ausdrücklich
nicht der Kameraposition.

Zweiter Schritt auf demselben Bild (1 Credit, Job
`f21ff583-599b-4467-ad31-8c5a9f63add8`): der Rinderschädel liegt jetzt auf den
Schwellen zwischen den Schienen im Vordergrund. Er gehört ins **Element**, nicht
in den Prompttext — was im Referenzbild steht, kommt ins Bild; was nur im Text
steht, fällt weg. Der Videotext muss ihn danach nur noch wegblasen.

## Nächste Schritte

1. Still als Element speichern (`TOWN-FAR`, environment).
2. 15-s-Prompt erneut, mit `@TOWN-FAR` statt `@TRAIN-STATION-SOUTH-2` und
   `@WILDWEST` (`82b6c889-…`) als Eigentümer der Landschaft.
3. Offen, ob im selben Lauf: die fünf toten Sekunden beheben — Kamera sinkt
   während des Bebens weiter statt zu halten, plus der Schädel auf der Schwelle
   als sichtbares Ereignis im Vordergrund.

Generator-Settings für S01: Seedance 2.5, **15 s**, 1080p, 21:9, Audio an,
Multi-Shot aus, Bitrate high, kein Startbild. (Die 30 s aus
`S01-ESTABLISHER-BASELINE.md` sind für diesen Shot verworfen.)
