"""Screens and components for the UI kit reference page: Layout help (four tabs and the
Microsoft variant), setup and calibration, terminal/editor scene, glitch-repair duel and
confidence-aware input feedback.

build_reference.py imports this module and stitches the sections into reference.html.
Everything is static HTML/CSS/SVG (no script). Colours, spacing, radii, type sizes and
z-layers come from tokens.css; the few layout sizes (panel widths, key widths) are
local to a component.
"""

# --------------------------------------------------------------------------- helpers


def ico(name, size=24):
    return (f'<svg class="kh-ico" width="{size}" height="{size}" viewBox="0 0 24 24" aria-hidden="true">'
            f'<use href="#i-{name}"/></svg>')


def mk(name, cls="", style=""):
    return (f'<svg class="kh-marker {cls}" style="{style}" viewBox="0 0 64 64" aria-hidden="true">'
            f'<use href="#m-{name}"/></svg>')


def mico(name, size=32):
    """A marker symbol used as an inline icon (not positioned on the stage)."""
    return (f'<svg class="kh-ico" width="{size}" height="{size}" viewBox="0 0 64 64" aria-hidden="true">'
            f'<use href="#m-{name}"/></svg>')


def keycap(label, cls="", tag=None, tagcls=""):
    t = f'<span class="kh-tag {tagcls}">{tag}</span>' if tag else ""
    return f'<span class="kh-keyunit"><span class="kh-key {cls}">{label}</span>{t}</span>'


def kc(label, cls="sm"):
    """Inline keycap (small by default)."""
    return f'<span class="kh-key {cls}">{label}</span>'


# --------------------------------------------------------------------------- sprite additions
SPRITE_EXTRA = """
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <!-- Feedback state icons: eye = observed, person with check = you confirmed, shield with keyhole = OS-reserved -->
  <symbol id="i-eye" viewBox="0 0 24 24">
    <path d="M1.5 12 C5 5.5 9 4.5 12 4.5 C15 4.5 19 5.5 22.5 12 C19 18.5 15 19.5 12 19.5 C9 19.5 5 18.5 1.5 12 Z" fill="currentColor"/>
    <circle cx="12" cy="12" r="3.6" fill="#182B38"/>
  </symbol>
  <symbol id="i-person-check" viewBox="0 0 24 24">
    <circle cx="9" cy="7.5" r="4.2" fill="currentColor"/>
    <path d="M1.5 21 C1.5 15 5 12.8 9 12.8 C11 12.8 12.6 13.3 13.8 14.2 L13.8 21 Z" fill="currentColor"/>
    <path d="M14.5 17 L18 20.5 L23 13.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/>
  </symbol>
  <symbol id="i-shield-key" viewBox="0 0 24 24">
    <path d="M12 1.5 L21 4.8 V12 C21 17.2 17.2 20.8 12 22.5 C6.8 20.8 3 17.2 3 12 V4.8 Z" fill="currentColor"/>
    <circle cx="12" cy="10" r="2.9" fill="#182B38"/>
    <path d="M10.6 11.5 H13.4 L14.2 17 H9.8 Z" fill="#182B38"/>
  </symbol>
  <symbol id="i-circle" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="3"/></symbol>
  <symbol id="i-skip" viewBox="0 0 24 24"><path d="M4 5 L15 12 L4 19 Z M18.5 4.5 V19.5" fill="currentColor" stroke="currentColor" stroke-width="2.6" stroke-linejoin="miter"/></symbol>
  <symbol id="i-warn" viewBox="0 0 24 24">
    <path d="M12 2 L23 21.5 H1 Z" fill="currentColor"/>
    <path d="M12 9 V15" stroke="#182B38" stroke-width="2.8" stroke-linecap="square"/><rect x="10.7" y="16.7" width="2.6" height="2.6" fill="#182B38"/>
  </symbol>
  <symbol id="i-target" viewBox="0 0 24 24"><path d="M12 2 L22 12 L12 22 L2 12 Z" fill="currentColor"/><circle cx="12" cy="12" r="3" fill="#182B38"/></symbol>
  <symbol id="i-arrow-left" viewBox="0 0 24 24"><path d="M21 12 H4 M11 5 L4 12 L11 19" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
</svg>
"""

