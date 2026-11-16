// POST /api/partner — emails a partnership application to salam@qariai.app via Brevo.
// Needs env var BREVO_API_KEY (Vercel > Settings > Environment Variables).
const TRACKS = { creator: 'Creator / Podcast', mosque: 'Mosque / Community', teacher: 'Teacher / Madrasah' };
const clean = (v, n) => String(v || '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n);
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

module.exports = async (req, res) => {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ ok: false }); }
  const b = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  if (b.company) return res.status(200).json({ ok: true }); // honeypot: silently drop bots
  const track = TRACKS[b.track] ? b.track : null;
  const name = clean(b.name, 120), email = clean(b.email, 160), country = clean(b.country, 80);
  const link = clean(b.link, 300), notes = clean(b.notes, 1500);
  if (!track || !name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !country || !link) {
    return res.status(400).json({ ok: false, error: 'invalid' });
  }
  const key = process.env.BREVO_API_KEY;
  if (!key) return res.status(500).json({ ok: false, error: 'not_configured' });
  const rows = [['Track', TRACKS[track]], ['Name', name], ['Email', email], ['Country', country], ['Link', link], ['About', notes || '-']];
  const html = '<table cellpadding="6">' + rows.map(([k, v]) => `<tr><td><b>${k}</b></td><td>${esc(v)}</td></tr>`).join('') + '</table>';
  try {
    const r = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: { 'api-key': key, 'content-type': 'application/json', accept: 'application/json' },
      body: JSON.stringify({
        sender: { name: 'QariAI Partners', email: 'salam@qariai.app' },
        to: [{ email: 'salam@qariai.app' }],
        replyTo: { email, name },
        subject: `Partnership application: ${TRACKS[track]} - ${name}`,
        htmlContent: html,
      }),
    });
    if (!r.ok) return res.status(502).json({ ok: false, error: 'send_failed' });
    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(502).json({ ok: false, error: 'send_failed' });
  }
};
