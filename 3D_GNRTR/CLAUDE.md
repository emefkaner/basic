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
  Das gilt genauso fuer alles mit **Leserichtung**: Logo, Schrift,
  Gravur. Beim RC-Koffer war das Scharnier umgerechnet, das Logo nicht --
  der Schriftzug kam spiegelverkehrt aus dem Drucker. Gegenprobe ist
  eine Ansicht des Teils in EINBAULAGE (`ansicht_deckel_aussen.svg`);
  in Druckkoordinaten sieht ein spiegelverkehrtes Logo voellig normal
  aus.
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
  Semantik beim Zerlegen: die **Verschachtelung ueber alle Farben
  hinweg** entscheidet, nicht die Pfadreihenfolge. Jede Kontur wird ein
  Koerper ihrer Farbe und bekommt als Loecher die Konturen, die DIREKT
  in ihr liegen -- gleich welcher Farbe. Nur so stimmt der Fall, an dem
  eine Reihenfolge-Regel scheitert: rote Punzen mitten in der gelben
  Schrift. Fuer die Aussparung im Traeger nur die aeussersten Konturen
  nehmen: ein Loch im Loch bringt die Brueckentriangulierung zu Fall.
  Bei Pixelbildern echte Loecher NICHT aus den Farbmasken holen -- an
  einer Farbgrenze liefern zwei Masken deckungsgleiche Konturen, die
  sich gegenseitig blockieren. Loecher kommen aus der
  Vordergrundmaske (dort scheint der Hintergrund durch).
  Quelle: SVG schlaegt PNG (keine Pixeltreppen, und nur dort stehen die
  Farben). Pfad-Parser (M/L/H/V/C/S/Q/T/Z, absolut und relativ, Beziers
  abtasten) in `rc-transportbox/generate.py`; fuer Pixelbilder Marching
  Squares + Douglas-Peucker.
  **Auto-vektorisierte Dateien sind schmutzig** -- vier Fallen, alle in
  `rc-transportbox/generate.py` abgefangen: (1) doppelte Konturen
  (Buchstabe einmal als evenodd-Loch im Grundpfad, einmal als eigene
  Farbflaeche) ueber die Ueberdeckung der HUELLRECHTECKE zusammenfassen,
  Schwerpunkte taugen nicht; (2) Punkte aus dem Pixelraster, die nach
  dem Skalieren aufeinanderliegen -> Kante der Laenge 0 laesst das
  Ear-Clipping haengen (`polygon_saeubern`); (3) Splitter von 1-3 mm2 in
  Zwischentoenen an den Farbkanten wegfiltern; (4) Selbstueberschneidungen
  -> Notausgang, der die Kontur schrittweise per Douglas-Peucker
  vereinfacht. Und die Bruecke fuer ein Loch ueber einen echten
  **Sichtbarkeitstest** suchen (keine Kante kreuzen, Mitte im Material),
  Loecher von rechts nach links einbauen -- die Heuristik "naechstes
  Punktpaar, dann Triangulierung probieren" scheitert ab etwa fuenf
  Loechern in einer Flaeche.
  Gegenprobe: Zufallspunkte ueber der Grafik werfen und zaehlen, wieviele
  Koerper jeden decken -- es muss ueberall genau einer sein.
- **Unsichere Fremdmasze durch eine Feder ersetzen, nicht durch eine
  Schaetzung.** Wie weit das Drehrad des Controllers laengs uebersteht,
  war aus Fotos nicht zu messen -- eine Blattfeder am Kopfende drueckt
  ihn gegen eine sichere Kante, und die Frage ist erledigt.
- **Fremdmasze vom Nutzer koennen falsch sein -- Konturen MESSEN.**
  Beim RC-Koffer waren die angesagten 190 x 131 in Wahrheit 215 x 151;
  vermutlich war ein ausladender Teil nicht mitgemessen. Verfahren
  (`rc-transportbox/kontur_aus_foto.py`): Teil flach auf DIN A4, Foto
  senkrecht von oben, ueber die vier Blattecken per Homographie (DLT)
  entzerren, dann die Silhouette segmentieren. Auf weissem Papier ist
  die Trennung eindeutig, an einer roten Platte unter farbigem Licht
  nicht. Drei Fallen: (1) die Bezugsflaeche muss das Teil GANZ tragen,
  sonst ist die Silhouette abgeschnitten; (2) nie die konvexe Huelle der
  Bezugsflaeche als Suchbereich nehmen -- bei schraeg liegendem Blatt
  greift sie darueber hinaus und der dunkle Boden zaehlt als Teil
  (gemessen wurden 293 x 265 statt 215 x 151); (3) das Teil in die Mitte
  legen, am Bildrand verzerrt der schraege Blick zusaetzlich.