# --------------------------------------------------------------------------- CSS
CSS = """
/* ---- Screen shells: every new screen is a 1366 x 768 viewport with the 1280 x 720 stage ------ */
.shot{position:relative;padding:var(--space-6) 0 var(--space-5)}
.shot .sheet-head{width:1280px;margin:0 auto var(--space-4)}
.shot .sheet-head h2{font-size:var(--text-2xl);margin-bottom:var(--space-2)}
.shot .sheet-head .lede{color:var(--text-muted);margin:0;max-width:980px}
.shot .viewport{margin:0 auto}
.shot .a{position:absolute;left:0;top:0;width:1px;height:1px}
.shot .note{width:1280px;margin:var(--space-3) auto 0;color:var(--text-muted);font-size:var(--text-sm)}
.stage .scrim{z-index:var(--z-overlay)}
.stage .scrim.scene{background:var(--scrim-scene);z-index:var(--z-world-fx)}
.page:has(.a:target)>:not(.shot){display:none}
.page:has(.a:target)>.shot:not(:has(.a:target)){display:none}
html:has(.a:target){overflow:hidden}
.shot:has(.a:target){padding:0}
.shot:has(.a:target) .sheet-head,.shot:has(.a:target) .note{display:none}
.shot:has(.a.g:target) .viewport{filter:grayscale(1)}
.mono{font-family:var(--font-mono)}
b,strong{font-weight:var(--weight-bold)}

/* ---- Segmented control and buttons ---------------------------------------------------------- */
.seg{display:inline-flex;border:2px solid var(--border);border-radius:var(--radius-pill);padding:2px;gap:2px;background:var(--panel-sunken)}
.seg span{display:inline-flex;align-items:center;gap:var(--space-2);padding:var(--space-1) var(--space-4);border-radius:var(--radius-pill);font:var(--weight-bold) var(--text-sm)/1.2 var(--font-body);color:var(--text);white-space:nowrap}
.seg span[aria-pressed="true"]{background:var(--paper);color:var(--ink)}
.seg span.focus{outline:2px solid var(--focus);outline-offset:2px}
.kh-btn{display:inline-flex;align-items:center;gap:var(--space-2);padding:var(--space-2) var(--space-4);border:2px solid var(--border);border-radius:var(--radius-md);background:var(--panel-raised);color:var(--text);font:var(--weight-bold) var(--text-sm)/1.2 var(--font-body);white-space:nowrap}
.kh-btn.primary{background:var(--paper);color:var(--ink);border-color:var(--paper)}
.kh-btn.focus{outline:2px solid var(--focus);outline-offset:3px}
.kh-btn .kh-key.sm{height:28px;min-width:28px;box-shadow:0 2px 0 var(--key-edge);margin-bottom:2px}

/* ---- Layout help ------------------------------------------------------------------------------ */
.lh-overlay{left:16px;right:16px;top:16px;bottom:16px;gap:6px;padding:var(--space-2) var(--space-5) var(--space-3)}
.lh-overlay .kh-lh{gap:6px}
.lh-overlay .top{gap:var(--space-4)}
.lh-overlay .top h2{font-size:var(--text-xl)}
.lh-how{margin:0;font-size:var(--text-sm);color:var(--text-muted)}
.lh-how b{color:var(--text)}
.kh-lk.same{color:var(--key-dim-text)}
.kh-lk.same .s{font-weight:var(--weight-regular)}
.kh-lk.silent .l{font-weight:var(--weight-bold)}
.kh-lk.silent .s{font-weight:var(--weight-regular)}
.kh-lk.half{height:29px;flex-direction:row;gap:var(--space-1);margin:0}
.kh-lk.half .s{font-weight:var(--weight-bold)}
.kh-lk.layerkey .s,.kh-lk.map .s{color:inherit}
.lh-stack{display:flex;flex-direction:column;gap:var(--key-gap);margin-bottom:3px}
.lh-gap{flex:none}
.lh-detail.lh-4{grid-template-columns:auto 1fr 1fr}
.lh-detail .hintline{grid-column:1/-1;margin:0;padding-top:var(--space-2);border-top:2px solid var(--border);font-size:var(--text-base)}
.lh-detail .hintline .hint{color:var(--text-muted)}
.lh-detail .hintline b{color:var(--text)}
.lh-cards{display:grid;grid-template-columns:1.15fr 1.45fr 1fr;gap:var(--space-3)}
.lh-card{background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-2) var(--space-4);display:flex;flex-direction:column;gap:var(--space-1);font-size:var(--text-sm)}
.lh-card p{margin:0;font-size:var(--text-sm);color:var(--text-muted)}
.lh-card p b{color:var(--text)}
.lh-card .kh-label{display:flex;align-items:center;gap:var(--space-2)}
.lh-card .seq{display:flex;align-items:center;gap:var(--space-2);flex-wrap:wrap}
.lh-card .seq .kh-key{height:36px;min-width:36px;font-size:var(--text-sm);box-shadow:0 3px 0 var(--key-edge)}
.lh-card.locked{border-style:dashed;background:var(--panel-sunken)}
.lh-card .row{display:flex;align-items:center;gap:var(--space-3)}
.lh-card .row .kh-key{height:40px;min-width:40px;box-shadow:0 3px 0 var(--key-edge)}
.lh-foot{display:flex;gap:var(--space-5);align-items:center;flex-wrap:wrap;justify-content:space-between}
.lh-device{display:inline-flex;align-items:center;gap:var(--space-3);font-size:var(--text-sm);color:var(--text-muted)}
.lh-remap{display:flex;gap:var(--space-4);flex-wrap:wrap;font-size:var(--text-sm);color:var(--text)}
.lh-remap span{display:inline-flex;align-items:center;gap:var(--space-2)}
.lh-also{font-size:var(--text-sm);color:var(--text-muted);margin:0}
.lh-also b{color:var(--text)}

/* ---- Feedback card ------------------------------------------------------------------------------ */
.kh-fb{background:var(--panel-raised);border-radius:var(--radius-md);padding:var(--space-3) var(--space-4);display:flex;flex-direction:column;gap:var(--space-2)}
.kh-fb.observed{border:2px solid var(--accent-terminal)}
.kh-fb.confirmed{border:6px double var(--paper);padding:calc(var(--space-3) - 4px) calc(var(--space-4) - 4px)}
.kh-fb.reserved{border:2px dashed var(--border)}
.kh-fb .what{display:flex;align-items:center;gap:var(--space-2);font:var(--weight-bold) var(--text-base)/var(--leading-tight) var(--font-body)}
.kh-fb.observed .what{color:var(--accent-terminal)}
.kh-fb.confirmed .what{color:var(--text)}
.kh-fb.reserved .what{color:var(--text)}
.kh-fb dl{margin:0;display:grid;grid-template-columns:1fr;gap:0}
.kh-fb dt{font:var(--weight-bold) var(--text-sm)/1.3 var(--font-body);letter-spacing:var(--tracking-label);text-transform:uppercase;color:var(--text-muted)}
.kh-fb dd{margin:0 0 var(--space-1);font-size:var(--text-base);line-height:1.5}
.kh-fb dd .mono{font-weight:var(--weight-bold)}
.kh-fb dd.fx{color:var(--accent-discovery);font-weight:var(--weight-bold)}
.kh-fb dd .kh-key.sm{vertical-align:middle}
.kh-fb .why{margin:0;font-size:var(--text-sm);color:var(--text-muted)}
.kh-fb .why b{color:var(--text)}
.kh-chip{display:inline-flex;align-items:center;gap:var(--space-2);padding:var(--space-1) var(--space-3);border-radius:var(--radius-pill);font:var(--weight-bold) var(--text-sm)/1.2 var(--font-body);white-space:nowrap;color:var(--text)}
.kh-chip.confirmed{border:2px solid var(--paper);background:var(--panel-sunken)}
.kh-chip.unconfirmed{border:2px dashed var(--border);background:var(--panel-sunken);color:var(--text-muted)}
.kh-chip.obs{border:2px solid var(--accent-terminal);background:var(--panel-sunken)}
.kh-chip.skip{border:2px dashed var(--border);background:var(--panel-sunken);color:var(--text-muted)}
.kh-chip.todo{border:2px solid var(--border);background:var(--panel-sunken);color:var(--text-muted)}

/* Feedback sheet (three states + wording rules) */
.fb-sheet{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-4)}
.fb-cell{display:flex;flex-direction:column;gap:var(--space-2)}
.fb-cell>p{margin:0;font-size:var(--text-sm);color:var(--text-muted)}
.fb-rules{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4)}
.fb-rules .kh-panel{padding:var(--space-3) var(--space-4)}
.fb-rules h3{font-size:var(--text-lg);margin-bottom:var(--space-2);display:flex;align-items:center;gap:var(--space-2)}
.fb-rules ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:var(--space-2);font-size:var(--text-sm)}
.fb-rules li{display:grid;grid-template-columns:24px 1fr;gap:var(--space-2);align-items:start}
.fb-rules li .kh-ico{margin-top:1px}
.fb-rules .no li span.q{color:var(--text-muted);text-decoration:line-through}
.fb-layers{display:flex;gap:var(--space-3);align-items:center;flex-wrap:wrap;font-size:var(--text-sm);color:var(--text-muted)}
.fb-layers .box{background:var(--panel-sunken);border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3);color:var(--text);display:inline-flex;align-items:center;gap:var(--space-2)}

/* ---- Setup and calibration ----------------------------------------------------------------------- */
.su{left:16px;right:16px;top:16px;bottom:16px;padding:var(--space-3) var(--space-5);gap:var(--space-2)}
.su .top .sub{font-size:var(--text-sm);color:var(--text-muted)}
.kh-label .kh-chip{text-transform:none;letter-spacing:0}
.su .top h2{font-size:var(--text-xl)}
.su-choice{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4)}
.su-opt{display:grid;grid-template-columns:1fr auto;gap:var(--space-1) var(--space-3);background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-3) var(--space-4)}
.su-opt.sel{border-color:var(--focus);outline:2px solid var(--focus);outline-offset:2px}
.su-opt h3{font-size:var(--text-lg);display:flex;align-items:center;gap:var(--space-2)}
.su-opt .pick{display:inline-flex;align-items:center;gap:var(--space-1);font:var(--weight-bold) var(--text-sm)/1 var(--font-body);color:var(--text-muted)}
.su-opt.sel .pick{color:var(--text)}
.su-opt p{margin:0;grid-column:1/-1;font-size:var(--text-sm);color:var(--text-muted)}
.su-opt p b{color:var(--text)}
.su-opt .strip{grid-column:1/-1;display:flex;gap:4px;align-items:flex-end;margin-top:var(--space-1)}
.su-opt .strip .kh-key{min-width:50px;height:36px;padding:0 var(--space-2);font-size:var(--text-sm);box-shadow:0 3px 0 var(--key-edge);margin-bottom:3px}
.su-opt .strip .kh-key.dim{box-shadow:0 3px 0 var(--key-dim-edge)}
.su-opt .strip .kh-key.sp{min-width:120px}
.su-opt .strip .map{position:relative}
.su-opt .strip .arrowto{font:var(--weight-bold) var(--text-sm)/1 var(--font-body);color:var(--text);padding:0 var(--space-1)}
.su-body{display:grid;grid-template-columns:660px 1fr;gap:var(--space-4);flex:1;min-height:0}
.su-steps{display:flex;flex-direction:column;gap:6px;min-width:0}
.su-steps .head{display:flex;align-items:baseline;justify-content:space-between;gap:var(--space-3)}
.su-step{display:grid;grid-template-columns:28px 1fr auto;gap:0 var(--space-3);align-items:center;background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-1) var(--space-3)}
.su-step.cur{border-color:var(--focus);outline:2px solid var(--focus);outline-offset:2px}
.su-step .n{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:var(--radius-pill);background:var(--paper);color:var(--ink);font:var(--weight-bold) var(--text-sm)/1 var(--font-body);grid-row:1/3}
.su-step .t{display:flex;align-items:center;gap:var(--space-2);font-weight:var(--weight-bold);font-size:var(--text-base)}
.su-step .t .mono{font-size:var(--text-sm);color:var(--text-muted);font-weight:var(--weight-regular)}
.su-step .kh-chip{grid-row:1;grid-column:3}
.su-step .d{grid-column:2/4;font-size:var(--text-sm);color:var(--text-muted);line-height:1.3}
.su-step .d b{color:var(--text)}
.su-foot{margin:0;font-size:var(--text-sm);color:var(--text-muted)}
.su-foot b{color:var(--text)}
.su-side{display:flex;flex-direction:column;gap:var(--space-2);min-width:0}
.su-diagram{background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-2) var(--space-4);display:flex;flex-direction:column;gap:var(--space-2)}
.su-diagram .head{display:flex;align-items:center;justify-content:space-between;gap:var(--space-2);flex-wrap:wrap}
.sk-rows{display:flex;flex-direction:column;gap:3px;align-items:flex-start}
.sk-row{display:flex;gap:3px}
.kh-sk{height:var(--key-unit-sm);border-radius:5px;background:var(--key-dim-face);color:var(--key-dim-text);box-shadow:0 2px 0 var(--key-dim-edge);display:flex;align-items:center;justify-content:center;font:var(--weight-regular) var(--text-sm)/1 var(--font-mono);flex:none;margin-bottom:2px}
.kh-sk.layerkey{background:var(--key-held-face);color:var(--key-held-text);box-shadow:0 1px 0 var(--key-held-edge);font-weight:var(--weight-bold);position:relative;top:2px}
.kh-sk.target{background:var(--key-face);color:var(--key-text);box-shadow:0 3px 0 var(--key-edge);font-weight:var(--weight-bold);outline:2px solid var(--focus);outline-offset:2px}
.kh-sk.lit{background:var(--key-face);color:var(--key-text);box-shadow:0 3px 0 var(--key-edge);font-weight:var(--weight-bold)}
.su-diagram .cap{margin:0;font-size:var(--text-sm);color:var(--text-muted)}
.su-diagram .cap b{color:var(--text)}
.su-toggle{background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-2) var(--space-4);display:flex;flex-direction:column;gap:var(--space-2)}
.su-toggle p{margin:0;font-size:var(--text-sm);color:var(--text-muted)}
.su-toggle p b{color:var(--text)}
.su-toggle .seq{display:flex;align-items:center;gap:var(--space-2);flex-wrap:wrap}
.su-toggle .seq .kh-key{height:36px;min-width:36px;font-size:var(--text-sm);box-shadow:0 3px 0 var(--key-edge)}
.su-toggle .kh-label{display:flex;align-items:center;justify-content:space-between;gap:var(--space-2)}

/* ---- Terminal / editor scene -------------------------------------------------------------------- */
.kh-term{position:absolute;z-index:var(--z-dialogue);left:var(--stage-margin);top:var(--stage-margin);width:900px;padding:var(--space-3) var(--space-4);display:flex;flex-direction:column;gap:var(--space-2)}
.kh-term .bar{width:auto;margin:0;padding:0;background:transparent;display:flex;align-items:center;gap:var(--space-3);font-size:var(--text-sm)}
.kh-term .bar .name{font:var(--weight-bold) var(--text-base)/1 var(--font-mono);color:var(--text)}
.kh-term .bar .where{color:var(--text-muted)}
.kh-term .bar .grow{flex:1}
.kh-term .bar .leave{display:inline-flex;align-items:center;gap:var(--space-2);color:var(--text-muted)}
.kh-task{display:grid;grid-template-columns:1fr auto;gap:var(--space-1) var(--space-4);align-items:center;background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3)}
.kh-task p{margin:0;font-size:var(--text-base);line-height:1.35}
.kh-task p .hint{color:var(--text-muted)}
.kh-task p b{color:var(--text)}
.kh-task .count{display:inline-flex;align-items:center;gap:var(--space-2);color:var(--accent-discovery);font:var(--weight-bold) var(--text-base)/1 var(--font-mono);grid-row:1/2;grid-column:2}
.kh-task.ok{border-color:var(--accent-discovery);border-width:3px}
.kh-task.ok .win{display:flex;align-items:center;gap:var(--space-3);font-size:var(--text-base)}
.kh-task.ok .win b{color:var(--accent-discovery)}
.kh-code{background:var(--panel-sunken);border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-2) 0;font:var(--weight-regular) var(--text-base)/32px var(--font-mono);color:var(--text)}
.kh-line{display:grid;grid-template-columns:64px 1fr;white-space:pre;position:relative}
.kh-line .no{display:flex;align-items:center;justify-content:flex-end;gap:var(--space-1);padding-right:var(--space-3);color:var(--text-muted)}
.kh-line .no .kh-ico{color:var(--accent-discovery)}
.kh-line.tl{background:color-mix(in srgb,var(--gold) 16%,transparent)}
.kh-line.tl .no{color:var(--accent-discovery);font-weight:var(--weight-bold)}
.kh-line .tag{position:absolute;right:var(--space-3);top:4px;height:24px;display:inline-flex;align-items:center;gap:var(--space-1);padding:0 var(--space-2);border:2px solid var(--accent-discovery);border-radius:var(--radius-sm);font:var(--weight-bold) var(--text-sm)/1 var(--font-body);color:var(--accent-discovery);background:var(--panel-sunken);white-space:nowrap}
.kh-code .k{color:var(--text-muted)}
.kh-code .sel{background:var(--selection-bg);color:var(--selection-text);box-shadow:0 4px 0 var(--focus)}
.kh-code .cur{background:var(--cursor-face);color:var(--cursor-text);outline:2px solid var(--focus);outline-offset:1px;position:relative}
.kh-code .tw{outline:2px dashed var(--accent-discovery);outline-offset:2px;border-radius:2px}
.kh-code .done{background:color-mix(in srgb,var(--gold) 28%,transparent);box-shadow:0 4px 0 var(--accent-discovery)}
.kh-code .gl{text-decoration:underline wavy var(--accent-glitch) 2px;text-underline-offset:5px}
.kh-code .gtag{color:var(--accent-glitch);font-weight:var(--weight-bold)}
.kh-code .field{display:inline-block;min-width:260px;border:2px solid var(--border);border-radius:var(--radius-sm);padding:0 var(--space-2);line-height:28px;vertical-align:middle;background:var(--panel-bg)}
.kh-code .field.on{border-color:var(--focus);outline:2px solid var(--focus);outline-offset:2px}
.kh-region{margin:var(--space-2);border:3px dashed var(--accent-terminal);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3);display:flex;flex-direction:column;gap:var(--space-1)}
.kh-region .lab{display:flex;align-items:center;gap:var(--space-2);font:var(--weight-bold) var(--text-sm)/1.3 var(--font-body);color:var(--accent-terminal);letter-spacing:var(--tracking-label);text-transform:uppercase}
.kh-region .frow{display:grid;grid-template-columns:140px 1fr;align-items:center;font:var(--weight-regular) var(--text-base)/36px var(--font-body);color:var(--text)}
.kh-announce{display:flex;align-items:center;gap:var(--space-3);background:var(--panel-sunken);border:2px solid var(--accent-terminal);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3);font-size:var(--text-sm)}
.kh-announce .kh-label{color:var(--accent-terminal);white-space:nowrap}
.kh-term.glitch{border-color:var(--violet)}
.kh-term .glt{display:flex;align-items:center;gap:var(--space-2);font:var(--weight-bold) var(--text-lg)/1.2 var(--font-display);color:var(--accent-glitch)}
.kh-side{position:absolute;z-index:var(--z-dialogue);left:932px;width:332px;display:flex;flex-direction:column;gap:var(--space-3)}
.kh-side .kh-panel{padding:var(--space-3) var(--space-4)}
.kh-turns{display:flex;flex-direction:column;gap:var(--space-2)}
.kh-turns h3{font-size:var(--text-lg);display:flex;align-items:center;gap:var(--space-2)}
.kh-turn{display:grid;grid-template-columns:28px 1fr;gap:var(--space-2);align-items:center;font-size:var(--text-sm)}
.kh-turn .dot{width:28px;height:28px;border-radius:var(--radius-pill);border:2px solid var(--border);display:inline-flex;align-items:center;justify-content:center;color:var(--accent-discovery)}
.kh-turn.cur .dot{border-color:var(--accent-glitch);color:var(--accent-glitch)}
.kh-turn.cur{font-weight:var(--weight-bold)}
.kh-turn.todo{color:var(--text-muted)}
.kh-turns .free{display:inline-flex;align-items:center;gap:var(--space-2);color:var(--text-muted);font-size:var(--text-sm)}
.kh-retry{display:flex;gap:var(--space-3);flex-wrap:wrap}
.inset-tall .kh-mini{margin-bottom:var(--space-1)}
.inset-tall .kh-effect{font-size:var(--text-base)}
.kh-mini .kh-key.gap{visibility:hidden;min-width:14px}
"""


