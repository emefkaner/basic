# Lynkeus — Quelldateien

Hieraus werden ZWEI Single-File-Varianten derselben App gebaut (Gemini/Veo-
Funkel-Wasserzeichen aus Videos und Fotos herausrechnen, alles lokal):

- **`../lynkeus.html`** — Nachtdesign (Lila, Regenbogenband)
- **`../lynkeus-lidl.html`** — Lidl-Design (hell, Blau/Gelb/Rot; Designsprache
  aus den Projekten mconow und instorecommunications)

## Bauen

```
npm install mediabunny esbuild     # einmalig, in diesem Ordner
node bauen.mjs                     # baut IMMER beide Varianten
```

Gemeinsam sind `src/struktur.html` (Aufbau samt Logo/Wortmarke, deren Farben
über CSS-Variablen laufen) und `src/app.js`/`src/engine.js` (Logik). Je
Variante gibt es `src/thema-lynkeus.css` bzw. `src/thema-lidl.css` und ein
Favicon (`favicon.png` lila, `favicon-lidl.png` blau).

**REGEL: Jede Änderung gilt für BEIDE Varianten.** Struktur- und
Logik-Änderungen landen automatisch in beiden; bei Design-Änderungen beide
`thema-*.css` bedienen (bzw. bewusst entscheiden und dokumentieren, wenn
etwas nur eine Variante betrifft). Die App liest Suchrahmen-Farben über
`--rahmenAktiv`/`--rahmenOriginal` aus dem Theme.

## Versionierung

Aktuelle Version: **2.7** (Kommentar in `src/struktur.html` + Konstante VERSION in `bauen.mjs`; sichtbar nur im Footer des Nachtdesigns — die Lidl-Fußzeile nennt auf Wunsch stattdessen den Ersteller). Regel: **Bei jeder Änderung um 0,1 erhöhen.**
Die Nummer steht an zwei Stellen in `src/struktur.html` (Kommentar im `<head>`
und im Footer) — beide nachziehen, neu bauen, BEIDE fertigen Dateien mit
committen.

- 1.0 — Erstfassung: Video-Konverter mit Vorschau/Feinreglern, Lynkeus-Look
- 1.1 — Foto-Modus mit Umschalter, Logo (Luchsauge), Version + „Created by
  emefka" im Footer
- 1.2 — Automatische Sternsuche (Mustervergleich übers Bild, bei Videos über
  das Mittel mehrerer Einzelbilder; misst Position, Größe UND Deckkraft —
  falls Google Logo oder Position ändert); Regenbogenband dreht per Skript
  in jedem Browser
- 1.3 — Schriftzug in Cinzel Decorative (SIL OFL, als woff2-Teilmenge nur mit
  den Buchstaben des Namens eingebettet, ~1,3 KB) und in Lila; Knöpfe, Regler
  und Umschalter im selben Lilaton neu gestaltet; FEHLERBEHEBUNG: Klicks auf
  die Knöpfe gingen ins Leere, wenn die Karte per rotateX/preserve-3d gekippt
  war (Chromium-Treffer-Prüfung) — Kipp-Effekt entfernt, nie wieder einbauen
- 1.4 — Fußzeile nennt ausdrücklich die 100 % lokale Verarbeitung (belegt:
  null Netzwerkzugriffe während Laden und kompletter Umwandlung)
- 1.5 — Knöpfe neu: schlichte Lila-Outline, beim Überfahren komplett gefüllt
  mit einem wandernden Verlauf aus Lilatönen (dreht über --winkel, bewegt
  sich also nur bei sichtbarem Hover)
- 1.6 — auch der Foto/Video-Umschalter nutzt exakt diesen Knopf-Stil; nur der
  gewählte Modus bleibt als Zustandsanzeige statisch gefüllt
- 1.7 — Hover-Füllung vollflächig im Standardlila statt Verlauf (helle Töne
  machten den Text unlesbar); Favicon als PNG (`favicon.png`, aus dem
  Logo-SVG gerendert) statisch im <head> statt per Skript als SVG — bei
  Logo-Änderungen das PNG neu erzeugen
- 1.8 — neues Logo nach Entwurf des Nutzers (Auge, dessen Strahlen den
  Gemini-Stern zersplittern), von Hand als skalierbares SVG nachgebaut und
  in die Lilatöne übersetzt; liegt auch einzeln als `logo.svg` hier; Favicon
  daraus neu gerendert
