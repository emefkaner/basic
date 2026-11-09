; ====================================================================
; BETT RAEUMEN -- schiebt die Teile nach vorne vom Bett
; erzeugt von 3D_GNRTR/bett-raeumen/generate.py
; Bauraum angenommen: 340 x 320 mm
; ====================================================================

; ---- 1. abkuehlen, sonst haftet alles fest ----
M400                     ; laufende Bewegungen abwarten
M104 S0                  ; Hotend aus (heisse Duese schmilzt sich ins Teil)
M140 S0                  ; Heizbett aus
M106 P1 S0               ; Bauteilluefter aus
M106 P2 S255             ; Hilfsluefter voll
M106 P3 S255             ; Kammerluefter voll
M190 R35                ; warten, bis das Bett 35 C hat
G4 S60                  ; Sicherheitszuschlag

; Falls die Maschine M190 R beim ABKUEHLEN nicht abwartet (sie faehrt
; dann sofort weiter los), die Zeile loeschen und stattdessen hart
; warten, z.B. G4 S420 fuer sieben Minuten.

; ---- 2. schieben: je Hoehe einmal ueber alle Bahnen ----
M17                      ; Motoren halten lassen
G90                      ; absolute Koordinaten
M83                      ; Extruder relativ (nichts wird extrudiert)

; --- Durchgang auf 0.8 mm ---
G1 Z60.0 F3000
G1 X20.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X45.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X70.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X95.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X120.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X145.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X170.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X195.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X220.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X245.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X270.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X295.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X320.0 Y300.0 F12000
G1 Z0.8 F3000
G1 Y2.0 F1500          ; schieben

; --- Durchgang auf 3.0 mm ---
G1 Z60.0 F3000
G1 X20.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X45.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X70.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X95.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X120.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X145.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X170.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X195.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X220.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X245.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X270.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X295.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X320.0 Y300.0 F12000
G1 Z3.0 F3000
G1 Y2.0 F1500          ; schieben

; --- Durchgang auf 8.0 mm ---
G1 Z60.0 F3000
G1 X20.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X45.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X70.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X95.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X120.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X145.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X170.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X195.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X220.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X245.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X270.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X295.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben
G1 Z60.0 F3000
G1 X320.0 Y300.0 F12000
G1 Z8.0 F3000
G1 Y2.0 F1500          ; schieben

G1 Z60.0 F3000
M400
M106 P2 S0               ; Luefter aus
M106 P3 S0

; Nach einem Lauf, bei dem es geknirscht hat: die Maschine hat
; vermutlich Schritte verloren. Dann von Hand referenzieren,
; bevor der naechste Druck startet.
