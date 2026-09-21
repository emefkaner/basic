# GKV-vs-PKV-Rechner — Nachbau

Nachbau des Rechners von `krankenversicherungsportal24.de/rechner`
(Stand 21.09.2026) als **eine eigenständige HTML-Datei** ohne Bauschritt:
`index.html` im Browser öffnen, fertig.

## Was das Original ist

Eine React/Vite-Einzelseiten-App mit Tailwind, shadcn/ui (Radix), Framer Motion
und React Router. Alles steckt in zwei Dateien:

| Datei | Größe |
|---|---|
| `/assets/index-BEtfWKaN.js` | 723 KB |
| `/assets/index-AmqVn65-.css` | 84 KB |

Eine Quellkarte gibt es nicht. Die Analyse lief deshalb über das minifizierte
Bündel (Komponente `VO`) plus Rendern im kopflosen Chromium.

## Die Rechnung — aus dem Bündel gelesen, nicht geraten

Die GKV-Seite rechnet mit den Werten der Techniker Krankenkasse für 2026:

| Größe | Wert |
|---|---|
| Beitragsbemessungsgrenze | 6.450 € / Monat |
| Allgemeiner Beitragssatz | 14,6 % |
| Zusatzbeitrag | 2,69 % |
| Pflegeversicherung | 3,6 % |
| Zuschlag für Kinderlose | + 0,6 % |

```
beitragspflichtig = min(brutto/12, 6450)
gesamtsatz        = 14,6 % + 2,69 % + 3,6 % + (kinder == 0 ? 0,6 % : 0)
```

Angestellte teilen sich alles hälftig mit dem Arbeitgeber — **außer dem
Kinderlosen-Zuschlag**, der bleibt ganz beim Arbeitnehmer. Selbstständige
zahlen den vollen Satz, der Arbeitgeberanteil ist 0.

Der PKV-Beitrag ist eine reine Schätztabelle, keine echte Tarifabfrage:

```
Grundbeitrag nach Alter
  < 25 Jahre   320 €
  25–34        380 € + (Alter − 25) ×  8
  35–44        460 € + (Alter − 35) × 12
  45–54        580 € + (Alter − 45) × 15
  ≥ 55         730 € + (Alter − 55) × 18

+ 100 € bei Brutto > 100.000 €/Jahr, sonst + 50 € bei > 70.000 €
× 1,5    wenn verheiratet UND Ehepartner familienversichert
+ 150 €  je Kind
```

Der Arbeitgeber steuert `min(pkvGesamt / 2, gkvArbeitgeberanteil)` bei —
die gesetzliche Deckelung des Zuschusses. Die Ersparnis ist die Differenz
der beiden Arbeitnehmerbeiträge, hochgerechnet auf 10, 20 und 30 Jahre
ohne Verzinsung und ohne Beitragssteigerung.

Weitere Eigenheiten, die übernommen wurden:

- **Mindesteinkommen**: Angestellte 77.400 €/Jahr (Versicherungspflichtgrenze),
  Selbstständige 60.000 €. Beim Wechsel der Tätigkeit zieht die Seite den
  Wert selbsttätig hoch.
- **Reglergrenzen**: jährlich 77.400/60.000 … 180.000 € in 1.000er-Schritten,
  monatlich 6.450/5.000 … 15.000 € in 100er-Schritten.
- **Ergebnis-Sperre**: Nach „Jetzt berechnen" sind alle Zahlen weichgezeichnet.
  Erst das Kontaktformular mit Name, E-Mail und Telefonnummer deckt sie auf —
  das ist der eigentliche Zweck der Seite (Lead-Erfassung). **Der Nachbau hat
  das nicht**: er rechnet beim Laden und zeigt alles sofort.

## Geprüft, nicht behauptet

- **Formel**: 3.960 Eingabekombinationen (Status × Brutto × Alter ×
  Familienstand × Ehepartner × Kinder) gegen den unveränderten, minifizierten
  Originalcode gerechnet — **0 Abweichungen**.
- **Beispiel zum Nachrechnen** (Standardwerte: 100.000 €/Jahr, 30 Jahre,
  angestellt, Single, kinderlos). Original und Nachbau liefern beide:

  | | |
  |---|---|
  | GKV Arbeitnehmer | 712,40 € |
  | GKV gesamt | 1.386,11 € |
  | GKV Arbeitgeber | 673,70 € |
  | PKV Arbeitnehmer | 235,00 € |
  | PKV gesamt | ~470,00 € |
  | Ersparnis / Monat | 477,40 € |
  | Ersparnis / Jahr | 5.728,83 € |
  | in 30 Jahren | 171.865 € |

