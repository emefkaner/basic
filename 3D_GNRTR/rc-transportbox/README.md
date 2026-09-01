# Transportkoffer — Hot Wheels RC 1:64 Lamborghini Temerario

## Projektstand (nach dem ersten Lehrendruck korrigiert)

| | |
|---|---|
| **Koffer außen** | 266 × 238 × 66 mm (Bett 350 × 320: 42/41 mm Rand) |
| **Controllerfach** | fest auf 166 × 230 — davon hängt der Deckel ab |
| **Controller (gemessen)** | 215,1 × 151,1 mm, Gehäuse 42 dick, mit Drehrad 57 |
| **Muldenluft** | 2,0 mm je Seite (war 4,0 — im Lehrendruck zu viel) |
| **Abzugsaussparung** | 45 × 41 mm, grob, aus dem Lehrenfoto gemessen |
| **Längsfeder** | 55 mm Sehne, 1,4 dick, 10 mm Hub (war 5) |
| **Auto-Box** | 100 × 50 × 50 mm |
| **Hot Wheels (längstes)** | 88 × 35 × 30 mm, **drei** Einzelfächer |
| **Zubehörfach** | 28 × 108 mm neben der Auto-Box (Ladekabel, Ersatzräder) |
| **Scharnierachse** | 179 mm rohes 1,75-mm-Filament |
| **Logo** | `logo.svg`, 130 mm breit, zwei Farbteile |

**Als Nächstes:** die korrigierte Passlehre gegenprüfen
(`rcbox_0_passlehre_zuerst_drucken.stl`, rund 40 min). Sitzt der
Controller samt Abzug, ist die Wanne dran.

**Der Deckel darf schon vorher gedruckt werden.** Das Controllerfach hat
seit dieser Änderung ein festes Außenmaß (`FACHC_FEST` = 166 × 230), die
Mulde wird darin zentriert. Damit hängt die Kofferhülle — und mit ihr
Deckel, Scharnier, Falz und Logo — nicht mehr an der Muldenform. Reserve:
die Mulde darf noch 2,0 mm je Seite wachsen, bevor der Randsteg unter
3 mm fällt; das deckt den ganzen Weg zurück zur alten Muldenluft von
4 mm ab. Reicht es doch nicht, bricht der Generator ab und sagt es, statt
still ein anderes Außenmaß zu erzeugen — ein bereits gedruckter Deckel
wäre sonst Ausschuss.

### Was der erste Lehrendruck gezeigt hat

Der Controller lag drin, aber drei Dinge stimmten nicht. Alle drei sind
aus dem Foto **gemessen** worden, nicht geschätzt: die Lehre selbst ist
die Bezugsfläche, über ihre vier Ecken wird das Foto entzerrt.

| Befund | Messung | Korrektur |
|---|---|---|
| Abzug lag auf dem Material auf | der orangene Hebel belegt 35,4 × 31,2 mm, davon lagen 44 von 90 Umrisspunkten auf Material, bis 15,4 mm tief | 45 × 41 mm große, grob gerundete Aussparung, in die Mulde eingeschmolzen |
| „fast ein bisschen zu lang" | durch das Loch war ringsum Holz zu sehen, rund 10 % der Muldenfläche | `MULDE_LUFT` 4,0 → 2,0 mm; die 4 mm werden nicht am Außenmaß gespart, sondern als Randsteg-Reserve gelassen (siehe oben) |
| Feder zu klein | 5 mm Hub greifen nicht bis ans Gehäuse — die Silhouette von oben enthält das überstehende Drehrad, in der Muldenzone endet das Gehäuse früher | 10 mm Hub, 55 mm Sehne, 1,4 mm dick |

Der Abzug ist damit nicht formgetreu ausgespart, sondern grob — ein
formgetreuer Ausschnitt wäre kaum einzufädeln. Damit die Aussparung und
die Mulde **ein** Loch werden (und nicht ein Materialsteg dazwischen
stehen bleibt), schmilzt `polygon_vereinigen()` das Rechteck in die
Muldenkontur: die Muldenpunkte im Rechteck werden durch einen Umweg über
dessen Außenrand ersetzt. Ohne Boolean-Bibliothek, und das Ergebnis ist
wieder ein einfaches Polygon.

