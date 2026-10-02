// Tiny escaping template helper. Components return strings built with `html`; nothing here touches the DOM.
// A value is escaped unless it is wrapped by `raw()` or came out of another `html` call.

export class Raw {
  constructor(s) { this.s = String(s); }
  toString() { return this.s; }
}

export const raw = (s) => new Raw(s);

export function esc(v) {
  return String(v)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function part(v) {
  if (v === null || v === undefined || v === false || v === true) return '';
  if (v instanceof Raw) return v.s;
  if (Array.isArray(v)) return v.map(part).join('');
  return esc(v);
}

/** Tagged template: html`<p>${text}</p>` returns Raw, so nested calls compose without double escaping. */
export function html(strings, ...vals) {
  let out = strings[0];
  for (let i = 0; i < vals.length; i++) out += part(vals[i]) + strings[i + 1];
  return new Raw(out);
}

/** `data-cmd` attribute carrying a ui:command payload (JSON, attribute-escaped). */
export function cmdAttr(command) {
  return raw(`data-cmd="${esc(JSON.stringify(command))}"`);
}

/** Remove tags and decode the few entities `esc` produces: used by tests and screen-reader labels. */
export function textOf(markup) {
  return String(markup)
    .replace(/<[^>]*>/g, ' ')
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim();
}