- 1.9 — Original-SVG des Nutzers übernommen (ersetzt den 1.8-Nachbau):
  Bildmarke und LYNKEUS-Schriftzug per Lage getrennt (Schriftpfade liegen
  unter y≈610), alles in Standardlila (#8b5cf6) umgefärbt. Kopf + Favicon =
  Bildmarke; `logo.svg` = Komplettfassung; `logo-original.svg` = unverändertes
  Original in Schwarz
- 2.0 — Schriftzug auf Wunsch in Monoton (SIL OFL, Neon-Linien-Retro) statt
  Cinzel; `lynkeus-schrift.woff2` ist jetzt die Monoton-Teilmenge (1,2 KB),
  ausgewählt aus zehn gerenderten Vorschlägen
- 2.1 — Untertitel „GEMINI-Fighter" unter dem Schriftzug
- 2.2 — Lynkeus-Schriftzug = Original-Wortmarke aus dem Logo-SVG (Vektor,
  Lila-Verlauf); Monoton bleibt nur für den Untertitel (Teilmenge jetzt mit
  den „GEMINI-Fighter"-Buchstaben, 1,7 KB)
- 2.3 — Untertitel in leichter, weit gesperrter Systemschrift (Gewicht 300);
  keine eingebettete Schrift mehr — Monoton und die woff2-Teilmenge sind raus
- 2.4 — Projekt auf zwei Designvarianten umgebaut: gemeinsame Struktur/Logik,
  Themes thema-lynkeus.css und thema-lidl.css, Bau erzeugt immer beide
  Dateien (lynkeus.html + lynkeus-lidl.html)
- 2.5 — Lidl-Variante: umlaufendes drehendes Band um die Container in den
  drei Lidl-Farben (statt statischem Streifen oben)
- 2.6 — Lidl-Band mit HARTEN Farbkanten: nur Blau/Gelb/Rot als Segmente,
  keine Zwischenfarben (der weiche Verlauf mischte Grün/Orange/Violett)
- 2.7 — Lidl-Variante: Team-Kunde-Logo oben rechts im Kopfbalken (aus dem
  MCO-Now-Konverter, `kundelogo.png` = verkleinertes sales-kunde.png) und
  eigene Fußzeile „Lynkeus – GEMINI Fighter · Erstellt von Marc Ferdinand
  Körner – Team Kunde"; Kopf-rechts und Fußzeile sind jetzt
  Varianten-Bausteine in bauen.mjs

## Dateien

- `src/engine.js` — Mathematik: umgekehrte Alpha-Mischung, Geometrie
  (Video: Größe ≈ kurze Seite/15, Abstand ≈ kurze Seite/10, Standard-Feintuning
  Stärke 0,6 / Versatz −kurzeSeite/30; Foto: exakt 96 px Stern/64 px Rand über
  1024×1024, sonst 48/32, Stärke 1). Übernommen aus
  [dearabhin/gemini-watermark-remover](https://github.com/dearabhin/gemini-watermark-remover) (MIT).
- `src/app.js` — Oberfläche und Video-Pipeline (mediabunny/WebCodecs:
  dekodieren → Sternbereich säubern → H.264/MP4 kodieren, Ausweg VP9/WebM;
  Tonspur wird unverändert durchgereicht).
- `src/struktur.html` — gemeinsamer Aufbau inkl. Logo/Wortmarke (Farben über
  CSS-Variablen `--logoMarke`, `--wm1..3`).
- `src/thema-lynkeus.css` / `src/thema-lidl.css` — die beiden Designs.
- `bg_48.png`, `bg_96.png` — Alphamasken des Gemini-Funkelsterns.

## Prüfen

Im Sandkasten fehlen H.264/AAC (nur VP8/VP9/AV1/Opus) und ffmpeg. Getestet
wird deshalb mit synthetischen Videos/Bildern, in die der Stern exakt
einkomponiert wird; die Skripte liegen bewusst NICHT im Repo (Kritzelordner).
Gemessen am 13.08.2026: Video-Restabweichung im Sternbereich = reines
Kodier-Rauschen (Mittel 2,3 statt 6,1); Foto pixelgenau (max. ±1).
