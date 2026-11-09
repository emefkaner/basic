# Bett räumen — Werkzeugkopf schiebt die Teile nach vorne

Nach dem Druck kühlt die Maschine ab und fährt dann in Bahnen flach über
die Platte, von hinten nach vorne. Kleine Teile rutschen dabei über die
Vorderkante.

**Das ist kein Bambu-Feature.** Es gibt nichts Offizielles dafür. Was
hier steht, ist der in der Community übliche Weg, nachgebaut für die
H2S, aber auf **meiner** Seite ungetestet — in dieser Umgebung steht kein
Drucker. Die Maße der H2S stammen aus Herstellerangaben (340 × 320 ×
340 mm), nicht aus einer Messung an deinem Gerät.

## Wann es funktioniert und wann nicht

| | |
|---|---|
| **Geht gut** | kleine Teile, kompakte Grundfläche, glatte Unterseite |
| **Geht nicht** | große flache Teile. Deine Wanne mit 191 × 226 mm oder das Türschild mit 221 × 240 mm haftet stärker, als die Düse schieben kann. Dann überspringt der Riemen Zähne und die Maschine verliert ihre Position. |
| **Pflicht** | kalte Platte. Warmes PEI hält fest, kaltes lässt los. |
| **Pflicht** | offene Tür. Die H2S ist geschlossen; sonst sammeln sich die Teile an der Vorderkante, statt herauszufallen. |

Geschoben wird mit der **Düsenspitze**. Die ist dafür nicht gebaut. Wer
das dauernd macht, hängt besser einen gedruckten Schieber an den
Werkzeugkopf; auf Printables gibt es fertige für die Bambu-Köpfe.

## Dateien

    python3 generate.py

schreibt zwei Schnipsel nach `gcode/`:

| Datei | Zweck |
|---|---|
| `bett_raeumen_trockenlauf.gcode` | dieselben Wege in 40 mm Höhe, berührt nichts |
| `bett_raeumen_h2s.gcode` | der scharfe Lauf: abkühlen, dann schieben |

Parameter: `--bahnen 25` (Abstand der Schiebebahnen), `--y-vorne 2`
(vorderster Punkt), `--y-hinten 300` (hinterster Punkt). Der Generator
bricht ab, wenn eine Bahn aus dem Bauraum läuft.

## Vor dem ersten Lauf: die eigenen Grenzen ablesen

Zwei Zahlen entscheiden, ob es kracht. Beide stehen nicht im Datenblatt,
sondern an deinem Gerät.

1. Drucker einschalten, Platte **leer**, Tür **auf**.
2. Am Display den Werkzeugkopf von Hand nach ganz **vorne** fahren.
3. Ablesen, welcher Y-Wert dort steht, und ob der Kopf dabei irgendwo
   anstößt. Das ist dein `--y-vorne`, plus 2 mm Sicherheit.
4. Dasselbe nach ganz **hinten**. Achte auf die Reinigungsstation und
   die Abwurföffnung — da darf die Bahn nicht hineinfahren. Das ist dein
   `--y-hinten`, minus 10 mm.
5. Kommen andere Zahlen heraus als 2 und 300, den Generator damit neu
   laufen lassen.

## Einbauen in Bambu Studio

1. Bambu Studio öffnen, oben rechts den Schalter **Advanced** (bzw.
   **Erweitert**) einschalten — ohne ihn fehlt der ganze Abschnitt.
2. Links auf den Reiter **Printer** (Drucker), dann auf
   **Machine G-code** (Maschinen-G-Code).
3. Das Feld **Machine end G-code** (G-Code am Ende) aufklappen.
4. Den vorhandenen Text **nicht löschen**. Erst eine Sicherung machen:
   alles markieren, kopieren, in eine Textdatei sichern.
5. Den Inhalt der gewünschten Datei **ganz unten anhängen**.
6. Neben dem Profilnamen auf die Diskette klicken und als **eigenes
   Profil speichern**, etwa `H2S Bett raeumen`. Nie das Bambu-Profil
   überschreiben: Updates setzen es zurück.

Erfolg erkennst du daran, dass der Profilname jetzt deiner ist und in
der Liste unter **User presets** steht.

## Testablauf, in dieser Reihenfolge

1. **Trockenlauf.** `bett_raeumen_trockenlauf.gcode` einbauen, ein
   winziges Testteil drucken (ein 20-mm-Würfel reicht), Tür auf,
   zuschauen. Der Kopf fährt in 40 mm Höhe alle Bahnen ab. Stößt er
   irgendwo an, abbrechen und die Grenzen korrigieren.
2. **Scharf, mit einem kleinen Teil.** Den scharfen Schnipsel einbauen,
   denselben Würfel drucken, Tür auf, Hand am Not-Halt. Vorne einen
   Karton hinstellen.
3. **Hören.** Knirscht oder knallt es, sofort abbrechen: dann haftet das
   Teil noch, die Platte war zu warm oder die Höhe zu groß.
4. Nach einem Lauf, bei dem es geknirscht hat, die Maschine **von Hand
   referenzieren**, bevor der nächste Druck startet. Sonst druckt sie
   versetzt.

## Was im G-Code passiert

| Abschnitt | Zweck |
|---|---|
| `M104 S0`, `M140 S0` | Düse und Bett aus. Eine heiße Düse schmilzt sich in das Teil, statt es zu schieben. |
| `M106 P2 S255`, `P3 S255` | Hilfs- und Kammerlüfter voll, damit die Platte schneller unter 35 °C kommt. |
| `M190 R35` | warten, bis das Bett 35 °C hat. |
| `M17` | Motoren halten lassen, falls das Bambu-Ende sie schon stromlos gemacht hat. |
| Bahnen | je Höhe einmal über alle x-Bahnen: hoch, nach hinten, auf Schiebehöhe, nach vorne. |

**Eine Zeile zum Nachprüfen:** Ob die Maschine `M190 R35` beim
*Abkühlen* wirklich abwartet, konnte ich von hier nicht testen. Fährt
sie sofort weiter los, ist die Wartezeit wirkungslos — dann die Zeile
löschen und stattdessen hart warten, etwa `G4 S420` für sieben Minuten.
Das erkennst du beim ersten Lauf daran, ob zwischen Druckende und
Schieben eine Pause liegt.

## Quellen

- [Infinity Flow 3D: Auto Bed Clearing, Beispiel P1S](https://infinityflow3d.com/blogs/3d-printer-automation/3d-printer-auto-bed-clearing-bambu-p1s-example)
  — Vorlage für den Aufbau mit mehreren Höhen.
- [Bambu-Forum: Project to automatically remove parts from build plate](https://forum.bambulab.com/t/project-to-automatically-remove-parts-from-build-plate/17231)
  — Erfahrungen, auch die schlechten.
- [Bambu-Forum: Custom G-code](https://forum.bambulab.com/t/custom-g-code/10446)
  — wo der Abschnitt in Bambu Studio liegt.
- [Bambu-Forum: Auto eject/repeat print concept](https://forum.bambulab.com/t/auto-eject-repeat-print-concept/72761)
- [Fabbaloo über 3DQue](https://www.fabbaloo.com/news/3dques-auto-eject-feature-now-available-for-bambu-lab-equipment)
  — kommerzielle Lösung, kühlt ebenfalls erst ab.

Alle Fundstellen betreffen P1P, P1S, X1C und A1. Zur H2D oder H2S habe
ich nichts gefunden.
