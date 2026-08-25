# Transportkoffer — Hot Wheels RC 1:64 Lamborghini Temerario

Kompakter Klappkoffer für das RC-Auto **in seiner Originalbox** plus den
Pistolengriff-Controller. Außen **190 × 134 × 84 mm** (plus Griffbügel),
verschließbar, mit abnehmbarem Tragegriff — komplett gedruckt, keine
Schrauben, keine Metallteile.

## Teile

| Teil | Datei | Drucken |
|---|---|---|
| Wanne | `rcbox_1_wanne_1x_drucken.stl` | 1 × |
| Deckel | `rcbox_2_deckel_1x_drucken.stl` | 1 × |
| Griff | `rcbox_3_griff_1x_drucken.stl` | 1 × |
| Achsstift | `rcbox_4_achsstift_2x_drucken.stl` | **2 ×** |

## Warum nichts wackelt (trotz geschätzter Controller-Maße)

Die Originalbox ist gemessen (100 × 50 × 50). Der Controller ist eine
begründete Schätzung (liegend ~115 × 120 × 62) — die Händlerseiten mit den
exakten Maßen waren nicht abrufbar. Deshalb ist die Passung bewusst
**toleranzunempfindlich** gebaut:

- **Klemmrippen:** beide Fächer haben 1,1 mm dünne, federnde Rippen mit
  Anlauffase, die 5 mm in den Raum ragen. Sie klemmen alles fest, was bis
  zu ±4 mm vom Nennmaß abweicht.
- **Federbögen im Deckel:** vier gedruckte Blattfeder-Bögen drücken beim
  Schließen von oben auf Box und Controller — kein Klappern in der Höhe.

Wenn der Controller real anders misst: `CTRL_L/T/H` oben in `generate.py`
ändern, neu generieren, fertig. Genauso `AUTOBOX_*`.

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
- Der Controller liegt auf der Seite (Rad nach oben), die Auto-Box quer
  daneben — Deckel auf, beides greifbar.

## Drucken

- **Material:** PETG oder PLA. Bei PLA die Zungen vorsichtig behandeln
  (spröder); PETG ist für Schnapper und Federn die erste Wahl.
- **Alle Teile liegen druckfertig, keine Stützen.** Der Deckel wird mit
  der Innenseite nach oben gedruckt — die verrundete Außenkante liegt am
  Bett. Der Griff liegt flach.
- **Wände/Infill:** 3 Wandlinien, 12–15 % Infill. Die 2,8-mm-Außenwände
  werden dadurch praktisch massiv.
- **Schichthöhe:** 0,2 mm. Materialbedarf gesamt grob 320–380 g.

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

Ansichten: `stl/ansicht_koffer_zu.svg`, `stl/ansicht_wanne_offen.svg`,
`stl/ansicht_deckel_innen.svg`.
