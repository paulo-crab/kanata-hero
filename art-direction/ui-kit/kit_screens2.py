"""Second batch of reference screens (P1): artifact close-up, elevator map, seal award and toast,
Mira's route results and the five seal icons, settings and accessibility.

Imported by build_reference.py after kit_screens.py. Static HTML/CSS/SVG, no script.
"""
import math

from kit_screens import ico, mk, kc, mico, shot, chip_practice

# --------------------------------------------------------------------------- seals and patches
SEALS = [
    ("orientation", "Orientation", "06", "The Other Keyboard"),
    ("records", "Records", "11", "Marked for Review"),
    ("systems", "Systems", "16", "Crossed Wires"),
    ("night", "Night Shift", "19", "The Ledger"),
    ("executive", "Executive", "20", "Exit Interview"),
]
PATCHES = [
    # id, name, route that earns it, glyph keeps the Mira patch colour
    (1, "First Delivery", "Morning Mail"),
    (2, "Clear Address", "Courier Loop"),
    (3, "Archive Loop", "Lost Folios"),
    (4, "Signed and Sent", "Payroll Run"),
    (5, "Signal Keeper", "Glyph Dispatch"),
    (6, "Night Courier", "Lights-Out Delivery"),
]

SPRITE2 = """
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <path id="p-seal" d="M20 4 H44 L60 20 V44 L44 60 H20 L4 44 V20 Z"/>
  </defs>
  <!-- Five clearance seals: gold octagon, ink line, and a glyph that differs by shape -->
  <symbol id="s-orientation" viewBox="0 0 64 64">
    <use href="#p-seal" style="fill:var(--gold);stroke:#182B38;stroke-width:3.5;stroke-linejoin:round"/>
    <path d="M32 47 V30" stroke="#182B38" stroke-width="3.6" fill="none" stroke-linecap="square"/>
    <path d="M32 39 C23 39 18 33 18 24 C27 24 32 30 32 39 Z" fill="#182B38"/>
    <path d="M32 34 C32 26 37 20 46 20 C46 29 41 34 32 34 Z" fill="#182B38"/>
  </symbol>
  <symbol id="s-records" viewBox="0 0 64 64">
    <use href="#p-seal" style="fill:var(--gold);stroke:#182B38;stroke-width:3.5;stroke-linejoin:round"/>
    <circle cx="32" cy="32" r="14" fill="none" stroke="#182B38" stroke-width="4.6"/>
    <circle cx="32" cy="32" r="4.6" fill="#182B38"/>
    <path d="M32 10 V15 M32 49 V54 M10 32 H15 M49 32 H54" stroke="#182B38" stroke-width="3.2"/>
  </symbol>
  <symbol id="s-systems" viewBox="0 0 64 64">
    <use href="#p-seal" style="fill:var(--gold);stroke:#182B38;stroke-width:3.5;stroke-linejoin:round"/>
    <path d="M32 32 V16 M32 32 L18 41 M32 32 L46 41" stroke="#182B38" stroke-width="3.6" fill="none"/>
    <circle cx="32" cy="32" r="6" fill="#182B38"/>
    <circle cx="32" cy="15" r="5" fill="#182B38"/><circle cx="17" cy="42" r="5" fill="#182B38"/><circle cx="47" cy="42" r="5" fill="#182B38"/>
  </symbol>
  <symbol id="s-night" viewBox="0 0 64 64">
    <use href="#p-seal" style="fill:var(--gold);stroke:#182B38;stroke-width:3.5;stroke-linejoin:round"/>
    <path d="M39 13 C27 15 20 24 20 34 C20 45 28 52 39 51 C32 47 29 41 29 34 C29 26 33 18 39 13 Z" fill="#182B38"/>
    <path d="M45 19 L46.6 23 L50.6 24.4 L46.6 25.8 L45 30 L43.4 25.8 L39.4 24.4 L43.4 23 Z" fill="#182B38"/>
  </symbol>
  <symbol id="s-executive" viewBox="0 0 64 64">
    <use href="#p-seal" style="fill:var(--gold);stroke:#182B38;stroke-width:3.5;stroke-linejoin:round"/>
    <circle cx="32" cy="26" r="11" fill="#182B38"/><circle cx="23" cy="31" r="7" fill="#182B38"/><circle cx="41" cy="31" r="7" fill="#182B38"/>
    <path d="M30 36 H34 V49 H30 Z" fill="#182B38"/>
    <path d="M30 49 L22 54 M34 49 L42 54 M32 49 V55" stroke="#182B38" stroke-width="3" fill="none" stroke-linecap="square"/>
  </symbol>
  <!-- Seal slot not earned yet: an empty octagon -->
  <symbol id="s-empty" viewBox="0 0 64 64">
    <use href="#p-seal" style="fill:none;stroke:var(--border);stroke-width:3.5;stroke-dasharray:7 5;stroke-linejoin:round"/>
  </symbol>

  <!-- Mira's six patches, 48 x 40: a stitched rounded patch in her colours -->
  <symbol id="pt-1" viewBox="0 0 48 40">
    <rect x="2.5" y="2.5" width="43" height="35" rx="8" style="fill:var(--patch-peach);stroke:#F4F2EC;stroke-width:2.5"/>
    <rect x="7" y="7" width="34" height="26" rx="4" fill="none" stroke="#182B38" stroke-width="1.6" stroke-dasharray="3 3"/>
    <rect x="14" y="14" width="20" height="13" rx="1.5" fill="#F4F2EC" stroke="#182B38" stroke-width="2"/>
    <path d="M14.6 14.8 L24 22.4 L33.4 14.8" fill="none" stroke="#182B38" stroke-width="2.2"/>
  </symbol>
  <symbol id="pt-2" viewBox="0 0 48 40">
    <rect x="2.5" y="2.5" width="43" height="35" rx="8" style="fill:var(--patch-lime);stroke:#F4F2EC;stroke-width:2.5"/>
    <rect x="7" y="7" width="34" height="26" rx="4" fill="none" stroke="#182B38" stroke-width="1.6" stroke-dasharray="3 3"/>
    <path d="M24 10.5 C19 10.5 16 14.5 16 18.5 C16 24.5 24 32 24 32 C24 32 32 24.5 32 18.5 C32 14.5 29 10.5 24 10.5 Z" fill="#182B38"/>
    <circle cx="24" cy="18.5" r="3.2" style="fill:var(--patch-lime)"/>
  </symbol>
  <symbol id="pt-3" viewBox="0 0 48 40">
    <rect x="2.5" y="2.5" width="43" height="35" rx="8" style="fill:var(--patch-brass);stroke:#F4F2EC;stroke-width:2.5"/>
    <rect x="7" y="7" width="34" height="26" rx="4" fill="none" stroke="#182B38" stroke-width="1.6" stroke-dasharray="3 3"/>
    <circle cx="24" cy="20" r="8" fill="none" stroke="#182B38" stroke-width="3.6"/>
    <rect x="29.5" y="12" width="3.4" height="3.4" style="fill:var(--patch-glint)"/>
  </symbol>
  <symbol id="pt-4" viewBox="0 0 48 40">
    <rect x="2.5" y="2.5" width="43" height="35" rx="8" style="fill:var(--patch-navy);stroke:#F4F2EC;stroke-width:2.5"/>
    <rect x="7" y="7" width="34" height="26" rx="4" fill="none" stroke="#F4F2EC" stroke-width="1.6" stroke-dasharray="3 3"/>
    <path d="M15 21 L22 28 L34 13" fill="none" stroke="#F4F2EC" stroke-width="4" stroke-linecap="square"/>
  </symbol>
  <symbol id="pt-5" viewBox="0 0 48 40">
    <rect x="2.5" y="2.5" width="43" height="35" rx="8" style="fill:var(--patch-pale);stroke:#F4F2EC;stroke-width:2.5"/>
    <rect x="7" y="7" width="34" height="26" rx="4" fill="none" stroke="#182B38" stroke-width="1.6" stroke-dasharray="3 3"/>
    <rect x="14" y="21" width="5.5" height="9" fill="#182B38"/><rect x="21.3" y="16" width="5.5" height="14" fill="#182B38"/><rect x="28.6" y="11" width="5.5" height="19" fill="#182B38"/>
  </symbol>
  <symbol id="pt-6" viewBox="0 0 48 40">
    <rect x="2.5" y="2.5" width="43" height="35" rx="8" style="fill:var(--patch-navy);stroke:#F4F2EC;stroke-width:2.5"/>
    <rect x="7" y="7" width="34" height="26" rx="4" fill="none" stroke="#F4F2EC" stroke-width="1.6" stroke-dasharray="3 3"/>
    <path d="M27 11 C20 12 16 17 16 22 C16 28 21 31 27 30 C23 28 21.5 25 21.5 22 C21.5 17 24 14 27 11 Z" style="fill:var(--patch-glint)"/>
    <rect x="30" y="14" width="4" height="4" style="fill:var(--patch-glint)"/>
  </symbol>

  <!-- Interface icons (24 x 24, currentColor) -->
  <symbol id="i-medal" viewBox="0 0 24 24">
    <path d="M7 14 L4.5 23 L12 19.5 L19.5 23 L17 14 Z" fill="currentColor"/>
    <circle cx="12" cy="9" r="7" fill="currentColor"/>
    <path d="M8.6 9 L11 11.4 L15.6 6.6" fill="none" stroke="#182B38" stroke-width="2.4" stroke-linecap="square"/>
  </symbol>
  <symbol id="i-doc" viewBox="0 0 24 24">
    <path d="M5 2 H15 L20 7 V21 A1 1 0 0 1 19 22 H5 A1 1 0 0 1 4 21 V3 A1 1 0 0 1 5 2 Z" fill="currentColor"/>
    <path d="M15 2 V7 H20" fill="#182B38"/>
    <path d="M8 12 H16 M8 16 H16" stroke="#182B38" stroke-width="2"/>
  </symbol>
  <symbol id="i-receipt" viewBox="0 0 24 24">
    <path d="M5 2 H19 V22 L16.5 20 L14 22 L11.5 20 L9 22 L6.5 20 L5 22 Z" fill="currentColor"/>
    <path d="M8.5 7 H15.5 M8.5 11 H15.5 M8.5 15 H13" stroke="#182B38" stroke-width="2"/>
  </symbol>
  <symbol id="i-lift" viewBox="0 0 24 24">
    <rect x="3" y="2" width="18" height="20" rx="2" fill="currentColor"/>
    <path d="M8 10 L12 6 L16 10 Z M8 14 L12 18 L16 14 Z" fill="#182B38"/>
  </symbol>
  <symbol id="i-arrow-up" viewBox="0 0 24 24"><path d="M12 21 V4 M5 11 L12 4 L19 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
  <symbol id="i-arrow-down" viewBox="0 0 24 24"><path d="M12 3 V20 M5 13 L12 20 L19 13" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="square"/></symbol>
  <symbol id="i-here" viewBox="0 0 24 24"><path d="M2 3 L22 12 L2 21 Z" fill="currentColor"/></symbol>
  <symbol id="i-text" viewBox="0 0 24 24"><path d="M2 20 L8 4 H10 L16 20 M4.4 14 H13.6 M16 20 L19.5 11 H20.5 L24 20" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="miter"/></symbol>
  <symbol id="i-contrast" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2.6"/><path d="M12 3 A9 9 0 0 1 12 21 Z" fill="currentColor"/></symbol>
  <symbol id="i-motion" viewBox="0 0 24 24"><path d="M3 8 H14 M3 12 H18 M3 16 H14 M17 5 L22 12 L17 19" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="square"/></symbol>
  <symbol id="i-sound" viewBox="0 0 24 24"><path d="M3 9 H7 L13 4 V20 L7 15 H3 Z" fill="currentColor"/><path d="M16 8.5 C18 10.5 18 13.5 16 15.5 M18.5 5.5 C22 9 22 15 18.5 18.5" fill="none" stroke="currentColor" stroke-width="2.2"/></symbol>
  <symbol id="i-sound-off" viewBox="0 0 24 24"><path d="M3 9 H7 L13 4 V20 L7 15 H3 Z" fill="currentColor"/><path d="M16 9 L22 15 M22 9 L16 15" stroke="currentColor" stroke-width="2.6" stroke-linecap="square"/></symbol>
  <symbol id="i-reset" viewBox="0 0 24 24"><path d="M20 12 A8 8 0 1 1 15.5 4.8 M15.5 1.5 V5.5 H19.5" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="square"/></symbol>
</svg>
"""


