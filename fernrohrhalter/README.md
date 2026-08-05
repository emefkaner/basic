# Fernrohrhalter fürs Kinderhaus

Schwenk- und neigbarer Halter für ein Kinderfernrohr, zum Anschrauben auf ein
Brett (Verandabrüstung). Das Fernrohr bleibt in jeder Stellung von selbst
stehen, weil es an seinem Schwerpunkt gelagert wird.

## Aufbau

| Teil | Datei | Drucken |
|---|---|---|
| 1 Grundplatte mit Pfosten | `fernrohrhalter_1_grundplatte_1x_drucken.stl` | 1 × |
| 2 Drehgabel | `fernrohrhalter_2_drehgabel_1x_drucken.stl` | 1 × |
| 3 Rohrschelle | `fernrohrhalter_3_rohrschelle_1x_drucken.stl` | 1 × |
| 4 Achsstift | `fernrohrhalter_4_achsstift_2x_drucken.stl` | **2 ×** |

- Die **Grundplatte** (110 × 110 × 8 mm) wird mit 4 Holzschrauben (4–4,5 mm,
  mit Unterlegscheibe) aufs Brett geschraubt. Die Schraubschlitze sind zum
  Rand hin offen — die Platte lässt sich bei nur gelösten Schrauben abnehmen.
  In der Mitte steht ein Pfosten (Ø 25 mm) nach oben.
- Die **Drehgabel** wird von oben über den Pfosten gestülpt und dreht sich
  frei — das ist das Schwenken links/rechts. Gravitation hält sie, zum
  Abbauen einfach abheben.
- Die **Rohrschelle** wird aufs Fernrohr geschnappt (C-Öffnung 100°) und
  zwischen die Gabelarme gesetzt. Seitlich trägt sie zwei rautenförmige
  Lagerböcke.
- Die **Achsstifte** werden von außen durch die Gabelarme gesteckt und in
  die Lagerböcke gepresst. Die Bohrung im Arm ist der Drehsitz — das ist
  das Neigen hoch/runter.

## Fürs ausfahrbare Piraten-Spyglass

Das Fernrohr ist das Print-in-Place-Spyglass von MakerWorld (Modell
2856680). Zwei Eigenheiten sind eingeplant:

- **Es ist ausfahrbar**, der Schwerpunkt wandert also beim Ausziehen. Reine
  Balance kann nicht beide Zustände halten — deshalb hat die Armbohrung
  bewusst nur 0,1 mm Spiel zum Achsstift (leichte Reibung). Balance auf
  **halb ausgezogen** einstellen, die Reibung fängt den Rest ab.
- **Es soll oft raus und rein** (mitnehmen, Pirat spielen). Die C-Öffnung
  ist deshalb 140° weit mit Einführlippen: Spyglass von oben in die Schelle
  drücken bis es schnappt, zum Entnehmen einfach herausziehen. Die Schelle
  selbst bleibt fest im Halter. Geklemmt wird am **dicksten Rohrsegment**.

## Balance einstellen

1. Spyglass **halb ausziehen** und quer auf einen Stift oder Besenstiel
   legen; verschieben, bis es waagerecht balanciert. Stelle markieren.
2. Diese Stelle gehört in die Mitte der Schelle.
3. Reibung testen: eingefahren und ausgefahren soll es die Neigung halten,
   sich aber mit einem Finger bewegen lassen. Zu stramm → Achsstift mit
   feinem Schleifpapier dünner schleifen; zu locker → einen Streifen
   Klebeband um den Stift.

## Maß nehmen und generieren

Der einzige kritische Wert ist der **Durchmesser des dicksten
Rohrsegments**. Am einfachsten: das Spyglass in Bambu Studio öffnen und
das dickste Segment messen (Messwerkzeug), oder am fertigen Druck mit dem
Messschieber. Notfalls Schnur herumwickeln, Umfang durch 3,14 teilen.

```bash
python3 generate.py --rohr 50      # Durchmesser in mm einsetzen
python3 vorschau.py                # Ansichten neu erzeugen
```

Standard ist 50 mm. Alle Folgemaße (Schelle, Gabelweite, Lagerhöhe,
Stiftlänge) rechnen sich automatisch daraus.

## Drucken

- **Material:** PETG (steht draußen an der Veranda — PLA erweicht in der
  Sommersonne und wird spröde).
- **Alle Teile liegen druckfertig orientiert, keine Stützen nötig.** Die
  Lagerböcke sind Rauten (45°-Flächen tragen sich selbst), die liegenden
  Bohrungen darin sind Tropfen mit Spitze nach oben.
- **Wände/Infill:** 4 Wandlinien, 25 % Infill — die Gabelarme und der
  Pfosten tragen das Fernrohr plus Kinderhände.
- **Achsstifte:** stehend drucken (so liegen sie in der Datei), mit Brim.
- Materialbedarf gesamt: grob 130–160 g.

## Zusammenbau

1. Grundplatte aufs Brett schrauben (4 Schrauben + Unterlegscheiben).
2. Drehgabel über den Pfosten stülpen.
3. Schelle am Schwerpunkt aufs Fernrohr schnappen (siehe oben).
4. Fernrohr mit Schelle zwischen die Gabelarme halten, Achsstifte von
   außen durch die Arme stecken und in die Lagerböcke drücken (Presssitz —
   fest drücken oder mit dem Handballen klopfen).
5. Neigung testen: das Rohr soll sich leicht bewegen lassen und stehen
   bleiben. Zu stramm → Stift minimal herausziehen; zu locker → Schelle
   näher an den Schwerpunkt.

Das Fernrohr lässt sich samt Gabel jederzeit vom Pfosten heben und mit
hineinnehmen — an der Veranda bleibt nur die flache Platte.

## Technik

Gleiche Mesh-Technik wie beim Schutzring-Projekt (reines Python, keine
Abhängigkeiten): jedes Teil besteht aus mehreren geschlossenen, sich
überlappenden Prismen in einer STL-Datei; der Slicer vereinigt sie beim
Slicen. Jede Schale wird auf Wasserdichtheit geprüft (jede Kante genau
zweimal). Bohrungen liegen in Extrusionsrichtung; quer liegende Bohrungen
sind Tropfenprofile, quer liegende Zapfenblöcke Rautenprofile — beides
druckt ohne Stützen.

Ansichten: `stl/ansicht_baugruppe.svg` (zusammengebaut, mit Fernrohr-
Attrappe) und `stl/ansicht_teile.svg` (alle Teile in Drucklage).