Zwei Prüfungen halten das künftig fest:
`abzug_pruefen()` legt den **gemessenen** Umriss des Hebels über die
fertige Mulde (jeder Punkt frei, mindestens 2 mm Luft), und
`mulde_pruefen()` verlangt, dass die Mulde die Silhouette überall um
mindestens 1,5 mm umschließt — sonst wäre `MULDE_LUFT` eine Zahl, an der
man sich unbemerkt festklemmt.

### Wie die Kontur entstanden ist — und was vorher schiefging

Die Silhouette wurde zuerst aus dem Foto der Original-Schaumschale
abgenommen: **190 × 131 mm**. In der gedruckten Lehre passte nichts.
Gemessen wurde dann mit `kontur_aus_foto.py` (Controller auf DIN A4,
Foto von oben, über die vier Blattecken entzerrt): **215,1 × 151,1 mm** —
25 mm länger, 20 mm breiter. Keine Formkorrektur hätte das gefunden, das
Teil war schlicht größer als angenommen.

Drei Fallen auf dem Weg, alle im Skript abgefangen:

- **Die Bezugsfläche muss das Teil ganz tragen.** Auf der 144 × 204 mm
  großen Lehre ragte der Controller über zwei Kanten hinaus — die
  Silhouette war dort abgeschnitten. Deshalb A4.
- **Nicht die konvexe Hülle der Bezugsfläche nehmen.** Liegt das Blatt
  schräg im Bild, greift sie über die Blattkanten hinaus, und der dunkle
  Boden dort zählt als Teil: gemessen wurden 293 × 265 statt 215 × 151.
  Jetzt wird exakt auf das Viereck der vier erkannten Ecken begrenzt.
- **Die Lehre taugt trotzdem als Bezug**, wenn das Teil daraufpasst: sie
  ist 8 mm dick, das Teil liegt auf ihrer Oberseite — also genau in der
  Ebene, über die kalibriert wird.

### Was am Muldenrand passiert

Die gemessene Kontur kommt aus einer Pixelmaske: maßlich richtig, aber
mit lauter kleinen Treppen, die sich im Druck als Nubsis wiederfinden.
Deshalb in dieser Reihenfolge:

1. **Chaikin**, drei Durchläufe — jede Ecke wird durch zwei Punkte auf
   der Kante ersetzt, die Kontur wird weich.
2. **Kerben überbrücken** (`kerben_fuellen`): liegen zwei Punkte näher
   als 16 mm beieinander, sind aber entlang der Kontur weiter als 40 mm
   auseinander, wird der Bogen dazwischen durch die direkte Verbindung
   ersetzt. Das glättet den Rand — genau dabei ist aber der Schlitz
   hinter dem Abzug mit verschwunden, weshalb der Hebel im ersten
   Lehrendruck auf dem Material auflag. Die grobe Abzugsaussparung wird
   deshalb hinterher wieder eingeschmolzen (`polygon_vereinigen`).
3. **0,6 mm nach außen versetzen** — die Mulde darf weiter werden, nie
   enger.
4. **Schlaufen entfernen** (`schlaufen_entfernen`): beim Versetzen
   überschlagen sich die Kanten an engen konkaven Stellen zu Schlaufen,
   und ein Polygon mit Schlaufe lässt sich nicht triangulieren.

**Keine Klemmrippen in der Controllermulde.** Sie standen als Nubsis im
Weg und werden nicht gebraucht, seit die Kontur gemessen ist. Das
Restspiel nimmt eine Blattfeder am Kopfende: 55 mm Sehne, 1,4 mm dick,
10 mm Hub. Sie darf bis auf Anschlag gehen — selbst flachgedrückt liegt
die Randdehnung bei 0,7 %, sie wirkt dann als Anschlag statt als
Bruchstelle. Vorgänger waren 15 mm Hub (Krücke gegen die damals
unbekannte Kontur) und 5 mm (griffen im Lehrendruck nicht weit genug,
weil die Silhouette von oben das überstehende Drehrad enthält).

## Überblick