def seal(name, size=64, cls=""):
    return (f'<svg class="kh-ico seal {cls}" width="{size}" height="{size}" viewBox="0 0 64 64" aria-hidden="true">'
            f'<use href="#s-{name}"/></svg>')


def patch(n, size=60, cls=""):
    return (f'<svg class="kh-ico patch {cls}" width="{size}" height="{round(size * 40 / 48)}" viewBox="0 0 48 40" aria-hidden="true">'
            f'<use href="#pt-{n}"/></svg>')


def seal_strip(earned, size=40, names=False):
    out = '<div class="seal-strip">'
    for i, (sid, name, lvl, lvname) in enumerate(SEALS):
        got = i < earned
        icon = seal(sid, size) if got else seal("empty", size)
        label = f'<span>{name}</span>' if names else ""
        state = "earned" if got else "not yet"
        out += f'<span class="seal-slot {"got" if got else ""}" title="{name} seal, {state}">{icon}{label}</span>'
    return out + "</div>"


# --------------------------------------------------------------------------- CSS
CSS = """
/* ---- Seals, patches, toasts -------------------------------------------------------------------- */
.seal-strip{display:flex;gap:var(--space-3);align-items:flex-start}
.seal-slot{display:inline-flex;flex-direction:column;align-items:center;gap:var(--space-1);font:var(--weight-bold) var(--text-sm)/1.2 var(--font-body);color:var(--text-muted)}
.seal-slot.got{color:var(--accent-discovery)}
.kh-toasts{position:absolute;z-index:var(--z-toast);left:50%;top:80px;transform:translateX(-50%);width:460px;display:flex;flex-direction:column;gap:var(--space-2)}
.kh-toast{display:grid;grid-template-columns:auto 1fr;gap:var(--space-1) var(--space-3);align-items:center;background:var(--panel-bg);border:2px solid var(--border);border-left:8px solid var(--gold);border-radius:var(--radius-md);padding:var(--space-2) var(--space-4) var(--space-2) var(--space-3)}
.kh-toast .ic{grid-row:1/3;display:inline-flex;align-items:center;justify-content:center;width:48px}
.kh-toast .t{font:var(--weight-bold) var(--text-base)/1.3 var(--font-body);color:var(--text)}
.kh-toast .t em{font-style:normal;color:var(--accent-discovery)}
.kh-toast .d{font-size:var(--text-sm);color:var(--text-muted);line-height:1.3}
.kh-toast.patchy{border-left-color:var(--patch-peach)}

/* ---- Award moment ------------------------------------------------------------------------------ */
.kh-award{position:absolute;z-index:calc(var(--z-overlay) + 1);left:300px;top:44px;width:680px;padding:var(--space-5) var(--space-6);border:3px solid var(--gold);display:flex;flex-direction:column;align-items:center;gap:var(--space-3);text-align:center}
.kh-award .burst{position:relative;width:180px;height:180px;display:flex;align-items:center;justify-content:center}
.kh-award .burst svg.rays{position:absolute;inset:0}
.kh-award h2{font-size:var(--text-2xl)}
.kh-award .kicker{color:var(--accent-discovery);font:var(--weight-bold) var(--text-sm)/1 var(--font-body);letter-spacing:var(--tracking-label);text-transform:uppercase}
.kh-award .what{margin:0;font-size:var(--text-base);color:var(--text-muted)}
.kh-award .changes{align-self:stretch;text-align:left;background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-3) var(--space-4);display:flex;flex-direction:column;gap:var(--space-2);font-size:var(--text-base)}
.kh-award .changes div{display:flex;align-items:center;gap:var(--space-3)}
.kh-award .changes .kh-ico{color:var(--accent-discovery)}
.kh-award .foot{display:flex;align-items:center;gap:var(--space-5);justify-content:space-between;align-self:stretch;font-size:var(--text-sm);color:var(--text-muted)}

/* ---- Artifact close-up ------------------------------------------------------------------------- */
.kh-artifact{position:absolute;z-index:calc(var(--z-overlay) + 1);left:300px;top:30px;width:680px;padding:var(--space-4) var(--space-5);display:flex;flex-direction:column;gap:var(--space-3)}
.kh-artifact .head{display:grid;grid-template-columns:auto 1fr auto;gap:var(--space-4);align-items:center}
.kh-slot{width:72px;height:72px;border-radius:var(--radius-md);background:var(--panel-raised);border:2px solid var(--accent-discovery);display:flex;align-items:center;justify-content:center;color:var(--accent-discovery)}
.kh-artifact h2{font-size:var(--text-xl)}
.kh-artifact .meta{font-size:var(--text-sm);color:var(--text-muted)}
.kh-paper{background:var(--paper);color:var(--ink);border:2px solid var(--ink);border-radius:var(--radius-sm);padding:var(--space-4) var(--space-5);font:var(--weight-regular) var(--text-base)/1.6 var(--font-mono);box-shadow:0 4px 0 var(--key-edge);position:relative}
.kh-paper::after{content:"";position:absolute;right:-2px;top:-2px;width:28px;height:28px;background:var(--panel-bg);border-left:2px solid var(--ink);border-bottom:2px solid var(--ink)}
.kh-paper .title{font:var(--weight-bold) var(--text-base)/1.4 var(--font-mono);letter-spacing:var(--tracking-label);text-transform:uppercase;border-bottom:2px solid var(--ink);margin-bottom:var(--space-2);padding-bottom:var(--space-1)}
.kh-paper .row{display:grid;grid-template-columns:200px 1fr}
.kh-paper .stamp{display:inline-block;margin-top:var(--space-2);padding:0 var(--space-3);border:3px solid var(--ink);border-radius:var(--radius-sm);font-weight:var(--weight-bold);letter-spacing:var(--tracking-label)}
.kh-artifact .caption{margin:0;font-size:var(--text-base);line-height:var(--leading-body);max-width:100%}
.kh-artifact .foot{display:flex;align-items:center;justify-content:space-between;gap:var(--space-4);font-size:var(--text-sm);color:var(--text-muted)}
.kh-artifact .foot .kept{display:inline-flex;align-items:center;gap:var(--space-2);color:var(--accent-discovery);font-weight:var(--weight-bold)}

/* ---- Elevator map ------------------------------------------------------------------------------ */
.kh-lift{display:grid;grid-template-columns:560px 1fr;gap:var(--space-5);flex:1;min-height:0}
.kh-shaft{position:relative;display:flex;flex-direction:column;gap:var(--space-3);padding-left:var(--space-6)}
.kh-shaft::before{content:"";position:absolute;left:14px;top:16px;bottom:16px;width:6px;background:var(--border);border-radius:3px}
.kh-stop{position:relative;display:grid;grid-template-columns:48px 1fr auto;gap:0 var(--space-3);align-items:center;background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3);min-height:104px}
.kh-stop::before{content:"";position:absolute;left:calc(-1 * var(--space-6) + 6px);top:50%;width:22px;height:22px;margin-top:-11px;border-radius:var(--radius-pill);background:var(--panel-sunken);border:4px solid var(--border)}
.kh-stop.open::before{border-color:var(--accent-discovery);background:var(--accent-discovery)}
.kh-stop.here::before{border-radius:3px;border-color:var(--paper);background:var(--paper)}
.kh-stop.sel{border-color:var(--focus);outline:2px solid var(--focus);outline-offset:2px}
.kh-stop .fl{display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;border-radius:var(--radius-md);background:var(--paper);color:var(--ink);font:var(--weight-bold) var(--text-xl)/1 var(--font-mono)}
.kh-stop.locked .fl{background:var(--panel-sunken);color:var(--text-muted);border:2px dashed var(--border)}
.kh-stop .nm{font:var(--weight-bold) var(--text-lg)/1.2 var(--font-display)}
.kh-stop .sub{font-size:var(--text-sm);color:var(--text-muted);display:flex;align-items:center;gap:var(--space-2);margin-top:2px}
.kh-stop .sub b{color:var(--text)}
.kh-stop .st{display:inline-flex;align-items:center;gap:var(--space-2);font:var(--weight-bold) var(--text-sm)/1 var(--font-body);white-space:nowrap}
.kh-stop .st.here{color:var(--text)}
.kh-stop .st.open{color:var(--accent-discovery)}
.kh-stop .st.locked{color:var(--text-muted)}
.kh-stop .st.here .kh-ico{color:var(--paper)}
.kh-lift .side{display:flex;flex-direction:column;gap:var(--space-3)}
.kh-lift .card{background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-4) var(--space-5);display:flex;flex-direction:column;gap:var(--space-3)}
.kh-lift .card h3{font-size:var(--text-xl);display:flex;align-items:center;gap:var(--space-2)}
.kh-lift .card p{margin:0;font-size:var(--text-base)}
.kh-lift .card p .mut{color:var(--text-muted)}
.kh-lift .need{display:flex;align-items:center;gap:var(--space-3);background:var(--panel-sunken);border:2px dashed var(--border);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3);font-size:var(--text-base)}
.kh-lift .btns{display:flex;gap:var(--space-3);flex-wrap:wrap}
.kh-lift .keys{display:flex;flex-direction:column;gap:var(--space-2);font-size:var(--text-sm);color:var(--text-muted)}
.kh-lift .keys b{color:var(--text)}

/* ---- Mira results ------------------------------------------------------------------------------ */
.kh-results{position:absolute;z-index:calc(var(--z-overlay) + 1);left:140px;top:40px;width:1000px;padding:var(--space-4) var(--space-5);display:flex;flex-direction:column;gap:var(--space-3)}
.kh-results .top2{display:flex;align-items:center;gap:var(--space-4)}
.kh-results .top2 h2{font-size:var(--text-xl)}
.kh-results .body{display:grid;grid-template-columns:1fr 1fr;gap:var(--space-4)}
.kh-results .card{background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-3) var(--space-4);display:flex;flex-direction:column;gap:var(--space-2)}
.kh-medal{display:flex;align-items:center;gap:var(--space-4);border:3px solid var(--gold);border-radius:var(--radius-lg);padding:var(--space-3) var(--space-4);background:var(--panel-sunken)}
.kh-medal .kh-ico{color:var(--gold)}
.kh-medal .t{font:var(--weight-bold) var(--text-xl)/1.2 var(--font-display);color:var(--accent-discovery)}
.kh-medal .d{font-size:var(--text-sm);color:var(--text-muted)}
.kh-stats{width:100%;border-collapse:collapse;font-size:var(--text-base)}
.kh-stats th{font:var(--weight-bold) var(--text-sm)/1.2 var(--font-body);letter-spacing:var(--tracking-label);text-transform:uppercase;color:var(--text-muted);text-align:left;padding:var(--space-1) var(--space-2) var(--space-1) 0}
.kh-stats td{padding:var(--space-1) var(--space-2) var(--space-1) 0;border-top:2px solid var(--border)}
.kh-stats td.ok{color:var(--accent-discovery);font-weight:var(--weight-bold)}
.kh-stats td .kh-ico{vertical-align:-4px}
.kh-patches{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-2)}
.kh-pt{display:flex;flex-direction:column;align-items:center;gap:var(--space-1);text-align:center;border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-2);background:var(--panel-sunken);font-size:var(--text-sm);line-height:1.25}
.kh-pt b{font-size:var(--text-sm)}
.kh-pt .via{color:var(--text-muted)}
.kh-pt.earned{border-color:var(--gold);border-width:3px}
.kh-pt.locked{border-style:dashed}
.kh-pt.locked .kh-ico.patch{opacity:.55;filter:grayscale(1)}
.kh-pt .state{display:inline-flex;align-items:center;gap:var(--space-1);font:var(--weight-bold) var(--text-sm)/1 var(--font-body)}
.kh-pt.earned .state{color:var(--accent-discovery)}
.kh-pt.locked .state{color:var(--text-muted)}

/* ---- Settings ---------------------------------------------------------------------------------- */
.kh-set{display:grid;grid-template-columns:480px 1fr;gap:var(--space-5);flex:1;min-height:0}
.kh-set .col{display:flex;flex-direction:column;gap:var(--space-2);min-width:0}
.kh-set h3{font-size:var(--text-lg)}
.kh-opt{display:grid;grid-template-columns:auto 1fr auto;gap:var(--space-1) var(--space-3);align-items:center;background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3)}
.kh-opt .nm{font:var(--weight-bold) var(--text-base)/1.2 var(--font-body)}
.kh-opt .ds{grid-column:2/3;font-size:var(--text-sm);color:var(--text-muted);line-height:1.3}
.kh-opt .kh-ico.lead{color:var(--accent-terminal)}
.kh-opt.sub{margin-left:var(--space-5)}
.kh-opt.focus{outline:2px solid var(--focus);outline-offset:2px;border-color:var(--focus)}
.kh-sw{display:inline-flex;align-items:center;gap:var(--space-2);font:var(--weight-bold) var(--text-sm)/1 var(--font-body);min-width:92px;justify-content:flex-end}
.kh-sw .track{position:relative;width:52px;height:30px;border-radius:var(--radius-pill);border:2px solid var(--border);background:var(--panel-sunken);flex:none}
.kh-sw .track::after{content:"";position:absolute;left:3px;top:3px;width:20px;height:20px;border-radius:var(--radius-pill);border:3px solid var(--text-muted);background:transparent}
.kh-sw.on .track{background:var(--teal);border-color:var(--teal)}
.kh-sw.on .track::after{left:25px;border:0;background:var(--ink)}
.kh-sw.on{color:var(--accent-terminal)}
.kh-sw.off{color:var(--text-muted)}
.kh-diff{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-3)}
.kh-lvl{display:flex;flex-direction:column;gap:var(--space-2);background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-3) var(--space-3)}
.kh-lvl.sel{border-color:var(--focus);outline:2px solid var(--focus);outline-offset:2px}
.kh-lvl h4{margin:0;display:flex;align-items:center;justify-content:space-between;gap:var(--space-2);font:var(--weight-bold) var(--text-lg)/1.2 var(--font-display)}
.kh-lvl h4 .pick{font:var(--weight-bold) var(--text-sm)/1 var(--font-body);color:var(--text-muted);display:inline-flex;align-items:center;gap:var(--space-1)}
.kh-lvl.sel h4 .pick{color:var(--text)}
.kh-lvl .what{margin:0;font-size:var(--text-sm);color:var(--text-muted)}
.kh-prev{background:var(--panel-sunken);border:2px solid var(--border);border-radius:var(--radius-md);padding:var(--space-2) var(--space-3);display:flex;flex-direction:column;gap:var(--space-1);font-size:var(--text-sm);line-height:1.4}
.kh-prev .l1{color:var(--text)}
.kh-prev .l1 b{color:var(--text)}
.kh-prev .l2{color:var(--text-muted)}
.kh-prev .l2 b{color:var(--text)}
.kh-prev .gone{color:var(--text-muted);border:2px dashed var(--border);border-radius:var(--radius-sm);padding:0 var(--space-2);display:inline-flex;align-items:center;gap:var(--space-2);align-self:flex-start}
.kh-reset{display:flex;flex-direction:column;gap:var(--space-2);background:var(--panel-raised);border:3px solid var(--paper);border-radius:var(--radius-lg);padding:var(--space-3) var(--space-4)}
.kh-reset .q{display:flex;align-items:center;gap:var(--space-3);font:var(--weight-bold) var(--text-lg)/1.3 var(--font-display)}
.kh-reset p{margin:0;font-size:var(--text-base)}
.kh-reset .btns{display:flex;gap:var(--space-3);flex-wrap:wrap}
"""


