import Anthropic from '@anthropic-ai/sdk';
import { config } from './config.js';

// Erzeugt aus Transkript (+ optionalem Titel) einen Podcast-Infotext.
// Nutzt Claude, wenn ein Anthropic-Key vorhanden ist; sonst einen einfachen Fallback.
export async function generateDescription({ transcript, title }) {
  const clean = (transcript || '').trim();

  if (!config.anthropicKey) {
    return fallbackDescription(clean);
  }

  const client = new Anthropic({ apiKey: config.anthropicKey });

  const prompt = [
    'Du schreibst die Beschreibung (Show Notes) für eine Podcast-Folge.',
    'Schreibe auf Deutsch, ansprechend und natürlich, in der 2.-3. Person aus Sicht des Podcasts.',
    'Ziel: neugierig machen, ohne zu übertreiben. Keine Emojis-Flut, keine Hashtags.',
    'Struktur: 2-4 Sätze Fließtext, danach optional 3-5 Stichpunkte mit den Kernthemen.',
    'Gib NUR den Beschreibungstext zurück, keine Vorrede.',
    '',
    title ? `Titel der Folge: ${title}` : '',
    '',
    'Transkript der Folge:',
    clean.slice(0, 12000) || '(kein Transkript verfügbar)',
  ].join('\n');

  try {
    const msg = await client.messages.create({
      model: 'claude-sonnet-5',
      max_tokens: 700,
      messages: [{ role: 'user', content: prompt }],
    });
    const text = msg.content
      ?.filter((b) => b.type === 'text')
      .map((b) => b.text)
      .join('')
      .trim();
    return text || fallbackDescription(clean);
  } catch (err) {
    console.error('Claude-Beschreibung fehlgeschlagen:', err.message);
    return fallbackDescription(clean);
  }
}

// Sehr einfacher Text, falls keine KI verfügbar ist: erste Sätze des Transkripts.
function fallbackDescription(transcript) {
  if (!transcript) return 'In dieser Folge geht es um …';
  const firstPart = transcript.split(/(?<=[.!?])\s+/).slice(0, 3).join(' ');
  return firstPart.length > 400 ? `${firstPart.slice(0, 397)}…` : firstPart;
}
