# 🎙️ Podcast Studio

Eine kleine, mobil-optimierte Web-App, mit der du **überall vom Handy** einen Podcast
aufnehmen oder eine Audiodatei hochladen kannst. Die App:

1. nimmt deine Aufnahme entgegen (Handy-Mikrofon **oder** Datei-Upload),
2. **optimiert die Sprache per KI/DSP** gegen Hintergrundgeräusche (an/aus + Stärke-Regler),
3. fügt automatisch **Intro + Aufnahme + Outro** zusammen,
4. **transkribiert** die Aufnahme (OpenAI Whisper),
5. erstellt einen **Infotext-Vorschlag** (Claude) – den du prüfen/ändern kannst,
6. und veröffentlicht die Folge **nach deiner Bestätigung** in deinen eigenen
   **RSS-Feed**, den Spotify automatisch abholt.

> **Wichtig zu Spotify:** Es gibt keine offizielle API, um Folgen direkt in
> „Spotify for Podcasters" hochzuladen. Der offizielle Weg ist ein **RSS-Feed**,
> den du **einmalig** bei Spotify einträgst. Danach erscheint jede neue Folge
> automatisch. Diese App ist genau dieser Feed – plus die ganze Aufnahme-/
> Verarbeitungs-Automatik.

---

## Schnellstart (lokal testen)

```bash
npm install
cp .env.example .env      # Werte eintragen (mind. APP_PASSWORD, OPENAI_API_KEY)
npm start
# -> http://localhost:3000
```

Auf dem Handy braucht die Mikrofon-Aufnahme **HTTPS** (lokal geht `localhost`).

## Umgebungsvariablen

| Variable            | Zweck                                                        |
|---------------------|-------------------------------------------------------------|
| `APP_PASSWORD`      | Login-Passwort (nur du kommst rein)                         |
| `SESSION_SECRET`    | langer Zufallswert zum Signieren der Login-Cookies          |
| `PUBLIC_URL`        | öffentliche Adresse der App, z. B. `https://…onrender.com`  |
| `OPENAI_API_KEY`    | Transkription (Whisper) – für den KI-Infotext aus Audio     |
| `ANTHROPIC_API_KEY` | KI-Infotext (Claude), optional – ohne Key einfacher Fallback|
| `DATA_DIR`          | Speicherort für Uploads/MP3s/Metadaten (Render: `/data`)    |
| `PORT`              | Server-Port (Standard 3000)                                 |

---

## Deployment (empfohlen: Render)

1. Repo zu GitHub pushen.
2. Auf [render.com](https://render.com): **New → Blueprint** → dieses Repo wählen
   (die mitgelieferte `render.yaml` legt Web-Service **und** persistenten Datenträger an).
3. Im Dashboard die Secrets setzen: `APP_PASSWORD`, `OPENAI_API_KEY`,
   ggf. `ANTHROPIC_API_KEY`.
4. Nach dem ersten Deploy `PUBLIC_URL` auf die echte Render-URL setzen
   (z. B. `https://podcast-studio.onrender.com`) und neu deployen.

> Alternativ läuft es genauso auf Railway, Fly.io oder jedem VPS
> (`docker build` + Volume auf `/data` mounten).

---

## Ersteinrichtung in der App

1. Einloggen → Menü (☰) → **Einstellungen**.
2. **Podcast-Infos** ausfüllen (Titel, Beschreibung, E-Mail – die verlangt Spotify).
3. **Intro-, Outro-** und **Cover-Bild** hochladen (Cover ist für Spotify Pflicht,
   quadratisch, ≥ 1400 px).
4. Fertig – die **RSS-Feed-URL** steht unten in den Einstellungen.

## Bei Spotify eintragen

1. [Spotify for Podcasters / Creators](https://podcasters.spotify.com) öffnen.
2. Neuen Podcast **via RSS-Feed** hinzufügen und deine `…/feed.xml`-URL eingeben.
3. Bestätigen. Ab jetzt zieht Spotify jede veröffentlichte Folge automatisch.

---

## Optionale, stärkere Rauschunterdrückung (RNNoise)

Standardmäßig läuft die KI-Optimierung über ffmpeg (kostenlos, lokal). Für noch
stärkere Trennung von Stimme und Umgebung (Auto/Restaurant) kannst du ein
**RNNoise-Modell** hinterlegen: Datei nach `data/assets/rnnoise.rnn` legen –
die App nutzt es dann automatisch zusätzlich.

---

## Was diese App bewusst NICHT tut

- Sie lädt **nicht** direkt in dein Spotify-Konto hoch (dafür gibt es keine API) –
  sie stellt den RSS-Feed bereit, den Spotify abholt.
- Sie veröffentlicht **nie** ohne deine Bestätigung.