# --------------------------------------------------------------------------- artifact close-up
def artifact_screen():
    inner = f"""
<section class="kh-panel kh-artifact" role="dialog" aria-label="Artifact: First route receipt">
  <div class="head">
    <span class="kh-slot" role="img" aria-label="Icon slot: receipt">{ico("receipt", 44)}</span>
    <div><span class="kh-label">Artifact · Orientation</span><h2>First route receipt</h2>
      <span class="meta">Found at the Records door. Kept in your journal.</span></div>
    <span class="kh-btn focus">Back to the world <span class="kh-key sm">Esc</span></span>
  </div>
  <div class="kh-paper" role="img" aria-label="Receipt text">
    <div class="title">Department of Motion: route receipt</div>
    <div class="row"><span>Employee</span><span>new engineer</span></div>
    <div class="row"><span>Route</span><span>lobby to east exit</span></div>
    <div class="row"><span>Detour counted as</span><span>successful movement</span></div>
    <div class="row"><span>Pace score</span><span>100%</span></div>
    <span class="stamp">COUNTED</span>
  </div>
  <p class="caption">Pace counted a detour as a successful movement. The receipt does not say who asked for the detour, only that it arrived.</p>
  <div class="foot"><span class="kept">{ico("check", 20)} Added to the journal</span><span>One frame for every artifact: the icon slot, the title, a document and two to four lines of caption.</span></div>
</section>"""
    return shot("artifact-closeup", "Artifact close-up frame",
                "One shared document frame for every artifact: an icon slot (72 px), the title and where it was found, the document on paper, a two-to-four-line caption and a visible way back to the world. Only the icon, title, document text and caption change.",
                inner)


