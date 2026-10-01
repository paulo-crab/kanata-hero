#!/usr/bin/env python3
"""Writes reference.html: the static UI kit reference page (task 10.2).

Only tokens.css, world-native.png and inline CSS/SVG are used; the page has no
scripts and no external dependencies. The repetitive Layout help keyboard is
generated here so the diagram and its key data stay in one place.

Run: python3 build_reference.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------- SVG sprite
SPRITE = """
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <path id="p-talk" d="M18 10 H46 A10 10 0 0 1 56 20 V32 A10 10 0 0 1 46 42 H30 L16 56 L20 42 H18 A10 10 0 0 1 8 32 V20 A10 10 0 0 1 18 10 Z"/>
    <path id="p-terminal" d="M14 10 H50 A6 6 0 0 1 56 16 V38 A6 6 0 0 1 50 44 H37 V50 H46 V55 H18 V50 H27 V44 H14 A6 6 0 0 1 8 38 V16 A6 6 0 0 1 14 10 Z"/>
    <path id="p-route" d="M32 4 L60 32 L32 60 L4 32 Z"/>
    <path id="p-glitch" d="M14 6 H38 L52 20 V54 A4 4 0 0 1 48 58 H14 A4 4 0 0 1 10 54 V10 A4 4 0 0 1 14 6 Z"/>
  </defs>

  <!-- Markers: shape first, colour second. Paper halo + ink line keep them legible on any floor. -->
  <symbol id="m-talk" viewBox="0 0 64 64">
    <use href="#p-talk" class="halo"/><use href="#p-talk" class="line"/><use href="#p-talk" style="fill:var(--coral)"/>
    <circle cx="22" cy="26" r="3.2" fill="#182B38"/><circle cx="32" cy="26" r="3.2" fill="#182B38"/><circle cx="42" cy="26" r="3.2" fill="#182B38"/>
  </symbol>
  <symbol id="m-terminal" viewBox="0 0 64 64">
    <use href="#p-terminal" class="halo"/><use href="#p-terminal" class="line"/><use href="#p-terminal" style="fill:var(--teal)"/>
    <rect x="14" y="16" width="36" height="22" rx="2" fill="#182B38"/>
    <path d="M19 22 L26 27 L19 32 M30 33 H39" fill="none" stroke="#F4F2EC" stroke-width="3" stroke-linecap="square" stroke-linejoin="miter"/>
  </symbol>
  <symbol id="m-route" viewBox="0 0 64 64">
    <use href="#p-route" class="halo"/><use href="#p-route" class="line"/><use href="#p-route" style="fill:var(--gold)"/>
    <path d="M24 46 V31 A8 8 0 0 1 40 31 V46 Z" fill="#182B38"/>
    <rect x="21" y="46" width="22" height="3" fill="#182B38"/>
  </symbol>
  <symbol id="m-glitch" viewBox="0 0 64 64">
    <use href="#p-glitch" class="halo"/><use href="#p-glitch" class="line"/><use href="#p-glitch" style="fill:var(--violet)"/>
    <path d="M38 6 V20 H52 Z" fill="#182B38"/>
    <path d="M17 28 H44 M17 49 H44" fill="none" stroke="#182B38" stroke-width="3.5"/>
    <path d="M17 38 H27 L30 33 L34 43 L37 38 H44" fill="none" stroke="#182B38" stroke-width="3.5" stroke-linejoin="miter"/>
  </symbol>

  <!-- Small interface icons, 24 x 24, drawn with currentColor -->
  <symbol id="i-seal" viewBox="0 0 24 24">
    <path d="M8 2 H16 L22 8 V16 L16 22 H8 L2 16 V8 Z" fill="currentColor"/>
    <path d="M7 12 L11 16 L17 8" fill="none" stroke="#182B38" stroke-width="2.6" stroke-linecap="square"/>
  </symbol>
  <symbol id="i-bubble" viewBox="0 0 24 24">
    <path d="M6 3 H18 A4 4 0 0 1 22 7 V13 A4 4 0 0 1 18 17 H12 L6 22 L8 17 H6 A4 4 0 0 1 2 13 V7 A4 4 0 0 1 6 3 Z" fill="currentColor"/>
  </symbol>
  <symbol id="i-stopwatch" viewBox="0 0 24 24">
    <rect x="9" y="1" width="6" height="3" fill="currentColor"/>
    <circle cx="12" cy="14" r="8.5" fill="currentColor"/>
    <path d="M12 8.5 V14 L16 16.5" fill="none" stroke="#182B38" stroke-width="2.4" stroke-linecap="square"/>
  </symbol>
  <symbol id="i-check" viewBox="0 0 24 24"><path d="M4 12.5 L9.5 18 L20 6" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="square"/></symbol>
  <symbol id="i-lock" viewBox="0 0 24 24">
    <rect x="4" y="10" width="16" height="12" rx="2" fill="currentColor"/>
    <path d="M8 10 V7 A4 4 0 0 1 16 7 V10" fill="none" stroke="currentColor" stroke-width="2.6"/>
  </symbol>
  <symbol id="i-play" viewBox="0 0 24 24"><path d="M6 3 L20 12 L6 21 Z" fill="currentColor"/></symbol>
  <symbol id="i-step-east" viewBox="0 0 24 24"><path d="M2 12 H17 M11 5 L18 12 L11 19 M21 4 V20" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
  <symbol id="i-arrow-right" viewBox="0 0 24 24"><path d="M3 12 H20 M13 5 L20 12 L13 19" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
