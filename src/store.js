import fs from 'node:fs';
import { paths, defaultSettings } from './config.js';

// Sehr einfache "Datenbank": zwei JSON-Dateien auf der Platte.
// Für ein persönliches Tool völlig ausreichend und ohne DB-Setup.

function readJson(file, fallback) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return fallback;
  }
}

function writeJson(file, data) {
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2));
  fs.renameSync(tmp, file); // atomar, damit die Datei nie halb geschrieben ist
}

// ---- Episoden ----

export function listEpisodes() {
  const data = readJson(paths.store, { episodes: [] });
  return data.episodes || [];
}

export function getEpisode(id) {
  return listEpisodes().find((e) => e.id === id) || null;
}

export function saveEpisode(episode) {
  const episodes = listEpisodes();
  const idx = episodes.findIndex((e) => e.id === episode.id);
  if (idx >= 0) episodes[idx] = episode;
  else episodes.unshift(episode); // neueste zuerst
  writeJson(paths.store, { episodes });
  return episode;
}

export function deleteEpisode(id) {
  const episodes = listEpisodes().filter((e) => e.id !== id);
  writeJson(paths.store, { episodes });
}

// ---- Einstellungen ----

export function getSettings() {
  return { ...defaultSettings, ...readJson(paths.settings, {}) };
}

export function saveSettings(patch) {
  const next = { ...getSettings(), ...patch };
  writeJson(paths.settings, next);
  return next;
}
