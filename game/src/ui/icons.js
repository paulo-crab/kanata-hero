// SVG sprite: markers and interface icons, copied from art-direction/ui-kit/reference.html (same ids).
// Colours come from the kit tokens through `style="fill:var(--...)"`; no hex values live in this file.
import { raw } from './html.js';

const INK = 'style="fill:var(--ink)"';
const INK_STROKE = 'style="stroke:var(--ink)"';

export const SPRITE = `
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <path id="p-talk" d="M18 10 H46 A10 10 0 0 1 56 20 V32 A10 10 0 0 1 46 42 H30 L16 56 L20 42 H18 A10 10 0 0 1 8 32 V20 A10 10 0 0 1 18 10 Z"/>
    <path id="p-terminal" d="M14 10 H50 A6 6 0 0 1 56 16 V38 A6 6 0 0 1 50 44 H37 V50 H46 V55 H18 V50 H27 V44 H14 A6 6 0 0 1 8 38 V16 A6 6 0 0 1 14 10 Z"/>
    <path id="p-route" d="M32 4 L60 32 L32 60 L4 32 Z"/>
    <path id="p-glitch" d="M14 6 H38 L52 20 V54 A4 4 0 0 1 48 58 H14 A4 4 0 0 1 10 54 V10 A4 4 0 0 1 14 6 Z"/>
  </defs>
  <symbol id="m-talk" viewBox="0 0 64 64">
    <use href="#p-talk" class="halo"/><use href="#p-talk" class="line"/><use href="#p-talk" style="fill:var(--coral)"/>
    <circle cx="22" cy="26" r="3.2" ${INK}/><circle cx="32" cy="26" r="3.2" ${INK}/><circle cx="42" cy="26" r="3.2" ${INK}/>
  </symbol>
  <symbol id="m-terminal" viewBox="0 0 64 64">
    <use href="#p-terminal" class="halo"/><use href="#p-terminal" class="line"/><use href="#p-terminal" style="fill:var(--teal)"/>
    <rect x="14" y="16" width="36" height="22" rx="2" ${INK}/>
    <path d="M19 22 L26 27 L19 32 M30 33 H39" fill="none" style="stroke:var(--paper)" stroke-width="3" stroke-linecap="square" stroke-linejoin="miter"/>
  </symbol>
  <symbol id="m-route" viewBox="0 0 64 64">
    <use href="#p-route" class="halo"/><use href="#p-route" class="line"/><use href="#p-route" style="fill:var(--gold)"/>
    <path d="M24 46 V31 A8 8 0 0 1 40 31 V46 Z" ${INK}/>
    <rect x="21" y="46" width="22" height="3" ${INK}/>
  </symbol>
  <symbol id="m-route-teal" viewBox="0 0 64 64">
    <use href="#p-route" class="halo"/><use href="#p-route" class="line"/><use href="#p-route" style="fill:var(--teal)"/>
    <path d="M24 46 V31 A8 8 0 0 1 40 31 V46 Z" ${INK}/>
    <rect x="21" y="46" width="22" height="3" ${INK}/>
  </symbol>
  <symbol id="m-glitch" viewBox="0 0 64 64">
    <use href="#p-glitch" class="halo"/><use href="#p-glitch" class="line"/><use href="#p-glitch" style="fill:var(--violet)"/>
    <path d="M38 6 V20 H52 Z" ${INK}/>
    <path d="M17 28 H44 M17 49 H44" fill="none" ${INK_STROKE} stroke-width="3.5"/>
    <path d="M17 38 H27 L30 33 L34 43 L37 38 H44" fill="none" ${INK_STROKE} stroke-width="3.5" stroke-linejoin="miter"/>
  </symbol>
  <symbol id="i-seal" viewBox="0 0 24 24">
    <path d="M8 2 H16 L22 8 V16 L16 22 H8 L2 16 V8 Z" fill="currentColor"/>
    <path d="M7 12 L11 16 L17 8" fill="none" ${INK_STROKE} stroke-width="2.6" stroke-linecap="square"/>
  </symbol>
  <symbol id="i-bubble" viewBox="0 0 24 24">
    <path d="M6 3 H18 A4 4 0 0 1 22 7 V13 A4 4 0 0 1 18 17 H12 L6 22 L8 17 H6 A4 4 0 0 1 2 13 V7 A4 4 0 0 1 6 3 Z" fill="currentColor"/>
  </symbol>
  <symbol id="i-stopwatch" viewBox="0 0 24 24">
    <rect x="9" y="1" width="6" height="3" fill="currentColor"/>
    <circle cx="12" cy="14" r="8.5" fill="currentColor"/>
    <path d="M12 8.5 V14 L16 16.5" fill="none" ${INK_STROKE} stroke-width="2.4" stroke-linecap="square"/>
  </symbol>
  <symbol id="i-check" viewBox="0 0 24 24"><path d="M4 12.5 L9.5 18 L20 6" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="square"/></symbol>
  <symbol id="i-lock" viewBox="0 0 24 24">
    <rect x="4" y="10" width="16" height="12" rx="2" fill="currentColor"/>
    <path d="M8 10 V7 A4 4 0 0 1 16 7 V10" fill="none" stroke="currentColor" stroke-width="2.6"/>
  </symbol>
  <symbol id="i-play" viewBox="0 0 24 24"><path d="M6 3 L20 12 L6 21 Z" fill="currentColor"/></symbol>
  <symbol id="i-step-east" viewBox="0 0 24 24"><path d="M2 12 H17 M11 5 L18 12 L11 19 M21 4 V20" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
  <symbol id="i-arrow-right" viewBox="0 0 24 24"><path d="M3 12 H20 M13 5 L20 12 L13 19" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
  <symbol id="i-arrow-left" viewBox="0 0 24 24"><path d="M21 12 H4 M11 5 L4 12 L11 19" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
  <symbol id="i-arrow-up" viewBox="0 0 24 24"><path d="M12 21 V4 M5 11 L12 4 L19 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
  <symbol id="i-arrow-down" viewBox="0 0 24 24"><path d="M12 3 V20 M5 13 L12 20 L19 13" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
  <symbol id="i-eye" viewBox="0 0 24 24">
    <path d="M1.5 12 C5 5.5 9 4.5 12 4.5 C15 4.5 19 5.5 22.5 12 C19 18.5 15 19.5 12 19.5 C9 19.5 5 18.5 1.5 12 Z" fill="currentColor"/>
    <circle cx="12" cy="12" r="3.6" ${INK}/>
  </symbol>
  <symbol id="i-person-check" viewBox="0 0 24 24">
    <circle cx="9" cy="7.5" r="4.2" fill="currentColor"/>
    <path d="M1.5 21 C1.5 15 5 12.8 9 12.8 C11 12.8 12.6 13.3 13.8 14.2 L13.8 21 Z" fill="currentColor"/>
    <path d="M14.5 17 L18 20.5 L23 13.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/>
  </symbol>
  <symbol id="i-shield-key" viewBox="0 0 24 24">
    <path d="M12 1.5 L21 4.8 V12 C21 17.2 17.2 20.8 12 22.5 C6.8 20.8 3 17.2 3 12 V4.8 Z" fill="currentColor"/>
    <circle cx="12" cy="10" r="2.9" ${INK}/>
    <path d="M10.6 11.5 H13.4 L14.2 17 H9.8 Z" ${INK}/>
  </symbol>
  <symbol id="i-circle" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="3"/></symbol>
  <symbol id="i-skip" viewBox="0 0 24 24"><path d="M4 5 L15 12 L4 19 Z M18.5 4.5 V19.5" fill="currentColor" stroke="currentColor" stroke-width="2.6" stroke-linejoin="miter"/></symbol>
  <symbol id="i-warn" viewBox="0 0 24 24">
    <path d="M12 2 L23 21.5 H1 Z" fill="currentColor"/>
    <path d="M12 9 V15" ${INK_STROKE} stroke-width="2.8" stroke-linecap="square"/><rect x="10.7" y="16.7" width="2.6" height="2.6" ${INK}/>
  </symbol>
  <symbol id="i-target" viewBox="0 0 24 24"><path d="M12 2 L22 12 L12 22 L2 12 Z" fill="currentColor"/><circle cx="12" cy="12" r="3" ${INK}/></symbol>
</svg>`;

export const SPRITE_RAW = raw(SPRITE);

export const ICON_NAMES = [
  'seal', 'bubble', 'stopwatch', 'check', 'lock', 'play', 'step-east', 'arrow-right', 'arrow-left', 'arrow-up', 'arrow-down',
  'eye', 'person-check', 'shield-key', 'circle', 'skip', 'warn', 'target',
];

/** Small interface icon, drawn with currentColor. */
export function icon(name, size = 24) {
  return raw(`<svg class="kh-ico" width="${size}" height="${size}" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-${name}"/></svg>`);
}

/** Marker symbol: shape first, colour second. `name` is talk, terminal, route, route-teal or glitch. */
export function markerSvg(name, style = '', cls = '') {
  return raw(`<svg class="kh-marker ${cls}" style="${style}" viewBox="0 0 64 64" aria-hidden="true"><use href="#m-${name}"/></svg>`);
}

/** A marker used as an inline icon. */
export function markerIcon(name, size = 32) {
  return raw(`<svg class="kh-ico" width="${size}" height="${size}" viewBox="0 0 64 64" aria-hidden="true"><use href="#m-${name}"/></svg>`);
}