</svg>
"""


def mk(name, cls="", style=""):
    return f'<svg class="kh-marker {cls}" style="{style}" viewBox="0 0 64 64" aria-hidden="true"><use href="#m-{name}"/></svg>'


def ico(name, size=24):
    return f'<svg class="kh-ico" width="{size}" height="{size}" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-{name}"/></svg>'


# --------------------------------------------------------------------------- CSS
CSS = """
*{box-sizing:border-box}
html{background:var(--letterbox);-webkit-text-size-adjust:100%}
body{margin:0;background:var(--letterbox);color:var(--text);font:var(--weight-regular) var(--text-base)/var(--leading-body) var(--font-body)}
html:has(#grey:target) .page{filter:grayscale(1)}
#grey{position:absolute;top:0;left:0;width:1px;height:1px}
h1,h2,h3{font-family:var(--font-display);line-height:var(--leading-tight);margin:0}
a{color:var(--accent-terminal)}
code,.mono{font-family:var(--font-mono)}

/* ---- Panel, label ---------------------------------------------------------- */
.kh-panel{background:var(--panel-bg);color:var(--text);border:2px solid var(--border);border-radius:var(--radius-lg)}
.kh-label{font:var(--weight-bold) var(--text-sm)/var(--leading-tight) var(--font-body);letter-spacing:var(--tracking-label);text-transform:uppercase;color:var(--text-muted)}
.kh-ico{display:inline-block;vertical-align:middle;flex:none}

/* ---- Keycap ----------------------------------------------------------------- */
.kh-key{display:inline-flex;align-items:center;justify-content:center;min-width:var(--key-size-inset);height:var(--key-size-inset);padding:0 var(--space-3);
  background:var(--key-face);color:var(--key-text);border-radius:var(--radius-sm);box-shadow:0 4px 0 var(--key-edge);
  font:var(--weight-bold) var(--text-lg)/1 var(--font-mono);white-space:nowrap;position:relative;top:0;margin-bottom:4px}
.kh-key.wide{min-width:calc(var(--key-size-inset) * 2)}
.kh-key.held{background:var(--key-held-face);color:var(--key-held-text);box-shadow:0 1px 0 var(--key-held-edge);top:3px}
.kh-key.dim{background:var(--key-dim-face);color:var(--key-dim-text);box-shadow:0 3px 0 var(--key-dim-edge);font-weight:var(--weight-regular)}
.kh-key.silent{background:var(--key-silent-face);color:var(--key-silent-text);box-shadow:none;border:2px dashed var(--border);font-weight:var(--weight-regular);margin-bottom:4px}
.kh-key.sm{min-width:32px;height:32px;padding:0 var(--space-2);font-size:var(--text-sm);box-shadow:0 3px 0 var(--key-edge);border-radius:5px;margin-bottom:3px}
.kh-key.focus,.kh-lk.focus{outline:2px solid var(--focus);outline-offset:3px}
.kh-tag{display:block;margin-top:var(--space-2);text-align:center;font:var(--weight-bold) var(--text-sm)/1 var(--font-body);letter-spacing:var(--tracking-label);text-transform:uppercase}
.kh-tag.hold{color:var(--accent-terminal)}
.kh-tag.tap{color:var(--text)}
.kh-keyunit{display:flex;flex-direction:column;align-items:center}
.kh-order{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:var(--radius-pill);background:var(--paper);color:var(--ink);font:var(--weight-bold) var(--text-sm)/1 var(--font-body)}

/* ---- Stage ----------------------------------------------------------------- */
.viewport{position:relative;width:1366px;height:768px;background:var(--letterbox);overflow:hidden}
.stage{position:absolute;left:43px;top:24px;width:var(--stage-w);height:var(--stage-h);overflow:hidden;background:var(--letterbox)}
.stage.screen{position:relative;left:auto;top:auto;margin:0 auto}
.stage .world{position:absolute;left:0;top:0;display:block;width:calc(var(--world-w) * var(--world-zoom));height:calc(var(--world-h) * var(--world-zoom));image-rendering:pixelated;z-index:var(--z-world)}
.kh-marker{position:absolute;width:var(--marker-size);height:var(--marker-size);z-index:var(--z-marker);overflow:visible}
.halo{fill:var(--paper);stroke:var(--paper);stroke-width:9;stroke-linejoin:round}
.line{fill:var(--ink);stroke:var(--ink);stroke-width:5;stroke-linejoin:round}

/* ---- HUD -------------------------------------------------------------------- */
.kh-hud{position:absolute;z-index:var(--z-hud);display:flex;align-items:center;gap:var(--space-3);padding:var(--space-2) var(--space-4);background:var(--panel-bg);border:2px solid var(--border);border-radius:var(--radius-md);font-size:var(--text-lg)}
.kh-hud.obj{left:var(--stage-margin);top:var(--stage-margin);min-height:48px}
.kh-hud .title{font-weight:var(--weight-bold)}
.kh-hud .count{font-family:var(--font-mono);color:var(--text-muted);font-size:var(--text-base)}
.kh-hud .seals{display:inline-flex;align-items:center;gap:var(--space-2);color:var(--accent-discovery);font-size:var(--text-base);font-weight:var(--weight-bold)}
.kh-hud .sep{width:2px;align-self:stretch;background:var(--border)}
.kh-hud.shortcuts{right:var(--stage-margin);top:var(--stage-margin);gap:var(--space-4);font-size:var(--text-sm);min-height:48px}
.kh-hud .chip{display:inline-flex;align-items:center;gap:var(--space-2);font-size:var(--text-sm);color:var(--text)}

/* ---- Interaction prompt ------------------------------------------------------ */
.kh-prompt{position:absolute;z-index:var(--z-prompt);padding:var(--space-3) var(--space-4);background:var(--panel-bg);border:2px solid var(--accent-terminal);border-radius:var(--radius-md);display:flex;flex-direction:column;gap:var(--space-2)}
.kh-prompt::before{content:"";position:absolute;left:-12px;top:22px;width:20px;height:20px;background:var(--panel-bg);border-left:2px solid var(--accent-terminal);border-bottom:2px solid var(--accent-terminal);transform:rotate(45deg)}
.kh-prompt .action{font:var(--weight-bold) var(--text-lg)/var(--leading-tight) var(--font-body);display:flex;align-items:center;gap:var(--space-2)}
.kh-prompt .keys{display:flex;align-items:center;gap:var(--space-3);font-size:var(--text-sm);color:var(--text-muted)}
.kh-prompt .gesture{font-family:var(--font-mono);color:var(--text)}

/* ---- Keyboard teaching inset -------------------------------------------------- */
.kh-inset{position:absolute;z-index:var(--z-inset);left:var(--stage-margin);bottom:var(--stage-margin);width:572px;padding:var(--space-3) var(--space-4);border-color:var(--border-strong);display:flex;flex-direction:column;gap:var(--space-2)}
.kh-inset .head{display:flex;align-items:baseline;justify-content:space-between;gap:var(--space-3)}
.kh-inset .head h3{font-size:var(--text-xl)}
.kh-inset .head .layer{font-size:var(--text-sm);color:var(--accent-terminal);font-weight:var(--weight-bold)}
.kh-cell{background:var(--panel-sunken);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3);min-width:0}
.kh-cell .kh-label{display:flex;align-items:center;gap:var(--space-2);margin-bottom:var(--space-2)}
.kh-mini{display:flex;gap:4px;align-items:flex-end}
.kh-mini .kh-key{min-width:34px;height:32px;padding:0;font-size:var(--text-sm);box-shadow:0 3px 0 var(--key-edge);margin-bottom:3px}
.kh-mini .kh-key.cap{min-width:58px}
.kh-mini .kh-key.dim{box-shadow:0 3px 0 var(--key-dim-edge)}
.kh-mini .kh-key.held{box-shadow:0 1px 0 var(--key-held-edge)}
.kh-inset .row{display:grid;grid-template-columns:auto auto 1fr;gap:var(--space-2)}
.kh-hold{display:flex;align-items:flex-start;gap:var(--space-2)}
.kh-hold .plus{font:var(--weight-bold) var(--text-xl)/var(--key-size-inset) var(--font-body);height:var(--key-size-inset)}
.kh-out{font:var(--weight-bold) var(--text-base)/var(--leading-tight) var(--font-mono);display:flex;flex-direction:column;gap:var(--space-2);align-items:flex-start}
.kh-effect{white-space:nowrap;display:flex;align-items:center;gap:var(--space-2);font:var(--weight-bold) var(--text-lg)/var(--leading-tight) var(--font-body);color:var(--accent-discovery);height:var(--key-size-inset)}
.kh-inset .foot{font-size:var(--text-sm);color:var(--text-muted)}