Kompakter Klappkoffer für das RC-Auto **in seiner Originalbox**, den
Pistolengriff-Controller und **drei lose Hot Wheels** in Einzelfächern.
Außen **266 × 238 × 66 mm**, verschließbar, außen glatt — komplett
gedruckt, keine Schrauben, keine Metallteile.
Ein Steck-Tragegriff ist als Option eingebaut (`--mit-griff`), gehört
aber nicht zur Standardausgabe.

Der Controller liegt in einer **pistolenförmigen Konturmulde** nach dem
Vorbild des Original-Formfaser-Trays — nicht in einem Rechteckfach, in dem
er rotieren und schlagen könnte.

## Teile

| Teil | Datei | Drucken |
|---|---|---|
| **Passlehre (zuerst!)** | `rcbox_0_passlehre_zuerst_drucken.stl` | 1 × |
| Wanne | `rcbox_1_wanne_1x_drucken.stl` | 1 × |
| Deckel | `rcbox_2_deckel_1x_drucken.stl` | 1 × |
| Deckellogo je Farbe (nur mit `logo.svg`) | `rcbox_2b…filament2…`, `rcbox_2c…filament3…` | je 1 × |

Als Scharnierachse dient **179 mm rohes 1,75-mm-Filament** — es wird
nichts dafür gedruckt. Nur mit `--gedruckter-stift` entsteht zusätzlich
`rcbox_4_achsstift_2x_drucken.stl` (2 ×).

Der Griff (`rcbox_3_griff_1x_drucken.stl`) entsteht nur mit
`python3 generate.py --mit-griff`; ohne die Option löscht der Generator
eine alte Griff-STL wieder aus `stl/`, damit im Slicer nichts Falsches
erwischt wird.

## Zuerst die Passlehre drucken

`rcbox_0_passlehre_zuerst_drucken.stl` ist der Muldenquerschnitt als
8 mm flache Platte samt Längsfeder — 166 × 230 mm, rund 40 Minuten
Druckzeit. **Controller einlegen und prüfen, bevor die 870-g-Wanne
gedruckt wird.** Die Silhouette stammt aus Fotos, nicht aus einer
Zeichnung: eine Lehre ist billiger als ein Fehldruck. Klemmt es, den
Restspalt messen und `CTRL_BREITE`, `CTRL_LAENGE` oder `MULDE_LUFT`
anpassen und neu erzeugen.

Und die Lehre ist zugleich das **Messmittel**: ein Foto von oben, auf dem
alle vier Plattenecken zu sehen sind, reicht, um die Passung in
Millimetern auszuwerten (Homographie über die Ecken). So sind die
Abzugsaussparung und die gekürzte Muldenluft entstanden — durch das Loch
sichtbares Holz ist Spiel, und der orangene Hebel ist farblich eindeutig
zu finden.

## Warum nichts wackelt

Die Controller-Silhouette ist auf DIN A4 gemessen und in der gedruckten
Lehre gegengeprüft: **215,1 lang × 151,1 breit**, Gehäuse 42 dick, mit
Drehrad 57, Rad ⌀45 mm (Ränder 77/10 mm in der Breitenachse). Die
Sicherung ist dreifach:

- **Konturmulde** (30 mm tief): die Fachfüllung hat ein pistolenförmiges
  Loch mit 2 mm Luft je Seite — der Controller kann weder verrutschen
  noch rotieren, genau wie im Original-Tray. Der Abzug hat seine eigene
  grobe Aussparung, in dieselbe Kontur eingeschmolzen.
- **Keine Klemmrippen** in der Mulde: sie waren das Mittel gegen die
  damals unbekannte Kontur. Seit die Silhouette gemessen ist, stünden
  sie nur als Nubsis im Weg.
- **Federbögen im Deckel**, gezielt über Schnauze, Griffende und Auto-Box —
  **nicht** über dem Drehrad: drücken beim Schließen von oben nach, ohne
  das Rad zu klemmen. Der Hub wird je Stelle aus der Einbauhöhe gerechnet.

### Längsfeder am Kopfende

