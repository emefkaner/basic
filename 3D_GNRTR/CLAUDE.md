# 3D_GNRTR — Konstruktionslogik für alle 3D-Druck-Projekte

Dieser Ordner enthält parametrische STL-Generatoren (reines Python 3, ohne
CAD, ohne Abhängigkeiten außer wo vermerkt). Jedes Projekt ist ein eigener
Unterordner mit `generate.py` (STLs), `vorschau.py` (SVG-Ansichten),
`README.md` und `stl/`. Dieses Dokument ist die gesammelte Logik aus den
bisherigen Projekten — **so wird hier gearbeitet.**

## 1. Mesh-Technik (kein CAD, keine Booleans)

Bauteile entstehen aus **geschlossenen, sich überlappenden Prismen/Lofts
("Schalen")**, die zusammen in eine STL geschrieben werden. Der Slicer
vereinigt überlappende Schalen beim Slicen — Booleans sind unnötig, und
jede Schale ist einzeln beweisbar wasserdicht. Grundbausteine (in jedem
`generate.py` enthalten, das reichhaltigste Set hat
`rc-transportbox/generate.py` bzw. `fernrohrhalter/generate.py`):

- `prisma(poly, z0, z1)` — einfaches Polygon senkrecht extrudiert
  (Ear-Clipping-Triangulierung, konkav erlaubt, keine Löcher).
- `loften(profile, hoehen)` — Stapel von Querschnitten **gleicher
  Punktzahl und Reihenfolge** zu einem Körper; damit entstehen Fasen,
  Kantenverrundungen (Profil pro Stufe einziehen) und Kegel.
- `loch_prisma(aussen, innen, ...)` — Prisma mit genau einem Loch;
  außen/innen brauchen gleiche Punktzahl und radiale Korrespondenz
  (beide star-shaped um dasselbe Zentrum).
- Löcher in beliebigen Konturen (z. B. Schrift): Brücken-Triangulierung
  (`hochzeitsornament/generate.py`, `prisma_mit_loechern`); Mäntel aus den
  Originalkonturen, Kantencheck akzeptiert dort gerade Kantenzahlen.
- Andere Achsrichtungen durch Achsentausch-Rotationen wie
  `(x,y,z)->(z,x,y)` — zyklisch = Determinante +1, Normalen bleiben ok.
- Schrift: `fontTools` + TTF (Great Vibes liegt in `hochzeitsornament/`),
  quadratische Beziers mit impliziten On-Curve-Punkten expandieren.

**Ein Punkt niemals doppelt** am Polygonanfang/-ende (Kante der Länge 0
lässt das Ear-Clipping steckenbleiben).

## 2. Pflicht-Prüfungen vor jeder Lieferung

Der Generator prüft selbst und bricht bei Verstoß ab — nie ungeprüft
liefern:

1. **Dichtheit:** jede Kante exakt 2× (`kanten_pruefen`). Bei
   Brücken-Triangulierung: jede Kante in gerader Anzahl.
2. **Passung:** Nachbarteile als 2D-Konturen in Einbaulage übereinander
   legen, Punkte auf Überdeckung testen (Punkt-in-Polygon + Randabstand).
3. **Formschluss:** die Freigabebewegung testen, nicht raten. Achtung:
   in Polarkoordinaten konstruierte Verzahnungen lösen sich durch
   **Drehung** um das Zentrum, nicht durch Geradfahrt — ein
   Translationstest übersieht das (so geschehen, im Drehtest gefunden).