# --------------------------------------------------------------------------- elevator map
def stop(floor, name, kind, sub, status, selected=False):
    cls = {"here": "here", "open": "open", "locked": "locked"}[kind]
    icon = {"here": "here", "open": "target", "locked": "lock"}[kind]
    sel = " sel" if selected else ""
    return f"""
    <div class="kh-stop {cls}{sel}" role="listitem" aria-label="Floor {floor}, {name}, {status}">
      <span class="fl">{floor}</span>
      <div><div class="nm">{name}</div><div class="sub">{sub}</div></div>
      <span class="st {cls}">{ico(icon, 20)} {status}</span>
    </div>"""


def elevator_screen():
    stops = (
        stop(5, "Executive Floor", "locked", f'Needs {seal("night", 22)} <b>Night Shift seal</b>', "Locked")
        + stop(4, "Night Shift", "locked", f'Needs {seal("systems", 22)} <b>Systems seal</b>', "Locked")
        + stop(3, "Systems", "locked", f'Needs {seal("records", 22)} <b>Records seal</b>', "Locked", selected=True)
        + stop(2, "Records", "open", "Open since the Orientation review", "Open · new")
        + stop(1, "Orientation", "here", "Reception, garden, badge printer", "You are here")
    )
    inner = f"""
<div class="kh-panel overlay" role="dialog" aria-label="Elevator map">
  <div class="top"><h2>Elevator</h2><span class="kh-label">Five stops</span><span class="grow"></span>
    <span class="seals" style="display:inline-flex;align-items:center;gap:var(--space-2);color:var(--accent-discovery);font-weight:var(--weight-bold)">{ico("seal", 24)} Clearance seals 1 / 5</span>
    <span class="kh-btn focus">Back to the floor <span class="kh-key sm">Esc</span></span></div>
  <div class="kh-lift">
    <div class="kh-shaft" role="list" aria-label="Floors">{stops}</div>
    <div class="side">
      <div class="card">
        <span class="kh-label">Selected stop · floor 3</span>
        <h3>{ico("lock", 28)} Systems is locked</h3>
        <div class="need">{seal("records", 40)}<span><b>Needs the Records seal.</b> You earn it at the end of Records, in <b>11 Marked for Review</b>.</span></div>
        <p><span class="mut">Nearby objective:</span> Records is open. Noor has the next request at the archive desk.</p>
        <div class="btns"><span class="kh-btn primary">Go to Records <span class="kh-key sm">Return</span></span><span class="kh-btn">Stay on this floor <span class="kh-key sm">Esc</span></span></div>
      </div>
      <div class="card">
        <span class="kh-label">Seals</span>
        {seal_strip(1, 44, names=True)}
        <div class="keys">
          <span>To pick a floor, you need to press <b>Up arrow</b> or <b>Down arrow</b>. Hint: they are <b>tap-hold Caps + K</b> and <b>tap-hold Caps + J</b>.</span>
          <span>To ride to the chosen floor, you need to press <b>Return</b>. Hint: Return is <b>tap-hold Caps</b> + <b>N</b>.</span>
        </div>
      </div>
    </div>
  </div>
</div>"""
    return shot("elevator-map", "Elevator map",
                "Five stops, one per district. A locked stop shows the seal it needs and what to do next, never a blank door; the current floor has a filled marker and the words 'You are here'; Esc always goes back. Locked is a dashed floor badge, a lock and 'Needs …', so no state is colour alone.",
                inner)