Das Drehrad sitzt **oben auf** dem Gehäuse (z = 42 bis 57) und ragt in
Längsrichtung über die Gehäusekante hinaus. In der Muldenzone (0 bis
30 mm) ist dort also nur Gehäuse — die Mulde reicht aber bis zur
Radkante, der Controller könnte um den Radüberstand nach vorn wandern.
Wie weit das Rad genau übersteht, ist aus Fotos nicht sicher zu messen.
Statt zu raten, drückt eine **Blattfeder** (55 mm Sehne, 1,4 mm dünn,
10 mm Hub) am Kopfende den Controller gegen die Wand am Griffende — das
ist eine echte Gehäusekante. Damit ist die Längslage definiert, egal wie
der Radüberstand ausfällt. Der Hub ist genau deshalb von 5 auf 10 mm
gewachsen: im Lehrendruck war zu sehen, dass 5 mm gar nicht bis ans
Gehäuse reichen. Randdehnung selbst flachgedrückt 0,7 % — die Feder darf
auf Anschlag gehen.

### Drei Einzelfächer für lose Hot Wheels

Lichte Maße **38 × 91 × 30 mm** je Fach, runde Ecken (R5), ausgelegt auf
das längste gemessene Auto (88 × 35 × 30). Gehalten wird jedes Auto
dreifach: vier **Klemmrippen** an den Längsseiten, eine **Stirn-Blattfeder**
(1,2 mm dünn, 8 mm Hub, biegt in der Lagenebene) drückt auch kürzere Autos
ab etwa 80 mm gegen die Gegenseite, und die 30 mm hohen Fachwände lassen
das Auto gar nicht erst kippen.

- **Fach 1** liegt im Keil zwischen Rad- und Griffkontur des Controllers —
  genau die Stelle, an der im Original-Tray auch Luft ist.
- **Fach 2 und 3** liegen nebeneinander vorn im rechten Streifen. Dafür
  rückt die **Auto-Box nach hinten** statt mittig zu sitzen: aus zwei
  ungenutzten Streifen von je 48 mm wird einer von 96 mm.

**Warum der Koffer für das dritte Auto 30 mm breiter wurde.** Der Engpass
ist die Breite, nicht die Länge: ein Fach braucht 35 mm Auto + 2 × 1,5
Luft + 2 × 2,5 Wand = **43 mm**. Der Keil links läuft nach hinten spitz zu
(bei y = +60 sind nur noch 28 mm frei), der rechte Streifen war 58 mm
breit — für zwei Fächer nebeneinander fehlten 28 mm. Ein Packtest über
alle Winkel und Positionen fand im alten Gehäuse für Autolängen von 55 bis
90 mm immer dieselbe Zahl: zwei. Kürzere Autos bringen also nichts, nur
mehr Koffer. Drei Wege dorthin, gerechnet:

| Variante | Kosten | |
|---|---|---|
| Streifen auf 88 mm verbreitern, Fächer nebeneinander | **+30 mm in X** | gewählt |
| Fach hinter der Auto-Box | +70 mm in Y | mehr als doppelt so teuer |
| Fach quer vor der Box | +46 mm in Y | teurer, und die Box verliert den Anschlag |

Gewählt ist also die schmalste: **266 × 238 mm**, auf dem 350er Bett
bleiben 42 bzw. 41 mm Rand (`bauraum_pruefen()` rechnet das mit, seit der
Koffer wächst).

Der Streifen ist damit 88 mm breit, die Auto-Box braucht davon 58. Die
übrigen 28 mm sind kein Restmüll, sondern durch eine 3-mm-Trennwand ein
**Zubehörfach 28 × 108 mm** (Ladekabel, Ersatzräder). Die Wand muss sein:
ohne sie stünde die linke Klemmrippe der Box frei auf dem Boden — ein
1,1 mm dünnes Blatt, 30 mm hoch, das beim ersten Anstoßen abbricht.

Die Maße sind Parameter (`HW_L`, `HW_B`, `HW_H`, `HW_LUFT`, `HW_WAND`,
`HW_ECKE`, `HW_FED_HUB`). `hw_faecher_pruefen()` testet den Rahmenrand
Punkt für Punkt gegen Mulde, Auto-Box und Wannenwand — die Mulde ist
konkav, ein reiner Eckentest würde die Kerbe zwischen Rad und Griff
übersehen.

