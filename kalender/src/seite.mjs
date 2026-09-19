// Kleine Übersichtsseite neben der .ics-Datei: Abo-Adresse zum Kopieren,
// Knopf fürs Handy und die nächsten Termine zum Gegenprüfen.

const ZEITZONE = 'Europe/Berlin';

function deutschesDatum(datum) {
  return new Intl.DateTimeFormat('de-DE', {
    weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', timeZone: ZEITZONE,
  }).format(datum);
}

// Kurzform für die Tabelle: "Sa 03.10. 20:00" — die Jahreszahl steht in der
// Überschrift, und auf dem Handy zählt jede Spalte.
function kurzDatum(datum) {
  const teile = new Intl.DateTimeFormat('de-DE', {
    weekday: 'short', day: '2-digit', month: '2-digit',
    hour: '2-digit', minute: '2-digit', timeZone: ZEITZONE,
  }).formatToParts(datum);
  const hole = (art) => teile.find((t) => t.type === art)?.value ?? '';
  return `${hole('weekday').replace('.', '')} ${hole('day')}.${hole('month')}. ${hole('hour')}:${hole('minute')}`;
}

function schuetze(text) {
  return String(text ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

export function baueSeite({ spiele, gebautAm, saison, dateiname, zweiteDatei = null, name }) {
  const kommende = spiele.filter((s) => s.beginn > gebautAm).slice(0, 12);
  const zeilen = kommende.map((s) => `
      <tr>
        <td class="wann">${schuetze(kurzDatum(s.beginn))}</td>
        <td class="wer"><span class="marke ${s.kategorie === 'TSB Hunters' ? 'tsb' : 'nsu'}">${schuetze(s.kategorie)}</span></td>
        <td>${schuetze(s.heim)} – ${schuetze(s.gast)}</td>
        <td class="ort">${schuetze(s.ort || '')}</td>
      </tr>`).join('');

  return `<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${schuetze(name)}</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Ctext y='14' font-size='14'%3E%F0%9F%93%85%3C/text%3E%3C/svg%3E">
<style>
  :root { color-scheme: light dark; --rand: #d8dbe0; --gedaempft: #5c6470; --flaeche: #fff; --text: #15181d; }
  @media (prefers-color-scheme: dark) {
    :root { --rand: #2c3138; --gedaempft: #9aa3ae; --flaeche: #15181d; --text: #eceff3; }
  }
  body { margin: 0; padding: 2rem 1rem 4rem; background: var(--flaeche); color: var(--text);
         font: 16px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
  main { max-width: 46rem; margin: 0 auto; }
  h1 { font-size: 1.5rem; line-height: 1.25; margin: 0 0 .25rem; }
  h2 { font-size: 1.1rem; margin: 2.5rem 0 .75rem; }
  p.stand { color: var(--gedaempft); margin: 0 0 2rem; font-size: .9rem; }
  .adresse { display: block; width: 100%; box-sizing: border-box; padding: .75rem .9rem;
             font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .9rem;
             border: 1px solid var(--rand); border-radius: .5rem; background: transparent; color: inherit; }
  .knopf { display: inline-block; margin-top: .75rem; padding: .6rem 1.1rem; border-radius: .5rem;
           background: #0269b8; color: #fff; text-decoration: none; font-weight: 600; }
  ol { padding-left: 1.2rem; }
  ol li { margin-bottom: .4rem; }
  /* Lange Adressen dürfen umbrechen, statt die Seite breitzuziehen. */
  a { overflow-wrap: anywhere; }
  table { width: 100%; border-collapse: collapse; font-size: .92rem; table-layout: fixed; }
  td { border-bottom: 1px solid var(--rand); padding: .5rem .4rem; vertical-align: top;
       overflow-wrap: anywhere; }
  td.wann { white-space: nowrap; color: var(--gedaempft); width: 8.4rem; }
  td.wer { width: 7.6rem; padding-right: .7rem; }
  td.ort { color: var(--gedaempft); width: 8rem; }
  @media (max-width: 34rem) {
    td.ort { display: none; }
    td.wann { width: 7rem; font-size: .85rem; }
    td.wer { width: 6.6rem; }
  }
  .marke { display: inline-block; padding: .05rem .45rem; border-radius: .3rem; font-size: .78rem;
           font-weight: 600; white-space: nowrap; }
  .marke.tsb { background: #ff010b1a; color: #c4000a; }
  .marke.nsu { background: #0269b81a; color: #0269b8; }
  @media (prefers-color-scheme: dark) {
    .marke.tsb { color: #ff6b72; } .marke.nsu { color: #67b3ec; }
  }
  footer { margin-top: 3rem; color: var(--gedaempft); font-size: .85rem; }
  p.warnung { color: var(--gedaempft); font-size: .9rem; }
</style>
</head>
<body>
<main>
  <h1>${schuetze(name)}</h1>
  <p class="stand">Saison ${schuetze(saison)} · ${spiele.length} Termine · zuletzt gebaut am ${schuetze(deutschesDatum(gebautAm))} Uhr</p>

  <h2>Abonnieren</h2>
  <p>Diese Adresse kopieren:</p>
  <input class="adresse" readonly value="" id="adresse">
  <p><a class="knopf" id="knopf" href="#">Auf iPhone/iPad direkt abonnieren</a></p>

  <h2>So geht es am iPhone</h2>
  <ol>
    <li>Oben auf <strong>Auf iPhone/iPad direkt abonnieren</strong> tippen.</li>
    <li>Im Fenster <strong>Abonnieren</strong> tippen, dann <strong>Sichern</strong>.</li>
    <li>Fertig — die Spiele stehen in der Kalender-App.</li>
  </ol>

  <h2>So geht es in Google Kalender</h2>
  <ol>
    <li><a href="https://calendar.google.com/calendar/u/0/r/settings/addbyurl">calendar.google.com/calendar/u/0/r/settings/addbyurl</a> öffnen.</li>
    <li>Die Adresse von oben einfügen.</li>
    <li>Auf <strong>Kalender hinzufügen</strong> klicken.</li>
  </ol>

  ${zweiteDatei ? `<h2>Fassung mit Team-Einteilung</h2>
  <p>Dieselben Spiele, bei den Heimspielen zusätzlich mit der Einteilung fürs Livestream-Team:</p>
  <input class="adresse" readonly value="" id="adresse-zwei">
  <p><a class="knopf" id="knopf-zwei" href="#">Auf iPhone/iPad direkt abonnieren</a></p>
  <p class="warnung">Entweder diese Fassung <em>oder</em> die obere abonnieren — nicht beide, sonst steht jedes Spiel doppelt im Kalender.</p>` : ''}

  <h2>Nächste Termine</h2>
  <table><tbody>${zeilen || '<tr><td>Zurzeit stehen keine kommenden Spiele im Plan.</td></tr>'}</tbody></table>

  <footer>
    <p>Quellen: <a href="https://tsb-horkheim-hunters.de/calendar">tsb-horkheim-hunters.de</a> (TSB Hunters) und
    <a href="https://www.alsco-hbf.de/">alsco-hbf.de</a> (Sport-Union Neckarsulm).
    Der Kalender wird zweimal täglich neu gebaut. Angesetzte Zeiten können sich ändern —
    maßgeblich bleiben die Quellen.</p>
  </footer>
</main>
<script>
  // Adresse aus dem tatsächlichen Aufrufort ableiten, damit sie auch stimmt,
  // wenn die Seite unter einer anderen Adresse liegt.
  var basis = location.href.replace(/index\\.html$/, '').replace(/[^/]*$/, '');
  var adresse = basis + ${JSON.stringify(dateiname)};
  document.getElementById('adresse').value = adresse;
  document.getElementById('knopf').href = adresse.replace(/^https?:/, 'webcal:');
  var zweite = ${zweiteDatei ? JSON.stringify(zweiteDatei) : 'null'};
  if (zweite) {
    var zweiteAdresse = basis + zweite;
    document.getElementById('adresse-zwei').value = zweiteAdresse;
    document.getElementById('knopf-zwei').href = zweiteAdresse.replace(/^https?:/, 'webcal:');
  }
</script>
</body>
</html>
`;
}