4. **Containment:** Reliefs/Schrift müssen vollständig auf ihrer
   Grundfläche liegen, sonst wird in der Luft gedruckt (die Schleife
   einer „5" ragte einmal über den Herzrand — der Check fängt das).
5. **Bauraum:** beste Drehlage auf dem Bett suchen (alle Winkel, größter
   Randabstand). Bett: Bambu H2S, angenommen 350 × 350, real evtl.
   350 × 320 — **mindestens 20 mm Rand** fordern (Platz für Brim und
   Bettunsicherheit). Ein Kreis braucht seinen Durchmesser in BEIDEN
   Achsen; Drehen macht runde Teile nicht schmaler, Kippen scheitert
   an der Z-Grenze.
6. **Volumen** (Divergenzsatz) als Plausibilitäts- und Materialschätzung.

## 3. Druckbarkeits-Regeln (alles ohne Stützen)

- Teile so konstruieren, dass sie **in Drucklage generiert** werden.
- Querliegende Bohrungen → **Tropfenprofil** (Spitze nach oben, 45°).
- Querliegende Blöcke/Lagerböcke → **Rautenprofil** (45° trägt sich).
- Senkrechte Prismen haben keine Überhänge; Verrundungen oben über
  Loft-Einzug, Unterkanten scharf (Standfläche) oder als Fuß-Fase.
- Ein Deckel mit verrundeter Außenkante wird **mit der Innenseite nach
  oben** gedruckt; alles was dann auf der Außenfläche sitzen soll, darf
  keine Hohlräume brauchen, die andere Schalen füllen würden —
  Anbauten stattdessen an den Wandring verlegen.
- Schnapper/Federn: Biegung **in der Lagenebene** (Zug in XY), nie über
  Lagenhaftung.

## 4. Toleranzen & Verbindungen (bewährte Werte, PETG)

| Verbindung | Wert |
|---|---|
| Schiebesitz (Verzahnung, Schwalbe) | 0,12–0,15 mm je Flanke |
| Klebespalt (Epoxid) | 0,15 mm je Flanke |
| Presssitz Stift in Bohrung | 0,2–0,3 mm Übermaß, Einführfase 1–1,5 mm |
| Drehsitz Stift in Bohrung | 0,2–0,3 mm Spiel; 0,1 mm = gewollte Reibung |
| Drehspiel Hülse auf Pfosten | 0,6–0,7 mm im Durchmesser |
| Schnappzunge | Randdehnung ε ≈ 3·t·δ/(2·L²) ≤ 4 % halten |
| Klemmrippen (Crush-Ribs) | 1,1 mm dünn, 5 mm tief, Anlauffase; schlucken ±4 mm — **das Mittel der Wahl bei unsicheren Fremdmaßen** |
| Niederhalten im Deckel | Blattfeder-Bögen (1 mm dick, ~10 mm Hub) |

Formschluss-Prinzipien, die sich bewährt haben:
- **Hinterschnittene Doppel-Verzahnung** (innerer Zahn spreizt nach innen,
  äußerer nach außen → sperren sich gegenseitig; senkrecht steckbar).
- **T-Nut mit Blindende:** Last zieht gegen das Blindende — Formschluss
  statt Reibung (Tragegriff).
- Bei **2 Segmenten** liegen beide Stoßflächen in einer Ebene (seitlich
  zusammenschiebbar); ab 3 Segmenten nur senkrecht fügen — das letzte
  Teil muss in beide Nachbarn gleichzeitig.
- Verbindungsklötze bauen **nur nach außen** auf, lichte Innenmaße
  bleiben unangetastet.

## 5. Material-Faustregeln

- **PETG:** draußen, Feuchtigkeit, Schnapper, Dauerstöße (Roboter).
- **PLA (matt):** drinnen, Deko, wird lackiert (matt = bester
  Lackträger; Silk verträgt keine feinen Details und lackiert schlecht).
- Wandstärken: 5 mm freistehende Wand, 2,8 mm Kofferwand, 4 mm Platte.
- Empfohlene Slicer-Werte stehen im jeweiligen README.

## 6. Prozess-Regeln (aus Fehlern gelernt)

- **Eine STL pro Bauteil-Variante, Stückzahl in den Dateinamen**
  (`..._5x_drucken.stl`). Keine Alternativ-Varianten im Ordner ablegen —
  im Slicer wird sonst die falsche erwischt und Ausschuss gedruckt
  (genau so ein Segment zu viel entstanden). Alternativen nur per Flag —
  und wenn ein Flag ein Teil abschaltet, die alte STL beim Erzeugen
  **löschen**, sonst bleibt sie als Falle im Ordner liegen.
- **Anbauten kosten Außenmaß.** Vor jedem Zusatzteil ausrechnen, was es
  an der Hülle anrichtet, und gegen die Stil-Anforderung halten: der
  T-Nut-Griff machte den RC-Koffer 18 mm tiefer (Nutblöcke) plus 36 mm
  höher (Bügel) — bei 0,8 kg Traggewicht und griffigen Rundecken war
  „außen clean" mehr wert als der Bügel. Solche Umkehrungen einer
  früheren Nutzer-Vorgabe nicht still machen, sondern mit Zahlen
  vorschlagen und als Schalter anbieten.
- **Freie Fläche ist nicht nutzbare Fläche.** Restflächen neben einer
  konkaven Kontur sehen im 3D-Bild viel größer aus, als sie sind. Vor
  jeder Zusage über eine Stückzahl einen **Packtest** rechnen: Kandidaten-
  rechtecke (Bauteil + Luft + Wand) über alle Winkel und Positionen gegen
  die echte Kontur prüfen, mit Wandabstand. Beim RC-Koffer ergab das für
  Autolängen von 55 bis 90 mm immer dieselbe Zahl — der Engpass war die
  Breite, nicht die Länge, und das war ohne Rechnung nicht zu sehen.
  Das Ergebnis dem Nutzer als **maßstäbliche Draufsicht** zeigen, nicht
  als Behauptung.
- **Ueberlappende Schalen koennen Hohlraeume auffressen.** Die
  Schalen-Union ist bequem, aber ein Fach, das in einer Fuellschale
  liegt, muss dort auch als **Loch** stehen — sonst ist es massiv, und
  die STL sieht dabei voellig normal aus. Gegenprobe per Strahltest:
  senkrechte Strahlen durch den Hohlraum schicken und jede Flaeche
  oberhalb des Bodens melden (`hw_hohlraum_pruefen`).
- **Gespiegelt gedruckte Teile: Positionen umrechnen.** Der Kofferdeckel
  wird um Y gespiegelt gedruckt ((x,y,z)->(-x,y,z_top-z)). Alles, was
  zum Gegenstueck passen muss (Scharniersegmente!), gehoert bei -x
  konstruiert. Symmetrische Anbauten verzeihen den Fehler, verzahnte
  nicht — die Segmente lagen uebereinander statt ineinander, unsichtbar
  in der STL. Verzahnungen deshalb als **Intervalle in Einbaulage**
  pruefen (`scharnier_pruefen`).
- **Scharnierachsen: rohes Filament statt gedrucktem Stift.** 1,75-mm-
  Filament ist gezogen, homogen, rund und glatt — als Achse besser als
  jeder Druck, und es kostet kein Bauteil. Bohrung 2,2 mm (Tropfen, weil
  liegend), ein Aussensegment mit Ansenkung zum Einschieben, das andere
  mit Blindende; Ueberstand mit dem Loetkolben zum Nietkopf verschmelzen,
  der in der Senkung versinkt. Tragfaehig, weil ein vielfach gelagertes
  Band die Last als **Scherung** durch die Uebergaenge leitet und die
  freie Biegelaenge nur der Segmentspalt ist (Rechnung im README).
  Muss doch gedruckt werden: lange duenne Stifte **liegend**, sonst
  liegen alle Lagen quer zur Achse.
- **Tragende Scharniere breit aufteilen:** zwei 12-mm-Nasen trugen einen
  0,8-kg-Koffer auf 24 mm — ein Klavierband mit 7 Segmenten bringt
  101 mm, bei kleineren Augen sogar mit weniger Ueberstand.
- **Mehrfarbige Logos fuer AMS: ein Bauteil je Farbe, buendig.** Kein
  Relief, keine Tasche, kein Einleger -- der Traeger bekommt die
  Silhouette als Aussparung (LOGO_TIEFE 0,6 mm = 3 Lagen decken sauber,
  darueber laeuft die Grundfarbe weiter und spart Purge), und je
  Fuellfarbe entsteht eine STL mit demselben Ursprung. In Bambu Studio
  alle zusammen laden, "mehrteiliges Objekt?" -> Ja, je Teil das
  Filament setzen. Erhaben geht nicht, wenn das Teil mit dieser Flaeche
  am Bett liegt.
  Semantik beim Zerlegen: innerhalb eines SVG-Pfades trennt die
  **Verschachtelung** Flaeche und Loch; zwischen Pfaden gilt die
  **Zeichenreihenfolge** -- spaetere Farben aus den frueheren
  herausstanzen, sonst liegen zwei Koerper im selben Raum. Fuer die
  Aussparung im Traeger nur die aeussersten Konturen nehmen: ein Loch
  im Loch bringt die Brueckentriangulierung zu Fall.
  Quelle: SVG schlaegt PNG (keine Pixeltreppen, und nur dort stehen die
  Farben). Pfad-Parser (M/L/H/V/C/S/Q/T/Z, absolut und relativ, Beziers
  abtasten) in `rc-transportbox/generate.py`; fuer Pixelbilder Marching
  Squares + Douglas-Peucker.
- **Unsichere Fremdmasze durch eine Feder ersetzen, nicht durch eine
  Schaetzung.** Wie weit das Drehrad des Controllers laengs uebersteht,
  war aus Fotos nicht zu messen -- eine Blattfeder am Kopfende drueckt
  ihn gegen eine sichere Kante, und die Frage ist erledigt.
- **Passlehre vor dem grossen Druck.** Wenn eine Kontur aus Fotos statt
  aus einer Zeichnung stammt, zuerst ein flaches Abbild davon drucken
  (Querschnitt als 8-mm-Platte mit den Klemmrippen, ~40 min) und das
  Original einlegen lassen. Billiger als ein Fehldruck des Hauptteils,
  und die Rueckmeldung ist ein gemessener Restspalt statt einer
  Vermutung.
- **Aus Fotos abgenommene Konturen konvex glaetten,** wo die genaue Form
  unsicher ist: die konvexe Huelle ist nie enger als das Original, das
  Teil passt also sicher, und die Mulde wird nur etwas weiter (die
  Klemmrippen fangen das). Konkave Bereiche, die man BRAUCHT (die Kerbe,
  in der ein Zusatzfach liegt), davon ausnehmen.
- **Klemmrippen nur dort, wo das Gegenstueck starr ist** — nie auf einem
  beweglichen Teil (das Drehrad des Controllers) und nie auf einer
  Flaeche, die in der Fachhoehe gar nicht anliegt.
- **Maße misstrauen:** Ein Maßband über eine Wölbung misst Bogenlänge,
  nicht Durchmesser (2–3 cm Fehler beim Tellerfuß). Besser: Anschläge,
  Messschieber, oder ein bereits gedrucktes Teil als Lehre (anschieben,
  Restspalt messen). Unbekannte Fremdmaße → Crush-Ribs statt Präzision.
- **Immer rendern und ansehen** bevor geliefert wird. `vorschau.py`
  schreibt SVGs (eigener kleiner Painter-Renderer); Rasterisieren:
  `/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell
  --headless --no-sandbox --screenshot=... datei.svg` — lokal tut es
  jeder Browser. Große Dreiecke für Attrappen stückeln (Painter
  sortiert sonst falsch).
- Jede Änderung: `python3 generate.py` (Prüfungen laufen mit), dann
  `python3 vorschau.py`, committen, pushen.
- Physik kurz gegenrechnen, bevor gebaut wird: Hebel (Standbreite gegen
  Anstoßhöhe), Schwerpunkt (Balance-Lagerung am Schwerpunkt; bei
  veränderlichem Schwerpunkt Balance auf Mittelstellung + definierte
  Reibung), Zungendehnung.
- Anfahrkanten für Roboter **steil, nie als Rampe** (Rampen sind
  Kletterhilfen); Barrieren ≥ 40 mm hoch, Kletterhöhe der Sauger ~20 mm.
- Fremd-Fonts: Lizenz (OFL.txt) mit ins Repo.

## 7. Neues Projekt anlegen

1. `3D_GNRTR/<projektname>/` mit `generate.py` — Basis von
   `rc-transportbox/generate.py` (Koffer/Mechanik) oder
   `fernrohrhalter/generate.py` (Gelenke/Rundteile) oder
   `bodenroboter-schutzring/generate.py` (Ringe/Segmente/Loft) kopieren.
2. Alle Maße als benannte Konstanten oben, abgeleitete Werte in einer
   Funktion; Nutzereingaben (`--fuss`, `--rohr` …) per argparse.
3. Prüfungen aus Abschnitt 2 einbauen, `vorschau.py` danebenlegen.
4. README: Welche Datei, wie oft drucken, Material, Zusammenbau,
   Annahmen + wie man nachmisst und regeneriert.

## Projektübersicht

| Ordner | Inhalt | Besonderheit |
|---|---|---|
| `bodenroboter-schutzring/` | Schutzringe um Möbelfüße (Tisch 375, Stuhl 645 innen) | Loft, hinterschnittene Steck-Verzahnung, Formschluss-Drehtest |
| `rennsitz-verkleidung/` | Designblatt, wartet auf Foto/Maße | — |
| `fernrohrhalter/` | Alt-Az-Halter fürs Piraten-Spyglass | Raute/Tropfen, Balance + Reibung, Schnapp-Schelle |
| `hochzeitsornament/` | Herz „Ute & Werner · 50" + Sockel | fontTools-Schrift, Brücken-Triangulierung, Containment-Check |
| `rc-transportbox/` | Koffer für Hot Wheels RC 1:64 + 2 lose Autos | Crush-Ribs, Federbögen, Schnapper, Stufenfalz, Scharnier, T-Nut-Griff optional (`--mit-griff`) |
