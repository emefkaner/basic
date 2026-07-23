import express from 'express';
import multer from 'multer';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { paths } from '../config.js';
import { requireAuth } from '../auth.js';
import { listEpisodes, getEpisode, saveEpisode, deleteEpisode, getSettings } from '../store.js';
import { buildEpisode } from '../audio.js';
import { transcribe } from '../transcribe.js';
import { generateDescription } from '../describe.js';

const router = express.Router();
router.use(requireAuth);

// Uploads landen zunächst als Rohdatei im uploads-Ordner.
const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => cb(null, paths.uploads),
    filename: (req, file, cb) => {
      const ext = path.extname(file.originalname) || '.webm';
      cb(null, `${Date.now()}-${crypto.randomBytes(4).toString('hex')}${ext}`);
    },
  }),
  limits: { fileSize: 500 * 1024 * 1024 }, // 500 MB – reicht für lange Folgen
});

// Alle Episoden auflisten.
router.get('/', (req, res) => {
  res.json(listEpisodes());
});

// Einzelne Episode (zum Pollen des Verarbeitungsstatus).
router.get('/:id', (req, res) => {
  const ep = getEpisode(req.params.id);
  if (!ep) return res.status(404).json({ error: 'Nicht gefunden' });
  res.json(ep);
});

// Neue Aufnahme/Upload entgegennehmen und Verarbeitung im Hintergrund starten.
router.post('/', upload.single('audio'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'Keine Audiodatei erhalten' });

  const id = `${Date.now()}-${crypto.randomBytes(4).toString('hex')}`;
  const episode = {
    id,
    title: (req.body.title || '').trim() || 'Neue Folge',
    description: '',
    transcript: '',
    status: 'processing', // processing -> draft -> published
    rawFile: req.file.filename,
    audioFile: '',
    duration: 0,
    size: 0,
    // KI-Sprachoptimierung: an/aus + Stärke 0..100 (Regler in der App).
    enhance: {
      enabled: req.body.enhance === 'true' || req.body.enhance === '1',
      strength: Math.min(100, Math.max(0, Number(req.body.strength) || 60)),
    },
    error: '',
    createdAt: new Date().toISOString(),
    publishedAt: null,
  };
  saveEpisode(episode);

  // Nicht auf die (langsame) Verarbeitung warten – Client pollt den Status.
  processEpisode(id).catch((err) => {
    console.error('Verarbeitung fehlgeschlagen:', err);
    const ep = getEpisode(id);
    if (ep) saveEpisode({ ...ep, status: 'error', error: err.message });
  });

  res.status(202).json(episode);
});

// Titel/Beschreibung bearbeiten (Freigabe/Änderung durch den Nutzer).
router.put('/:id', (req, res) => {
  const ep = getEpisode(req.params.id);
  if (!ep) return res.status(404).json({ error: 'Nicht gefunden' });
  if (typeof req.body.title === 'string') ep.title = req.body.title.trim();
  if (typeof req.body.description === 'string') ep.description = req.body.description;
  saveEpisode(ep);
  res.json(ep);
});

// Veröffentlichen – passiert nur nach ausdrücklicher Bestätigung im Frontend.
router.post('/:id/publish', (req, res) => {
  const ep = getEpisode(req.params.id);
  if (!ep) return res.status(404).json({ error: 'Nicht gefunden' });
  if (ep.status === 'processing') return res.status(409).json({ error: 'Wird noch verarbeitet' });
  if (!ep.audioFile) return res.status(409).json({ error: 'Keine fertige Audiodatei' });
  ep.status = 'published';
  ep.publishedAt = ep.publishedAt || new Date().toISOString();
  saveEpisode(ep);
  res.json(ep);
});

// Veröffentlichung zurückziehen (Folge verschwindet wieder aus dem Feed).
router.post('/:id/unpublish', (req, res) => {
  const ep = getEpisode(req.params.id);
  if (!ep) return res.status(404).json({ error: 'Nicht gefunden' });
  ep.status = 'draft';
  saveEpisode(ep);
  res.json(ep);
});

// Episode löschen (inkl. Dateien).
router.delete('/:id', (req, res) => {
  const ep = getEpisode(req.params.id);
  if (!ep) return res.status(404).json({ error: 'Nicht gefunden' });
  for (const [dir, file] of [[paths.uploads, ep.rawFile], [paths.episodes, ep.audioFile]]) {
    if (file) fs.rmSync(path.join(dir, file), { force: true });
  }
  deleteEpisode(ep.id);
  res.json({ ok: true });
});

// ---- Die eigentliche Pipeline ----
async function processEpisode(id) {
  const settings = getSettings();
  let ep = getEpisode(id);
  if (!ep) return;

  const rawPath = path.join(paths.uploads, ep.rawFile);
  const introPath = settings.intro ? path.join(paths.assets, settings.intro) : null;
  const outroPath = settings.outro ? path.join(paths.assets, settings.outro) : null;
  const outFile = `${id}.mp3`;
  const outPath = path.join(paths.episodes, outFile);

  // 1) Intro + Aufnahme + Outro zusammenfügen.
  const { duration, size } = await buildEpisode({
    intro: introPath,
    main: rawPath,
    outro: outroPath,
    outFile: outPath,
    enhance: ep.enhance,
  });

  ep = getEpisode(id);
  ep.audioFile = outFile;
  ep.duration = duration;
  ep.size = size;
  saveEpisode(ep);

  // 2) Transkribieren (nur die Rohaufnahme, ohne Intro/Outro).
  let transcript = '';
  try {
    transcript = await transcribe(rawPath);
  } catch (err) {
    console.error('Transkription fehlgeschlagen:', err.message);
  }

  // 3) Infotext-Vorschlag generieren.
  const description = await generateDescription({ transcript, title: ep.title });

  ep = getEpisode(id);
  ep.transcript = transcript;
  ep.description = description;
  ep.status = 'draft'; // bereit zur Freigabe durch den Nutzer
  saveEpisode(ep);
}

export default router;