/* ---- Dialogue --------------------------------------------------------------- */
.kh-dialogue{position:absolute;z-index:var(--z-dialogue);right:var(--stage-margin);bottom:var(--stage-margin);width:672px;height:224px;padding:var(--space-4);display:flex;gap:var(--space-4)}
.kh-portrait{flex:none;width:var(--portrait-size);height:var(--portrait-size);border-radius:var(--radius-md);border:2px solid var(--accent-conversation);background:
  repeating-linear-gradient(45deg,var(--panel-sunken) 0 12px,var(--panel-raised) 12px 24px);display:flex;align-items:flex-end;justify-content:center;padding:var(--space-2)}
.kh-portrait span{background:var(--panel-bg);border-radius:var(--radius-sm);padding:2px var(--space-2);font:var(--weight-bold) var(--text-sm)/1.3 var(--font-mono);text-align:center}
.kh-dialogue .body{display:flex;flex-direction:column;min-width:0;flex:1}
.kh-dialogue .who{display:flex;align-items:center;gap:var(--space-2);font:var(--weight-bold) var(--text-xl)/var(--leading-tight) var(--font-display)}
.kh-dialogue .who .role{font:var(--weight-regular) var(--text-sm)/1 var(--font-body);color:var(--text-muted)}
.kh-dialogue .say{margin:var(--space-2) 0 0;font-size:var(--text-base);line-height:var(--leading-body)}
.kh-dialogue .hint{margin:var(--space-1) 0 0;font-size:var(--text-base);color:var(--text-muted)}
.kh-dialogue .hint b{color:var(--text)}
.kh-dialogue .ctl{margin-top:auto;display:flex;gap:var(--space-4);font-size:var(--text-sm);color:var(--text-muted);align-items:center}
.kh-dialogue .ctl span{display:inline-flex;align-items:center;gap:var(--space-2);white-space:nowrap}
.kh-dialogue .ctl b{color:var(--text)}