# --------------------------------------------------------------------------- seals: award, toast, Mira results
def award_screen():
    rays = ''.join(
        f'<line x1="{90 + 62 * math.cos(a * math.pi / 8):.1f}" y1="{90 + 62 * math.sin(a * math.pi / 8):.1f}" x2="{90 + 86 * math.cos(a * math.pi / 8):.1f}" y2="{90 + 86 * math.sin(a * math.pi / 8):.1f}"/>'
        for a in range(16))
    inner = f"""
<section class="kh-panel kh-award" role="dialog" aria-label="Seal awarded: Orientation">
  <span class="kicker">Clearance seal 1 of 5</span>
  <div class="burst">
    <svg class="rays" viewBox="0 0 180 180" aria-hidden="true"><g stroke="var(--gold)" stroke-width="4" stroke-linecap="square" opacity="0.7">{rays}</g></svg>
    {seal("orientation", 120)}
  </div>
  <h2>Orientation seal</h2>
  <p class="what">Awarded for level 06, The Other Keyboard: a clean changed-context review.</p>
  <div class="changes">
    <div>{ico("target", 24)}<span>The east door to <b>Records</b> opens.</span></div>
    <div>{ico("target", 24)}<span>A shortcut across the garden is unlocked for return visits.</span></div>
    <div>{ico("target", 24)}<span>The background workers stop walking in step.</span></div>
  </div>
  <div class="foot"><span>With reduced motion the seal appears at rest: no spin, no burst.</span>
    <span class="kh-btn primary focus">Continue <span class="kh-key sm">Return</span></span></div>
  {seal_strip(1, 36, names=False)}
</section>"""
    return shot("seal-award", "Seal award moment",
                "A centred card over the dimmed world: the earned seal in gold with static rays (no motion), what it was awarded for, the visible changes it caused, and the five-seal strip with the new seal filled. Unearned seals are dashed outlines, so earned and unearned differ by shape.",
                inner)


