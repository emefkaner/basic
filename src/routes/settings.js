import express from 'express';
import multer from 'multer';
import path from 'node:path';
import fs from 'node:fs';
import { paths } from '../config.js';
import { requireAuth } from '../auth.js';
import { getSettings, saveSettings } from '../store.js';

const router = express.Router();
router.use(requireAuth);

// Assets (Intro/Outro/Cover) landen im assets-Ordner mit festem, sprechendem Namen.
const upload = multer({
  storage: multer.diskStorage({
    destination: (req, file, cb) => cb(null, paths.assets),
    filename: (req, file, cb) => {
      const kind = file.fieldname; // 'intro' | 'outro' | 'cover'
      const ext = path.extname(file.originalname) || (kind === 'cover' ? '.jpg' : '.mp3');
      cb(null, `${kind}${ext}`);
    },
  }),
  limits: { fileSize: 50 * 1024 * 1024 },
});

router.get('/', (req, res) => {
  res.json(getSettings());
});

// Textfelder speichern (Titel, Beschreibung, Autor, E-Mail, ...).
router.put('/', (req, res) => {
  const allowed = ['title', 'description', 'author', 'ownerName', 'ownerEmail', 'language', 'category', 'explicit'];
  const patch = {};
  for (const key of allowed) {
    if (key in req.body) patch[key] = key === 'explicit' ? Boolean(req.body[key]) : req.body[key];
  }
  res.json(saveSettings(patch));
});

// Intro/Outro/Cover hochladen.
router.post(
  '/assets',
  upload.fields([
    { name: 'intro', maxCount: 1 },
    { name: 'outro', maxCount: 1 },
    { name: 'cover', maxCount: 1 },
  ]),
  (req, res) => {
    const patch = {};
    for (const kind of ['intro', 'outro', 'cover']) {
      const f = req.files?.[kind]?.[0];
      if (f) {
        // Alte Datei mit anderer Endung ggf. entfernen, um Verwaisung zu vermeiden.
        const current = getSettings()[kind];
        if (current && current !== f.filename) {
          fs.rmSync(path.join(paths.assets, current), { force: true });
        }
        patch[kind] = f.filename;
      }
    }
    res.json(saveSettings(patch));
  }
);

export default router;