/* ---- Sheet sections ------------------------------------------------------------ */
.sheet{width:1280px;margin:0 auto;padding:var(--space-6) 0 var(--space-5)}
.sheet h2{font-size:var(--text-2xl);margin-bottom:var(--space-2)}
.sheet .lede{color:var(--text-muted);margin:0 0 var(--space-5);max-width:900px}
.bar{width:1366px;margin:0 auto;padding:var(--space-3) 43px;display:flex;gap:var(--space-5);align-items:center;font-size:var(--text-sm);color:var(--text-muted);background:var(--panel-sunken)}
.bar a{font-weight:var(--weight-bold)}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--space-4)}
.card{background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-4);display:flex;flex-direction:column;gap:var(--space-3)}
.card h3{font-size:var(--text-lg)}
.card p{margin:0;font-size:var(--text-sm);color:var(--text-muted)}
.card p b{color:var(--text)}
.card .pair{display:flex;gap:var(--space-4);align-items:center;background:var(--panel-sunken);border-radius:var(--radius-md);padding:var(--space-3)}
.card .pair .kh-marker{position:static;width:80px;height:80px}
.card .pair .grey{filter:grayscale(1)}
.keystates{display:flex;flex-wrap:wrap;gap:var(--space-6);align-items:flex-start;background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-5)}
.keystates .kh-keyunit p{margin:var(--space-2) 0 0;font-size:var(--text-sm);color:var(--text-muted);text-align:center;max-width:170px}

/* ---- Full-screen overlays: journal and Layout help ------------------------------ */
.scrim{position:absolute;inset:0;background:var(--scrim);z-index:var(--z-overlay)}
.overlay{position:absolute;left:24px;right:24px;top:24px;bottom:24px;z-index:calc(var(--z-overlay) + 1);padding:var(--space-4) var(--space-5);display:flex;flex-direction:column;gap:var(--space-3)}
.overlay .top{display:flex;align-items:center;gap:var(--space-5)}
.overlay .top h2{font-size:var(--text-2xl);margin:0;white-space:nowrap}
.overlay .top .tab,.overlay .top .close{white-space:nowrap}
.lh-note{font-size:var(--text-sm);color:var(--text-muted);line-height:1.3;align-self:center;flex:none}
.overlay .top .grow{flex:1}
.overlay .close{display:inline-flex;align-items:center;gap:var(--space-2);font-size:var(--text-sm);color:var(--text-muted)}
.tabs{display:flex;gap:var(--space-2)}
.tab{padding:var(--space-2) var(--space-4);border-radius:var(--radius-pill);border:2px solid var(--border);font:var(--weight-bold) var(--text-sm)/1.2 var(--font-mono);color:var(--text)}
.tab[aria-selected="true"]{background:var(--paper);color:var(--ink);border-color:var(--paper)}