# --------------------------------------------------------------------------- shell
def shot(sid, title, lede, inner, scrim="scrim", note=None, world=True):
    """One 1366 x 768 viewport with the 1280 x 720 stage; sid names the #s-<sid> and #s-<sid>-grey targets."""
    img = ('<img class="world" src="world-native.png" width="320" height="180" alt="">' if world else "")
    nt = f'<p class="note">{note}</p>' if note else ""
    return f"""
<section class="shot" aria-label="{title}">
  <span class="a" id="s-{sid}"></span><span class="a g" id="s-{sid}-grey"></span>
  <div class="sheet-head"><h2>{title}</h2><p class="lede">{lede}</p></div>
  <div class="viewport"><div class="stage">
    {img}{'' if scrim == 'none' else '<div class="scrim ' + (scrim if scrim != 'scrim' else '') + '"></div>'}
    {inner}
  </div></div>
  {nt}
</section>"""


# --------------------------------------------------------------------------- feedback component
def fb_card(state, gesture, output, effect, why=None, style=""):
    """state: observed | confirmed | reserved. gesture/output/effect are HTML."""
    head = {
        "observed": ("eye", "Observed output"),
        "confirmed": ("person-check", "You confirmed this gesture"),
        "reserved": ("shield-key", "Can't be observed here (OS-reserved)"),
    }[state]
    w = f'<p class="why">{why}</p>' if why else ""
    return f"""
<div class="kh-fb {state}" style="{style}" role="status">
  <div class="what">{ico(head[0], 24)}<span>{head[1]}</span></div>
  <dl>
    <dt>Gesture shown</dt><dd>{gesture}</dd>
    <dt>Output</dt><dd>{output}</dd>
    <dt>Effect</dt><dd class="fx">{effect}</dd>
  </dl>
  {w}
</div>"""


