// POST /api/qaf — emails a Qaf Studio inquiry (beta signup, talent application, partnership) to salam@qariai.app via Brevo.
// Needs env var BREVO_API_KEY (already set for /api/partner).
const KINDS = {
  beta: 'Early access / Beta Lab',
  talent: 'Build with us (talent)',
  partner: 'Partnership / sponsorship',
};
const ROLES = ['Engineer', 'Designer', "Qur'an teacher", 'Linguist', 'Other'];
const ORGS = ['Masjid', 'School / madrasah', 'Youth tournament', 'Media', 'Other'];
const INTERESTS = ['Tajweed', 'Hifz', 'Games', 'Khatti'];
const clean = (v, n) => String(v || '').replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n);
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const pick = (arr, allowed) => (Array.isArray(arr) ? arr : []).map((x) => clean(x, 40)).filter((x) => allowed.includes(x));
const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

module.exports = async (req, res) => {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ ok: false }); }
  let b;
  try { b = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {}); } catch (e) { return res.status(400).json({ ok: false, error: 'invalid' }); }
  if (b.company) return res.status(200).json({ ok: true }); // honeypot: silently drop bots
  const kind = KINDS[b.kind] ? b.kind : null;
  const email = clean(b.email, 160);
  if (!kind || !EMAIL.test(email)) return res.status(400).json({ ok: false, error: 'invalid' });

  const name = clean(b.name, 120);
  const link = clean(b.link, 300);
  const notes = clean(b.notes, 1500);
  const country = clean(b.country, 80);
  const org = clean(b.org, 160);
  let rows = [['Type', KINDS[kind]], ['Email', email]];

  if (kind === 'beta') {
    rows.push(['Interests', pick(b.tags, INTERESTS).join(', ') || '-']);
  } else if (kind === 'talent') {
    const tags = pick(b.tags, ROLES);
    if (!name || !tags.length) return res.status(400).json({ ok: false, error: 'invalid' });
    rows.push(['Name', name], ['Roles', tags.join(', ')], ['Link', link || '-'], ['About', notes || '-']);
  } else {
    const tags = pick(b.tags, ORGS);
    if (!name || !org || !tags.length) return res.status(400).json({ ok: false, error: 'invalid' });
    rows.push(['Organisation type', tags.join(', ')], ['Organisation', org], ['Contact', name], ['Country', country || '-'], ['Message', notes || '-']);
  }

  const key = process.env.BREVO_API_KEY;
  if (!key) return res.status(500).json({ ok: false, error: 'not_configured' });
  const html = '<table cellpadding="6">' + rows.map(([k, v]) => `<tr><td><b>${esc(k)}</b></td><td>${esc(v)}</td></tr>`).join('') + '</table>';
  try {
    const r = await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: { 'api-key': key, 'content-type': 'application/json', accept: 'application/json' },
      body: JSON.stringify({
        sender: { name: 'Qaf Studio site', email: 'salam@qariai.app' },
        to: [{ email: 'salam@qariai.app' }],
        replyTo: name ? { email, name } : { email },
        subject: `Qaf Studio: ${KINDS[kind]}${name ? ' - ' + name : ''}`,
        htmlContent: html,
      }),
    });
    if (!r.ok) return res.status(502).json({ ok: false, error: 'send_failed' });
    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(502).json({ ok: false, error: 'send_failed' });
  }
};