/* Journal */
.kh-journal{display:grid;grid-template-columns:540px 1fr;gap:var(--space-5);flex:1;min-height:0}
.kh-journal .list{display:flex;flex-direction:column;gap:var(--space-3);overflow:hidden}
.kh-journal .group h3{display:flex;align-items:center;gap:var(--space-2);font:var(--weight-bold) var(--text-lg)/1.2 var(--font-display);margin-bottom:var(--space-2)}
.kh-journal .group.req h3{color:var(--accent-conversation)}
.kh-journal .group.spd h3{color:var(--accent-terminal)}
.qrow{display:grid;grid-template-columns:1fr auto;gap:var(--space-1) var(--space-3);background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3);margin-bottom:var(--space-2)}
.qrow.sel{border-color:var(--focus);outline:2px solid var(--focus);outline-offset:2px}
.qrow .t{font-weight:var(--weight-bold)}
.qrow .d{grid-column:1/-1;font-size:var(--text-sm);color:var(--text-muted)}
.state{display:inline-flex;align-items:center;gap:var(--space-1);font:var(--weight-bold) var(--text-sm)/1 var(--font-body)}
.state.active{color:var(--accent-terminal)}
.state.locked{color:var(--text-muted)}
.state.done{color:var(--accent-discovery)}
.kh-journal .detail{background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-5);display:flex;flex-direction:column;gap:var(--space-3)}
.kh-journal .detail h3{font-size:var(--text-xl)}
.steps{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:var(--space-2)}
.steps li{display:flex;align-items:center;gap:var(--space-3)}
.steps .dot{width:28px;height:28px;border-radius:var(--radius-pill);border:2px solid var(--border);display:inline-flex;align-items:center;justify-content:center;flex:none;color:var(--accent-discovery)}
.steps li.next .dot{border-color:var(--accent-terminal);color:var(--accent-terminal)}
.steps li.todo{color:var(--text-muted)}
.keysline{display:flex;align-items:center;gap:var(--space-3);flex-wrap:wrap;background:var(--panel-sunken);border-radius:var(--radius-md);padding:var(--space-3)}
.keysline .kh-key{height:40px;min-width:40px;font-size:var(--text-base);box-shadow:0 3px 0 var(--key-edge)}
.keysline .kh-key.held{box-shadow:0 1px 0 var(--key-held-edge)}

/* Layout help */
.kh-lh{display:flex;flex-direction:column;gap:var(--space-3);flex:1;min-height:0}
.lh-rows{display:flex;flex-direction:column;gap:var(--key-gap);align-items:center}
.lh-row{display:flex;gap:var(--key-gap)}
.kh-lk{height:var(--key-unit);border-radius:var(--radius-sm);background:var(--key-dim-face);color:var(--key-dim-text);box-shadow:0 3px 0 var(--key-dim-edge);display:flex;flex-direction:column;align-items:center;justify-content:center;font:var(--weight-regular) var(--text-sm)/1.15 var(--font-mono);position:relative;margin-bottom:3px;flex:none}
.kh-lk .l{font-size:var(--text-base)}
.kh-lk .s{font:var(--weight-bold) var(--text-sm)/1.1 var(--font-body);white-space:nowrap}
.kh-lk .s.arrow{font-size:var(--text-lg);line-height:1}
.kh-lk.map{background:var(--key-face);color:var(--key-text);box-shadow:0 4px 0 var(--key-edge);font-weight:var(--weight-bold)}
.kh-lk.map::before{content:"";position:absolute;left:8px;right:8px;top:0;height:4px;background:var(--key-held-edge);border-radius:0 0 3px 3px}
.kh-lk.layerkey{background:var(--key-held-face);color:var(--key-held-text);box-shadow:0 1px 0 var(--key-held-edge);top:3px;font-weight:var(--weight-bold)}
.kh-lk.silent{background:var(--key-silent-face);color:var(--key-silent-text);border:2px dashed var(--border);box-shadow:none}
.lh-detail{display:grid;grid-template-columns:auto 1fr 1fr;gap:var(--space-4) var(--space-5);align-items:start;background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-3) var(--space-5)}
.lh-detail .big{display:flex;flex-direction:column;align-items:center;gap:var(--space-2)}
.lh-detail .big .kh-key{min-width:72px;height:72px;font-size:var(--text-2xl)}
.lh-detail dl{margin:0;display:grid;grid-template-columns:1fr;gap:var(--space-1)}
.lh-detail dt{font:var(--weight-bold) var(--text-sm)/1.2 var(--font-body);letter-spacing:var(--tracking-label);text-transform:uppercase;color:var(--text-muted)}
.lh-detail dd{margin:0 0 var(--space-2);font-size:var(--text-base)}
.lh-legend{display:flex;gap:var(--space-5);align-items:center;font-size:var(--text-sm);color:var(--text-muted);flex-wrap:wrap}
.lh-legend span{display:inline-flex;align-items:center;gap:var(--space-2)}
.lh-legend .kh-lk{width:44px;height:36px;margin:0;font-size:var(--text-sm)}
"""


# --------------------------------------------------------------------------- stage
def keycap(label, cls="", tag=None, tagcls=""):
    t = f'<span class="kh-tag {tagcls}">{tag}</span>' if tag else ""
    return f'<span class="kh-keyunit"><span class="kh-key {cls}">{label}</span>{t}</span>'


def stage():
    # Marker boxes (64 px) centred on the cells the approved scene used, at cell * 16 px * zoom 4.
    markers = "".join([
        mk("talk", style="left:480px;top:92px"),        # Ivo (8.0, 1.95)
        mk("terminal", style="left:646px;top:28px"),    # badge printer sign (10.6, 0.95)
        mk("route", style="left:1090px;top:252px"),     # Records door (17.55, 4.45)
        mk("glitch", style="left:198px;top:186px"),     # paper-fold glitch (3.6, 3.4)
    ])
    hud = f"""