def chip_practice(confirmed):
    if confirmed:
        return f'<span class="kh-chip confirmed">{ico("person-check", 20)} Practice layer: player-confirmed</span>'
    return f'<span class="kh-chip unconfirmed">{ico("circle", 20)} Practice layer: unconfirmed</span>'


FB_OBSERVED = dict(
    state="observed",
    gesture=f'{kc("F")} hold + {kc("Caps")} hold + {kc("W")} tap',
    output='<span class="mono">Shift + Option + Right</span>',
    effect="Selected the next word",
    why="The game saw this output. It cannot see which physical key made it.",
)
FB_CONFIRMED = dict(
    state="confirmed",
    gesture=f'{kc("Space")} hold, then {kc("A")} tap',
    output='<span class="mono">1</span> observed; the 1 key gives it too',
    effect="Counts as confirmed, not as observed",
    why="You said you used <b>Space + A</b>. It stays your word, never proof.",
)
FB_RESERVED = dict(
    state="reserved",
    gesture=f'{kc("Tab")} hold about 250 ms',
    output="none the browser can see",
    effect="Confirm it, or skip: no penalty",
    why="macOS handles it before the page. A missing event is not a mistake.",
)


# --------------------------------------------------------------------------- Layout help
def u2px(u):
    return round(u * 64 + (u - 1) * 6)


def mac_rows():
    r1 = [("`", "`", 1)] + [(c, c, 1) for c in "1234567890-="] + [("Backspace", "Backspace", 2)]
    r2 = [("Tab", "Tab", 1.5)] + [(c, c, 1) for c in "qwertyuiop[]"] + [("\\", "\\", 1.5)]
    r3 = [("Caps", "Caps", 1.75)] + [(c, c, 1) for c in "asdfghjkl;'"] + [("Return", "Return", 2.25)]
    r4 = [("Shift-L", "Shift", 2.25)] + [(c, c, 1) for c in "zxcvbnm,./"] + [("Shift-R", "Shift", 2.75)]
    r5 = [("fn", "fn", 1), ("Ctrl-L", "Ctrl", 1), ("Opt-L", "Opt", 1), ("Cmd-L", "Cmd", 1.25),
          ("Space", "Space", 5), ("Cmd-R", "Cmd", 1.25), ("Opt-R", "Opt", 1), ("gap", "", 0.5),
          ("Left", "←", 1), ("UpDown", "", 1), ("Right", "→", 1)]
    return [r1, r2, r3, r4, r5]


def ms_row():
    """Bottom row of a Microsoft keyboard (arrow cluster is separate and not drawn)."""
    return [("Ctrl-L", "Ctrl", 1.25), ("Win-L", "Win", 1.25), ("Alt-L", "Alt", 1.25), ("Space", "Space", 6.25),
            ("Alt-R", "Alt", 1.25), ("Win-R", "Win", 1.25), ("Menu", "Menu", 1.25), ("Ctrl-R", "Ctrl", 1.25)]


# What each key does on each tab: id -> (sublabel, kind, arrow-size?)
HOLD = {"a": "Ctrl", "s": "Opt", "d": "Cmd", "f": "Shift", "j": "Shift", "k": "Cmd", "l": "Opt", ";": "Ctrl"}
BASE = {k: (v, "map", 0) for k, v in HOLD.items()}
BASE.update({"Caps": ("Esc | nav", "map", 0), "Space": ("tap Space | hold numbers", "map", 0),
             "Tab": ("Homerow", "map", 0), "r": ("reload", "map", 0), "v": ("toggle", "map", 0),
             "Cmd-R": ("+ nav", "map", 0)})
NAVL = {"0": ("Line ←", "map", 0), "4": ("Line →", "map", 0), "w": ("Word →", "map", 0),
        "b": ("Word ←", "map", 0), "u": ("Page ↑", "map", 0), "d": ("Page ↓", "map", 0),
        "t": ("Doc ↑", "map", 0), "g": ("Doc ↓", "map", 0),
        "h": ("←", "map", 1), "j": ("↓", "map", 1), "k": ("↑", "map", 1), "l": ("→", "map", 1),
        "[": ("Esc", "map", 0), "m": ("Bksp", "map", 0), "x": ("Ctrl+D", "map", 0), ",": ("Delete", "map", 0),
        "n": ("Return", "map", 0), "Space": ("Bksp", "map", 0),
        "a": ("= a", "same", 0), "s": ("= s", "same", 0), "f": ("= f", "same", 0),
        "Caps": ("hold", "layer", 0)}
NUMS = {"Space": ("hold", "layer", 0), "Caps": ("nav", "map", 0), "Tab": ("Homerow", "map", 0),
        "n": ("= n", "same", 0), "m": ("= m", "same", 0)}
for key, out in zip("asdfghjkl;'", "1234567890-"):
    NUMS[key] = (out, "map", 1)
for key, out in zip("qwertyuiop[]", "!@#$%^&*()_+"):
    NUMS[key] = (out, "map", 1)

PRACTICE = dict(BASE)
for key in "1234567890":
    PRACTICE[key] = (key, "silent", 0)
for key, name in (("Backspace", "Bksp"), ("Return", "Return"), ("Shift-L", "Shift"), ("Shift-R", "Shift"),
                  ("Ctrl-L", "Ctrl"), ("Opt-L", "Opt"), ("Cmd-L", "Cmd"), ("Cmd-R", "Cmd"), ("Opt-R", "Opt"),
                  ("Left", "←"), ("Right", "→")):
    PRACTICE[key] = (name, "silent", 0)
PRACTICE["UpDown"] = ("", "silent", 0)

MS_BASE = {"Win-L": ("→ Opt", "map", 0), "Alt-L": ("→ Cmd", "map", 0), "Alt-R": ("→ R Cmd", "map", 0),
           "Win-R": ("→ R Opt", "map", 0)}


def lk(kid, label, u, ann, focus=False):
    sub, kind, arrow = ann.get(kid, ("", "", 0))
    px = u2px(u)
    if kind == "silent":
        shown = "XX"
        cls = "silent"
    else:
        shown = label.upper() if len(label) == 1 and label.isalpha() else label
        cls = {"map": "map", "layer": "layerkey", "same": "same"}.get(kind, "")
    s = f'<span class="s{" arrow" if arrow else ""}">{sub}</span>' if sub else ""
    f = " focus" if focus else ""
    return f'<div class="kh-lk {cls}{f}" style="width:{px}px" data-key="{kid}"><span class="l">{shown}</span>{s}</div>'


