; ====================================================================
; TROCKENLAUF -- beruehrt nichts, nur zum Zuschauen
; erzeugt von 3D_GNRTR/bett-raeumen/generate.py
; Bauraum angenommen: 340 x 320 mm
; ====================================================================

; Faehrt alle Bahnen in 40 mm Hoehe ab. Damit pruefen, ob der
; Kopf ueberall hinkommt, bevor es ernst wird.

; ---- 2. schieben: je Hoehe einmal ueber alle Bahnen ----
M17                      ; Motoren halten lassen
G90                      ; absolute Koordinaten
M83                      ; Extruder relativ (nichts wird extrudiert)

; --- Durchgang auf 40.0 mm ---
G1 Z40.0 F3000
G1 X20.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X45.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X70.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X95.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X120.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X145.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X170.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X195.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X220.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X245.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X270.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X295.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z40.0 F3000
G1 X320.0 Y300.0 F12000
G1 Z40.0 F3000
G1 Y2.0 F1500          ; schieben

G1 Z40.0 F3000
M400
M106 P2 S0               ; Luefter aus
M106 P3 S0

; Nach einem Lauf, bei dem es geknirscht hat: die Maschine hat
; vermutlich Schritte verloren. Dann von Hand referenzieren,
; bevor der naechste Druck startet.