<div class="kh-hud obj" role="status">
  <span class="title">Visit the four desks</span>
  <span class="count">2 / 4</span>
  <span class="sep"></span>
  <span class="seals">{ico("seal", 24)} Seals 0</span>
</div>
<div class="kh-hud shortcuts">
  <span class="chip">Journal <span class="kh-key sm">Tab</span></span>
  <span class="chip">Layout help <span class="kh-key sm">?</span></span>
</div>"""
    prompt = f"""
<div class="kh-prompt" style="left:812px;top:128px;width:340px">
  <div class="action">{ico("play", 20)} Use the badge printer</div>
  <div class="keys"><span class="kh-key sm">Return</span><span class="gesture">tap-hold Caps + N</span></div>
</div>"""
    inset = f"""
<section class="kh-panel kh-inset" aria-label="Keyboard teaching inset: Move east">
  <div class="head"><h3>Move east</h3><span class="layer">nav layer · tap-hold Caps · 200 ms</span></div>
  <div class="kh-cell">
    <div class="kh-label"><span class="kh-order">1</span> Key position <span style="font-weight:400;text-transform:none;letter-spacing:0">home row</span></div>
    <div class="kh-mini" aria-label="Home row: Caps A S D F G H J K L ; apostrophe">
      <span class="kh-key cap held">Caps</span><span class="kh-key dim">A</span><span class="kh-key dim">S</span><span class="kh-key dim">D</span><span class="kh-key dim">F</span><span class="kh-key dim">G</span><span class="kh-key dim">H</span><span class="kh-key dim">J</span><span class="kh-key dim">K</span><span class="kh-key">L</span><span class="kh-key dim">;</span><span class="kh-key dim">'</span>
    </div>
  </div>
  <div class="row">
    <div class="kh-cell">
      <div class="kh-label"><span class="kh-order">2</span> Hold order</div>
      <div class="kh-hold">
        {keycap("Caps", "wide held", "Hold", "hold")}
        <span class="plus">+</span>
        {keycap("L", "", "Tap", "tap")}
      </div>
    </div>
    <div class="kh-cell">
      <div class="kh-label"><span class="kh-order">3</span> Output</div>
      <div class="kh-out"><span class="kh-key">{ico("arrow-right", 28)}</span><span>Right arrow</span></div>
    </div>
    <div class="kh-cell">
      <div class="kh-label"><span class="kh-order">4</span> Effect</div>
      <div class="kh-effect">{ico("step-east", 28)}<span>Step east</span></div>
    </div>
  </div>
</section>"""
    dialogue = """
<section class="kh-panel kh-dialogue" aria-label="Dialogue with Ivo">
  <div class="kh-portrait" role="img" aria-label="Portrait slot, 48 by 48 pixels shown at 4 times"><span>48 x 48 portrait<br>at x4 = 192 px</span></div>
  <div class="body">
    <div class="who">Ivo <span class="role">Reception lead</span></div>
    <p class="say">To walk to the east exit, you need to press <b>Right arrow</b>.</p>
    <p class="hint">Hint: Right arrow is <b>tap-hold Caps</b> + <b>L</b>.</p>
    <div class="ctl">
      <span><b>Continue</b> <span class="kh-key sm">Return</span> tap-hold Caps + N</span>
      <span><b>Skip</b> <span class="kh-key sm">Esc</span></span>
    </div>
  </div>
</section>"""
    return f"""
<div class="viewport" id="viewport">
  <div class="stage" id="stage">
    <img class="world" src="world-native.png" width="320" height="180" alt="Orientation lobby: avatar east of the garden, Ivo at the printer, the Records door on the east wall">
    {markers}{hud}{prompt}{inset}{dialogue}
  </div>
</div>"""


# --------------------------------------------------------------------------- sections
def markers_section():
    items = [
        ("talk", "Conversation", "Speech bubble", "A coworker has something to say. Coral.", "Over a person's head"),
        ("terminal", "Terminal", "Monitor", "A device you can use. Teal.", "On or above the device"),
        ("route", "Route", "Diamond with a doorway", "A path that is open or newly open. Gold.", "At the door or shortcut"),
        ("glitch", "Glitch", "Folded page", "A repair duel. Violet, glitches only.", "Above the glitch"),
    ]
    cards = ""
    for name, title, shape, meaning, where in items:
        cards += f"""
<div class="card">
  <h3>{title}</h3>
  <div class="pair">{mk(name)}{mk(name, "grey")}</div>
  <p><b>Shape: {shape}.</b> {meaning}</p>
  <p>{where}. Left: colour. Right: forced greyscale.</p>
</div>"""
    return f"""
