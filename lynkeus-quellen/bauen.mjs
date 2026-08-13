// Baut die Single-File-HTML: bündelt app.js (samt mediabunny) und bettet die
// Funkel-Vorlage als Daten-URI ein.
import { build } from 'esbuild';
import fs from 'fs';

const HIER = new URL('.', import.meta.url).pathname;
const ZIEL = process.argv[2] || HIER + '../lynkeus.html';

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

let html = fs.readFileSync(HIER + 'src/vorlage.html', 'utf8');
html = html.split('__BG96__').join(uri(HIER + 'bg_96.png'));
html = html.split('__BG48__').join(uri(HIER + 'bg_48.png'));
// split/join statt replace: das Bundle enthält $-Zeichen, die replace() deuten würde
html = html.split('__BUNDLE__').join(bundle);

fs.writeFileSync(ZIEL, html);
console.log('geschrieben:', ZIEL, Math.round(html.length / 1024) + ' KB');
