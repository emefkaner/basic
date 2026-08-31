# Transportkoffer — Hot Wheels RC 1:64 Lamborghini Temerario

Kompakter Klappkoffer für das RC-Auto **in seiner Originalbox** plus den
Pistolengriff-Controller. Außen **211 × 210 × 72 mm** (plus Griffbügel),
verschließbar, mit abnehmbarem Tragegriff — komplett gedruckt, keine
Schrauben, keine Metallteile.

Der Controller liegt in einer **pistolenförmigen Konturmulde** nach dem
Vorbild des Original-Formfaser-Trays — nicht in einem Rechteckfach, in dem
er rotieren und schlagen könnte.

## Teile

| Teil | Datei | Drucken |
|---|---|---|
| Wanne | `rcbox_1_wanne_1x_drucken.stl` | 1 × |
| Deckel | `rcbox_2_deckel_1x_drucken.stl` | 1 × |
| Griff | `rcbox_3_griff_1x_drucken.stl` | 1 × |
| Achsstift | `rcbox_4_achsstift_2x_drucken.stl` | **2 ×** |

## Warum nichts wackelt

Die Controller-Silhouette wurde aus dem Foto des Original-Trays vermessen
(Maßstab über die bekannte 100-mm-Auto-Box, Messgitter-Overlay) und auf
die **gemessenen** Werte kalibriert: 190 lang × 131 breit × 50 dick. Die
Sicherung ist dreifach:

- **Konturmulde** (26 mm tief): die Fachfüllung hat ein pistolenförmiges
  Loch mit 4 mm Luft — der Controller kann weder verrutschen noch
  rotieren, genau wie im Original-Tray.
- **8 Klemmrippen** entlang der Kontur (Schnauze, Rad, Rücken, Griff):
  1,1 mm dünn, federnd, mit Anlauffase — sie nehmen die Resttoleranz der
  Foto-Kontur von ±3–4 mm auf.
- **Federbögen im Deckel**, gezielt über Drehrad, Griffende und Auto-Box:
  drücken beim Schließen von oben nach — kein Klappern in der Höhe.

Silhouette, Maße (`CTRL_LAENGE`, `CTRL_BREITE`, `CTRL_H`, `AUTOBOX_*`)
und Muldenluft (`MULDE_LUFT`) sind Parameter in `generate.py`.

## Mechanik

- **Scharnier hinten:** Rautenaugen mit Tropfenbohrung an Wanne und Deckel
  (verzahnt versetzt), zwei Achsstifte von außen einstecken — Presssitz im
  Deckelauge, Drehsitz im Wannenauge.
- **Verschluss vorn:** zwei federnde Schnappzungen am Deckel rasten mit
  Rautenhaken unter Keile an der Wannenfront (1,4 mm Eingriff). Öffnen:
  beide Zungen mit den Daumen leicht nach vorn ziehen, Deckel aufklappen.
- **Griff:** Bügel mit T-Füßen, wird von unten in zwei vertikale T-Nuten
  außen am Deckelring geschoben. Die Nuten haben oben ein Blindende — beim
  Tragen ziehen die Füße dagegen, die Last läuft also über Formschluss,
  nicht über Reibung. Griff abziehbar (nach unten), z. B. fürs Regal.
- Der Controller liegt auf der Seite (Rad nach oben) in seiner Mulde,
  die Auto-Box daneben — Deckel auf, beides greifbar.

## Drucken

- **Material:** PETG oder PLA. Bei PLA die Zungen vorsichtig behandeln
  (spröder); PETG ist für Schnapper und Federn die erste Wahl.
- **Alle Teile liegen druckfertig, keine Stützen.** Der Deckel wird mit
  der Innenseite nach oben gedruckt — die verrundete Außenkante liegt am
  Bett. Der Griff liegt flach.
- **Wände/Infill:** 3 Wandlinien, 10–12 % Infill. Die Füllschale der
  Konturmulde ist volumig — das niedrige Infill hält sie leicht, die
  2,8-mm-Außenwände bleiben trotzdem praktisch massiv.
- **Schichthöhe:** 0,2 mm. Materialbedarf gesamt grob 420–480 g.

## Zusammenbau

1. Deckel hinten an die Wanne halten, Augen fluchten lassen, beide
   Achsstifte von außen durchstecken und eindrücken.
2. Griff von unten in die T-Nuten des Deckels schieben.
3. Controller liegend ins große Fach drücken (Rippen geben nach), Auto-Box
   ins kleine Fach.
4. Deckel zu — die Zungen schnappen hörbar ein.

## Technik

Bewährter Baukasten der Nachbarprojekte: geschlossene, überlappende
Prismen-Schalen je STL (der Slicer vereinigt beim Slicen), jede Schale auf
Wasserdichtheit geprüft. Querliegende Bohrungen als Tropfen, querliegende
Blöcke als Rauten. Die Schnapper-Dimensionierung ist auf ≤4 % Randdehnung
beim Schnappen ausgelegt (Zunge 1,4 mm, Hub 1,4 mm).

Ansichten: `stl/ansicht_koffer_zu.svg`, `stl/ansicht_wanne_offen.svg`
(mit Attrappen), `stl/ansicht_wanne_leer.svg`, `stl/ansicht_deckel_innen.svg`.