<div class="sheet">
  <h2>Markers</h2>
  <p class="lede">Shape carries the meaning; colour is a second signal. Each marker is an inline SVG symbol with a paper halo and an ink line so it reads on light and dark floors. Open <a href="#grey">#grey</a> to see the whole page in greyscale.</p>
  <div class="cards">{cards}</div>
</div>"""


def keystates_section():
    return f"""
<div class="sheet">
  <h2>Keycap states</h2>
  <p class="lede">Keycaps are DOM components. A held key is teal, sits lower and carries the word "Hold", so no state depends on colour alone.</p>
  <div class="keystates">
    {keycap("L", "", "Tap", "tap")}
    {keycap("Caps", "wide held", "Hold", "hold")}
    {keycap("H", "dim")}
    {keycap("XX", "silent")}
    {keycap("N", "focus")}
    {keycap("Return", "wide")}
    <span class="kh-keyunit"><span class="kh-key">{ico("arrow-right", 28)}</span></span>
    <div class="kh-keyunit"><span class="kh-key sm">Tab</span><p>Small keycap, used in prompts and the HUD</p></div>
  </div>
  <p class="lede" style="margin:var(--space-3) 0 0">From left: tap, held, neighbour (dim), silent on the practice layer (dashed, XX), keyboard focus (ring), wide, arrow output, small.</p>
</div>"""


def screen(inner):
    return f"""
<div class="stage screen">
  <img class="world" src="world-native.png" width="320" height="180" alt="">
  <div class="scrim"></div>
  {inner}
</div>"""


def row(title, desc, state, sel=False):
    cls, icon, label = state
    return (f'<div class="qrow{" sel" if sel else ""}"><span class="t">{title}</span>'
            f'<span class="state {cls}">{ico(icon, 20)} {label}</span><span class="d">{desc}</span></div>')


def journal_section():
    active = ("active", "play", "Active, 2 of 4")
    locked = ("locked", "lock", "Locked")
    inner = f"""
<div class="kh-panel overlay" role="dialog" aria-label="Quest journal">
  <div class="top"><h2>Quest journal</h2><span class="kh-label">Orientation</span><span class="grow"></span>
    <span class="seals" style="display:inline-flex;align-items:center;gap:var(--space-2);color:var(--accent-discovery);font-weight:var(--weight-bold)">{ico("seal", 24)} Clearance seals 0 / 5</span>
    <span class="close"><span class="kh-key sm">Esc</span> tap Caps to close</span></div>
  <div class="kh-journal">
    <div class="list">
      <div class="group main"><h3>{ico("seal", 24)} Main work</h3>
        {row("01 The Lobby", "Ivo wants four desks visited before the first ticket.", active, True)}
        {row("02 Badge Printer", "Opens after The Lobby.", locked)}
      </div>
      <div class="group req"><h3>{ico("bubble", 24)} Coworker requests</h3>
        {row("Plant Tags", "Ivo asks for five typed labels on duplicated planters.", locked)}
      </div>
      <div class="group spd"><h3>{ico("stopwatch", 24)} Optional speed, Mira</h3>
        {row("Morning Mail", "Needs: base taps and ordinary text. Opens after 02.", locked)}
      </div>
    </div>
    <div class="detail">
      <span class="kh-label">Main work, Orientation</span>
      <h3>01 The Lobby: visit the four desks</h3>
      <ul class="steps">
        <li><span class="dot">{ico("check", 18)}</span> West desk</li>
        <li><span class="dot">{ico("check", 18)}</span> Garden loop</li>
        <li class="next"><span class="dot">{ico("play", 14)}</span> East exit: Records door</li>
        <li class="todo"><span class="dot"></span> Return to Ivo</li>
      </ul>
      <span class="kh-label">Keys for this step</span>
      <div class="keysline"><span class="kh-key held">Caps</span>+<span class="kh-key">L</span><span>Right arrow</span><span style="color:var(--text-muted)">tap-hold Caps + L</span></div>
      <span class="kh-label">Layout reference</span>
      <div class="keysline"><span class="kh-key sm">?</span><span>Open Layout help from here or anywhere</span></div>
    </div>
  </div>
</div>"""
    return f"""
<div class="sheet">
  <h2>Quest journal</h2>
  <p class="lede">Opened on demand over a dimmed world. Main work, coworker requests and Mira's optional speed routes have separate headings and icons: a seal, a speech bubble and a stopwatch. State is text plus an icon (play, lock, check).</p>
  {screen(inner)}