- **Oberfläche**: im kopflosen Chromium durchgespielt — sofortige Anzeige beim
  Laden, Live-Neuberechnung bei jedem Regler und jeder Auswahl,
  Tätigkeitswechsel, Monats-/Jahresansicht, Ehepartner-Block,
  Bemessungsgrenzen-Umschalter, Handybreite 390 px (kein waagerechter
  Überlauf), keine Konsolenfehler.

## Datenbasis — was belegt ist und was nicht

Nachgeschlagen am 21.09.2026, jeweils an der Quelle, nicht aus dem Gedächtnis.

### Die GKV-Seite: belegt, bis auf eine Zahl

| Wert | Original | Belegt? | Quelle |
|---|---|---|---|
| Allgemeiner Beitragssatz | 14,6 % | ✅ | § 241 SGB V im Wortlaut |
| TK-Zusatzbeitrag 2026 | 2,69 % | ✅ | TK-Pressemitteilung, Verwaltungsrat vom 19.12.2025 |
| Pflegeversicherung | 3,6 % | ✅ | BMG, Glossar „Beitragszuschlag für Kinderlose" |
| Zuschlag für Kinderlose | + 0,6 % (4,2 % gesamt) | ✅ | ebenda; der Zuschlag trägt allein der Arbeitnehmer |
| Versicherungspflichtgrenze | 77.400 €/Jahr | ✅ | § 2 Abs. 1 SVBezGrV 2026 |
| **Beitragsbemessungsgrenze** | **6.450 €/Monat** | ❌ **falsch** | s. u. |

**Der Fehler:** 6.450 €/Monat (= 77.400 €/Jahr) ist die *Versicherungspflicht­grenze*
nach § 6 Abs. 6 SGB V — die Schwelle, ab der man die GKV überhaupt verlassen darf.
Die *Beitragsbemessungsgrenze* 2026 ist die Grenze nach § 6 Abs. 7 SGB V und liegt
bei **69.750 €/Jahr = 5.812,50 €/Monat**. Das Bundesgesundheitsministerium schreibt
es wörtlich: „Im Jahr 2026 beträgt die Beitragsbemessungsgrenze jährlich 69.750 Euro
bzw. monatlich 5.812,50 Euro." (Stand 18.02.2026)

Das Original kennt beide Zahlen — 77.400 € benutzt es als Mindesteinkommen für
Angestellte — setzt aber die falsche in die Beitragsrechnung ein.

**Auswirkung** bei den Standardwerten (100.000 €/Jahr, 30 Jahre, angestellt,
Single, kinderlos):

| | Original (6.450 €) | Amtlich (5.812,50 €) |
|---|---|---|
| GKV gesamt | 1.386,11 € | 1.249,11 € |
| GKV Arbeitnehmer | 712,40 € | 641,99 € |
| Ersparnis / Monat | 477,40 € | 406,99 € |
| in 30 Jahren | 171.865 € | 146.517 € |

Der GKV-Beitrag fällt rund **11 % zu hoch** aus, die ausgewiesene Ersparnis
dadurch **17 % zu hoch** — über 30 Jahre gut **25.000 €**. Der Fehler geht
durchgehend zugunsten der PKV, also zugunsten des Vermittlungsgeschäfts.

Der Nachbau rechnet standardmäßig weiter mit 6.450 €, damit er ein ehrliches
Spiegelbild bleibt. Im Hinweiskasten unter dem Ergebnis steht der Fehler, und
ein Umschalter rechnet auf Klick mit dem amtlichen Wert.

Kleinere Ungenauigkeit oben­drein: Die Pflegeversicherung wird hälftig geteilt
(1,8 % / 1,8 %). In **Sachsen** trägt der Arbeitnehmer 2,3 % und der Arbeitgeber
1,3 % — dort rechnen Original und Nachbau zu niedrig.

### Die PKV-Seite: nichts davon ist belegt

Die PKV-Zahlen stammen aus **keiner Datenquelle**. Es ist eine fest verdrahtete
Tabelle im Quelltext der Seite: fünf Altersstufen, dazu Aufschläge für Einkommen,
Ehepartner und Kinder. Keine Tarifdatenbank, keine Abfrage bei Versicherern,
keine Gesundheitsprüfung — obwohl die Seite mit „Zugriff auf über 40 akkreditierte
deutsche PKV-Gesellschaften" wirbt.