def updown(ann):
    silent = ann.get("UpDown", ("", "", 0))[1] == "silent"
    out = '<div class="lh-stack" style="width:64px">'
    for g in ("↑", "↓"):
        if silent:
            out += f'<div class="kh-lk half silent"><span class="l">{g}</span><span class="s">XX</span></div>'
        else:
            out += f'<div class="kh-lk half"><span class="l">{g}</span></div>'
    return out + "</div>"


def diagram(ann, focus_id, device="mac"):
    rows = mac_rows()
    if device == "ms":
        rows = rows[:4] + [ms_row()]
    out = '<div class="lh-rows">'
    for r in rows:
        out += '<div class="lh-row">'
        for kid, label, u in r:
            if kid == "gap":
                out += f'<div class="lh-gap" style="width:{u2px(u) - 6}px"></div>'
            elif kid == "UpDown":
                out += updown(ann)
            else:
                out += lk(kid, label, u, ann, kid == focus_id)
        out += "</div>"
    return out + "</div>"


TABS = ("base", "nav", "numbers-symbols", "practice")

DETAIL = {
    "base": dict(
        big=kc("F", "") , dl1=[("Tap", 'types <span class="mono">f</span>'),
                               ("Tap-hold, 200 ms", 'Left Shift (<span class="mono">lsft</span>). A roll with a left-hand key types the letter.')],
        dl2=[("On base", "The home-row hold is the Shift. Pick a key on the other hand."),
             ("On practice", "Normal: the hold still works.")],
        action="To type a capital J, you need to press <b>Shift + J</b>.",
        hint="Hint: Shift is <b>tap-hold F</b>, then tap <b>J</b>."),
    "nav": dict(
        big=kc("L", ""), dl1=[("Tap", 'types <span class="mono">l</span>'),
                              ("Tap-hold, 200 ms", 'Right Option (<span class="mono">ralt</span>)')],
        dl2=[("On nav", "Right arrow."), ("On practice", "Normal: the home-row hold still works.")],
        action="To step one cell east, you need to press <b>Right arrow</b>.",
        hint="Hint: Right arrow is <b>tap-hold Caps</b> + <b>L</b>."),
    "numbers-symbols": dict(
        big=kc("Q", ""), dl1=[("Tap", 'types <span class="mono">q</span>'),
                              ("Tap-hold", "none: Q is a plain letter")],
        dl2=[("On numbers-symbols", "<span class=\"mono\">!</span> (Shift + 1), after Space is held about 220 ms."),
             ("On practice", "Normal: held Space still gives it.")],
        action="To type an exclamation mark, you need to press <b>!</b> (Shift + 1).",
        hint="Hint: <b>!</b> is <b>tap-hold Space</b> + <b>Q</b>."),
    "practice": dict(
        big=kc("XX", "silent"), dl1=[("Tap", "silent: the key sends nothing"), ("Tap-hold", "none")],
        dl2=[("On practice", "Backspace is XX. Caps + M sends Backspace instead."),
             ("On base", "Normal Backspace.")],
        action="To delete the character before the cursor, you need to press <b>Backspace</b>.",
        hint="Hint: Backspace is <b>tap-hold Caps</b> + <b>M</b>."),
}
FOCUS = {"base": "f", "nav": "l", "numbers-symbols": "q", "practice": "Backspace"}
ANN = {"base": BASE, "nav": NAVL, "numbers-symbols": NUMS, "practice": PRACTICE}

LEGEND = {
    "base": [("map", "A", "hold action underneath"), ("", "B", "unchanged")],
    "nav": [("map", "W", "output with Caps held"), ("same", "A", "stays a letter"), ("", "Q", "unchanged"),
            ("layerkey", "Caps", "Caps held")],
    "numbers-symbols": [("map", "Q", "symbol while Space is held"), ("same", "N", "stays a letter"), ("", "Z", "unchanged"),
                        ("layerkey", "Spc", "Space held")],
    "practice": [("silent", "XX", "silent: sends nothing"), ("map", "A", "still works here"), ("", "B", "unchanged")],
}


def legend(tab):
    out = '<div class="lh-legend">'
    for cls, letter, text in LEGEND[tab]:
        inner = "XX" if cls == "silent" else letter
        out += f'<span><span class="kh-lk {cls}" style="width:44px"><span class="l">{inner}</span></span> {text}</span>'
    return out + "</div>"


def seg(items, focus=None):
    s = '<div class="seg" role="group">'
    for name, on in items:
        f = " focus" if name == focus else ""
        mark = ico("check", 16) if on else ""
        s += f'<span class="{f.strip()}" aria-pressed="{"true" if on else "false"}">{mark}{name}</span>'
    return s + "</div>"


def layout_screen(tab, device="mac"):
    tabs = "".join(f'<span class="tab" role="tab" aria-selected="{"true" if t == tab else "false"}">{t}</span>' for t in TABS)
    ann = dict(ANN[tab])
    if device == "ms":
        ann.update(MS_BASE)
    d = DETAIL[tab]
    focus = FOCUS[tab]
    if device == "ms":
        focus = "Alt-L"
    dev = seg([("MacBook", device == "mac"), ("Microsoft", device == "ms")], focus="Microsoft" if device == "ms" else None)
    how = ('<p class="lh-how">Switch tab: <b>Left / Right</b> (tap-hold Caps + H / L) or <b>Tab / Shift + Tab</b>. '
           'Click and hold the drawn <b>Caps</b> or <b>Space</b> to preview that layer. <b>Esc</b> (tap Caps) closes.</p>')
    if device == "ms":
        detail = f"""
    <div class="lh-detail">
      <div class="big">{kc("Alt", "")}</div>
      <dl><dt>Physical key</dt><dd>Left Alt, next to Space</dd><dt>Result</dt><dd>Command (<span class="mono">lmet</span>) on this keyboard only</dd></dl>
      <dl><dt>Also remapped</dt><dd>Windows becomes Option; Right Alt becomes Right Command and also holds nav; Right Windows becomes Right Option.</dd></dl>
      <p class="hintline">To save a file, you need to press <b>Command + S</b>. <span class="hint">Hint: Command is <b>physical Alt</b> on this keyboard (tap-hold D works on both).</span></p>
    </div>"""
        foot = f"""
    <div class="lh-foot">
      <div class="lh-remap"><span>{kc("Alt")} {ico("arrow-right", 16)} Command</span><span>{kc("Win")} {ico("arrow-right", 16)} Option</span><span>{kc("Alt")} right {ico("arrow-right", 16)} Right Command + nav</span></div></div>"""
        also = ""
    elif tab == "practice":
        detail = f"""
    <div class="lh-cards">
      <div class="lh-card">
        <span class="kh-label">Focused key</span>
        <div class="row">{kc("XX", "silent")}<div><b>Backspace</b> is silent. Caps + M sends it instead.</div></div>
        <p>To delete the character before the cursor, you need to press <b>Backspace</b>. Hint: it is <b>tap-hold Caps</b> + <b>M</b>.</p>
      </div>
      <div class="lh-card">
        <span class="kh-label">Toggle out of practice</span>
        <div class="seq">{kc("Control")}+{kc("Alt")}+{kc("GUI")}+{kc("V")}</div>
        <p>To return to base, you need to press <b>physical Control + Alt + GUI + V</b>. Hint: home-row holds do not count. The game cannot see this: tell it.</p>
      </div>
      <div class="lh-card locked">
        <span class="kh-label">{ico("lock", 20)} Emergency exit</span>
        <p><b>Shown after its runtime behaviour is verified</b> on this machine.</p>
      </div>
    </div>"""
        foot = f"""
    <div class="lh-foot">{legend(tab)}</div>"""
        also = ('<p class="lh-also"><b>Also silent:</b> Esc, Forward Delete, Home, End, Page Up and Down. '
                'Digits 1 to 0 and their symbols are blocked; <span class="mono">- = `</span> still type.</p>')
    else:
        detail = f"""
    <div class="lh-detail">
      <div class="big">{d['big']}</div>
      <dl>{''.join(f'<dt>{a}</dt><dd>{b}</dd>' for a, b in d['dl1'])}</dl>
      <dl>{''.join(f'<dt>{a}</dt><dd>{b}</dd>' for a, b in d['dl2'])}</dl>
      <p class="hintline">{d['action']} <span class="hint">{d['hint']}</span></p>
    </div>"""
        foot = f"""
    <div class="lh-foot">{legend(tab)}</div>"""
        also = ""
    return f"""
<div class="kh-panel overlay lh-overlay" role="dialog" aria-label="Layout help, {tab} tab">
  <div class="top"><h2>Layout help</h2>
    <div class="tabs" role="tablist">{tabs}</div>
    <span class="lh-device">Keyboard {dev}</span><span class="grow"></span>
    <span class="close"><span class="kh-key sm">Esc</span> tap Caps to close</span></div>
  {how}
  <div class="kh-lh">
    {diagram(ann, focus, device)}
    {also}
    {detail}
    {foot}
  </div>
</div>"""


