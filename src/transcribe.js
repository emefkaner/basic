import fs from 'node:fs';
import OpenAI from 'openai';
import { config } from './config.js';

// Wandelt die Aufnahme per OpenAI Whisper in Text um.
// Gibt "" zurück, wenn kein Key gesetzt ist (App funktioniert dann ohne Transkript).
export async function transcribe(file) {
  if (!config.openaiKey) return '';
  const client = new OpenAI({ apiKey: config.openaiKey });
  const result = await client.audio.transcriptions.create({
    file: fs.createReadStream(file),
    model: 'whisper-1',
    // Sprache automatisch erkennen lassen; Whisper kommt mit Deutsch gut klar.
    response_format: 'text',
  });
  // Bei response_format 'text' kommt ein reiner String zurück.
  return typeof result === 'string' ? result.trim() : (result.text || '').trim();
}