Die Werte sind für einen jungen, gesunden Angestellten plausibel, aber sie sind
**geschätzt, nicht ermittelt**. Was die Tabelle systematisch ausblendet:

- **Gesundheitsprüfung.** Vorerkrankungen führen zu Risikozuschlägen oder
  Ablehnung. Die Tabelle kennt nur das Alter.
- **Beitragsentwicklung.** Die 30-Jahre-Hochrechnung unterstellt auf **beiden**
  Seiten konstante Beiträge. PKV-Beiträge steigen im Alter typischerweise
  deutlich — genau das ist der Haken an der PKV, und genau das fehlt.
- **Rückkehr in die GKV** ist ab 55 praktisch ausgeschlossen. Kommt nicht vor.
- **Kinder** kosten in der PKV je 150 € extra, in der GKV sind sie beitragsfrei
  familienversichert. Das ist zwar eingerechnet, wird aber nirgends erklärt.

**Kurz:** Die GKV-Seite ist nachrechenbar und bis auf die Bemessungsgrenze
korrekt. Die PKV-Seite ist eine Hausnummer. Der Vergleich stellt damit eine
belegte Zahl einer geschätzten gegenüber und nennt die Differenz „Ihre
potenzielle Ersparnis".

### Quellen

- § 241 SGB V — <https://www.gesetze-im-internet.de/sgb_5/__241.html>
- SVBezGrV 2026, § 2 — <https://www.gesetze-im-internet.de/svbezgrv_2026/BJNR1160A0025.html>
- BMG, Beitragsbemessungsgrenze — <https://www.bundesgesundheitsministerium.de/service/begriffe-von-a-z/b/beitragsbemessungsgrenze>
- BMG, Beitragszuschlag für Kinderlose — <https://www.bundesgesundheitsministerium.de/service/begriffe-von-a-z/b/beitragszuschlag-fuer-kinderlose>
- TK, Zusatzbeitrag 2026 — <https://www.tk.de/presse/themen/gesundheitssystem/selbstverwaltung/zusatzbeitrag-2026-festgelegt-2188214>

## Keine Datenerhebung

Der Nachbau sammelt nichts. Es gibt kein Kontaktformular, kein Eingabefeld für
Name, E-Mail oder Telefon, keinen Tracker und keinen Netzwerkaufruf außer dem
Laden der Schriften. Die Rechnung läuft vollständig im Browser und die
Ergebnisse stehen sofort beim Laden da — jeder Regler rechnet live nach.

## Bewusste Abweichungen vom Original

| | Original | Nachbau | Warum |
|---|---|---|---|
| Marke, Impressum, Datenschutz, Erstinformation | echte Firma | neutral, keine Firmendaten | Kein Nachbau einer fremden Firmenidentität. |
| Meta Pixel, CRM-Anbindung | vorhanden | entfernt | Kein Tracking, keine Datenweitergabe. |
| Zahlenformat | `477.40 €` (englisch) | `477,40 €` | Auf einer deutschen Seite ein Fehler. |
| Negative Ersparnis | „Ihre potenzielle Ersparnis: -107.60 €", Balken kaputt | Überschrift wechselt zu „Mehrbelastung", Balken bleiben heil | Bei 5 Kindern + familienversichertem Ehepartner ist die PKV teurer — das tritt wirklich ein. |
| Dunkler Modus | nur im CSS angelegt, nie erreichbar | folgt der Systemeinstellung | — |
| Technik | React + Vite, 800 KB | eine HTML-Datei, 38 KB | Kein Bauschritt, kein Abhängigkeitsbaum. |
| Ergebnis-Sperre | Zahlen weichgezeichnet bis zur Abgabe von Name, E-Mail und Telefon | **ganz entfernt** — rechnet beim Laden, zeigt alles sofort, rechnet live nach | Ein Rechner, der erst die Kontaktdaten will, ist kein Rechner, sondern ein Formular. |
| Beitragsbemessungsgrenze | 6.450 € ohne Hinweis | 6.450 € **mit** Hinweis und Umschalter auf 5.812,50 € | Der Wert ist falsch (s. o.); ihn stillschweigend zu übernehmen wäre ein Defekt. |

## Was der Nachbau ausdrücklich **nicht** ist

Eine Versicherungsberatung. Die PKV-Zahlen sind eine Schätztabelle aus dem
Original; echte Beiträge hängen von Gesundheitsprüfung und Tarif ab. Die
Hochrechnung auf 30 Jahre unterstellt einen über drei Jahrzehnte konstanten
Beitrag — das trifft weder für die GKV noch für die PKV zu.
