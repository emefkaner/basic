import 'dotenv/config';
import path from 'node:path';
import fs from 'node:fs';

const DATA_DIR = path.resolve(process.env.DATA_DIR || './data');

// Unterordner für die verschiedenen Datei-Arten.
export const paths = {
  data: DATA_DIR,
  uploads: path.join(DATA_DIR, 'uploads'),   // Roh-Aufnahmen/Uploads
  episodes: path.join(DATA_DIR, 'episodes'), // fertige MP3s (Intro+Audio+Outro)
  assets: path.join(DATA_DIR, 'assets'),     // Intro, Outro, Cover
  store: path.join(DATA_DIR, 'store.json'),  // Episoden-Metadaten
  settings: path.join(DATA_DIR, 'settings.json'), // Podcast-Einstellungen
};

// Ordner beim Start anlegen.
for (const dir of [paths.data, paths.uploads, paths.episodes, paths.assets]) {
  fs.mkdirSync(dir, { recursive: true });
}

export const config = {
  port: Number(process.env.PORT || 3000),
  password: process.env.APP_PASSWORD || '',
  sessionSecret: process.env.SESSION_SECRET || 'unsicheres-standard-secret-bitte-aendern',
  publicUrl: (process.env.PUBLIC_URL || `http://localhost:${process.env.PORT || 3000}`).replace(/\/$/, ''),
  openaiKey: process.env.OPENAI_API_KEY || '',
  anthropicKey: process.env.ANTHROPIC_API_KEY || '',
};

// Standard-Podcast-Einstellungen (können in der App überschrieben werden).
export const defaultSettings = {
  title: 'Mein Podcast',
  description: 'Beschreibung meines Podcasts.',
  author: 'Ich',
  ownerName: 'Ich',
  ownerEmail: process.env.OWNER_EMAIL || '',
  language: 'de',
  category: 'Society & Culture',
  explicit: false,
  // Dateinamen der hochgeladenen Assets (im assets-Ordner). Leer = noch nicht gesetzt.
  intro: '',
  outro: '',
  cover: '',
};
