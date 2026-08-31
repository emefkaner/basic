# Transportkoffer — Hot Wheels RC 1:64 Lamborghini Temerario

Kompakter Klappkoffer für das RC-Auto **in seiner Originalbox** plus den
Pistolengriff-Controller. Außen **213 × 212 × 66 mm** (plus Griffbügel),
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
die **gemessenen** Werte kalibriert: 190 lang × 131 breit, Gehäuse 42 dick,
mit Drehrad 57, Rad ⌀45 mm (Ränder 77/10 mm in der Breitenachse). Die Sicherung ist dreifach:

- **Konturmulde** (30 mm tief): die Fachfüllung hat ein pistolenförmiges
  Loch mit 4 mm Luft — der Controller kann weder verrutschen noch
  rotieren, genau wie im Original-Tray.
- **8 Klemmrippen** entlang der Kontur (Schnauze, Rad, Rücken, Griff):
  1,1 mm dünn, federnd, mit Anlauffase — sie nehmen die Resttoleranz der
  Foto-Kontur von ±3–4 mm auf.
- **Federbögen im Deckel**, gezielt über Schnauze, Griffende und Auto-Box —
  **nicht** über dem Drehrad: drücken beim Schließen von oben nach, ohne
  das Rad zu klemmen. Der Hub wird je Stelle aus der Einbauhöhe gerechnet.

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

## Mechanik

- **Scharnier hinten:** Rautenaugen mit Tropfenbohrung an Wanne und Deckel
  (verzahnt versetzt), zwei Achsstifte von außen einstecken — Presssitz im
  Deckelauge, Drehsitz im Wannenauge.
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
  4-mm-Außenwände bleiben trotzdem praktisch massiv.
- **Schichthöhe:** 0,2 mm. Materialbedarf gesamt grob 430–490 g.
- **Der Falz ist die einzige Passung, die beim Druck sitzen muss.** Wenn
  dein Drucker breit extrudiert, kann die Lippe stramm gehen: dann
  `FALZ_SP` auf 0,35 setzen und den Deckel neu erzeugen.

## Zusammenbau

1. Deckel hinten an die Wanne halten, Augen fluchten lassen, beide
   Achsstifte von außen durchstecken und eindrücken.
2. Griff von unten in die T-Nuten des Deckels schieben.
3. Controller **mit dem Drehrad nach oben** in die Mulde drücken (Rippen
   geben nach), Auto-Box ins kleine Fach.
4. Deckel zu — die Lippe zentriert sich in den Falz, die Zungen schnappen
   hörbar ein.

## Technik

Bewährter Baukasten der Nachbarprojekte: geschlossene, überlappende
Prismen-Schalen je STL (der Slicer vereinigt beim Slicen), jede Schale auf
Wasserdichtheit geprüft. Querliegende Bohrungen als Tropfen, querliegende
Blöcke als Rauten. Die Schnapper-Dimensionierung ist auf ≤4 % Randdehnung
beim Schnappen ausgelegt (Zunge 1,4 mm, Hub 1,4 mm).

Die Wanne ist innen in zwei Zonen geteilt: unten die **Muldenzone** (30 mm,
dort sitzen Füllschale, Trennwand, Blöcke und Rippen), darüber die
**Falzzone** (9 mm), die vollständig frei bleiben muss. Ein Innenteil, das
dort hineinragt, würde das Schließen verhindern, ohne dass man es der STL
ansieht — deshalb prüft `falzzone_pruefen()` jedes Dreieck der Wanne gegen
den Lippenquerschnitt. Der Test arbeitet über z-Intervalle statt über
Eckpunkte, weil ein durchquerendes Prisma in der Zone gar keinen Eckpunkt
hat und einem Punkttest entginge.

Ansichten: `stl/ansicht_koffer_zu.svg`, `stl/ansicht_wanne_offen.svg`
(mit Attrappen), `stl/ansicht_wanne_leer.svg`, `stl/ansicht_deckel_innen.svg`,
`stl/ansicht_falz_schnitt.svg` (maßstäblicher Schnitt durch die Fuge).
