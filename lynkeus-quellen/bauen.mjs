// Baut BEIDE Single-File-Varianten aus einer gemeinsamen Struktur:
//   ../lynkeus.html       — Nachtdesign (Lila/Regenbogenband)
//   ../lynkeus-lidl.html  — Lidl-Design (hell, Blau/Gelb/Rot)
// Gemeinsam: src/struktur.html (Aufbau), src/app.js + src/engine.js (Logik).
// Je Variante: src/thema-*.css und favicon*.png.
// WICHTIG: Jede Änderung an Struktur oder Logik landet automatisch in beiden
// Varianten — Design-Änderungen gehören in BEIDE thema-Dateien, wo sinnvoll.
import { build } from 'esbuild';
import fs from 'fs';

const HIER = new URL('.', import.meta.url).pathname;

const ergebnis = await build({
  entryPoints: [HIER + 'src/app.js'],
  bundle: true,
  minify: true,
  format: 'iife',
  target: ['chrome109', 'safari16'],
  write: false,
  legalComments: 'none',
});
const bundle = ergebnis.outputFiles[0].text;

const uri = (pfad) => 'data:image/png;base64,' + fs.readFileSync(pfad).toString('base64');
const struktur = fs.readFileSync(HIER + 'src/struktur.html', 'utf8');

const VARIANTEN = [
  { thema: 'thema-lynkeus.css', favicon: 'favicon.png', ziel: '../lynkeus.html' },
  { thema: 'thema-lidl.css', favicon: 'favicon-lidl.png', ziel: '../lynkeus-lidl.html' },
];

for (const v of VARIANTEN) {
  let html = struktur;
  html = html.split('__THEMA__').join(fs.readFileSync(HIER + 'src/' + v.thema, 'utf8'));
  html = html.split('__FAVICON__').join(uri(HIER + v.favicon));
  html = html.split('__BG96__').join(uri(HIER + 'bg_96.png'));
  html = html.split('__BG48__').join(uri(HIER + 'bg_48.png'));
  // split/join statt replace: das Bundle enthält $-Zeichen, die replace() deuten würde
  html = html.split('__BUNDLE__').join(bundle);
  const ziel = HIER + v.ziel;
  fs.writeFileSync(ziel, html);
  console.log('geschrieben:', ziel, Math.round(html.length / 1024) + ' KB');
}
