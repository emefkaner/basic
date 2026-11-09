#!/usr/bin/env python3
"""Bett raeumen: G-Code, der den Werkzeugkopf flach ueber die Platte
schiebt und die fertigen Teile nach vorne vom Bett wirft.

    python3 generate.py                 # beide Dateien
    python3 generate.py --bahnen 25     # engere Bahnen
    python3 generate.py --y-vorne 5     # weniger weit nach vorne

Erzeugt zwei Dateien in gcode/:

  bett_raeumen_trockenlauf.gcode -- dieselben Wege, aber in 40 mm Hoehe.
      Beruehrt nichts. Damit ZUERST schauen, ob der Kopf ueberall
      hinkommt, ohne irgendwo anzustossen.
  bett_raeumen_h2s.gcode -- der scharfe Lauf: abkuehlen, dann in
      Bahnen von hinten nach vorne schieben.

Beides sind Schnipsel fuer den Abschnitt "Machine end G-code" in Bambu
Studio, keine fertigen Druckdateien.

WARUM DAS NICHT IMMER FUNKTIONIERT -- bitte vorher lesen:

  * Grosse, flache Teile haften zu stark. Eine Wanne mit 191 x 226 mm
    Grundflaeche schiebt keine Duese weg; stattdessen ueberspringt der
    Riemen Zaehne und die Maschine verliert ihre Position. Das hier ist
    fuer kleine Teile gedacht.
  * Die Platte muss kalt sein. Warmes PEI haelt fest, kaltes laesst los.
    Deshalb kuehlt der Lauf erst ab und wartet.
  * Geschoben wird mit der Duesenspitze. Sie ist kein Werkzeug dafuer.
    Wer das oft macht, haengt besser einen gedruckten Schieber an den
    Werkzeugkopf (es gibt fertige auf Printables).
  * Die H2S ist geschlossen. Ohne offene Tuer faellt nichts heraus,
    sondern sammelt sich an der Vorderkante.

Masse der H2S sind Parameter, keine Gewissheit: die Quellen nennen
340 x 320 x 340 mm Bauraum. Vor dem ersten scharfen Lauf die wirklich
anfahrbaren Grenzen am Geraet selbst ablesen (siehe README).
"""

import argparse
import os

HIER = os.path.dirname(os.path.abspath(__file__))

# Bauraum H2S laut Herstellerangaben -- nachmessen, nicht glauben
BETT_X = 340.0
BETT_Y = 320.0

# Wo die Bahnen anfangen und aufhoeren. Hinten bleibt Abstand zur
# Reinigungsstation und zur Abwurfoeffnung, vorne zum Rahmen.
Y_HINTEN = 300.0
Y_VORNE = 2.0
X_LINKS = 20.0
X_RECHTS = 320.0
BAHN_ABSTAND = 25.0        # Abstand der Schiebebahnen in x

# Schiebehoehen ueber der Platte. Zuerst flach -- da rutscht ein Teil,
# statt zu kippen. Danach hoeher fuer alles, was die Duese sonst
# untergraebt.
HOEHEN = (0.8, 3.0, 8.0)

V_SCHIEBEN = 1500          # mm/min, bewusst langsam
V_FAHRT = 12000            # mm/min, Leerfahrten
Z_FREI = 60.0              # Hoehe fuer Leerfahrten nach hinten
Z_TROCKEN = 40.0           # Hoehe fuer den Trockenlauf

BETT_AUS_BEI = 35.0        # Grad, darunter laesst PEI los
NACHWARTEN = 60            # Sekunden Sicherheitszuschlag


def bahnen():
    xs, x = [], X_LINKS
    while x <= X_RECHTS + 1e-9:
        xs.append(round(x, 1))
        x += BAHN_ABSTAND
    return xs


def kopf(titel):
    return [
        "; " + "=" * 68,
        "; " + titel,
        "; erzeugt von 3D_GNRTR/bett-raeumen/generate.py",
        "; Bauraum angenommen: %.0f x %.0f mm" % (BETT_X, BETT_Y),
        "; " + "=" * 68,
        "",
    ]


def abkuehlen():
    """Heizungen aus, Luefter an, warten bis die Platte loslaesst."""
    return [
        "; ---- 1. abkuehlen, sonst haftet alles fest ----",
        "M400                     ; laufende Bewegungen abwarten",
        "M104 S0                  ; Hotend aus (heisse Duese schmilzt sich ins Teil)",
        "M140 S0                  ; Heizbett aus",
        "M106 P1 S0               ; Bauteilluefter aus",
        "M106 P2 S255             ; Hilfsluefter voll",
        "M106 P3 S255             ; Kammerluefter voll",
        "M190 R%.0f                ; warten, bis das Bett %.0f C hat"
        % (BETT_AUS_BEI, BETT_AUS_BEI),
        "G4 S%d                  ; Sicherheitszuschlag" % NACHWARTEN,
        "",
        "; Falls die Maschine M190 R beim ABKUEHLEN nicht abwartet (sie faehrt",
        "; dann sofort weiter los), die Zeile loeschen und stattdessen hart",
        "; warten, z.B. G4 S420 fuer sieben Minuten.",
        "",
    ]