def layout_sections():
    out = ""
    specs = [
        ("layout-base", "base", "mac", "Layout help: base tab (MacBook, the default diagram)",
         "Home-row letters carry their hold action underneath; Caps, Space and Tab show tap and hold; R and V are the reload and practice-toggle chords; Right Command also holds the nav layer. The bottom row is the MacBook's. Detail card: F."),
        ("layout-nav", "nav", "mac", "Layout help: nav tab",
         "Caps is drawn held. Every key that does something with Caps down prints its output; A, S and F stay letters. Detail card: L (Right arrow)."),
        ("layout-numbers-symbols", "numbers-symbols", "mac", "Layout help: numbers-symbols tab",
         "Space is drawn held. The home row gives 1 to 0 and minus, the top row gives the twelve symbols; N and M stay letters; Caps and Tab keep their roles. Detail card: Q."),
        ("layout-practice", "practice", "mac", "Layout help: practice tab",
         "Silenced physical keys are dashed and read XX (the key's name is underneath). Home-row holds, Caps and held Space still work. The toggle-out sequence is shown; the emergency exit stays locked until its behaviour is verified."),
        ("layout-base-microsoft", "base", "ms", "Layout help: base tab, Microsoft keyboard selected",
         "Same screen with the keyboard switch set to Microsoft: the bottom row is a PC row, and Alt becomes Command, Windows becomes Option. The default (MacBook) is the first render."),
    ]
    for sid, tab, dev, title, lede in specs:
        out += shot(sid, title, lede, layout_screen(tab, dev))
    return out


# --------------------------------------------------------------------------- Setup and calibration
SK_ROWS = [
    [("`", 1)] + [(c, 1) for c in "1234567890-="] + [("Bksp", 2)],
    [("Tab", 1.5)] + [(c, 1) for c in "qwertyuiop[]"] + [("\\", 1.5)],
    [("Caps", 1.75)] + [(c, 1) for c in "asdfghjkl;'"] + [("Return", 2.25)],
    [("Shift", 2.25)] + [(c, 1) for c in "zxcvbnm,./"] + [("Shift", 2.75)],
    [("Ctrl", 1.5), ("Opt", 1.5), ("Cmd", 1.5), ("Space", 5), ("Cmd", 1.5), ("Opt", 1.5)],
]
SK_NUMS = dict(zip("asdfghjkl;'", "1234567890-"))
SK_NUMS.update(dict(zip("qwertyuiop[]", "!@#$%^&*()_+")))


def sk_px(u):
    return round(u * 28 + (u - 1) * 3)


def setup_diagram(mode):
    """Compact keyboard for the Space + Q calibration step. mode: positions | characters."""
    out = '<div class="sk-rows">'
    for r in SK_ROWS:
        out += '<div class="sk-row">'
        for label, u in r:
            cls = ""
            shown = label
            if label == "Space":
                cls = "layerkey"
                shown = "Space (held)" if mode == "positions" else "Space"
            elif label == "q":
                cls = "target"
            if mode == "characters" and label in SK_NUMS and len(label) == 1:
                shown = SK_NUMS[label]
            elif len(label) == 1 and label.isalpha() and mode == "positions":
                shown = label.upper()
            out += f'<div class="kh-sk {cls}" style="width:{sk_px(u)}px">{shown}</div>'
        out += "</div>"
    return out + "</div>"


def step_row(n, title, outv, text, status, cur=False):
    chip = {
        "todo": f'<span class="kh-chip todo">{ico("circle", 20)} Not started</span>',
        "obs": f'<span class="kh-chip obs">{ico("eye", 20)} Observed output</span>',
        "skip": f'<span class="kh-chip skip">{ico("skip", 20)} Skipped</span>',
    }[status]
    return f"""
    <div class="su-step{' cur' if cur else ''}">
      <span class="n">{n}</span>
      <span class="t">{title} <span class="mono">{outv}</span></span>
      {chip}
      <span class="d">{text}</span>
    </div>"""


def strip_mac():
    return (f'<div class="strip"><span class="kh-key dim">Ctrl</span><span class="kh-key dim">Opt</span>'
            f'<span class="kh-key">Cmd</span><span class="kh-key sp">Space</span><span class="kh-key">Cmd</span>'
            f'<span class="kh-key dim">Opt</span></div>')


def strip_ms():
    return (f'<div class="strip"><span class="kh-key dim">Ctrl</span><span class="kh-key dim">Win</span>'
            f'<span class="arrowto">{ico("arrow-right", 16)} Opt</span>'
            f'<span class="kh-key">Alt</span><span class="arrowto">{ico("arrow-right", 16)} Cmd</span>'
            f'<span class="kh-key sp">Space</span></div>')


def setup_screen(device, mode):
    mac_sel = device == "mac"
    pick = lambda on: (f'<span class="pick">{ico("check", 18)} Selected</span>' if on
                       else '<span class="pick">Not selected</span>')
    steps = (
        step_row(1, "Caps + H", "→ Left arrow",
                 "To walk west, you need to press <b>Left arrow</b>. Hint: it is <b>tap-hold Caps + H</b>.", "obs")
        + step_row(2, "Caps + N", "→ Return",
                   "To submit, you need to press <b>Return</b>. Hint: Return is <b>tap-hold Caps + N</b>.", "obs")
        + step_row(3, "Space + A", "→ 1",
                   "To type a one, you need to press <b>1</b>. Hint: 1 is <b>tap-hold Space + A</b>.", "obs")
        + step_row(4, "Space + Q", "→ !",
                   "To type an exclamation mark, you need to press <b>!</b>. Hint: it is <b>tap-hold Space + Q</b>.", "todo", cur=True)
        + step_row(5, "Shift on the home row", "→ capital J",
                   "To type a capital J, you need to press <b>Shift + J</b>. Hint: Shift is <b>tap-hold F</b>, then J.", "skip")
    )
    if mode == "positions":
        cap = "<b>Physical positions</b>: hold <b>Space</b> about 220 ms, then tap <b>Q</b>."
    else:
        cap = "<b>Resulting characters</b> while Space is held: <b>Q</b> gives <b>!</b>."
    return f"""
<div class="kh-panel overlay su" role="dialog" aria-label="Setup and calibration">
  <div class="top"><h2>Set up your keyboard</h2><span class="sub">About two minutes. Nothing here blocks the story.</span>
    <span class="grow"></span>
    <span class="kh-btn">Skip setup <span class="kh-key sm">Esc</span></span>
    <span class="kh-btn primary focus">Continue <span class="kh-key sm">Return</span></span></div>
  <div class="su-choice" role="radiogroup" aria-label="Keyboard">
    <div class="su-opt{' sel' if mac_sel else ''}" role="radio" aria-checked="{'true' if mac_sel else 'false'}">
      <h3>MacBook keyboard <span class="kh-label">default</span></h3>{pick(mac_sel)}
      {strip_mac()}
      <p>The diagrams are drawn for this keyboard.</p>
    </div>
    <div class="su-opt{' sel' if not mac_sel else ''}" role="radio" aria-checked="{'false' if mac_sel else 'true'}">
      <h3>Microsoft keyboard</h3>{pick(not mac_sel)}
      {strip_ms()}
      <p>Right Alt becomes Right Command and also holds nav.</p>
    </div>
  </div>
  <div class="su-body">
    <div class="su-steps">
      <div class="head"><span class="kh-label">Calibration: five optional steps</span><span class="kh-label">3 observed · 1 skipped</span></div>
      {steps}
      <p class="su-foot">The number row gives the same 1 and ! as Space + A and Space + Q, so observed output never proves which key you used.</p>
    </div>
    <div class="su-side">
      <div class="su-diagram">
        <div class="head"><span class="kh-label">Diagram</span>{seg([("Physical positions", mode == "positions"), ("Resulting characters", mode == "characters")], focus="Resulting characters" if mode == "characters" else None)}</div>
        {setup_diagram(mode)}
        <p class="cap">{cap}</p>
      </div>
      <div class="su-toggle">
        <span class="kh-label">Practice toggle-out</span>
        <div class="seq">{kc("Control")}+{kc("Alt")}+{kc("GUI")}+{kc("V")}</div>
        <p>To return to base, you need to press <b>physical Control + Alt + GUI + V</b>. Hint: home-row holds do not count.</p>
        <div>{chip_practice(False)}</div>
      </div>
    </div>
  </div>
</div>"""


