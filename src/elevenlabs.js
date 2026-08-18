// Anbindung an ElevenLabs: Sprachausgabe, Stimme aufräumen, Mitschrift.
//
// Bewusst ohne SDK — die drei Endpunkte sind schlichte HTTP-Aufrufe, und ein
// weiteres Paket im Bild kostet nur Platz. Node 22 bringt fetch, FormData und
// fs.openAsBlob mit; damit lassen sich auch große Dateien anhängen, ohne sie
// vorher komplett in den Speicher zu laden.
//
// Belegt an der Doku (nicht aus dem Gedächtnis), Stand 18.08.2026:
//   Sprachausgabe  POST /v1/text-to-speech/{voice_id}   (JSON, gibt Audio zurück)
//   Aufräumen      POST /v1/audio-isolation             (multipart, Feld "audio")
//   Mitschrift     POST /v1/speech-to-text              (multipart, "model_id" Pflicht)
//   Stimmen        GET  /v1/voices
// Angemeldet wird über den Kopfzeilen-Eintrag `xi-api-key` — mit falschem
// Schlüssel antwortet die API 401 `{"detail":{"message":"Invalid API key"}}`.

import fs from 'node:fs';
import path from 'node:path';
import { config } from './config.js';

// Basis kommt aus der Konfiguration (regionale Server, Ersatzserver im Test).
const basis = () => config.elevenlabs.basis;

// Grenzen laut Doku. Sie hier festzuhalten spart einen Fehlschlag nach dem
// Hochladen von hunderten Megabyte.
export const GRENZEN = {
  // Stimme aufräumen: 1 Stunde und 500 MB je Datei.
  isolationSekunden: 60 * 60,
  isolationBytes: 500 * 1024 * 1024,
  // Mitschrift: 10 Stunden und 3 GB je Datei.
  scribeSekunden: 10 * 60 * 60,
  scribeBytes: 3 * 1024 * 1024 * 1024,
};

export function elevenlabsAktiv() {
  return Boolean(config.elevenlabs.key);
}

// Fehler müssen den Grund nennen — ein blankes „Fehler" hat hier schon einmal
// mehrere Deploy-Runden gekostet. ElevenLabs verpackt den Grund in
// `detail.message` (manchmal ist `detail` selbst nur ein String).
async function pruefeAntwort(res, was) {
  if (res.ok) return res;
  let grund = `HTTP ${res.status}`;
  try {
    const text = await res.text();
    try {
      const j = JSON.parse(text);
      const d = j.detail ?? j;
      grund = (typeof d === 'string' ? d : d?.message) || text.slice(0, 300) || grund;
    } catch {
      if (text) grund = text.slice(0, 300);
    }
  } catch { /* Antwortkörper nicht lesbar – dann bleibt der Statuscode */ }
  throw new Error(`ElevenLabs (${was}): ${grund}`);
}

function kopfzeilen(extra = {}) {
  if (!config.elevenlabs.key) {
    throw new Error('Kein ElevenLabs-Schlüssel gesetzt (ELEVENLABS_API_KEY).');
  }
  return { 'xi-api-key': config.elevenlabs.key, ...extra };
}

// ---- Stimmen auflisten (für die Auswahl in den Einstellungen) ----

export async function stimmenListe() {
  const res = await fetch(`${basis()}/voices`, { headers: kopfzeilen() });
  await pruefeAntwort(res, 'Stimmen holen');
  const daten = await res.json();
  return (daten.voices || []).map((v) => ({
    id: v.voice_id,
    name: v.name,
    art: v.category || '',
    probe: v.preview_url || '',
  }));
}

// ---- Sprachausgabe ----

// Erzeugt aus Text eine MP3 und legt sie unter `outFile` ab.
// Kosten: 1 Zeichen = 1 Credit (Flash-Modelle die Hälfte).
export async function spracheErzeugen({ text, outFile, voiceId, modelId, tempo }) {
  const inhalt = (text || '').trim();
  if (!inhalt) throw new Error('Kein Text für die Sprachausgabe angegeben.');

  const stimme = voiceId || config.elevenlabs.voiceId;
  if (!stimme) {
    throw new Error('Keine Stimme ausgewählt (ELEVENLABS_VOICE_ID oder in den Einstellungen setzen).');
  }

  const koerper = {
    text: inhalt,
    model_id: modelId || config.elevenlabs.model,
  };
  if (tempo && tempo !== 1) koerper.voice_settings = { speed: tempo };

  const url = `${basis()}/text-to-speech/${encodeURIComponent(stimme)}?output_format=mp3_44100_128`;
  const res = await fetch(url, {
    method: 'POST',
    headers: kopfzeilen({ 'Content-Type': 'application/json', accept: 'audio/mpeg' }),
    body: JSON.stringify(koerper),
  });
  await pruefeAntwort(res, 'Sprachausgabe');

  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(outFile, buf);
  return { datei: outFile, bytes: buf.length, zeichen: inhalt.length };
}

