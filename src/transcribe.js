import fs from 'node:fs';
import path from 'node:path';
import OpenAI from 'openai';
import { config, paths } from './config.js';
import { toTranscriptionAudio } from './audio.js';
import { geminiClient, geminiGenerate } from './gemini.js';
import { elevenlabsAktiv, mitScribeTranskribieren } from './elevenlabs.js';

// Welcher Dienst schreibt mit?
//
// Vorgabe bleibt Gemini (kostenloser Kontingentbereich). ElevenLabs Scribe wird
// nur genommen, wenn es ausdrücklich eingestellt ist — sonst wäre ein
// gesetzter Schlüssel gleichbedeutend mit stillen Kosten bei jeder Folge.
export function sttAnbieter() {
  const gewuenscht = (config.sttAnbieter || 'auto').toLowerCase();
  if (gewuenscht === 'elevenlabs') return elevenlabsAktiv() ? 'elevenlabs' : 'auto-aus';
  if (gewuenscht === 'gemini') return config.geminiKey ? 'gemini' : 'auto-aus';
  if (gewuenscht === 'openai') return config.openaiKey ? 'openai' : 'auto-aus';
  if (config.geminiKey) return 'gemini';
  if (config.openaiKey) return 'openai';
  if (elevenlabsAktiv()) return 'elevenlabs';
  return 'keiner';
}

// Wandelt eine Aufnahme in Text um. Welcher Dienst das tut, entscheidet
// `sttAnbieter()` — Vorgabe ist Gemini (kostenloser Kontingentbereich, gut bei
// Deutsch und Eigennamen). Ohne jeden Schlüssel kommt "" zurück; die App
// funktioniert dann ohne Transkript.
// Mehrere Aufnahme-Teile nacheinander transkribieren und zusammenfügen.
// Gibt Text UND Fehlergründe zurück: Ein leises Scheitern hat schon dazu
// geführt, dass am Ende gar kein Infotext entstand, ohne dass jemand wusste warum.
// „melde" bekommt kurze Sätze über den aktuellen Schritt. Ohne das sitzt der
// Nutzer minutenlang vor einer Anzeige, die nichts sagt.
//
// Ein Eintrag in `quellen` ist entweder ein Dateipfad (wie bisher) oder
// `{ datei, adresse }`. Die `adresse` ist die öffentliche Speicheradresse der
// Aufnahme; ElevenLabs Scribe holt sie damit selbst ab, statt dass sie durch
// die App hindurchgeschoben wird.
export async function transcribeAll(quellen, melde = () => {}) {
  const parts = [];
  const fehler = [];
  for (let i = 0; i < quellen.length; i++) {
    const teil = (text) => melde({ teil: i + 1, gesamt: quellen.length, phase: text });
    try {
      const text = await transcribe(quellen[i], teil);
      if (text) parts.push(text);
    } catch (err) {
      console.error('Transkription eines Teils fehlgeschlagen:', err.message);
      fehler.push(err.message);
    }
  }
  return { text: parts.join('\n\n'), fehler };
}

export async function transcribe(quelle, melde = () => {}) {
  const { datei, adresse } = typeof quelle === 'string' ? { datei: quelle, adresse: '' } : (quelle || {});
  const anbieter = sttAnbieter();
  if (anbieter === 'keiner' || anbieter === 'auto-aus') return '';

  // ElevenLabs Scribe: Wenn die Aufnahme öffentlich im Speicher liegt, wird sie
  // gar nicht erst angefasst — kein Herunterladen, kein Umwandeln, kein
  // Hochladen. Das ist der mit Abstand sparsamste Weg.
  if (anbieter === 'elevenlabs' && adresse) {
    return await mitScribeTranskribieren({ sourceUrl: adresse, melde });
  }

  if (!datei) throw new Error('Aufnahme liegt weder als Datei noch unter einer abrufbaren Adresse vor.');

  // Für die Übertragung eine schlanke Mono-MP3 erzeugen (klein und überall lesbar).
  const slim = path.join(paths.tmp, `stt-${path.basename(datei)}.mp3`);
  let source = datei;
  try {
    melde('Aufnahme wird für die Übertragung verkleinert');
    await toTranscriptionAudio(datei, slim);
    source = slim;
  } catch (err) {
    console.error('Konvertierung für Transkription fehlgeschlagen, nutze Originaldatei:', err.message);
  }

  try {
    if (anbieter === 'elevenlabs') return await mitScribeTranskribieren({ file: source, melde });
    if (anbieter === 'gemini') return await transcribeWithGemini(source, melde);
    melde('Aufnahme wird mitgeschrieben');
    return await transcribeWithWhisper(source);
  } finally {
    if (source === slim) fs.rmSync(slim, { force: true });
  }
}

async function transcribeWithGemini(file, melde = () => {}) {
  const ai = geminiClient();

  // Datei hochladen (funktioniert auch für lange Folgen, anders als Inline-Daten).
  melde('Aufnahme wird zu Google übertragen');
  const uploaded = await ai.files.upload({ file, config: { mimeType: 'audio/mpeg' } });

  // Warten, bis die Datei serverseitig verarbeitet ist (max. ~2 Minuten).
  let info = uploaded;
  for (let i = 0; i < 60 && info.state === 'PROCESSING'; i++) {
    melde('Google bereitet die Aufnahme vor');
    await new Promise((r) => setTimeout(r, 2000));
    info = await ai.files.get({ name: uploaded.name });
  }
  if (info.state === 'FAILED') throw new Error('Gemini konnte die Audiodatei nicht verarbeiten.');
  if (info.state === 'PROCESSING') throw new Error('Gemini brauchte zu lange für die Audiodatei (Zeitüberschreitung).');

  const prompt = [
    'Transkribiere diese Audioaufnahme vollständig und wortgetreu.',
    'Die Sprache ist überwiegend Deutsch.',
    'Achte besonders auf korrekte Schreibweise von Eigennamen',
    '(Filmtitel, Regisseure, Schauspielerinnen und Schauspieler).',
    'Gib ausschließlich den Transkripttext zurück – keine Zeitstempel, keine Vorrede,',
    'keine Sprecher-Labels, keine Kommentare.',
  ].join(' ');

  try {
    melde('Aufnahme wird mitgeschrieben (der längste Schritt)');
    const res = await geminiGenerate({
      contents: [
        { role: 'user', parts: [
          { fileData: { fileUri: info.uri, mimeType: info.mimeType } },
          { text: prompt },
        ] },
      ],
    });
    return (res.text || '').trim();
  } finally {
    // Hochgeladene Datei wieder entfernen (Speicher im Konto freigeben).
    ai.files.delete({ name: uploaded.name }).catch(() => {});
  }
}

async function transcribeWithWhisper(file) {
  const client = new OpenAI({ apiKey: config.openaiKey });
  const result = await client.audio.transcriptions.create({
    file: fs.createReadStream(file),
    model: 'whisper-1',
    language: 'de',
    response_format: 'text',
  });
  return typeof result === 'string' ? result.trim() : (result.text || '').trim();
}
