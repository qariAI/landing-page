// Qari AI — Live Tajweed Demo Worker
// Deploy to: jolly-firefly-cb72 (Cloudflare Workers)
// Secret required: GEMINI_API_KEY

const ALLOWED_ORIGINS = ['https://qariai.app', 'https://www.qariai.app'];

function getCorsHeaders(request) {
  const origin = request.headers.get('Origin') || '';
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };
}

const AYAHS = {
  'fatiha-1': { arabic: 'بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ', ref: 'Al-Fatiha 1:1' },
  'fatiha-2': { arabic: 'الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ', ref: 'Al-Fatiha 1:2' },
  'fatiha-7': { arabic: 'صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ', ref: 'Al-Fatiha 1:7' },
  'ikhlas-1': { arabic: 'قُلْ هُوَ اللَّهُ أَحَدٌ', ref: 'Al-Ikhlas 112:1' },
  'ikhlas-2': { arabic: 'اللَّهُ الصَّمَدُ', ref: 'Al-Ikhlas 112:2' },
  'ikhlas-4': { arabic: 'وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ', ref: 'Al-Ikhlas 112:4' },
};

// Simple in-memory rate limiting (per IP, resets per isolate lifecycle ~few minutes)
const rateLimitMap = new Map();
const RATE_LIMIT = 5; // max 5 requests per IP per isolate

function isRateLimited(ip) {
  const count = rateLimitMap.get(ip) || 0;
  if (count >= RATE_LIMIT) return true;
  rateLimitMap.set(ip, count + 1);
  return false;
}

async function analyzeRecitation(audioBase64, mimeType, ayah, apiKey) {
  const prompt = `You are a tajweed (Quranic recitation rules) expert evaluating a student's recitation.

The student is reciting: "${ayah.arabic}" (${ayah.ref})

Evaluate ONLY tajweed quality. Return a JSON object with exactly these fields:
{
  "tajweed_score": <integer 0-100>,
  "grade": <"Excellent" | "Good" | "Needs Work" | "Keep Trying">,
  "top_mistake": <string, one specific tajweed issue found, or null if none>,
  "encouragement": <string, one short motivational sentence in English>
}

Be encouraging but honest. Score 90+ only for near-perfect tajweed.`;

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          parts: [
            { text: prompt },
            { inline_data: { mime_type: mimeType, data: audioBase64 } }
          ]
        }],
        generationConfig: {
          temperature: 0.2,
          responseMimeType: 'application/json',
        }
      })
    }
  );

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Gemini API error: ${response.status} ${err}`);
  }

  const data = await response.json();
  const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error('Empty response from Gemini');

  return JSON.parse(text);
}

export default {
  async fetch(request, env) {
    const cors = getCorsHeaders(request);

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: cors });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: cors });
    }

    // Rate limiting
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (isRateLimited(ip)) {
      return new Response(JSON.stringify({ error: 'Too many requests. Try again shortly.' }), {
        status: 429,
        headers: { ...cors, 'Content-Type': 'application/json' }
      });
    }

    try {
      const body = await request.json();
      const { audio, mimeType, ayahId } = body;

      if (!audio || !mimeType || !ayahId) {
        return new Response(JSON.stringify({ error: 'Missing required fields' }), {
          status: 400,
          headers: { ...cors, 'Content-Type': 'application/json' }
        });
      }

      const ayah = AYAHS[ayahId];
      if (!ayah) {
        return new Response(JSON.stringify({ error: 'Unknown ayah' }), {
          status: 400,
          headers: { ...cors, 'Content-Type': 'application/json' }
        });
      }

      const result = await analyzeRecitation(audio, mimeType, ayah, env.GEMINI_API_KEY);

      return new Response(JSON.stringify(result), {
        headers: { ...cors, 'Content-Type': 'application/json' }
      });

    } catch (err) {
      console.error(err);
      return new Response(JSON.stringify({ error: 'Analysis failed. Please try again.' }), {
        status: 500,
        headers: { ...cors, 'Content-Type': 'application/json' }
      });
    }
  }
};
