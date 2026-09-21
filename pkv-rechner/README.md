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
  Erst das Kontaktformular deckt sie auf — das ist der eigentliche Zweck der
  Seite (Lead-Erfassung).

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

- **Oberfläche**: im kopflosen Chromium durchgespielt — Rechnen, Sperre,
  Freischalten, Tätigkeitswechsel, Monats-/Jahresansicht, Ehepartner-Block,
  Handybreite 390 px (kein waagerechter Überlauf), keine Konsolenfehler.

## Bewusste Abweichungen vom Original

| | Original | Nachbau | Warum |
|---|---|---|---|
| Marke, Impressum, Datenschutz, Erstinformation | echte Firma | neutral, keine Firmendaten | Kein Nachbau einer fremden Firmenidentität. |
| Meta Pixel, CRM-Anbindung | vorhanden | entfernt | Kein Tracking, keine Datenweitergabe; das Formular prüft und schaltet nur lokal frei. |
| Zahlenformat | `477.40 €` (englisch) | `477,40 €` | Auf einer deutschen Seite ein Fehler. |
| Negative Ersparnis | „Ihre potenzielle Ersparnis: -107.60 €", Balken kaputt | Überschrift wechselt zu „Mehrbelastung", Balken bleiben heil | Bei 5 Kindern + familienversichertem Ehepartner ist die PKV teurer — das tritt wirklich ein. |
| Dunkler Modus | nur im CSS angelegt, nie erreichbar | folgt der Systemeinstellung | — |
| Technik | React + Vite, 800 KB | eine HTML-Datei, 45 KB | Kein Bauschritt, kein Abhängigkeitsbaum. |

## Was der Nachbau ausdrücklich **nicht** ist

Eine Versicherungsberatung. Die PKV-Zahlen sind eine Schätztabelle aus dem
Original; echte Beiträge hängen von Gesundheitsprüfung und Tarif ab. Die
Hochrechnung auf 30 Jahre unterstellt einen über drei Jahrzehnte konstanten
Beitrag — das trifft weder für die GKV noch für die PKV zu.
