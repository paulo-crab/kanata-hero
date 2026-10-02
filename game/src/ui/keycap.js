// Keycap component (kit COMPONENTS.md "Keycap"). Pure markup builders.
import { html, raw } from './html.js';
import { icon } from './icons.js';

const WIDE = new Set(['Return', 'Caps', 'Space', 'Shift', 'Backspace', 'Tab', 'Esc', 'Escape', 'Control', 'Option', 'Command']);
const ARROWS = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right' };
const ARROW_WORDS = { up: 'Up arrow', down: 'Down arrow', left: 'Left arrow', right: 'Right arrow' };

/** Accessible name: the Backtick key draws a glyph but is always spoken as a word. */
export function keycapName(k) {
  if (k.glyph === '`' || k.key === 'Backquote' || k.key === 'Backtick') return 'Backtick';
  if (ARROWS[k.key]) return ARROW_WORDS[ARROWS[k.key]];
  if (k.silent) return `${k.label} (silent)`;
  return k.label;
}

/**
 * One keycap from a KeycapVM {key,label,held?,dim?,silent?,glyph?}.
 * @param {{sm?:boolean, wide?:boolean, cls?:string, size?:number}} [o]
 */
export function keycap(k, o = {}) {
  const cls = ['kh-key'];
  if (o.sm) cls.push('sm');
  if (o.wide || (!o.sm && WIDE.has(k.label))) cls.push('wide');
  if (k.held) cls.push('held');
  if (k.dim) cls.push('dim');
  if (k.silent) cls.push('silent');
  if (o.cls) cls.push(o.cls);
  const arrow = ARROWS[k.key];
  const face = arrow ? icon(`arrow-${arrow}`, o.sm ? 20 : 28) : (k.glyph ?? k.label);
  return html`<span class="${cls.join(' ')}" aria-label="${keycapName(k)}">${face}</span>`;
}

/** Keycap with its Hold or Tap tag underneath (inset hold order). */
export function keyunit(k, tag) {
  const t = tag ? html`<span class="kh-tag ${tag.toLowerCase() === 'hold' ? 'hold' : 'tap'}">${tag}</span>` : '';
  return html`<span class="kh-keyunit">${keycap(k)}${t}</span>`;
}

/** KeycapVM for a key named the way the level data names it ('Escape', 'Backtick', 'Down Arrow', 'Q', '?'). */
export function keycapForName(name) {
  const n = String(name);
  const map = {
    Escape: { key: 'Escape', label: 'Esc' },
    Esc: { key: 'Escape', label: 'Esc' },
    Backtick: { key: 'Backquote', label: 'Backtick', glyph: '`' },
    Return: { key: 'Enter', label: 'Return' },
    Enter: { key: 'Enter', label: 'Return' },
    'Up Arrow': { key: 'ArrowUp', label: 'Up' },
    'Down Arrow': { key: 'ArrowDown', label: 'Down' },
    'Left Arrow': { key: 'ArrowLeft', label: 'Left' },
    'Right Arrow': { key: 'ArrowRight', label: 'Right' },
  };
  return map[n] || { key: n, label: n.length === 1 ? n.toUpperCase() : n };
}

/** A row of keycaps joined by "+" (toggle-out sequence, hold order). */
export function sequence(keys, o = { sm: true }) {
  const out = [];
  keys.forEach((k, i) => {
    if (i > 0) out.push(raw('<span class="plus" aria-hidden="true">+</span>'));
    out.push(keycap(k, o));
  });
  return html`${out}`;
}
