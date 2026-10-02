// Repo-relative locations used by every test. No wall-clock, no randomness.
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
export const GAME_ROOT = path.resolve(here, '..', '..');
export const REPO_ROOT = path.resolve(GAME_ROOT, '..');

/** Absolute path of a root-absolute URL path such as '/design/levels/world.json'. */
export function repoPath(urlPath) {
  return path.join(REPO_ROOT, urlPath.replace(/^\/+/, ''));
}