</div>"""


# Layout help --------------------------------------------------------------------
ROWS = [
    [("`", 1)] + [(c, 1) for c in "1234567890-="] + [("Backspace", 2)],
    [("Tab", 1.5)] + [(c, 1) for c in "qwertyuiop[]"] + [("\\", 1.5)],
    [("Caps", 1.75)] + [(c, 1) for c in "asdfghjkl;'"] + [("Return", 2.25)],
    [("Shift", 2.25)] + [(c, 1) for c in "zxcvbnm,./"] + [("Shift", 2.75)],
    [(None, 3.75), ("Space", 6.25)],
]
# Keys that change on the nav layer (from kanata.kbd): key -> (sublabel, is_arrow)
NAV = {
    "0": ("Line ←", 0), "4": ("Line →", 0),
    "w": ("Word →", 0), "u": ("Page ↑", 0), "t": ("Doc ↑", 0),
    "d": ("Page ↓", 0), "g": ("Doc ↓", 0),
    "h": ("←", 1), "j": ("↓", 1), "k": ("↑", 1), "l": ("→", 1),
    ";": ("ö", 0), "[": ("Esc", 0),
    "b": ("Word ←", 0), "m": ("Bksp", 0), "x": ("Ctrl+D", 0), ",": ("Delete", 0),
    "n": ("Return", 0), "Space": ("Bksp", 0),
}


def lk(label, u, sub=None, arrow=False, cls=""):
    px = round(u * 64 + (u - 1) * 6)
    shown = label.upper() if len(label) == 1 and label.isalpha() else label
    s = f'<span class="s{" arrow" if arrow else ""}">{sub}</span>' if sub else ""
    return f'<div class="kh-lk {cls}" style="width:{px}px"><span class="l">{shown}</span>{s}</div>'


def layout_rows():
    out = ""
    for r in ROWS:
        out += '<div class="lh-row">'
        for key, u in r:
            if key is None:
                out += f'<div class="lh-note" style="width:{round(u * 64 + (u - 1) * 6) - 12}px;margin-right:12px;text-align:right">Click-hold Caps or Space to preview a layer</div>'
            elif key == "Caps":
                out += lk("Caps", u, "hold", cls="layerkey")
            elif key in NAV:
                sub, ar = NAV[key]
                out += lk(key, u, sub, bool(ar), "map" + (" focus" if key == "l" else ""))
            else:
                out += lk(key, u)
        if r[0][0] is None:
            out += '<div class="lh-note" style="width:340px;margin-left:12px">Switch tabs: Left / Right (tap-hold Caps + H / L), or Tab / Shift + Tab</div>'
        out += "</div>"
    return out


def layout_section():
    tabs = "".join(
        f'<span class="tab" role="tab" aria-selected="{"true" if t == "nav" else "false"}">{t}</span>'
        for t in ("base", "nav", "numbers-symbols", "practice"))
    inner = f"""
<div class="kh-panel overlay" role="dialog" aria-label="Layout help">
  <div class="top"><h2>Layout help</h2>
    <div class="tabs" role="tablist">{tabs}</div><span class="grow"></span>
    <span class="close"><span class="kh-key sm">Esc</span> tap Caps to close</span></div>
  <div class="kh-lh">
    <div class="lh-rows">{layout_rows()}</div>
    <div class="lh-detail">
      <div class="big"><span class="kh-key">L</span></div>
      <dl>
        <dt>Tap</dt><dd>types <span class="mono">l</span></dd>
        <dt>Tap-hold, 200 ms</dt><dd>Right Option (<span class="mono">ralt</span>)</dd>
      </dl>
      <dl>
        <dt>On nav</dt><dd>Right arrow, from <b>tap-hold Caps</b> + <b>L</b>.</dd>
        <dt>On practice</dt><dd>Normal: the home-row hold still works.</dd>
      </dl>
    </div>
    <div class="lh-legend">
      <span><span class="kh-lk map" style="width:44px"><span class="l">W</span></span> changes on this tab, new action underneath</span>
      <span><span class="kh-lk" style="width:44px"><span class="l">A</span></span> unchanged</span>
      <span><span class="kh-lk silent" style="width:44px"><span class="l">XX</span></span> silent on practice</span>
    </div>
  </div>
</div>"""
    return f"""
<div class="sheet">
  <h2>Layout help</h2>
  <p class="lede">Rendered from the layout manifest; the keys below follow <span class="mono">kanata.kbd</span> for the <span class="mono">nav</span> tab (Caps is the layer key, drawn held). The focus ring is on L, whose detail card follows the hint grammar.</p>
  {screen(inner)}
</div>"""


def page():
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kanata Hero UI kit reference</title>
<!-- Generated by build_reference.py. Do not hand-edit. Uses tokens.css and world-native.png only. -->
<link rel="stylesheet" href="tokens.css">
<style>{CSS}</style>
</head>
<body>
<span id="grey"></span>
{SPRITE}
<div class="page">
{stage()}
<div class="bar"><span>Reference stage: 1280 x 720 at world zoom x4, letterboxed in 1366 x 768.</span><a href="#grey">Greyscale</a><a href="#">Colour</a></div>
{markers_section()}
{keystates_section()}
{journal_section()}
{layout_section()}
</div>
</body>
</html>
"""


if __name__ == "__main__":
    with open(os.path.join(HERE, "reference.html"), "w", encoding="utf-8") as f:
        f.write(page())
    print("reference.html written")