### Einbaulage: Rad nach oben

Der Controller hat zwei Dicken — Gehäuse 42 mm, mit Drehrad 57 mm. Das Rad
steht also 15 mm einseitig über. Er wird mit dem **Rad nach oben** eingelegt:
dann liegt das Gehäuse flach in der Mulde und das Rad ragt frei in den
Deckelraum (3 mm Luft). Andersherum läge er auf dem Rad und würde kippeln —
die asymmetrische Pistolenform der Mulde lässt die gespiegelte Lage aber
ohnehin nicht zu. Der Generator prüft zweierlei und bricht bei Verstoß ab: dass das Rad in
der Höhe in den Deckel passt (aktuell 27 mm Rad gegen 30 mm Deckel = 3 mm
Luft), und dass keine Deckelfeder über dem Radkreis steht.

Silhouette, Maße (`CTRL_LAENGE`, `CTRL_BREITE`, `CTRL_GEHAEUSE_D`,
`CTRL_RAD_UEBER`, `AUTOBOX_*`)
und Muldenluft (`MULDE_LUFT`) sind Parameter in `generate.py`.

## Logo auf dem Deckel (mehrfarbig, AMS)

Liegt `logo.svg` neben `generate.py`, entstehen **zusätzliche Bauteile,
eines je Füllfarbe des Logos** — beim Hot-Wheels-Logo also zwei (Flamme
und Schriftzug). Keine Tasche, kein Einleger, kein Absatz: die Körper
liegen bündig in der Deckelfläche und sind genauso hoch. Gedruckt wird
alles in einem Zug, der Farbwechsel passiert in der Ebene.

Die Farbe reicht `LOGO_TIEFE` = 0,6 mm tief (3 Lagen — deckt sauber);
darüber läuft der Deckel in der Grundfarbe weiter. Das hält die Zahl der
Filamentwechsel und damit den Purge klein.

**Der Deckel wird gespiegelt gedruckt** ((x,y,z) → (−x, y, z_top−z)) —
die Außenfläche liegt ja am Bett. Ein Logo hat anders als ein Scharnier
eine **Leserichtung**, muss in den Druckkoordinaten also bei −x stehen.
Ohne das kommt der Schriftzug spiegelverkehrt aus dem Drucker (genau so
passiert). Kontrolliert wird es an `stl/ansicht_deckel_aussen.svg`: dort
ist der Deckel in Gebrauchslage gezeichnet, und da muss der Schriftzug
lesbar sein.

**Import in Bambu Studio:**

1. Alle Deckel-STLs zusammen auswählen und laden:
   `rcbox_2_deckel…`, `rcbox_2b_deckellogo_filament2…`,
   `rcbox_2c_deckellogo_filament3…`
2. *„Als ein einzelnes Objekt mit mehreren Teilen laden?"* → **Ja**.
   Alle STLs haben denselben Ursprung und liegen dadurch passgenau.
3. Im Objektbaum je Teil das Filament setzen — die Dateinamen sagen,
   welches. Der Generator gibt beim Lauf aus, welche Logofarbe zu
   welchem Filament gehört.

**Warum das sauber aufgeht:** Maßgeblich ist die **Verschachtelung über
alle Farben hinweg**, nicht die Reihenfolge der Pfade. Jede Kontur wird
ein Körper ihrer Farbe und bekommt als Löcher genau die Konturen, die
direkt in ihr liegen — gleich welcher Farbe. Damit stimmt auch der Fall,
an dem eine reine Reihenfolge-Regel scheitert: **rote Punzen mitten in
der gelben Schrift**, die wieder die Farbe der Flamme zeigen.

Bei Pixelbildern kommt dazu: echte Löcher werden **nicht** aus den
Farbmasken genommen. An einer Farbgrenze liefern zwei Masken praktisch
deckungsgleiche Konturen, die sich in der Verschachtelung gegenseitig
blockieren (die Brückentriangulierung bricht dann ab). Ein Loch ist nur
dort, wo der **Hintergrund** durchscheint — seine Kontur kommt aus der
Vordergrundmaske.