def setup_sections():
    out = shot("setup-calibration", "Setup and calibration: MacBook, physical positions",
               "First-run screen. Keyboard choice, five calibration steps with a status each (not started, observed output, skipped), the diagram in its physical-positions view, and the practice toggle-out sequence. Everything can be skipped.",
               setup_screen("mac", "positions"))
    out += shot("setup-characters", "Setup and calibration: Microsoft keyboard, resulting characters",
                "The same screen with the Microsoft keyboard selected and the diagram switched to resulting characters.",
                setup_screen("ms", "characters"))
    return out


# --------------------------------------------------------------------------- Terminal and editor scenes
def code_line(n, body, cls="", tag="", icon="target"):
    marker = ico(icon, 16) if "tl" in cls else ""
    t = f'<span class="tag">{ico(icon, 16)} {tag}</span>' if tag else ""
    return f'<div class="kh-line {cls}"><span class="no">{marker}{n}</span><span>{body}</span>{t}</div>'


def inset_scene(title, layer, row_top, row_home, hold, tap, outcap, effect, foot):
    top = "".join(row_top)
    home = "".join(row_home)
    return f"""
<section class="kh-panel kh-inset inset-tall" aria-label="Keyboard teaching inset: {title}">
  <div class="head"><h3>{title}</h3><span class="layer">{layer}</span></div>
  <div class="kh-cell">
    <div class="kh-label"><span class="kh-order">1</span> Key position <span style="font-weight:400;text-transform:none;letter-spacing:0">top row and home row</span></div>
    <div class="kh-mini" aria-hidden="true">{top}</div>
    <div class="kh-mini" aria-label="Home row" style="margin-top:2px">{home}</div>
  </div>
  <div class="row">
    <div class="kh-cell">
      <div class="kh-label"><span class="kh-order">2</span> Hold order</div>
      <div class="kh-hold">{keycap("Caps", "held", "Hold", "hold")}<span class="plus">+</span>{keycap(tap, "", "Tap", "tap")}</div>
    </div>
    <div class="kh-cell">
      <div class="kh-label"><span class="kh-order">3</span> Output</div>
      <div class="kh-out"><span class="kh-key">{outcap[0]}</span><span>{outcap[1]}</span></div>
    </div>
    <div class="kh-cell">
      <div class="kh-label"><span class="kh-order">4</span> Effect</div>
      <div class="kh-effect">{ico("step-east", 28)}<span>{effect}</span></div>
    </div>
  </div>
  </section>"""


def mini(row, bright, held=None):
    out = []
    for k in row:
        if k == held:
            out.append(f'<span class="kh-key cap held">{k}</span>')
        elif k == bright:
            out.append(f'<span class="kh-key">{k.upper() if len(k)==1 else k}</span>')
        elif k == "gap":
            out.append('<span class="kh-key gap"></span>')
        else:
            out.append(f'<span class="kh-key dim">{k.upper() if len(k)==1 else k}</span>')
    return out


def term_scene(state="working"):
    ok = state == "success"
    l1 = code_line(1, '<span class="k">FROM</span>    records-desk')
    l2 = code_line(2, '<span class="k">TO</span>      harbour-street-12')
    if ok:
        l3 = code_line(3, '<span class="k">NOTE</span>    parcel was moved twice')
        l4 = code_line(4, '<span class="k">NOTE</span>    <span class="sel">address</span><span class="cur"> </span>does not match the form', "tl", tag="selected", icon="check")
    else:
        l3 = code_line(3, '<span class="k">NOTE</span>    parcel <span class="sel">was moved</span><span class="cur"> </span>twice')
        l4 = code_line(4, '<span class="k">NOTE</span>    <span class="tw">address</span> does not match the form', "tl", tag="target line")
    l5 = code_line(5, '<span class="k">STATUS</span>  waiting for review')
    if ok:
        task = f"""
  <div class="kh-task ok" role="status">
    <div class="win">{ico("check", 28)}<span><b>Done.</b> <b>address</b> is selected on the target line. Next, to delete it you need to press <b>Backspace</b>. Hint: Backspace is <b>tap-hold Caps</b> + <b>M</b>.</span></div>
    <span class="count">{ico("target", 20)} 2 / 3</span>
  </div>"""
    else:
        task = f"""
  <div class="kh-task">
    <p>To select the next word, you need to press <b>Shift + Option + Right</b>. <span class="hint">Hint: Shift + Option + Right is <b>tap-hold F</b> (Shift) first, then <b>tap-hold Caps + W</b>.</span></p>
    <span class="count">{ico("target", 20)} 1 / 3</span>
  </div>"""
    top = mini(["Tab", "q", "w", "e", "r", "t", "y"], "w")
    home = mini(["Caps", "a", "s", "d", "f", "g", "h"], None, held="Caps")
    inset = inset_scene("Select the next word", "nav layer · tap-hold Caps · 200 ms", top, home, None, "W",
                        (ico("arrow-right", 28), "Option + Right"), "Next word",
                        "Hold Shift first: tap-hold F, then Caps + W.")
    fb = fb_card(**FB_OBSERVED)
    return f"""
<section class="kh-panel kh-term" aria-label="Terminal scene: ticket log">
  <div class="bar"><span class="name">ticket-4821.log</span><span class="where">Records · Filing Drift</span><span class="grow"></span>
    <span class="leave">Leave the terminal <span class="kh-key sm">Esc</span> tap Caps</span></div>
  {task}
  <div class="kh-code" aria-label="Log, five lines">{l1}{l2}{l3}{l4}{l5}</div>
</section>
<div class="kh-hud shortcuts"><span class="chip">Layout help <span class="kh-key sm">?</span></span></div>
<div class="kh-side" style="top:88px">{fb}</div>
{inset}"""


def tab_scene():
    top = mini(["Tab", "q", "w", "e", "r", "t", "y"], "Tab")
    home = mini(["Caps", "a", "s", "d", "f", "g", "h"], None, held=None)
    inset = f"""
<section class="kh-panel kh-inset inset-tall" aria-label="Keyboard teaching inset: Tab">
  <div class="head"><h3>Move to the next field</h3><span class="layer">base layer · tap Tab</span></div>
  <div class="kh-cell">
    <div class="kh-label"><span class="kh-order">1</span> Key position <span style="font-weight:400;text-transform:none;letter-spacing:0">top row, left edge</span></div>
    <div class="kh-mini" aria-hidden="true">{''.join(top)}</div>
  </div>
  <div class="row">
    <div class="kh-cell">
      <div class="kh-label"><span class="kh-order">2</span> Hold order</div>
      <div class="kh-hold">{keycap("Tab", "wide", "Tap", "tap")}</div>
    </div>
    <div class="kh-cell">
      <div class="kh-label"><span class="kh-order">3</span> Output</div>
      <div class="kh-out"><span class="kh-key wide">Tab</span><span>Tab</span></div>
    </div>
    <div class="kh-cell">
      <div class="kh-label"><span class="kh-order">4</span> Effect</div>
      <div class="kh-effect">{ico("step-east", 28)}<span>Next field</span></div>
    </div>
  </div>
</section>"""
    return f"""
<section class="kh-panel kh-term" aria-label="Terminal scene: ticket form, Tab practice region">
  <div class="bar"><span class="name">ticket-form</span><span class="where">Orientation · The Clock</span><span class="grow"></span>
    <span class="leave">Leave the region <span class="kh-key sm">Esc</span> tap Caps</span></div>
  <div class="kh-task">
    <p>To move to the next field, you need to press <b>Tab</b>. <span class="hint">Hint: Tab is <b>tap Tab</b>: a tap, not a hold.</span></p>
    <span class="count">{ico("target", 20)} 2 / 3</span>
  </div>
  <div class="kh-code" style="padding:0">
    <div class="kh-region" role="group" aria-label="Tab practice region">
      <span class="lab">{ico("lock", 18)} Tab practice region: Tab moves between these fields only</span>
      <div class="frow"><span>Ticket</span><span class="field">4821</span></div>
      <div class="frow"><span>Desk</span><span class="field on">West desk</span></div>
      <div class="frow"><span>Note</span><span class="field">&nbsp;</span></div>
    </div>
  </div>
  <div class="kh-announce" role="status"><span class="kh-label">{ico("eye", 18)} Announced</span>
    <span>You are in the Tab practice region. Tab moves between three fields. <b>Esc</b> (tap Caps) leaves it at any time.</span></div>
</section>
<div class="kh-hud shortcuts"><span class="chip">Layout help <span class="kh-key sm">?</span></span></div>
<div class="kh-side" style="top:88px">{fb_card("observed", kc("Tab") + " tap", '<span class="mono">Tab</span>', "Focus moved to Desk", "The game saw the Tab key event. Tab never leaves the region on its own.")}</div>
{inset}"""