def toast_screen():
    inner = f"""
<div class="kh-hud obj" role="status">
  <span class="title">Visit Records</span><span class="count">0 / 4</span><span class="sep"></span>
  <span class="seals">{ico("seal", 24)} Seals 1</span>
</div>
<div class="kh-hud shortcuts"><span class="chip">Journal <span class="kh-key sm">Tab</span></span><span class="chip">Layout help <span class="kh-key sm">?</span></span></div>
{mk("route", style="left:1090px;top:252px")}
<div class="kh-toasts" aria-live="polite">
  <div class="kh-toast"><span class="ic">{seal("orientation", 44)}</span><span class="t">Seal earned: <em>Orientation</em></span><span class="d">The Records door is open.</span></div>
  <div class="kh-toast"><span class="ic">{ico("receipt", 30)}</span><span class="t">Artifact found: <em>First route receipt</em></span><span class="d">Added to your journal.</span></div>
  <div class="kh-toast patchy"><span class="ic">{patch(1, 46)}</span><span class="t">New patch: <em>First Delivery</em></span><span class="d">Mira recorded your Morning Mail baseline.</span></div>
</div>"""
    return shot("toast", "Toasts",
                "Top-centre stack, z 90, at most three, each with a gold bar, an icon, a bold line and one muted line. They announce politely (aria-live), carry no key and fade after about six seconds (or just disappear under reduced motion). The world changes too: the Records door is marked with the route diamond.",
                inner, scrim="none")