Nachgemessen an den fertigen STLs, an drei Punkten: in der Flamme
beginnt das Deckelmaterial bei z = 0,60 und der rote Körper füllt
0,00–0,60; in der Schrift dasselbe mit dem gelben, Rot ist dort nicht
vorhanden; in einer roten Punze innerhalb der Schrift wieder Rot,
kein Gelb.

- **Was an einer auto-vektorisierten SVG schiefgeht** (und jetzt
abgefangen wird):

- **Doppelte Konturen.** Der rote Pfad enthält die Buchstaben als Löcher
  (`fill-rule="evenodd"`), und derselbe Umriss steht nochmal als gelbe
  Fläche da. Beide als Loch einzubauen macht die Brücken-Triangulierung
  unlösbar. Deckungsgleiche Konturen werden über die Überdeckung ihrer
  Hüllrechtecke erkannt und zusammengefasst — Schwerpunkte taugen dafür
  nicht, zwei Trace-Varianten derselben Form liegen ein bis zwei
  Millimeter auseinander.
- **Punkte im Pixelraster.** Nach dem Skalieren liegen manche praktisch
  aufeinander; eine Kante der Länge ~0 lässt das Ear-Clipping
  steckenbleiben. `polygon_saeubern()` entfernt sie und kollineare
  Punkte.
- **Splitter.** Der Trace hinterlässt an Farbkanten Fragmente von
  1–3 mm² in Zwischentönen (`#ff9800`, `#ff4700` …). Alles unter 3 mm²
  fliegt raus.
- **Selbstüberschneidungen.** Geht eine Kontur trotzdem nicht durch,
  wird sie schrittweise per Douglas-Peucker vereinfacht, bis sie sich
  triangulieren lässt.
- **Viele Löcher in einer Fläche.** Die Flamme hat neun. Die Brücke wird
  jetzt über einen echten Sichtbarkeitstest gesucht (keine Kante kreuzen,
  Mitte im Material), und die Löcher werden von rechts nach links
  eingebaut.

Geprüft mit 300 Zufallspunkten über dem Logo: **jeder Punkt der ersten
Schicht wird von genau einem Körper gedeckt** — keine Lücke, keine
Überlappung.

**SVG ist die Quelle der Wahl:** keine Pixeltreppen, und nur dort
  stehen die Farben drin. Der Parser versteht M/L/H/V/C/S/Q/T/Z absolut
  und relativ und tastet die Béziers ab; die Füllfarbe kommt aus `fill`
  oder aus `style="fill:…"`.
- **PNG geht genauso mehrfarbig:** die dominanten Farbtöne werden
  geclustert (Marching Squares + Douglas-Peucker je Cluster), danach
  läuft dieselbe Zerlegung. Anforderungen: weißer Hintergrund, klare
  Farbflächen, ab etwa 600 px Breite.
- `LOGO_BREITE` (130 mm) und `LOGO_TIEFE` (0,6 mm) sind Parameter.
  Fehlt die Datei, bleibt der Deckel glatt und es entstehen keine
  Logoteile — alte werden dabei gelöscht.
- Ein Markenlogo gehört seinem Inhaber: fürs eigene Regal in Ordnung,
  nicht zum Verkaufen oder Weitergeben.

## Mechanik