def duel_scene():
    code = f"""
{code_line(1, '<span class="k">ship_to</span> = "Harbour <span class="gl">Strret</span> 12"')}
{code_line(2, '<span class="k">items</span>   = 3')}
{code_line(3, '<span class="k">paid</span>    = true')}"""
    top = mini(["Tab", "z", "x", "c", "v", "b", "n", "m"], "m")
    home = mini(["Caps", "a", "s", "d", "f", "g", "h"], None, held="Caps")
    inset = inset_scene("Delete a letter", "nav layer · tap-hold Caps · 200 ms", top, home, None, "M",
                        ("⌫", "Backspace"), "Remove a letter",
                        "The cursor sits after the extra letter. Try again as often as you like.")
    # use bottom-row slice for the position cell label
    inset = inset.replace("top row and home row", "bottom row and home row")
    turns = f"""
<section class="kh-panel kh-turns" aria-label="Repair turns">
  <h3>{mico("glitch", 28)} Turns</h3>
  <div class="kh-turn">{'<span class="dot">' + ico("check", 18) + '</span>'}<span>Turn 1: found the token</span></div>
  <div class="kh-turn cur"><span class="dot">{ico("play", 14)}</span><span>Turn 2: fix the token</span></div>
  <div class="kh-turn todo"><span class="dot"></span><span>Turn 3: send the order</span></div>
  <span class="free">{ico("circle", 18)} Untimed. Nothing is lost on a retry.</span>
</section>"""
    fb = fb_card("observed", kc("Caps") + " hold, then " + kc("M") + " tap", '<span class="mono">Backspace</span>',
                 "Removed one letter: &quot;Strret&quot; is now &quot;Stret&quot;", "Not quite yet: one letter is still wrong. Retry restarts this turn.")
    return f"""
<section class="kh-panel kh-term glitch" aria-label="Glitch repair duel">
  <div class="bar"><span class="glt">{mico("glitch", 32)} Glitch repair: the misprinted address</span><span class="grow"></span>
    <span class="leave">Leave the duel <span class="kh-key sm">Esc</span> tap Caps</span></div>
  <div class="kh-task">
    <p>To delete the extra letter, you need to press <b>Backspace</b>. <span class="hint">Hint: Backspace is <b>tap-hold Caps</b> + <b>M</b>.</span></p>
    <span class="count">{ico("target", 20)} turn 2 / 3</span>
  </div>
  <div class="kh-code" aria-label="Code fragment">{code}</div>
  <div class="kh-retry"><span class="kh-btn focus">{ico("arrow-left", 18)} Retry this turn <span class="kh-key sm">Return</span></span>
    <span class="kh-btn">Leave the duel <span class="kh-key sm">Esc</span></span></div>
</section>
<div class="kh-hud shortcuts"><span class="chip">Layout help <span class="kh-key sm">?</span></span></div>
<div class="kh-side" style="top:88px">{turns}{fb}</div>
{inset}"""


def scene_sections():
    out = shot("terminal-scene", "Terminal scene: editor with the keyboard inset open",
               "Widened reading column (900 px, 18 px mono), the world dimmed but still visible, a strong block cursor, a selection with a bar under it, a target line (gold gutter marker and tag) and a target word (dashed outline). The inset sits below the editor and never covers the cursor line.",
               term_scene("working"), scrim="scene")
    out += shot("terminal-success", "Terminal scene: success state",
                "Success is shown as text, a check icon, a thicker gold frame and a gold highlight on the target; no full-screen effect. The counter advances.",
                term_scene("success"), scrim="scene")
    out += shot("terminal-tab-practice", "Terminal scene: Tab practice region",
                "Tab lessons run inside a dashed, labelled region. The announcement is written out (and read by screen readers); Esc leaves at any time, and the region never traps focus.",
                tab_scene(), scrim="scene")
    out += shot("glitch-duel", "Glitch-repair duel",
                "Turn-based and untimed. Violet frames and glyphs only; the title text uses the lighter glitch accent. Retry is a visible button; a wrong result gets a plain explanation.",
                duel_scene(), scrim="scene")
    return out


# --------------------------------------------------------------------------- Input feedback sheet
def feedback_sheet():
    cells = [
        ("The game saw a character or key event it can score.", FB_OBSERVED),
        ("The output is ambiguous or external; you vouched for the physical gesture.", FB_CONFIRMED),
        ("macOS or the browser keeps the shortcut. Nothing can be scored.", FB_RESERVED),
    ]
    cols = "".join(f'<div class="fb-cell"><p>{d}</p>{fb_card(**kw)}</div>' for d, kw in cells)
    inner = f"""
<div class="kh-panel overlay su" role="dialog" aria-label="Input feedback states">
  <div class="top"><h2>Input feedback</h2><span class="sub">Three states, each with its own icon, border and words.</span><span class="grow"></span>
    {chip_practice(True)} {chip_practice(False)}</div>
  <div class="fb-sheet">{cols}</div>
  <div class="fb-layers"><span class="kh-label">Two layer facts, kept apart</span>
    <span class="box">{ico("eye", 20)} The scene is showing: <b>nav</b> (the game's own scene)</span>
    <span class="box">{ico("person-check", 20)} You said practice is: <b>active</b> (only your word)</span></div>
  <div class="fb-rules">
    <div class="kh-panel">
      <h3>{ico("check", 22)} Say</h3>
      <ul>
        <li>{ico("eye", 20)}<span>&quot;<b>Observed output</b>: Option + Right.&quot;</span></li>
        <li>{ico("person-check", 20)}<span>&quot;<b>You confirmed</b> tap-hold Space + A.&quot;</span></li>
        <li>{ico("shield-key", 20)}<span>&quot;<b>Can't be observed here</b> (OS-reserved).&quot; Then confirm or skip.</span></li>
        <li>{ico("circle", 20)}<span>&quot;Practice layer: <b>player-confirmed</b> / <b>unconfirmed</b>.&quot;</span></li>
      </ul>
    </div>
    <div class="kh-panel no">
      <h3>{ico("lock", 22)} Never say</h3>
      <ul>
        <li>{ico("warn", 20)}<span><span class="q">You are in the nav layer.</span> Held layers are invisible.</span></li>
        <li>{ico("warn", 20)}<span><span class="q">You pressed Space + A.</span> Or the number row: same 1.</span></li>
        <li>{ico("warn", 20)}<span><span class="q">Practice mode detected.</span> It cannot be detected.</span></li>
        <li>{ico("warn", 20)}<span><span class="q">Failed</span>, for an OS-reserved shortcut.</span></li>
      </ul>
    </div>
  </div>
</div>"""
    return shot("input-feedback", "Confidence-aware input feedback",
                "Every result says what the game can know. Observed output is solid teal with an eye; a confirmation is a double paper border with a person and a check; an OS-reserved case is a dashed border with a shield. The wording rules follow game-design acceptance criteria 5 and 6.",
                inner)


def p0_sections():
    return layout_sections() + setup_sections() + scene_sections() + feedback_sheet()
