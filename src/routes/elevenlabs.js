import express from 'express';
import fs from 'node:fs';
import path from 'node:path';
import { paths, config } from '../config.js';
import { requireAuth } from '../auth.js';
import { getSettings, saveSettings, coverUrlOf } from '../store.js';
import { uploadFile, deleteKey } from '../storage.js';
import {
  elevenlabsAktiv, stimmenListe, spracheErzeugen, isolationCredits,
} from '../elevenlabs.js';

const router = express.Router();
router.use(requireAuth);

// Kurze Auskunft für die Oberfläche: Ist ein Schlüssel da, welche Stimme ist
// eingestellt, was kostet das Aufräumen ungefähr.
router.get('/status', (req, res) => {
  const s = getSettings();
  res.json({
    aktiv: elevenlabsAktiv(),
    stimme: s.elevenVoiceId || config.elevenlabs.voiceId || '',
    modell: config.elevenlabs.model,
    scribeModell: config.elevenlabs.scribeModel,
    sttAnbieter: config.sttAnbieter,
    // Damit in der App eine echte Zahl steht statt „kostet was".
    creditsProStunde: isolationCredits(3600),
  });
});

router.get('/stimmen', async (req, res, next) => {
  if (!elevenlabsAktiv()) {
    return res.status(400).json({ error: 'Kein ElevenLabs-Schlüssel hinterlegt (ELEVENLABS_API_KEY).' });
  }
  try {
    res.json({ stimmen: await stimmenListe() });
  } catch (err) {
    next(err);
  }
});

// Stimme merken, damit sie nicht bei jedem Aufruf mitgeschickt werden muss.
router.put('/stimme', (req, res) => {
  const id = String(req.body?.stimme || '').trim();
  res.json(saveSettings({ elevenVoiceId: id }));
});

// Kurzes Vorhören: erzeugt Sprache und schickt die MP3 direkt zurück.
// Bewusst ohne Ablegen im Speicher – eine Hörprobe muss nirgends bleiben.
router.post('/probe', async (req, res, next) => {
  const text = String(req.body?.text || '').trim();
  if (!text) return res.status(400).json({ error: 'Bitte einen Text eingeben.' });
  if (text.length > 500) {
    return res.status(400).json({ error: `Die Hörprobe ist auf 500 Zeichen begrenzt (dein Text hat ${text.length}).` });
  }

  const tmp = path.join(paths.tmp, `probe-${Date.now()}.mp3`);
  try {
    const stimme = String(req.body?.stimme || '').trim() || getSettings().elevenVoiceId || '';
    await spracheErzeugen({ text, outFile: tmp, voiceId: stimme });
    res.type('audio/mpeg').send(fs.readFileSync(tmp));
  } catch (err) {
    next(err);
  } finally {
    fs.rmSync(tmp, { force: true });
  }
});

// Intro oder Outro aus Text sprechen lassen und als Asset ablegen –
// derselbe Platz, an dem sonst eine hochgeladene Datei landet.
router.post('/ansage', async (req, res, next) => {
  const text = String(req.body?.text || '').trim();
  const ziel = String(req.body?.ziel || '').trim();
  if (!['intro', 'outro'].includes(ziel)) {
    return res.status(400).json({ error: 'Ziel muss „intro" oder „outro" sein.' });
  }
  if (!text) return res.status(400).json({ error: 'Bitte einen Text eingeben.' });

  const tmp = path.join(paths.tmp, `${ziel}-tts-${Date.now()}.mp3`);
  try {
    const aktuell = getSettings();
    const stimme = String(req.body?.stimme || '').trim() || aktuell.elevenVoiceId || '';
    const erg = await spracheErzeugen({ text, outFile: tmp, voiceId: stimme });

    const dateiname = `${ziel}-${Date.now()}.mp3`;
    if (aktuell[ziel] && aktuell[ziel] !== dateiname) {
      await deleteKey(`assets/${aktuell[ziel]}`).catch(() => {});
    }
    await uploadFile(tmp, `assets/${dateiname}`, 'audio/mpeg');

    // Den gesprochenen Text mitschreiben: Sonst weiß beim nächsten Mal
    // niemand mehr, was da eigentlich gesagt wird.
    const next_ = saveSettings({ [ziel]: dateiname, [`${ziel}Text`]: text });
    res.json({ ...next_, coverUrl: coverUrlOf(next_), zeichen: erg.zeichen });
  } catch (err) {
    next(err);
  } finally {
    fs.rmSync(tmp, { force: true });
  }
});

export default router;
