# Lynkeus — Quelldateien

Hieraus wird die Single-File-App **`../lynkeus.html`** gebaut (Gemini/Veo-Funkel-
Wasserzeichen aus Videos und Fotos herausrechnen, alles lokal im Browser).

## Bauen

```
npm install mediabunny esbuild     # einmalig, in diesem Ordner
node bauen.mjs ../lynkeus.html
```

`bauen.mjs` bündelt `src/app.js` (samt mediabunny) mit esbuild und bettet die
beiden Funkel-Masken (`bg_48.png`, `bg_96.png`) als Daten-URIs in
`src/vorlage.html` ein. Ergebnis ist eine einzige HTML-Datei ohne externe
Abhängigkeiten — sie funktioniert direkt über `file://`.

## Versionierung

Aktuelle Version: **1.7**. Regel: **Bei jeder Änderung um 0,1 erhöhen.**
Die Nummer steht an zwei Stellen in `src/vorlage.html` (Kommentar im `<head>`
und im Footer) — beide nachziehen, neu bauen, fertige `lynkeus.html` mit
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

## Dateien

- `src/engine.js` — Mathematik: umgekehrte Alpha-Mischung, Geometrie
  (Video: Größe ≈ kurze Seite/15, Abstand ≈ kurze Seite/10, Standard-Feintuning
  Stärke 0,6 / Versatz −kurzeSeite/30; Foto: exakt 96 px Stern/64 px Rand über
  1024×1024, sonst 48/32, Stärke 1). Übernommen aus
  [dearabhin/gemini-watermark-remover](https://github.com/dearabhin/gemini-watermark-remover) (MIT).
- `src/app.js` — Oberfläche und Video-Pipeline (mediabunny/WebCodecs:
  dekodieren → Sternbereich säubern → H.264/MP4 kodieren, Ausweg VP9/WebM;
  Tonspur wird unverändert durchgereicht).
- `src/vorlage.html` — Aufbau, Styles (Regenbogenband, 3D-Effekte), Logo-SVG.
- `bg_48.png`, `bg_96.png` — Alphamasken des Gemini-Funkelsterns.

## Prüfen

Im Sandkasten fehlen H.264/AAC (nur VP8/VP9/AV1/Opus) und ffmpeg. Getestet
wird deshalb mit synthetischen Videos/Bildern, in die der Stern exakt
einkomponiert wird; die Skripte liegen bewusst NICHT im Repo (Kritzelordner).
Gemessen am 13.08.2026: Video-Restabweichung im Sternbereich = reines
Kodier-Rauschen (Mittel 2,3 statt 6,1); Foto pixelgenau (max. ±1).