def schieben(hoehen, z_frei, mit_motoren=True):
    """Bahnen von hinten nach vorne, je Hoehe ein Durchgang."""
    aus = ["; ---- 2. schieben: je Hoehe einmal ueber alle Bahnen ----"]
    if mit_motoren:
        aus.append("M17                      ; Motoren halten lassen")
    aus += [
        "G90                      ; absolute Koordinaten",
        "M83                      ; Extruder relativ (nichts wird extrudiert)",
        "",
    ]
    for h in hoehen:
        aus.append("; --- Durchgang auf %.1f mm ---" % h)
        for x in bahnen():
            aus += [
                "G1 Z%.1f F3000" % z_frei,
                "G1 X%.1f Y%.1f F%d" % (x, Y_HINTEN, V_FAHRT),
                "G1 Z%.1f F3000" % h,
                "G1 Y%.1f F%d          ; schieben" % (Y_VORNE, V_SCHIEBEN),
            ]
        aus.append("")
    aus += [
        "G1 Z%.1f F3000" % z_frei,
        "M400",
        "M106 P2 S0               ; Luefter aus",
        "M106 P3 S0",
        "",
        "; Nach einem Lauf, bei dem es geknirscht hat: die Maschine hat",
        "; vermutlich Schritte verloren. Dann von Hand referenzieren,",
        "; bevor der naechste Druck startet.",
    ]
    return aus


def grenzen_pruefen():
    """Keine Bahn darf aus dem Bauraum laufen -- ein Tippfehler im
    Parameter waere sonst ein Crash gegen den Rahmen."""
    fehler = []
    for x in bahnen():
        if not 0.0 <= x <= BETT_X:
            fehler.append("Bahn x=%.1f liegt ausserhalb 0..%.0f" % (x, BETT_X))
    for y, name in ((Y_VORNE, "Y_VORNE"), (Y_HINTEN, "Y_HINTEN")):
        if not 0.0 <= y <= BETT_Y:
            fehler.append("%s=%.1f liegt ausserhalb 0..%.0f" % (name, y, BETT_Y))
    if Y_HINTEN <= Y_VORNE:
        fehler.append("Y_HINTEN muss groesser als Y_VORNE sein")
    return fehler


def schreiben(name, zeilen):
    ziel = os.path.join(HIER, "gcode")
    os.makedirs(ziel, exist_ok=True)
    pfad = os.path.join(ziel, name)
    with open(pfad, "w") as f:
        f.write("\n".join(zeilen) + "\n")
    return pfad, len(zeilen)


def main():
    global BAHN_ABSTAND, Y_VORNE, Y_HINTEN
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bahnen", type=float, default=BAHN_ABSTAND,
                    help="Abstand der Schiebebahnen in mm (Standard: %(default)s)")
    ap.add_argument("--y-vorne", type=float, default=Y_VORNE,
                    help="vorderster Punkt der Schiebebahn (Standard: %(default)s)")
    ap.add_argument("--y-hinten", type=float, default=Y_HINTEN,
                    help="hinterster Punkt der Schiebebahn (Standard: %(default)s)")
    a = ap.parse_args()
    BAHN_ABSTAND, Y_VORNE, Y_HINTEN = a.bahnen, a.y_vorne, a.y_hinten

    fehler = grenzen_pruefen()
    if fehler:
        raise SystemExit("FEHLER Bauraum: " + "; ".join(fehler))

    trocken = (kopf("TROCKENLAUF -- beruehrt nichts, nur zum Zuschauen")
               + ["; Faehrt alle Bahnen in %.0f mm Hoehe ab. Damit pruefen, ob der"
                  % Z_TROCKEN,
                  "; Kopf ueberall hinkommt, bevor es ernst wird.", ""]
               + schieben((Z_TROCKEN,), Z_TROCKEN))
    scharf = (kopf("BETT RAEUMEN -- schiebt die Teile nach vorne vom Bett")
              + abkuehlen() + schieben(HOEHEN, Z_FREI))

    p1, n1 = schreiben("bett_raeumen_trockenlauf.gcode", trocken)
    p2, n2 = schreiben("bett_raeumen_h2s.gcode", scharf)

    anz = len(bahnen())
    weg = anz * len(HOEHEN) * (Y_HINTEN - Y_VORNE)
    print("Bahnen: %d (x %.0f bis %.0f, Abstand %.0f mm)"
          % (anz, X_LINKS, X_RECHTS, BAHN_ABSTAND))
    print("Hoehen: %s mm" % ", ".join("%.1f" % h for h in HOEHEN))
    print("Schiebeweg gesamt: %.1f m bei %.0f mm/s -> rund %.0f Minuten "
          "(ohne Abkuehlen)" % (weg / 1000.0, V_SCHIEBEN / 60.0,
                                weg / V_SCHIEBEN + anz * len(HOEHEN) * 0.1))
    print("%-42s %4d Zeilen" % (os.path.basename(p1), n1))
    print("%-42s %4d Zeilen" % (os.path.basename(p2), n2))
    print("\nERST den Trockenlauf, bei offener Tuer, mit der Hand am "
          "Not-Halt. Siehe README.md.")


if __name__ == "__main__":
    main()
