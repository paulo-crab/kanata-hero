// Task 6.4, automated half: static accessibility lint over game/css, game/index.html and game/src,
// plus the kit's contrast checker. The runtime half (focus order, traps, live region, reduced motion,
// larger text, high contrast in the rendered page) is in ACCESSIBILITY.md and game/tools/browser-check.mjs.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { GAME_ROOT, REPO_ROOT, repoPath } from '../harness/index.js';

const walk = (d, ext) => (existsSync(d) ? readdirSync(d, { withFileTypes: true }).flatMap((e) =>
  (e.isDirectory() ? walk(path.join(d, e.name), ext) : e.name.endsWith(ext) ? [path.join(d, e.name)] : [])) : []);

const cssFiles = walk(path.join(GAME_ROOT, 'css'), '.css');
const jsFiles = walk(path.join(GAME_ROOT, 'src'), '.js');
const html = readFileSync(path.join(GAME_ROOT, 'index.html'), 'utf8');
const tokens = readFileSync(repoPath('/art-direction/ui-kit/tokens.css'), 'utf8');
const stripComments = (s) => s.replace(/\/\*[\s\S]*?\*\//g, '');
const allCss = cssFiles.map((f) => ({ f: path.relative(GAME_ROOT, f), text: stripComments(readFileSync(f, 'utf8')) }));

test('the kit type scale has nothing below 16 px', () => {
  const sizes = [...tokens.matchAll(/--text-[a-z0-9]+:\s*(\d+(?:\.\d+)?)px/g)].map((m) => Number(m[1]));
  assert.ok(sizes.length >= 5);
  for (const s of sizes) assert.ok(s >= 16, `token size ${s}px`);
});

test('game css sets font sizes only from the kit scale or at 16 px and up', () => {
  for (const { f, text } of allCss) {
    for (const m of text.matchAll(/font-size:\s*([^;}]+)/g)) {
      const v = m[1].trim();
      if (/^var\(--text-/.test(v)) continue;
      const px = v.match(/^(\d+(?:\.\d+)?)px$/);
      const rem = v.match(/^(\d+(?:\.\d+)?)rem$/);
      const ok = (px && Number(px[1]) >= 16) || (rem && Number(rem[1]) >= 1) || /^(inherit|1em|100%|larger)$/.test(v);
      assert.ok(ok, `${f}: font-size ${v}`);
    }
    assert.doesNotMatch(text, /font:\s*[^;]*\b(1[0-5]|[0-9])px\b/, `${f}: font shorthand under 16 px`);
  }
});

test('game css takes colour from kit tokens only (no hex, rgb or named colour literals)', () => {
  for (const { f, text } of allCss) {
    const body = text.replace(/@import[^;]+;/g, '');
    assert.doesNotMatch(body, /#[0-9a-fA-F]{3,8}\b/, `${f}: hex literal`);
    assert.doesNotMatch(body, /\brgba?\(\s*\d/, `${f}: rgb literal`);
    assert.doesNotMatch(body, /\bhsla?\(/, `${f}: hsl literal`);
  }
});

test('game css imports the kit tokens by path', () => {
  assert.ok(allCss.some(({ text }) => /@import url\(["']?\/art-direction\/ui-kit\/tokens\.css["']?\)/.test(text)));
});

test('focus ring uses the --focus token and is never removed', () => {
  const joined = allCss.map((c) => c.text).join('\n');
  assert.match(joined, /:focus-visible\s*\{[^}]*var\(--focus\)/);
  assert.doesNotMatch(joined, /outline:\s*(none|0)\b(?![^}]*:focus-visible)/, 'outline removed without a replacement');
});

test('motion in css is guarded by prefers-reduced-motion or the .rm class', () => {
  const joined = allCss.map((c) => c.text).join('\n');
  const animates = /\banimation(-name)?\s*:|\btransition\s*:/.test(joined);
  if (animates) assert.match(joined, /prefers-reduced-motion|\.rm\b/);
});

test('index.html: language, polite live region, no positive tabindex, no audio', () => {
  assert.match(html, /<html[^>]*\blang="en"/);
  assert.match(html, /aria-live="polite"/);
  assert.doesNotMatch(html, /tabindex="[1-9]/);
  assert.doesNotMatch(html, /<audio|autoplay/i);
});

test('game/src never sets a positive tabindex or traps Tab', () => {
  for (const f of jsFiles) {
    const t = readFileSync(f, 'utf8');
    assert.doesNotMatch(t, /tabindex["'\s=:]+["']?[1-9]/i, `${f}: positive tabindex`);
    assert.doesNotMatch(t, /key\s*===?\s*['"]Tab['"][^;{]*preventDefault|preventDefault[^;]*['"]Tab['"]/, `${f}: Tab trapped`);
  }
});

// These become real once the UI team's stylesheet defines the settings classes; todo until then.
test('stylesheet defines the settings classes .rm, .large-text and .hc', {
  todo: allCss.some(({ text }) => /\.rm\b/.test(text) && /\.large-text\b/.test(text) && /\.hc\b/.test(text)) ? false : 'UI team css not merged yet',
}, () => {
  const joined = allCss.map((c) => c.text).join('\n');
  for (const c of ['.rm', '.large-text', '.hc']) assert.ok(joined.includes(c), c);
});

const PY = process.env.KH_PY || 'python3';
const noPython = spawnSync(PY, ['--version']).error ? `python not found (${PY}); set KH_PY` : false;
test('kit contrast checker passes (WCAG AA for every text-on-panel pair in tokens.css)', { skip: noPython }, () => {
  const r = spawnSync(PY, ['art-direction/ui-kit/check_contrast.py'], { cwd: REPO_ROOT, encoding: 'utf8', timeout: 60000 });
  assert.equal(r.status, 0, r.stdout + r.stderr);
});
