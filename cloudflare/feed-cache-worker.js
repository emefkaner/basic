// Cloudflare Worker: Zwischenspeicher für /feed.xml.
//
// Zweck: Podcast-Verzeichnisse fragen den Feed viel öfter ab, als sich etwas
// ändert — Render (Gratis-Plan) schläft nur nach 15 Minuten OHNE Aufruf ein,
// jeder Aufruf weckt ihn sofort wieder. Fragt irgendwer öfter als alle 15
// Minuten an, bleibt Render dauerhaft wach und die 750 Gratis-Instanzstunden
// sind schnell aufgebraucht.
//
// Zwei Wege, wie der Zwischenspeicher aktuell bleibt:
//   1. Aktiv: Die App auf Render ruft nach jeder Änderung (neue Folge,
//      Einstellungen) selbst /purge?secret=… auf. Render ist in diesem
//      Moment ohnehin wach — kostet also nichts zusätzlich. Das deckt den
//      Normalfall „ich habe etwas geändert" sofort ab.
//   2. Passiv, als Rückfalllösung: Ohne Leerung hält der Zwischenspeicher
//      höchstens CACHE_SEKUNDEN, danach holt der NÄCHSTE tatsächliche
//      Aufruf einmal frisch nach — nie von selbst, nur wenn wirklich jemand
//      fragt. Das fängt eine EINGEPLANTE Folge auf, die ohne dein Zutun zu
//      ihrer Zeit fällig wird. WICHTIG: CACHE_SEKUNDEN muss GRÖSSER als 15
//      Minuten sein — sonst holt der Zwischenspeicher öfter nach, als Render
//      zum Einschlafen braucht, und nichts ist gewonnen.
//
// CACHE_SEKUNDEN steht auf 48 Stunden: Eingeplante Folgen liegen laut Nutzer
// höchstens 48 h in der Zukunft, und eine Verzögerung bis zu dieser Grenze ist
// ausdrücklich in Ordnung. So kann Render tagelang durchschlafen, wenn niemand
// etwas ändert und niemand den Feed abruft — es wacht dann höchstens alle
// 48 Stunden einmal kurz auf, statt stündlich.
//
// Ursprungsadresse: die bestehende App bleibt unverändert erreichbar, dieser
// Worker fragt sie nur seltener ab, als es Verzeichnisse/Apps sonst täten.

const URSPRUNG = 'https://cinespasten.emefka.com/feed.xml';
const CACHE_SEKUNDEN = 48 * 60 * 60; // 48 Stunden Rückfalllösung — siehe Begründung oben
const CACHE_KEY = new Request('https://feed-cache.internal/feed.xml', { method: 'GET' });

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const cache = caches.default;

    if (url.pathname === '/purge') {
      if (!env.PURGE_SECRET || url.searchParams.get('secret') !== env.PURGE_SECRET) {
        return new Response('Falsches oder fehlendes Geheimnis', { status: 403 });
      }
      await cache.delete(CACHE_KEY);
      return new Response('ok');
    }

    let antwort = await cache.match(CACHE_KEY);
    if (antwort) return antwort;

    const ursprungsAntwort = await fetch(URSPRUNG, {
      headers: { 'User-Agent': 'podcast3r-feed-cache-worker' },
    });

    // Fehler beim Ursprung (Render schläft/deployed gerade) NICHT zwischenspeichern —
    // sonst hängt der Fehler bis zu 48 Stunden fest.
    if (!ursprungsAntwort.ok) return ursprungsAntwort;

    const body = await ursprungsAntwort.arrayBuffer();
    antwort = new Response(body, {
      status: 200,
      headers: {
        'content-type': ursprungsAntwort.headers.get('content-type') || 'application/rss+xml; charset=utf-8',
        'cache-control': `public, max-age=${CACHE_SEKUNDEN}`,
      },
    });

    ctx.waitUntil(cache.put(CACHE_KEY, antwort.clone()));
    return antwort;
  },
};