- **Scharnier hinten: durchgehendes Klavierband.** Sieben Segmente à
  25 mm über 180 mm Breite, abwechselnd Wanne (4) und Deckel (3),
  Rautenprofil mit Tropfenbohrung. Die tragende Breite an der Wanne ist
  damit **101 mm statt 24 mm**, der Stift 5 statt 4 mm — zwei kurze Nasen
  waren die Sollbruchstelle, wenn der volle Koffer am Deckel hängt.

  **Die Achse ist ein Stück rohes Filament (1,75 mm)** — nicht gedruckt.
  Gezogenes Filament ist homogen, rund und glatt: die bessere Achse, und
  sie kostet nichts. Bohrung 2,2 mm als Tropfen (liegend gedruckt), das
  linke Außensegment hat eine **Ansenkung** (Ø4, 2,5 mm tief), das rechte
  ein **Blindende** (3 mm Restwand). Also: 179 mm ablängen, von links
  einschieben bis es am Blindende ansteht, den Überstand in der Senkung
  mit Lötkolben oder Feuerzeug zu einem kleinen Kopf verschmelzen — der
  versinkt in der Senkung, außen bleibt alles bündig.

  Tragfähig ist das, weil das Band vielfach gelagert ist: frei biegen kann
  sich die Achse nur über die 0,5 mm Segmentspalte, die Last läuft als
  **Scherung** durch die sechs Übergänge. Bei 0,85 kg sind das 1,4 N je
  Stelle auf 2,4 mm² = 0,6 MPa, im Stoßfall 2,9 MPa — PLA/PETG halten
  40–60 MPa. Wer trotzdem lieber druckt: `--gedruckter-stift` erzeugt
  die alte Variante mit 5-mm-Stiften (2 × 89 mm, flach gedruckt).

  Der Deckel wird **gespiegelt** gedruckt ((x,y,z) → (−x,y,z_top−z)).
  Ein Segment, das im Gebrauch bei x liegen soll, muss deshalb im
  Druckmodell bei −x stehen. Ohne diese Umrechnung liegen Deckel- und
  Wannensegmente übereinander statt ineinander — in der STL nicht zu
  sehen, beim Zusammenbau fatal. `scharnier_pruefen()` testet die
  Intervalle in Einbaulage auf Überlappung und den Spalt dazwischen.
- **Stufenfalz rundum:** der Deckel trägt eine umlaufende, 1,5 mm dünne
  Lippe, die 9 mm tief in eine zurückgesetzte Kante der Wanne greift.
  Außen bleibt die Fuge eine bündige Linie — innen ist der Deckel geführt,
  kann nicht seitlich verrutschen, und die Fuge ist staubdicht. Die Lippe
  ist 0,5 mm kürzer als die Stufe tief ist: der Deckel liegt auf der
  Wannenwand auf, nicht auf der Lippe. Deshalb ist die Wand hier 4 mm
  statt der sonst üblichen 2,8 mm — 2 mm bleiben an der Wanne, 1,5 mm
  bekommt die Lippe, dazwischen 0,25 mm Spiel je Flanke.
- **Verschluss vorn:** zwei federnde Schnappzungen (26 mm breit) am Deckel
  rasten mit Rautenhaken unter Keile an der Wannenfront (1,4 mm Eingriff).
  Öffnen: beide Zungen mit den Daumen leicht nach vorn ziehen.

### Umdrehen ohne dass der Deckel abfällt

Den Halt geben **Scharnier hinten + zwei Schnappzungen vorn** — beides
formschlüssig, nicht Reibung. Der Falz übernimmt die Führung: er nimmt die
Querkraft auf, sodass sich der Deckel unter Last nicht aufbiegen und aus
den Schnappern schälen kann. Zusammen hält der geschlossene Koffer
kopfüber. Falls die Schnapper nach dem Testdruck zu leicht auslösen, sind
`HAKEN` (Rasteingriff) und `ZUNGE_BREIT` Parameter.
- Der Controller liegt auf der Seite (Rad nach oben) in seiner Mulde,
  die Auto-Box daneben — Deckel auf, beides greifbar.

### Warum standardmäßig kein Tragegriff

Der Koffer ist 213 × 212 × 66 mm groß und beladen rund 0,8 kg schwer —
das ist eine Größe, die man mit einer Hand seitlich umfasst; die
verrundeten Ecken (R12) sind dafür angenehmer als jeder Bügel. Der
Griff kostet dagegen sichtbar Bauform: die beiden T-Nut-Blöcke stehen
7 mm über die Deckelseiten hinaus und machen den Koffer 18 mm tiefer,
der Bügel selbst nochmal 36 mm höher. Das widerspricht dem „von außen
sauber abgeschlossen und clean". Deshalb ist der Standard glatt.

Wer den Bügel doch will: `python3 generate.py --mit-griff` erzeugt
Nuten und Griff wie zuvor (Bügel mit T-Füßen, von unten in zwei
vertikale T-Nuten am Deckelring geschoben; die Nuten haben oben ein
Blindende, beim Tragen ziehen die Füße dagegen — Formschluss statt
Reibung, Griff nach unten abziehbar). `python3 vorschau.py --mit-griff`
rendert die passenden Ansichten.

