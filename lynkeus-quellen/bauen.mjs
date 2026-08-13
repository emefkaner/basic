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

// Version (Fußzeile Nachtdesign) — beim Versionssprung hier UND im
// Kommentar in src/struktur.html nachziehen.
const VERSION = '2.8';

const VARIANTEN = [
  {
    thema: 'thema-lynkeus.css', favicon: 'favicon.png', ziel: '../lynkeus.html',
    kopfrechts: '',
    fusszeile1: `<strong>Lynkeus v${VERSION}</strong> · Created by emefka`,
  },
  {
    thema: 'thema-lidl.css', favicon: 'favicon-lidl.png', ziel: '../lynkeus-lidl.html',
    // Team-Kunde-Logo wie im MCO-Now-Konverter (sales-kunde.png, verkleinert)
    kopfrechts: `<div class="kundeblock"><span class="kundelabel">bereitgestellt von</span>` +
      `<img id="kundelogo" src="${uri(HIER + 'kundelogo.png')}" alt="Team Kunde"></div>`,
    fusszeile1: '<strong>Lynkeus – GEMINI Fighter</strong> · Erstellt von Marc Ferdinand Körner – Team Kunde',
  },
];

for (const v of VARIANTEN) {
  let html = struktur;
  html = html.split('__THEMA__').join(fs.readFileSync(HIER + 'src/' + v.thema, 'utf8'));
  html = html.split('__FAVICON__').join(uri(HIER + v.favicon));
  html = html.split('__KOPFRECHTS__').join(v.kopfrechts);
  html = html.split('__FUSSZEILE1__').join(v.fusszeile1);
  html = html.split('__BG96__').join(uri(HIER + 'bg_96.png'));
  html = html.split('__BG48__').join(uri(HIER + 'bg_48.png'));
  // split/join statt replace: das Bundle enthält $-Zeichen, die replace() deuten würde
  html = html.split('__BUNDLE__').join(bundle);
  const ziel = HIER + v.ziel;
  fs.writeFileSync(ziel, html);
  console.log('geschrieben:', ziel, Math.round(html.length / 1024) + ' KB');
}
