#!/usr/bin/env node
// Task 6.3: browser checks at 1366x768 and 1920x1080 with the keyboard inset open.
//
//   node game/tools/browser-check.mjs --model-only        # no browser: camera + inset model over level 01
//   python3 game/tools/serve.py &                         # then, in another shell:
//   node game/tools/browser-check.mjs [--url URL] [--out DIR]
//
// The live part needs Playwright, a DEV-ONLY tool that is NOT in package.json and not a runtime
// dependency. Install it outside the repo tree or ignore the lockfile, for example:
//   npm install --no-save --prefix /tmp/kh-playwright playwright && npx --prefix /tmp/kh-playwright playwright install chromium
//   NODE_PATH=/tmp/kh-playwright/node_modules node game/tools/browser-check.mjs
// (Alternatively drive the same checkpoints by hand with the Browser tools; see tests/checks/ACCESSIBILITY.md.)
//
// Exit codes: 0 pass, 1 an assertion failed (the cell is listed), 2 the live part was skipped (no Playwright).
import { mkdirSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  loadRealData, insetViolations, insetStageRect, level01Legs, walkScript, DIRS, STAGE_ZOOM,
} from '../tests/harness/index.js';
import { INSET_STAGE_RECT } from '../src/shared/layout.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const flag = (n) => args.includes(`--${n}`);
const opt = (n, d) => (args.includes(`--${n}`) ? args[args.indexOf(`--${n}`) + 1] : d);
const URL_ = opt('url', 'http://127.0.0.1:8000/game/index.html');
const OUT = path.resolve(opt('out', path.join(here, '..', 'tests', 'e2e', 'screenshots')));
const VIEWPORTS = [{ w: 1366, h: 768 }, { w: 1920, h: 1080 }];

const data = loadRealData();
let failed = false;

// ---- 1. Model assertion (same camera model as design/levels/SCHEMA.md) ------------------------
for (const vp of VIEWPORTS) {
  const zoom = Math.max(1, Math.floor(Math.min(vp.w / 320, vp.h / 180)));
  const v = insetViolations(data);
  const avatar = v.filter((x) => x.what === 'avatar');
  const target = v.filter((x) => x.what === 'target');
  console.log(`[model ${vp.w}x${vp.h} zoom x${zoom}] avatar overlaps: ${avatar.length}, target overlaps: ${target.length}`);
  for (const x of avatar) { console.log(`  FAIL ${x.leg}: avatar cell (${x.cell}) is inside the inset`); failed = true; }
  for (const x of target) console.log(`  WARN ${x.leg}: avatar cell (${x.cell}), target (${x.target}) drawn under the inset`);
}
if (flag('model-only')) process.exit(failed ? 1 : 0);

// ---- 2. Live page ----------------------------------------------------------------------------
let chromium;
try {
  const require = createRequire(import.meta.url);
  ({ chromium } = require('playwright'));
} catch {
  console.log('SKIP live checks: Playwright is not installed (dev-only, see the header of this file).');
  process.exit(failed ? 1 : 2);
}

mkdirSync(OUT, { recursive: true });
const CELL_MS = 300;       // a cell move is 16 steps = 266.7 ms; one tap per cell plus slack
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const legs = Object.fromEntries(level01Legs(data).map((l) => [l.id, l]));

const browser = await chromium.launch();
try {
  for (const vp of VIEWPORTS) {
    const page = await browser.newPage({ viewport: { width: vp.w, height: vp.h } });
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
    await page.goto(URL_);
    await sleep(500);
    const shot = (name) => page.screenshot({ path: path.join(OUT, `${name}-${vp.w}x${vp.h}.png`) });

    // Stage scale: the 1280x720 logical stage is scaled by CSS to the letterboxed window.
    const stage = await page.locator('#stage').boundingBox();
    const scale = stage.width / 1280;
    const insetSel = '[data-component="inset"], .inset, #inset';

    // Where the avatar's feet are on screen: the camera model fixes them at AVATAR_SCREEN (320x180 view) unless clamped.
    const assertOutsideInset = async (label, cell, targetCell) => {
      const box = await page.locator(insetSel).first().boundingBox().catch(() => null);
      if (!box) { console.log(`  FAIL ${label}: no inset element found (${insetSel})`); failed = true; return; }
      const want = insetStageRect(STAGE_ZOOM);
      const got = { x: (box.x - stage.x) / scale, y: (box.y - stage.y) / scale, w: box.width / scale, h: box.height / scale };
      for (const k of ['x', 'y', 'w', 'h']) {
        if (Math.abs(got[k] - want[k]) > 2) { console.log(`  FAIL ${label}: inset ${k}=${got[k].toFixed(1)}, expected ${want[k]} (${JSON.stringify(INSET_STAGE_RECT)})`); failed = true; }
      }
      const bad = insetViolations(data).filter((x) => x.cell[0] === cell[0] && x.cell[1] === cell[1] && x.what === 'avatar');
      for (const x of bad) { console.log(`  FAIL ${label}: avatar cell (${x.cell}) overlaps the inset`); failed = true; }
      void targetCell;
    };

    const press = async (key, hold = 60) => { await page.keyboard.down(key); await sleep(hold); await page.keyboard.up(key); };
    const walk = async (leg) => {
      for (const s of walkScript(leg.cells)) { await press(s.step); await sleep(CELL_MS); }
    };
    void DIRS;

    console.log(`[live ${vp.w}x${vp.h}] scale ${scale.toFixed(3)}`);
    await press('Escape'); await sleep(1200);           // skip setup, arrival plays
    await shot('arrival');
    await walk(legs.arrival); await press('Enter'); await sleep(300);
    for (let i = 0; i < 3; i += 1) { await press('Enter'); await sleep(200); }
    await press('Escape'); await sleep(300);            // popup
    for (let i = 0; i < 3; i += 1) { await press('Enter'); await sleep(200); }
    await press('q'); await sleep(200); await press('q'); await press('`'); await press('?'); await sleep(200);
    await shot('layout-help'); await press('Escape'); await sleep(200);
    await walk(legs['loop-down']);
    await assertOutsideInset('lap', legs['loop-down'].cells.at(-1), legs['loop-down'].target);
    await shot('lap');
    for (const id of ['loop-right', 'loop-up', 'loop-left']) await walk(legs[id]);
    await press('Enter'); await sleep(200);
    await walk(legs['stop-north']); await walk(legs['stop-west']); await sleep(300);
    await shot('label');
    for (const ch of 'west') await press(ch);
    await walk(legs['stop-south']); await walk(legs['stop-east']); await press('Enter'); await sleep(300);
    await shot('recall');
    if (errors.length) { console.log(`  FAIL console errors: ${errors.join(' | ')}`); failed = true; }
    await page.close();
  }
} finally {
  await browser.close();
}
console.log(failed ? 'FAILED' : 'PASSED');
process.exit(failed ? 1 : 0);
