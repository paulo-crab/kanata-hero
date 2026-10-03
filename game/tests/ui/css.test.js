import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import path from 'node:path';

import { INSET_STAGE_RECT, STAGE_W } from '../../src/shared/layout.js';
import { REPO, GAME, read } from './fixtures.js';

const FILES = ['main.css', 'components.css', 'screens.css'].map((f) => `game/css/${f}`);
const strip = (css) => css.replace(/\/\*[^]*?\*\//g, '');
const TOKENS = strip(read('art-direction/ui-kit/tokens.css'));
const tokenNames = new Set([...TOKENS.matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1]));
/** Custom properties set inline by the components (a number each), not kit tokens. */
const LOCAL_PROPS = new Set(['--w', '--gap', '--key-h']);

const rules = (css) => [...strip(css).matchAll(/([^{}]+)\{([^{}]*)\}/g)].map((m) => ({ sel: m[1].trim(), body: m[2] }));

test('stylesheets import the kit tokens by reference and the files exist', () => {
  const main = read('game/css/main.css');
  assert.match(main, /@import url\("\/art-direction\/ui-kit\/tokens\.css"\)/);
  for (const m of main.matchAll(/@import url\("([^"]+)"\)/g)) {
    assert.ok(existsSync(path.join(REPO, m[1])), `${m[1]} exists`);
  }
  assert.doesNotMatch(main, /:root\s*\{/, 'no token redefinition at the root');
});

test('stylesheet lint: no colour literals, only kit tokens', () => {
  for (const f of FILES) {
    const css = strip(read(f)).replace(/url\([^)]*\)/g, '');
    assert.doesNotMatch(css, /#[0-9a-fA-F]{3,8}\b/, `${f}: hex colour`);
    assert.doesNotMatch(css, /\b(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklch|oklab)\(/, `${f}: colour function`);
    for (const m of css.matchAll(/(?:^|[;{\s])(?:color|background|background-color|border(?:-[a-z]+)?|outline|fill|stroke|box-shadow)\s*:\s*([^;}]+)/g)) {
      const v = m[1].replace(/var\([^)]*\)/g, '').replace(/color-mix\([^)]*\)/g, '');
      assert.doesNotMatch(v, /\b(?:black|white|red|green|blue|gray|grey|yellow|orange|purple|pink|silver|navy|teal|gold|coral|violet)\b/i, `${f}: named colour in "${m[1].trim()}"`);
    }
  }
});

test('stylesheet lint: every var() resolves to a kit token (or a documented local prop)', () => {
  for (const f of FILES) {
    const css = strip(read(f));
    const defined = new Set([...css.matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1]));
    for (const m of css.matchAll(/var\((--[\w-]+)/g)) {
      assert.ok(tokenNames.has(m[1]) || LOCAL_PROPS.has(m[1]), `${f}: ${m[1]} is not a kit token`);
    }
    for (const d of defined) {
      assert.ok(tokenNames.has(d) || LOCAL_PROPS.has(d), `${f}: declares ${d}, which is not a kit token (only overrides of kit tokens are allowed)`);
    }
  }
});

test('stylesheet lint: type sizes come from the scale; nothing below 16 px; overrides only for larger text', () => {
  for (const f of FILES) {
    for (const { sel, body } of rules(read(f))) {
      for (const m of body.matchAll(/font-size\s*:\s*([^;]+)/g)) {
        assert.match(m[1].trim(), /^var\(--text-[\w-]+\)$/, `${f} ${sel}: font-size ${m[1]}`);
      }
      for (const m of body.matchAll(/(?:^|[;\s])font\s*:\s*([^;]+)/g)) {
        const noLineHeight = m[1].replace(/\/\s*[\d.]+(?:px)?/g, '').replace(/var\([^)]*\)/g, '');
        assert.doesNotMatch(noLineHeight, /\d+(?:\.\d+)?(?:px|rem|em|pt)/, `${f} ${sel}: literal font size in font shorthand`);
      }
      for (const m of body.matchAll(/(--text-[\w-]+)\s*:\s*([\d.]+)px/g)) {
        assert.equal(sel, '.stage.large-text', `${f}: only larger text overrides ${m[1]}`);
        assert.ok(Number(m[2]) >= 16, `${f}: ${m[1]} is ${m[2]} px`);
      }
      assert.doesNotMatch(body, /font-family\s*:\s*(?!\s|var\()/, `${f} ${sel}: font-family must be a token`);
    }
  }
  const tokens = Object.fromEntries([...TOKENS.matchAll(/(--text-[\w-]+)\s*:\s*(\d+)px/g)].map((m) => [m[1], Number(m[2])]));
  for (const [n, px] of Object.entries(tokens)) assert.ok(px >= 16, `${n} = ${px}`);
});

test('z-layers come from the kit tokens', () => {
  for (const f of FILES) {
    for (const { sel, body } of rules(read(f))) {
      for (const m of body.matchAll(/z-index\s*:\s*([^;]+)/g)) {
        assert.match(m[1].trim(), /^(?:var\(--z-[\w-]+\)|calc\(var\(--z-[\w-]+\) \+ \d+\))$/, `${f} ${sel}: z-index ${m[1]}`);
      }
    }
  }
});

test('focus ring: kit focus colour, 2 px ring and a 2 px ink gap', () => {
  const main = strip(read('game/css/main.css'));
  assert.match(main, /:focus-visible\s*\{[^}]*outline:\s*2px solid var\(--focus\)[^}]*box-shadow:\s*0 0 0 2px var\(--ink\)/);
});

test('accessibility modes exist: .rm, .large-text, .hc, and the OS reduced-motion query', () => {
  const main = read('game/css/main.css');
  assert.match(main, /\.stage\.rm\b/);
  assert.match(main, /\.stage\.large-text\s*\{[^}]*--text-base:\s*22px/);
  assert.match(main, /\.stage\.hc\s*\{[^}]*--border:\s*var\(--paper\)/);
  assert.match(main, /@media \(prefers-reduced-motion: reduce\)/);
});

test('inset and dialogue CSS match the stage geometry (inset rect x 16..588, dialogue starts at 592)', () => {
  const inset = rules(read('game/css/components.css')).find((r) => r.sel === '.kh-inset').body;
  assert.match(inset, /left:\s*var\(--stage-margin\)/);
  assert.match(inset, /bottom:\s*var\(--stage-margin\)/);
  const width = Number(/width:\s*(\d+)px/.exec(inset)[1]);
  assert.equal(width, INSET_STAGE_RECT.w);
  assert.equal(16 + width, INSET_STAGE_RECT.x + INSET_STAGE_RECT.w);
  const dlg = rules(read('game/css/components.css')).find((r) => r.sel === '.kh-dialogue').body;
  const dw = Number(/width:\s*(\d+)px/.exec(dlg)[1]);
  const dialogueLeft = STAGE_W - 16 - dw;
  assert.ok(dialogueLeft >= INSET_STAGE_RECT.x + INSET_STAGE_RECT.w, `dialogue starts at ${dialogueLeft}`);
});

test('no stylesheet references audio or a pixel font', () => {
  for (const f of FILES) {
    const css = read(f);
    assert.doesNotMatch(css, /audio|@font-face|Press Start|pixel font/i, f);
  }
  void GAME;
});