def results_screen():
    pts = ""
    for n, name, via in PATCHES:
        got = n == 1
        state = (f'<span class="state">{ico("check", 16)} Earned</span>' if got
                 else f'<span class="state">{ico("lock", 16)} Not yet</span>')
        pts += (f'<div class="kh-pt {"earned" if got else "locked"}">{patch(n, 64)}<b>{name}</b>'
                f'<span class="via">{via}</span>{state}</div>')
    inner = f"""
<section class="kh-panel kh-results" role="dialog" aria-label="Route results: Morning Mail">
  <div class="top2"><h2>Morning Mail</h2><span class="kh-label">Optional speed · Mira</span><span class="grow" style="flex:1"></span>
    <span class="kh-btn primary focus">Continue <span class="kh-key sm">Return</span></span></div>
  <div class="body">
    <div class="card">
      <div class="kh-medal">{ico("medal", 64)}<div><div class="t">Clean-run medal</div>
        <div class="d">Every task-critical output right, 95% or more correct, and no less accurate than your baseline.</div></div></div>
      <table class="kh-stats">
        <tr><th>Run</th><th>This run</th><th>Baseline</th></tr>
        <tr><td>Route time</td><td>1:36</td><td>1:41</td></tr>
        <tr><td>Accuracy</td><td>98%</td><td>97%</td></tr>
        <tr><td>Task-critical outputs</td><td class="ok">{ico("check", 20)} All correct</td><td>All correct</td></tr>
        <tr><td>Optional target</td><td class="ok">{ico("check", 20)} Reached (1:36)</td><td>about 5% faster</td></tr>
      </table>
      <span class="d" style="font-size:var(--text-sm);color:var(--text-muted)">Speed here is optional. It never changes your stars, seals or the ending. A faster run with extra errors would not earn the medal.</span>
    </div>
    <div class="card">
      <span class="kh-label">Mira's patches · 1 of 6</span>
      <div class="kh-patches">{pts}</div>
    </div>
  </div>
</section>"""
    return shot("mira-results", "Mira's route results",
                "The card after an optional speed route: the clean-run medal in gold, route time and accuracy next to the player's own baseline, and Mira's six patches by name. An earned patch has a gold frame, a check and the word Earned; the others are dashed, greyed and say Not yet. A first clean run says 'Baseline recorded' and awards the patch instead; the medal needs a later faster clean run.",
                inner)