## Drucken

- **Material:** PETG oder PLA. Bei PLA die Zungen vorsichtig behandeln
  (spröder); PETG ist für Schnapper und Federn die erste Wahl.
- **Alle Teile liegen druckfertig, keine Stützen.** Der Deckel wird mit
  der Innenseite nach oben gedruckt — die verrundete Außenkante liegt am
  Bett. Der Griff (nur mit `--mit-griff`) liegt flach.
- **Wände/Infill:** 3 Wandlinien, 10–12 % Infill. Die Füllschale der
  Konturmulde ist volumig — das niedrige Infill hält sie leicht, die
  4-mm-Außenwände bleiben trotzdem praktisch massiv.
- **Schichthöhe:** 0,2 mm. Materialbedarf gesamt grob 400–450 g
  (mit Griff rund 30 g mehr).
- **Der Falz ist die einzige Passung, die beim Druck sitzen muss.** Wenn
  dein Drucker breit extrudiert, kann die Lippe stramm gehen: dann
  `FALZ_SP` auf 0,35 setzen und den Deckel neu erzeugen.

## Zusammenbau

1. Deckel hinten an die Wanne halten, die Bandsegmente ineinander
   schieben, 179 mm Filament von links durchschieben bis es am Blindende
   ansteht, Überstand in der Senkung zum Kopf verschmelzen.
2. Controller **mit dem Drehrad nach oben** in die Mulde drücken (Rippen
   geben nach), Auto-Box ins kleine Fach.
3. Deckel zu — die Lippe zentriert sich in den Falz, die Zungen schnappen
   hörbar ein.

## Technik

Bewährter Baukasten der Nachbarprojekte: geschlossene, überlappende
Prismen-Schalen je STL (der Slicer vereinigt beim Slicen), jede Schale auf
Wasserdichtheit geprüft. Querliegende Bohrungen als Tropfen, querliegende
Blöcke als Rauten. Die Schnapper-Dimensionierung ist auf ≤4 % Randdehnung
beim Schnappen ausgelegt (Zunge 1,4 mm, Hub 1,4 mm).

Ein Fach kann fehlerfrei modelliert und trotzdem massiv zugefüllt sein,
wenn eine andere Schale darüber liegt — genau das passierte beim ersten
Hot-Wheels-Fach: der Rahmen stand da, aber die Füllschale der
Konturmulde füllte das Innere bis oben. In der STL sieht das völlig
unauffällig aus. Deshalb prüft `hw_hohlraum_pruefen()` mit senkrechten
Strahlen durch jedes Fach, ob dort wirklich Luft ist, und meldet jede
Fläche oberhalb des Bodens.

Die Wanne ist innen in zwei Zonen geteilt: unten die **Muldenzone** (30 mm,
dort sitzen Füllschale, Trennwand, Blöcke und Rippen), darüber die
**Falzzone** (9 mm), die vollständig frei bleiben muss. Ein Innenteil, das
dort hineinragt, würde das Schließen verhindern, ohne dass man es der STL
ansieht — deshalb prüft `falzzone_pruefen()` jedes Dreieck der Wanne gegen
den Lippenquerschnitt. Der Test arbeitet über z-Intervalle statt über
Eckpunkte, weil ein durchquerendes Prisma in der Zone gar keinen Eckpunkt
hat und einem Punkttest entginge.

Ansichten: `stl/ansicht_draufsicht.svg` (maßstäbliche Belegung von oben —
zeigt, was den Platz wirklich belegt), `stl/ansicht_koffer_zu.svg`,
`stl/ansicht_wanne_offen.svg` (mit Attrappen), `stl/ansicht_wanne_leer.svg`,
`stl/ansicht_deckel_innen.svg`, `stl/ansicht_falz_schnitt.svg`
(maßstäblicher Schnitt durch die Fuge), `stl/ansicht_schnitt.svg`
(waagerechter Materialschnitt aus der fertigen Geometrie — grau ist
Material, weiß ist Luft), `stl/ansicht_controller_lage.svg` (wie der
Controller in der Mulde liegt, mit Höhenschnitt),
`stl/ansicht_scharnier.svg` (Band von hinten).
