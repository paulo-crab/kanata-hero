// Confidence labels. The three labels of the input-interpretation spec; the manifest's per-row
// `verification` values are the same three words. Nothing here claims detection.

/** @typedef {'observed'|'player_confirmed'|'external_only'} Confidence */
export const CONFIDENCE_LABELS = Object.freeze({
  observed: 'Observed output',
  player_confirmed: 'Player confirmed',
  external_only: 'Not observable here',
});

/** Honesty order, weakest first: the weakest of several rows is the one a card may state. */
const ORDER = ['external_only', 'player_confirmed', 'observed'];

export function isConfidence(c) {
  return ORDER.includes(c);
}

export function confidenceLabel(c) {
  if (!isConfidence(c)) throw new RangeError(`Unknown confidence: ${c}`);
  return CONFIDENCE_LABELS[c];
}

/** The weakest confidence of the given list (an empty list is `observed`: nothing weaker is claimed). */
export function weakestConfidence(list) {
  let best = 2;
  for (const c of list) {
    const i = ORDER.indexOf(c);
    if (i < 0) throw new RangeError(`Unknown confidence: ${c}`);
    if (i < best) best = i;
  }
  return ORDER[best];
}