def seals_sheet():
    cells = "".join(
        f'<div class="seal-cell"><div class="seal-pair">{seal(sid, 96)}{seal(sid, 40)}{seal(sid, 24)}</div><b>{name}</b><span>level {lvl}: {lv}</span></div>'
        for sid, name, lvl, lv in SEALS)
    pcells = "".join(
        f'<div class="seal-cell"><div class="seal-pair">{patch(n, 96)}{patch(n, 48)}</div><b>{n} {name}</b><span>{via}</span></div>'
        for n, name, via in PATCHES)
    inner = f"""
<div class="kh-panel overlay su" role="group" aria-label="Seal and patch icons">
  <div class="top"><h2>Seals and patches</h2><span class="sub">Gold seals at 96, 40 and 24 px; Mira's patches at 96 and 48 px.</span></div>
  <span class="kh-label">Five clearance seals</span>
  <div class="seal-grid">{cells}</div>
  <span class="kh-label">Mira's six patches</span>
  <div class="seal-grid six">{pcells}</div>
</div>"""
    return shot("seal-icons", "Seal and patch icons",
                "Five clearance seals in gold; each is a gold octagon with an ink line and its own glyph (sprout, ring, network, crescent, tree), so they differ by shape in greyscale. Below, Mira's six patches in her colours, matching art-direction/cast/MIRA_PATCHES_SPEC.md.",
                inner)


# --------------------------------------------------------------------------- settings
def sw(on):
    return f'<span class="kh-sw {"on" if on else "off"}" role="switch" aria-checked="{"true" if on else "false"}"><span class="track"></span>{"On" if on else "Off"}</span>'


def settings_screen():
    def opt(icon, name, desc, on, focus=False, sub=False):
        d = f'<span class="ds">{desc}</span>' if desc else ""
        return (f'<div class="kh-opt{" sub" if sub else ""}{" focus" if focus else ""}">{ico(icon, 28)}'
                f'<span class="nm">{name}</span>{sw(on)}{d}</div>')
    left = (
        '<h3>Accessibility</h3>'
        + opt("text", "Larger text", "Body text 18 px becomes 22 px.", False)
        + opt("contrast", "High contrast", "Panels and keycaps use the strongest pairs.", False)
        + opt("motion", "Reduced motion", "No idle loops, burst or fades.", True, focus=True)
        + '<h3>Sound</h3>'
        + opt("sound-off", "Sound", "Off by default; effects and music are separate.", False)
        + opt("sound-off", "Effects", "", False, sub=True)
        + opt("sound-off", "Music", "", False, sub=True)
    )

    def lvl(name, what, l1, l2, selected=False, gone=None):
        pick = (f'<span class="pick">{ico("check", 16)} Selected</span>' if selected else '<span class="pick">Not selected</span>')
        return f"""
<div class="kh-lvl{' sel' if selected else ''}" role="radio" aria-checked="{'true' if selected else 'false'}">
  <h4>{name}{pick}</h4><p class="what">{what}</p>
  <div class="kh-prev" aria-label="Hint preview">{l1}{l2}{gone or ""}</div>
</div>"""
    diff = (
        lvl("Standard", "Action, key and gesture, always.",
            '<span class="l1">To submit the access code, you need to press <b>Return</b>.</span>',
            '<span class="l2">Hint: Return is <b>tap-hold Caps</b> + <b>N</b>.</span>', selected=True)
        + lvl("Focused", "Action and key. The gesture on request.",
              '<span class="l1">To submit the access code, you need to press <b>Return</b>.</span>',
              '<span class="l2">Hint: hidden until you ask.</span>',
              gone=f'<span class="gone">{ico("eye", 18)} Show hint</span>')
        + lvl("Violento", "Action only, once the gesture is introduced.",
              '<span class="l1">To submit the access code.</span>',
              '<span class="l2">Key and gesture are hidden.</span>')
    )
    right = f"""
<h3>Difficulty <span class="kh-label" style="margin-left:var(--space-2)">hint lines fade; every story stays untimed</span></h3>
<div class="kh-diff" role="radiogroup" aria-label="Difficulty">{diff}</div>
<div style="display:flex;align-items:center;gap:var(--space-3);font-size:var(--text-sm);color:var(--text-muted)">{chip_practice(False)}<span>Difficulty is separate from the Kanata practice layer, which the game never detects.</span></div>
<h3>Progress</h3>
<div class="kh-reset" role="alertdialog" aria-label="Reset progress">
  <div class="q">{ico("warn", 28)} Reset all progress on this device?</div>
  <p>Seals, stars, patches, artifacts and best scores are erased. Settings stay. This cannot be undone.</p>
  <div class="btns"><span class="kh-btn primary focus">Keep my progress <span class="kh-key sm">Esc</span></span><span class="kh-btn">{ico("reset", 18)} Reset progress</span></div>
</div>"""
    inner = f"""
<div class="kh-panel overlay su" role="dialog" aria-label="Settings and accessibility">
  <div class="top"><h2>Settings</h2><span class="sub">Saved on this device.</span><span class="grow"></span>
    <span class="kh-btn">Run setup again</span><span class="close"><span class="kh-key sm">Esc</span> tap Caps to close</span></div>
  <div class="kh-set"><div class="col">{left}</div><div class="col">{right}</div></div>
</div>"""
    return shot("settings", "Settings and accessibility",
                "Larger text, high contrast and reduced motion are switches that say On or Off in words and move a knob; sound is off by default with separate effects and music. Difficulty is a three-card choice with a live preview of how the hint lines fade. Reset progress always asks first, with the safe answer focused.",
                inner)


def p1_sections():
    return (artifact_screen() + elevator_screen() + award_screen() + toast_screen() + results_screen()
            + seals_sheet() + settings_screen())


CSS += """
.seal-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:var(--space-3)}
.seal-grid.six{grid-template-columns:repeat(6,1fr)}
.seal-cell{background:var(--panel-raised);border:2px solid var(--border);border-radius:var(--radius-lg);padding:var(--space-3);display:flex;flex-direction:column;align-items:center;gap:var(--space-2);text-align:center;font-size:var(--text-sm)}
.seal-cell span{color:var(--text-muted)}
.seal-pair{display:flex;align-items:flex-end;gap:var(--space-3);color:var(--accent-discovery)}
"""
