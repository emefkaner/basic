import express from 'express';
import cookieParser from 'cookie-parser';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { config, paths } from './config.js';
import { issueCookie, clearCookie, isLoggedIn, checkPassword } from './auth.js';
import { buildFeed } from './rss.js';
import episodesRouter from './routes/episodes.js';
import settingsRouter from './routes/settings.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.join(__dirname, '..', 'public');

const app = express();
app.use(cookieParser());
app.use(express.json({ limit: '1mb' }));
app.disable('x-powered-by');

// ---- Öffentliche Endpunkte (kein Login nötig) ----

// Health-Check (für Render/Railway).
app.get('/healthz', (req, res) => res.json({ ok: true }));

// RSS-Feed – DAS ist die URL, die du bei Spotify for Podcasters einträgst.
app.get('/feed.xml', (req, res) => {
  res.type('application/rss+xml; charset=utf-8').send(buildFeed());
});

// Fertige Audiodateien und Cover müssen öffentlich sein, damit Spotify sie laden kann.
app.use('/media/episodes', express.static(paths.episodes, { maxAge: '1y' }));
app.use('/media/assets', express.static(paths.assets, { maxAge: '1h' }));

// ---- Login ----
app.post('/login', (req, res) => {
  if (checkPassword(req.body?.password)) {
    issueCookie(res);
    return res.json({ ok: true });
  }
  res.status(401).json({ error: 'Falsches Passwort' });
});

app.post('/logout', (req, res) => {
  clearCookie(res);
  res.json({ ok: true });
});

app.get('/api/session', (req, res) => {
  res.json({ loggedIn: isLoggedIn(req) });
});

// ---- Geschützte API ----
app.use('/api/episodes', episodesRouter);
app.use('/api/settings', settingsRouter);

// ---- Frontend ----
// Login-Seite immer erreichbar; die App-Seite erfordert Login (sonst Redirect).
app.get('/login', (req, res) => res.sendFile(path.join(publicDir, 'login.html')));

app.get(['/', '/settings', '/episode/:id'], (req, res) => {
  if (!isLoggedIn(req)) return res.redirect('/login');
  res.sendFile(path.join(publicDir, 'index.html'));
});

// Übrige statische Dateien (JS/CSS/Manifest/Service-Worker).
app.use(express.static(publicDir));

app.listen(config.port, () => {
  console.log(`Podcast-App läuft auf Port ${config.port}`);
  console.log(`Öffentliche URL:  ${config.publicUrl}`);
  console.log(`RSS-Feed:         ${config.publicUrl}/feed.xml`);
  if (!config.password) console.warn('WARNUNG: APP_PASSWORD ist nicht gesetzt – Login nicht möglich.');
});
