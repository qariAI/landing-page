#!/usr/bin/env node
// Consistency check across vercel.json, sitemap.xml and llms.txt.
// No dependencies. Run from anywhere: node scripts/check-routes.js
//
//   1. Every sitemap URL resolves to a real file (via a vercel.json rewrite,
//      <path>.html, or <path>/index.html).
//   2. Every vercel.json rewrite to a local .html file points at a file that
//      exists, and that page is in the sitemap (unless it is a utility page).
//   3. Every content / comparison page in the sitemap is linked from llms.txt,
//      so AI crawlers can find it. Legal and utility pages are exempt, and
//      /academy/* articles are only required if listed in ACADEMY_PINNED.
//   4. Every non-utility sitemap page has Open Graph / Twitter card tags
//      (og:title, og:description, og:image, og:url, og:type, twitter:card, twitter:image),
//      so shared links get a proper preview.
//
// Exits 1 if any check fails, 0 otherwise.

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const SITE = 'https://qariai.app';

// Pages that do not need a sitemap entry (check 2) or an llms.txt entry (check 3).
const UTILITY = new Set([
  '/', '/privacy', '/terms', '/delete-account', '/feedback', '/thank-you',
  '/challenge', // retired page, deliberately not promoted
]);
// Academy articles are discovered through the Academy hub link in llms.txt, so
// check 3 skips /academy/* unless the article is pinned here (i.e. it has been
// linked from llms.txt on purpose and must stay linked).
const ACADEMY_PINNED = new Set([
  '/academy/ai-quran',
  '/academy/ai-tajweed',
  '/academy/ai-hifz',
  '/academy/memorize-quran-at-home',
  '/academy/hifz-self-study-roadmap',
  '/academy/hifz-planner',
]);
// Translated trees mirror English pages; llms.txt lists the English originals.
const LOCALE_PREFIX = /^\/(ar|fr|ms)(\/|$)/;

const read = (f) => fs.readFileSync(path.join(ROOT, f), 'utf8');
const exists = (rel) => fs.existsSync(path.join(ROOT, rel));
const norm = (p) => {
  p = p.split('#')[0].split('?')[0].replace(/[.,;:!]+$/, '');
  if (p.length > 1) p = p.replace(/\/+$/, '');
  return p || '/';
};
const toPath = (url) => norm(url.startsWith(SITE) ? url.slice(SITE.length) || '/' : url);

const errors = [];
const fail = (check, msg) => errors.push(`[${check}] ${msg}`);

// ---- load ----
let vercel;
try {
  vercel = JSON.parse(read('vercel.json'));
} catch (e) {
  console.error(`vercel.json is not valid JSON: ${e.message}`);
  process.exit(1);
}
const rewrites = new Map();   // source path -> destination (local only)
for (const r of vercel.rewrites || []) {
  if (!/^https?:/.test(r.destination)) rewrites.set(norm(r.source), r.destination);
}
const redirects = new Map();  // source path -> destination path (internal only)
for (const r of vercel.redirects || []) {
  const d = /^https?:/.test(r.destination) ? (r.destination.startsWith(SITE) ? toPath(r.destination) : null) : norm(r.destination);
  if (d) redirects.set(norm(r.source), d);
}

const sitemap = [...read('sitemap.xml').matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/g)].map((m) => toPath(m[1]));
const llms = new Set(
  [...read('llms.txt').matchAll(/https?:\/\/qariai\.app[^\s)>\]"']*|\]\((\/[^)\s]*)\)/g)]
    .map((m) => toPath(m[1] || m[0]))
    .map((p) => redirects.get(p) || p)
);

// Resolve a URL path to a file on disk, or null.
function resolveFile(p) {
  if (rewrites.has(p)) {
    const dest = rewrites.get(p).split('?')[0].replace(/^\//, '');
    return exists(dest) ? dest : null;
  }
  if (p === '/') return exists('index.html') ? 'index.html' : null;
  const rel = p.slice(1);
  if (exists(`${rel}.html`)) return `${rel}.html`;
  if (exists(`${rel}/index.html`)) return `${rel}/index.html`;
  return null;
}

// ---- check 1: sitemap URLs resolve ----
const seen = new Set();
const sitemapFiles = new Set();
for (const p of sitemap) {
  if (seen.has(p)) { fail(1, `duplicate sitemap entry: ${p}`); continue; }
  seen.add(p);
  const file = resolveFile(p);
  if (!file) fail(1, `sitemap URL has no route or file: ${p}`);
  else sitemapFiles.add(file);
}

// ---- check 2: rewrite targets exist and are in the sitemap ----
const reported = new Set();
for (const [src, dest] of rewrites) {
  const file = dest.split('?')[0].replace(/^\//, '');
  if (!file.endsWith('.html')) continue;
  if (!exists(file)) { fail(2, `rewrite ${src} -> ${dest}: file does not exist`); continue; }
  if (sitemapFiles.has(file) || reported.has(file)) continue;
  if (UTILITY.has(src) || LOCALE_PREFIX.test(src)) continue;
  reported.add(file);
  fail(2, `${file} is routed (${src}) but no sitemap URL points at it`);
}

// ---- check 3: content pages are in llms.txt ----
for (const p of new Set(sitemap)) {
  if (UTILITY.has(p) || LOCALE_PREFIX.test(p)) continue;
  if (p.startsWith('/academy/') && !ACADEMY_PINNED.has(p)) continue;
  if (!llms.has(p)) fail(3, `in sitemap but not linked from llms.txt: ${p}`);
}

// ---- check 4: social preview tags ----
const OG_REQUIRED = [
  ['og:title', 'property'], ['og:description', 'property'], ['og:image', 'property'],
  ['og:url', 'property'], ['og:type', 'property'], ['twitter:card', 'name'], ['twitter:image', 'name'],
];
function hasMeta(html, key) {
  return [...html.matchAll(/<meta\b[^>]*>/gi)].some((m) =>
    new RegExp(`(?:property|name)=["']${key}["']`, 'i').test(m[0]) && /content=["'][^"']+["']/i.test(m[0]));
}
for (const p of new Set(sitemap)) {
  if (UTILITY.has(p)) continue;
  const file = resolveFile(p);
  if (!file) continue; // already reported by check 1
  const html = read(file);
  const missing = OG_REQUIRED.filter(([k]) => !hasMeta(html, k)).map(([k]) => k);
  if (missing.length) fail(4, `${file} (${p}) is missing: ${missing.join(', ')}`);
}

// ---- report ----
if (!errors.length) {
  console.log(`OK: ${sitemap.length} sitemap URLs, ${rewrites.size} rewrites, ${llms.size} llms.txt links.`);
  process.exit(0);
}
console.log(errors.join('\n'));
console.log(`\n${errors.length} problem(s) found.`);
process.exit(1);
