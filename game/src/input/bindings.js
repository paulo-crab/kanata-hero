// Key bindings as data and the scene-aware resolver. Contract: game/CONTRACTS.md 4.2.
// Source of truth: design/ui-key-bindings.md (Decisions table and the numbered rules).

export const ARROW_DIRS = Object.freeze({ ArrowUp: 'n', ArrowDown: 's', ArrowRight: 'e', ArrowLeft: 'w' });

/**
 * One row per row of the Decisions table in design/ui-key-bindings.md, in table order.
 *  - `row`      the table's Action cell, verbatim (a test compares it with the markdown)
 *  - `gesture`  the table's Kanata gesture cell, verbatim
 *  - `action`   the ActionId the resolver returns for this row
 *  - `match`    how the browser event is matched: by `event.key` ('key'), by `event.key` lowercased
 *               ('keyLower') or by `event.code` ('code')
 *  - `outputs`  the logical outputs (InterpretedEvent.output) that match
 *  - `appearsIn` scene classes where the row is live (the vocabulary of art-direction/ui-kit/bindings.py)
 */
export const BINDINGS = Object.freeze([
  { id: 'interact', row: 'Interact (talk, use a device, call the elevator)', action: 'interact',
    match: { by: 'key', value: 'Enter' }, outputs: ['Enter'], gesture: 'tap-hold Caps + N', appearsIn: ['world'] },
  { id: 'continue', row: 'Continue (dialogue, award, results, setup)', action: 'continue',
    match: { by: 'key', value: 'Enter' }, outputs: ['Enter'], gesture: 'tap-hold Caps + N', appearsIn: ['dialogue', 'overlay'] },
  { id: 'skip', row: 'Skip (a conversation)', action: 'skip',
    match: { by: 'key', value: 'Escape' }, outputs: ['Escape'], gesture: 'tap Caps', appearsIn: ['dialogue'] },
  { id: 'back', row: 'Back, close, leave', action: 'back',
    match: { by: 'key', value: 'Escape' }, outputs: ['Escape'], gesture: 'tap Caps', appearsIn: ['overlay', 'scene', 'duel'] },
  { id: 'move', row: 'Move, and choose in a list', action: 'move',
    match: { by: 'key', value: 'Arrow*' }, outputs: ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'],
    gesture: 'tap-hold Caps + H, J, K, L', appearsIn: ['world', 'overlay'] },
  { id: 'hint', row: 'Show hint', action: 'hint',
    match: { by: 'code', value: 'Backquote' }, outputs: ['Backquote'], gesture: 'tap `, a plain tap',
    appearsIn: ['world', 'dialogue', 'instruction', 'scene'] },
  { id: 'journal', row: 'Journal', action: 'journal',
    match: { by: 'keyLower', value: 'q' }, outputs: ['q', 'Q'], gesture: 'tap Q, a plain tap', appearsIn: ['world'] },
  { id: 'layout-help', row: 'Layout help', action: 'layoutHelp',
    match: { by: 'key', value: '?' }, outputs: ['?'], gesture: 'tap-hold F (Shift), then tap `/`',
    appearsIn: ['world', 'dialogue', 'instruction', 'overlay', 'scene'] },
  { id: 'elevator-open', row: 'Elevator: open the map', action: 'interact',
    match: { by: 'key', value: 'Enter' }, outputs: ['Enter'], gesture: 'tap-hold Caps + N', appearsIn: ['world'] },
  { id: 'elevator-pick', row: 'Elevator: pick a floor, confirm, go back', action: 'choose',
    match: { by: 'key', value: 'ArrowUp|ArrowDown|Enter|Escape' }, outputs: ['ArrowUp', 'ArrowDown', 'Enter', 'Escape'],
    gesture: 'tap-hold Caps + K / J, tap-hold Caps + N, tap Caps', appearsIn: ['overlay'] },
  { id: 'retry', row: 'Retry (glitch duel, after a wrong result)', action: 'retry',
    match: { by: 'key', value: 'Enter' }, outputs: ['Enter'], gesture: 'tap-hold Caps + N', appearsIn: ['duel'] },
]);

const NONE = Object.freeze({ action: null, dir: null });

/**
 * Resolve an InterpretedEvent against the scene's key ownership.
 * Rules (ui-key-bindings.md): one press, one action (key-down only, repeat ignored); Q, Backtick, Return and
 * Esc act only with no Command, Control, Option or Shift down; `?` is the one place Shift is expected;
 * Tab and Space never resolve; Q is text in typing scenes; Esc does nothing in the open world (esc 'none').
 * @returns {{action:string|null, dir:'n'|'s'|'e'|'w'|null}}
 */
export function resolveAction(interp, ctx) {
  if (!interp || !ctx) return NONE;
  if (interp.phase !== 'down' || interp.repeat) return NONE;
  const { output, mods } = interp;
  if (output === 'Tab' || output === 'Space') return NONE;
  if (mods.ctrl || mods.meta || mods.alt) return NONE;

  if (output === '?') return ctx.layoutHelp ? { action: 'layoutHelp', dir: null } : NONE;
  if (mods.shift) return NONE;

  if (output === 'Backquote') return ctx.hint ? { action: 'hint', dir: null } : NONE;
  if (typeof output === 'string' && output.toLowerCase() === 'q') {
    return ctx.journal && !ctx.typing ? { action: 'journal', dir: null } : NONE;
  }
  if (output === 'Enter') {
    return ['interact', 'continue', 'confirm', 'retry'].includes(ctx.enter) ? { action: ctx.enter, dir: null } : NONE;
  }
  if (output === 'Escape') {
    return ctx.esc === 'skip' || ctx.esc === 'back' ? { action: ctx.esc, dir: null } : NONE;
  }
  const dir = ARROW_DIRS[output];
  if (dir) {
    return ctx.arrows === 'move' || ctx.arrows === 'choose' ? { action: ctx.arrows, dir } : NONE;
  }
  return NONE;
}