// ---- Stimme aufräumen (Voice Isolator) ----

// Holt Sprache aus einer verrauschten Aufnahme heraus und schreibt das Ergebnis
// nach `outFile`.
//
// ACHTUNG, zwei harte Grenzen (beide vorher geprüft, damit nicht erst nach dem
// Hochladen von 200 MB ein Fehler kommt):
//   * höchstens 1 Stunde je Datei — längere Aufnahmen vorher zerlegen,
//   * 1000 Credits je Minute Audio. Eine 2-Stunden-Folge kostet also rund
//     120.000 Credits; der Gratis-Tarif hat 10.000 im Monat.
export async function stimmeIsolieren({ inFile, outFile, dauerSekunden = 0 }) {
  if (!fs.existsSync(inFile)) throw new Error(`Datei nicht gefunden: ${inFile}`);

  const bytes = fs.statSync(inFile).size;
  if (bytes > GRENZEN.isolationBytes) {
    throw new Error(
      `Die Aufnahme ist ${(bytes / 1024 / 1024).toFixed(0)} MB groß. ` +
      'ElevenLabs nimmt beim Aufräumen höchstens 500 MB je Datei.',
    );
  }
  if (dauerSekunden > GRENZEN.isolationSekunden) {
    throw new Error(
      `Die Aufnahme ist ${Math.round(dauerSekunden / 60)} Minuten lang. ` +
      'ElevenLabs räumt höchstens 60 Minuten je Datei auf — den Teil vorher zerschneiden.',
    );
  }

  const form = new FormData();
  form.append('audio', await fs.openAsBlob(inFile), path.basename(inFile));

  const res = await fetch(`${basis()}/audio-isolation`, {
    method: 'POST',
    headers: kopfzeilen({ accept: 'audio/mpeg' }),
    body: form,
  });
  await pruefeAntwort(res, 'Stimme aufräumen');

  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(outFile, buf);
  return { datei: outFile, bytes: buf.length, credits: isolationCredits(dauerSekunden) };
}

// 1000 Credits je angefangener Minute.
export function isolationCredits(dauerSekunden) {
  return Math.ceil((dauerSekunden || 0) / 60) * 1000;
}

// ---- Mitschrift (Scribe) ----

// Wandelt eine Aufnahme in Text um. Entweder `file` (wird hochgeladen) ODER
// `sourceUrl` angeben.
//
// `sourceUrl` ist der sparsame Weg: ElevenLabs holt die Datei dann selbst vom
// Speicher, statt dass sie durch die App hindurchgeschoben wird. Bei einer
// 2-Stunden-Folge spart das je Lauf hunderte Megabyte ausgehende Bandbreite —
// und genau daran ist der Hobby-Tarif schon einmal hängen geblieben.
export async function mitScribeTranskribieren({ file, sourceUrl, sprache = 'deu', melde = () => {} }) {
  if (!file && !sourceUrl) throw new Error('Weder Datei noch Adresse für die Mitschrift angegeben.');

  const form = new FormData();
  form.append('model_id', config.elevenlabs.scribeModel);
  // Ohne Zeitstempel und ohne Sprecher-Trennung: Der Infotext braucht nur den
  // reinen Text, und jede Zusatzfunktion kostet extra.
  form.append('timestamps_granularity', 'none');
  form.append('diarize', 'false');
  form.append('tag_audio_events', 'false');
  if (sprache) form.append('language_code', sprache);

  if (sourceUrl) {
    form.append('source_url', sourceUrl);
    melde('Aufnahme wird von ElevenLabs direkt aus dem Speicher geholt');
  } else {
    const bytes = fs.statSync(file).size;
    if (bytes > GRENZEN.scribeBytes) {
      throw new Error(`Die Aufnahme ist zu groß für die Mitschrift (${(bytes / 1024 ** 3).toFixed(1)} GB, erlaubt sind 3 GB).`);
    }
    form.append('file', await fs.openAsBlob(file), path.basename(file));
    melde('Aufnahme wird zu ElevenLabs übertragen');
  }

  const res = await fetch(`${basis()}/speech-to-text`, {
    method: 'POST',
    headers: kopfzeilen(),
    body: form,
  });
  await pruefeAntwort(res, 'Mitschrift');

  const daten = await res.json();
  // Bei einkanaligem Audio kommt `text` direkt; bei mehrkanaligem steckt es in
  // `transcripts`. Beides abfangen, damit nicht leerer Text durchrutscht.
  if (typeof daten.text === 'string') return daten.text.trim();
  if (Array.isArray(daten.transcripts)) {
    return daten.transcripts.map((t) => (t.text || '').trim()).filter(Boolean).join('\n\n');
  }
  return '';
}
