#!/usr/bin/env node
// Guards against whole-page rewrites that land through the GitHub web UI (or
// anywhere else): for every commit in <base>..<head>, each .html file that was
// modified (not added, deleted or renamed) is compared with the same file in
// the commit's parent. The check fails if
//   - the file lost more than 40% of its lines, or
//   - its <title> changed AND more than 30% of its lines changed (a title edit on
//     its own, e.g. an SEO tweak, is fine; a new title on a mostly-new body means
//     the page was replaced).
// A commit whose message contains "[allow-rewrite]" is skipped, for deliberate
// rewrites and SEO title edits.
//
// No dependencies. Usage:
//   node scripts/check-rewrites.js <base> <head>   # every commit in base..head
//   node scripts/check-rewrites.js "" HEAD         # just the head commit
// <base> may be empty or all zeros (first push / manual run): only <head> is checked.
//
// Exits 1 if any commit trips the guard, 0 otherwise.

const { execFileSync } = require('child_process');

const MAX_DROP = 0.4;
const MAX_TITLE_CHURN = 0.3;
const OVERRIDE = '[allow-rewrite]';

const git = (args) => execFileSync('git', args, { encoding: 'utf8', maxBuffer: 256 * 1024 * 1024, stdio: ['ignore', 'pipe', 'pipe'] });
const gitOk = (args) => { try { git(args); return true; } catch { return false; } };

const [base = '', head = 'HEAD'] = process.argv.slice(2);

let commits;
if (base && !/^0+$/.test(base) && gitOk(['cat-file', '-e', `${base}^{commit}`])) {
  commits = git(['rev-list', '--reverse', `${base}..${head}`]).split('\n').filter(Boolean);
} else {
  commits = [git(['rev-parse', head]).trim()];
}

const lineCount = (s) => s.split('\n').length - (s.endsWith('\n') ? 1 : 0);
const titleOf = (s) => {
  const m = s.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  return m ? m[1].replace(/\s+/g, ' ').trim() : null;
};

const problems = [];
let checked = 0;
let skipped = 0;
for (const c of commits) {
  const parent = git(['rev-list', '--parents', '-n', '1', c]).trim().split(' ')[1];
  if (!parent) continue; // root commit, nothing to compare with
  const short = c.slice(0, 7);
  const subject = git(['log', '-1', '--format=%s', c]).trim();
  if (git(['log', '-1', '--format=%B', c]).includes(OVERRIDE)) {
    console.log(`${short}: ${OVERRIDE} in commit message, skipping.`);
    skipped++;
    continue;
  }
  const files = git(['diff', '--name-only', '--diff-filter=M', '-z', parent, c]).split('\0').filter((f) => f.endsWith('.html'));
  for (const f of files) {
    checked++;
    const before = git(['show', `${parent}:${f}`]);
    const after = git(['show', `${c}:${f}`]);
    const lb = lineCount(before);
    const la = lineCount(after);
    const drop = lb ? (lb - la) / lb : 0;
    if (drop > MAX_DROP) {
      problems.push(`${short} (${subject}): ${f} lost ${Math.round(drop * 100)}% of its lines (${lb} -> ${la})`);
    }
    const tb = titleOf(before);
    const ta = titleOf(after);
    if (tb !== ta) {
      // Lines changed = the larger of lines added / removed (a replaced line counts once).
      const [added, removed] = git(['diff', '--numstat', parent, c, '--', f]).trim().split(/\s+/).slice(0, 2).map(Number);
      const churn = Math.max(added, removed) / Math.max(lb, la, 1);
      if (churn > MAX_TITLE_CHURN) {
        problems.push(`${short} (${subject}): ${f} <title> changed ("${tb ?? '(none)'}" -> "${ta ?? '(none)'}") and ${Math.round(churn * 100)}% of its lines changed`);
      }
    }
  }
}

if (!problems.length) {
  console.log(`OK: ${commits.length} commit(s), ${checked} modified .html file(s) checked, ${skipped} commit(s) skipped by ${OVERRIDE}.`);
  process.exit(0);
}
console.log(problems.join('\n'));
console.log(`\n${problems.length} problem(s) found. This looks like a page was replaced wholesale.`);
console.log(`If the rewrite is deliberate, put ${OVERRIDE} in the commit message (amend or push a new commit),`);
console.log('otherwise restore the file from the parent commit: git checkout <parent> -- <file>');
process.exit(1);