- **Gemessene Pixelkonturen aufbereiten**, sonst stehen im Druck lauter
  Nubsis in der Mulde: Chaikin glaetten (drei Durchlaeufe), schmale
  Kerben ueberbruecken (`kerben_fuellen` -- ein formzutreu ausgesparter
  Clip laesst sich kaum einfaedeln), um ein halbes Zehntel nach AUSSEN
  versetzen (weiter ja, enger nie), danach `schlaufen_entfernen`: beim
  Versetzen ueberschlagen sich die Kanten an engen konkaven Stellen, und
  ein Polygon mit Schlaufe ist nicht triangulierbar.
- **Klemmrippen weglassen, wo die Kontur gemessen ist.** Sie sind das
  Mittel gegen unsichere Masze; ist die Form bekannt, stehen sie nur im
  Weg. Das Restspiel nimmt eine kurze, weiche Blattfeder (Randdehnung
  unter 1 %), keine 15-mm-Kruecke.
- **Passlehre vor dem grossen Druck.** Wenn eine Kontur aus Fotos statt
  aus einer Zeichnung stammt, zuerst ein flaches Abbild davon drucken
  (Querschnitt als 8-mm-Platte mit den Klemmrippen, ~40 min) und das
  Original einlegen lassen. Billiger als ein Fehldruck des Hauptteils,
  und die Rueckmeldung ist ein gemessener Restspalt statt einer
  Vermutung.
