// Fixtures for the UI tests: real data files from the repo, and view-models shaped like the runtime's (contract 7).
// The fake layoutHelpModel below stands in for input.layoutHelpModel (workstream B): same output shape, built from the real manifest.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
export const REPO = path.resolve(here, '..', '..', '..');
export const GAME = path.join(REPO, 'game');
export const read = (rel) => readFileSync(path.join(REPO, rel), 'utf8');
export const readJson = (rel) => JSON.parse(read(rel));

export const LEVEL = readJson('design/levels/orientation/levels/01-the-lobby.json');
export const MAP = readJson('design/levels/orientation/map.json');
export const DISTRICT = readJson('design/levels/orientation/district.json');
export const MANIFEST = readJson('design/layout/layout-manifest.json');
export const PORTRAITS = readJson('art-direction/portraits/portraits-atlas.json');

import * as B from './vm-builders.js';

export * from './vm-builders.js';
export const dialogueVm = (id, o) => B.dialogueVmFrom(LEVEL, PORTRAITS, id, o);
