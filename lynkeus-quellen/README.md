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

Aktuelle Version: **1.2**. Regel: **Bei jeder Änderung um 0,1 erhöhen.**
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