- **Was lange in Arbeit bleibt, von der Huelle ENTKOPPELN.** Beim
  RC-Koffer wuchs das Aussenmasz aus der Controllermulde heraus -- also
  haette jede Muldenkorrektur nach einem Lehrendruck auch den Deckel
  verschoben, und wer den Deckel schon gedruckt hat, hat 300 g Ausschuss.
  Loesung: das Fach auf ein FESTES Masz setzen (`FACHC_FEST`) und die
  Mulde darin zentrieren. Die Reserve wird zur Zusage ("die Mulde darf
  noch 2 mm je Seite wachsen") und der Generator bricht ab, wenn sie
  nicht reicht, statt still ein anderes Aussenmasz zu erzeugen. So laesst
  sich der fertige Teil parallel zum offenen Teil drucken. Kostet hier
  4 mm Aussenmasz -- billiger als ein Fehldruck und als Wartezeit.
- **Bild-y zeigt nach UNTEN, Modell-y nach OBEN.** Der teuerste Fehler des
  RC-Koffers: die Homographie bildete die Blattecken in Bildreihenfolge
  auf (0,0),(lang,0),(lang,kurz),(0,kurz) ab, das Ergebnis zaehlte y also
  nach unten. Als Modellpolygon extrudiert kam eine spiegelverkehrte
  Mulde heraus. Eine Spiegelung ist durch KEINE Drehung ruecknehmbar --
  und sie faellt bei einem konkav-organischen Umriss visuell kaum auf.
  Beim Umrechnen Bild -> Modell also immer die obere Bildkante auf das
  GROSSE v legen.
- **Eine flache Passlehre kann eine Spiegelung nicht aufdecken** -- man
  dreht die Platte um, und alles passt. Genau deshalb ging der Fehler
  durch den Lehrentest hindurch bis in die 900-g-Wanne. Haendigkeit
  deshalb gegen ein FOTO des echten Teils pruefen, nicht gegen eine
  Messung, die durch dieselbe Umrechnung gelaufen ist (die ist
  selbstkonsistent und bestaetigt jeden Spiegelfehler brav). Bild
  erzeugen: Fach von oben rendern (x rechts, y oben) und daneben das
  Foto in gleicher Ausrichtung -- ein asymmetrisches Merkmal (hier der
  orangene Abzug gegenueber der grossen Kerbe) entscheidet in einer
  Sekunde. "Gleiche Seite von"-Tests taugen NICHT: eine Spiegelung
  erhaelt sie.
- **Klemmrippen und Federn vom lichten Mass ABZIEHEN.** Es reicht nicht
  zu pruefen, dass sich Faecher nicht ueberlappen -- entscheidend ist,
  was nach den Einbauten uebrig bleibt. Beim RC-Koffer bekam die Auto-Box
  48 mm fuer 50 mm Breite und die Hot-Wheels-Faecher 28 mm fuer 35 mm
  breite Autos, weil die Rippen mit voller Tiefe hineinragten, das
  Fachmass sie aber nur mit (Tiefe - 1) einkalkulierte. Fachmass =
  Inhalt + 2*Rippentiefe - 2*Uebermass, und eine Pruefung, die genau
  diese Rechnung nachvollzieht (`klemmung_pruefen`).
- **Eine Suche, die scheitern kann, muss LAUT scheitern.** Die Suche nach
  dem Platz fuer ein Zusatzfach lief mit `while ... and not frei` durch
  und nahm danach die letzte Position -- mitten in der Mulde. Kein
  Fehler, keine Meldung, kaputte Geometrie. Immer: Erfolg explizit
  festhalten, sonst abbrechen.
- **Die Passlehre ist nicht nur ein Test, sie ist ein MESSMITTEL.** Ein
  Foto von oben, auf dem alle vier Plattenecken zu sehen sind, laesst
  sich ueber dieselbe Homographie auswerten wie das A4-Foto -- und die
  Lehre ist die genauere Bezugsflaeche, weil ihre Masze aus dem
  Generator stammen. Damit wird aus "passt fast" eine Zahl: beim
  RC-Koffer der Abzug (35,4 x 31,2 mm, lag bis 15,4 mm tief auf
  Material) und das Spiel rundum (durch das Loch sichtbarer Boden =
  Luft, rund 10 % der Muldenflaeche). Farbige Teile am Gegenstand sind
  dabei geschenkt: der orangene Abzug war ueber die Farbe eindeutig zu
  finden. Deshalb die Lehre auf einen Untergrund legen, der sich vom
  Bauteil unterscheidet.
- **Was die Lehre findet, wird eine Pruefung, nicht nur eine Korrektur.**
  Sonst faellt derselbe Fehler bei der naechsten Konturaenderung still
  wieder hinein. Aus dem Abzug wurde `abzug_pruefen()` (der GEMESSENE
  Umriss des Hebels gegen die fertige Mulde), aus der gekuerzten Luft
  `mulde_pruefen()` (Mulde mindestens 1,5 mm weiter als die Silhouette,
  gemessen am Rand, nicht am Parameter).
- **Glaettung kann Funktionsluecken zuschmelzen.** `kerben_fuellen`
  ueberbrueckt schmale Kerben, damit der Rand druckbar wird -- dabei ist
  der Schlitz hinter dem Abzug mitverschwunden, und der Hebel lag im
  Druck auf dem Material. Was gebraucht wird, danach wieder
  hineinschmelzen: `polygon_vereinigen(kontur, rechteck)` ersetzt die
  Konturpunkte im Zusatzstueck durch einen Umweg ueber dessen Aussenrand
  (Richtung so waehlen, dass der Umweg AUSSERHALB der Kontur liegt).
  Das ist eine Vereinigung ohne Boolean-Bibliothek und liefert wieder
  ein einfaches Polygon. Zwei getrennte Loecher waeren falsch -- dazwischen
  bliebe ein Steg genau dort, wo das Teil sitzt.
- **Aus Fotos abgenommene Konturen konvex glaetten,** wo die genaue Form
  unsicher ist: die konvexe Huelle ist nie enger als das Original, das
  Teil passt also sicher, und die Mulde wird nur etwas weiter (die
  Klemmrippen fangen das). Konkave Bereiche, die man BRAUCHT (die Kerbe,
  in der ein Zusatzfach liegt), davon ausnehmen.
- **Ein Fach mehr kostet immer Aussenmasz — die billigste Richtung
  ausrechnen, nicht die naechstliegende.** Fuer das dritte Hot-Wheels-Fach
  im RC-Koffer standen drei Wege offen: Streifen verbreitern (+30 mm X),
  Fach hinter die Auto-Box (+70 mm Y), Fach quer davor (+46 mm Y). Faktor
  zwei zwischen erster und schlechtester Loesung. Und: sobald ein Gehaeuse
  waechst, gehoert der **Bauraumcheck in den Generator** (Rechteck plus
  20 mm Rand je Seite gegen 350 x 320), sonst laeuft der Zuwachs still in
  die Bettgrenze.
- **Verbreiterte Faecher lassen Reststreifen zurueck — Wand rein.** Wird
  ein Streifen fuer zwei Faecher breiter gemacht, passt der alte Inhalt
  nur noch zur Haelfte hinein. Der Rest braucht eine echte Trennwand, aus
  zwei Gruenden: er wird zum brauchbaren Zubehoerfach, und die Klemmrippe
  des Nachbarfachs bekommt wieder eine Wand unter sich. Eine Rippe ist ein
  1,1-mm-Blatt; frei auf dem Boden stehend bricht sie ab.
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
| `rc-transportbox/` | Koffer für Hot Wheels RC 1:64 + 3 lose Autos | gemessene Konturmulde, Federbögen, Schnapper, Stufenfalz, Filament-Scharnier, AMS-Logo, T-Nut-Griff optional (`--mit-griff`) |
