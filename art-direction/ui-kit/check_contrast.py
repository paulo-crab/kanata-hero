#!/usr/bin/env python3
"""WCAG AA contrast check for tokens.css (task 10.1).

Run with the project interpreter:  PY check_contrast.py
Parses every `--name: value;` in tokens.css, resolves `var()` aliases, then asserts
  - every text-on-panel pair listed in PAIRS (>= 4.5:1 normal text, >= 3:1 large text or UI glyphs),
  - the panel alpha leaves text legible over the worst-case world (white and black),
  - the type scale never drops below 16 px and the body face is not a pixel font,
  - the stage maths (320x180 world at an integer zoom is the 1280x720 stage).
  - the generated reference page (every screen in kit_screens.py): no text under 16 px, no pixel font,
    teal/coral/violet never used as text colour (the lighter --accent-* tokens carry text), no violet fill
    behind text, and every "you need to press" instruction followed by a Kanata "Hint:".
Exit status 0 when everything passes.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(HERE, "tokens.css"), encoding="utf-8").read()
CSS_NOCOMMENT = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
RAW = dict(re.findall(r"--([\w-]+):\s*([^;]+);", CSS_NOCOMMENT))


def resolve(name, seen=()):
    v = RAW[name].strip()
    m = re.fullmatch(r"var\(--([\w-]+)\)", v)
    if m:
        if m.group(1) in seen:
            raise ValueError("cycle at " + name)
        return resolve(m.group(1), seen + (name,))
    return v


def rgb(name):
    v = resolve(name)
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", v)
    if not m:
        raise ValueError(f"--{name} is not a plain hex colour: {v}")
    h = m.group(1)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(x) for x in c)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def over(fg, bg, alpha):
    return tuple(round(fg[i] * alpha + bg[i] * (1 - alpha)) for i in range(3))


NORMAL, LARGE = 4.5, 3.0
# (foreground token, background token, minimum, where it is used)
PAIRS = [
    ("text", "panel", NORMAL, "body, dialogue, HUD text on a panel"),
    ("text", "panel-raised", NORMAL, "text on cards, journal rows, key wells"),
    ("text", "panel-sunken", NORMAL, "text on recessed wells"),
    ("text-muted", "panel", NORMAL, "labels and captions on a panel"),
    ("text-muted", "panel-raised", NORMAL, "labels and captions on cards"),
    ("text-muted", "panel-sunken", NORMAL, "labels on recessed wells"),
    ("accent-terminal", "panel", NORMAL, "teal text: terminal names, held-key tag"),
    ("accent-terminal", "panel-raised", NORMAL, "teal text on cards"),
    ("accent-conversation", "panel", NORMAL, "coral text: coworker request heading"),
    ("accent-conversation", "panel-raised", NORMAL, "coral text on cards"),
    ("accent-glitch", "panel", NORMAL, "violet text: glitch heading"),
    ("accent-glitch", "panel-raised", NORMAL, "violet text on cards"),
    ("accent-discovery", "panel", NORMAL, "gold text: the effect line, completed state"),
    ("accent-discovery", "panel-raised", NORMAL, "gold text on cards"),
    ("key-text", "key-face", NORMAL, "keycap legend"),
    ("key-held-text", "key-held-face", NORMAL, "held keycap legend"),
    ("key-dim-text", "key-dim-face", NORMAL, "neighbour keys in the position diagram"),
    ("key-silent-text", "key-silent-face", NORMAL, "XX keys on the practice layer"),
    ("text-on-light", "teal", NORMAL, "ink on teal fills"),
    ("text-on-light", "coral", NORMAL, "ink on coral fills"),
    ("text-on-light", "gold", NORMAL, "ink on gold fills"),
    ("text-on-light", "paper", NORMAL, "ink on paper"),
    # UI glyphs, borders and focus: 3:1
    ("border", "panel", LARGE, "panel and divider edges"),
    ("border", "panel-raised", LARGE, "card edges"),
    ("focus", "panel", LARGE, "focus ring on a panel"),
    ("focus", "panel-raised", LARGE, "focus ring on a card"),
    ("key-face", "panel", LARGE, "keycap against its panel"),
    ("key-held-face", "panel", LARGE, "held keycap against its panel"),
    ("key-dim-face", "panel", 1.0, "neighbour keys are decoration; their legend is checked above"),
    ("ink", "teal", LARGE, "marker outline on the monitor glyph"),
    ("ink", "coral", LARGE, "marker outline on the bubble glyph"),
    ("ink", "violet", LARGE, "marker outline on the page glyph"),
    ("ink", "gold", LARGE, "marker outline on the diamond glyph"),
    ("teal", "panel", LARGE, "terminal glyph on a panel"),
    ("coral", "panel", LARGE, "conversation glyph on a panel"),
    ("violet", "panel", LARGE, "glitch glyph on a panel"),
    ("gold", "panel", LARGE, "route glyph on a panel"),
    # ---- Screens added by the layout-help / setup / scene / feedback work ----------------------------
    ("accent-terminal", "panel-sunken", NORMAL, "teal text in code wells: region label, announcement"),
    ("accent-conversation", "panel-sunken", NORMAL, "coral text on recessed wells"),
    ("accent-glitch", "panel-sunken", NORMAL, "violet-tint text in the glitch code well"),
    ("accent-discovery", "panel-sunken", NORMAL, "gold text: target tag, success line, line number"),
    ("selection-text", "selection-bg", NORMAL, "selected text in an editor scene"),
    ("cursor-text", "cursor-face", NORMAL, "glyph under the block cursor"),
    ("focus", "selection-bg", LARGE, "3 px bar under a selection against the selection fill"),
    ("focus", "panel-sunken", LARGE, "selection bar against the code well"),
    ("cursor-face", "panel-sunken", LARGE, "block cursor against the code well"),
    ("focus", "panel-sunken", LARGE, "focus ring on a recessed well"),
    ("border", "panel-sunken", LARGE, "dashed and solid edges on a recessed well"),
    ("key-face", "panel-raised", LARGE, "keycap and double border against a card"),
    ("key-held-face", "panel-sunken", LARGE, "held keycap in the inset wells"),
    ("teal", "panel-raised", LARGE, "terminal glyph and held key on a card"),
    ("teal", "panel-sunken", LARGE, "terminal glyph on a well"),
    ("gold", "panel-raised", LARGE, "gold glyph and frame on a card"),
    ("gold", "panel-sunken", LARGE, "target marker on a well"),
    ("violet", "panel-sunken", LARGE, "glitch glyph on a well"),
    ("border-strong", "panel-raised", LARGE, "teal frame on a card"),
    ("text-muted", "key-silent-face", NORMAL, "legend text beside a silent key"),
    ("text", "key-silent-face", NORMAL, "XX legend on a silent key (Layout help)"),
]

# Synthetic backgrounds: a gold tint over the code well (the target line).
def blend(fg_name, bg_name, alpha):
    return over(rgb(fg_name), rgb(bg_name), alpha)


TARGET_LINE = blend("gold", "panel-sunken", 0.16)
PAIRS_RGB = [
    ("text", TARGET_LINE, NORMAL, "code text on the gold-tinted target line"),
    ("accent-discovery", TARGET_LINE, NORMAL, "gold line number and tag on the target line"),
    ("text-muted", TARGET_LINE, NORMAL, "muted code keyword on the target line"),
]

fails = 0


def report(ok, text):
    global fails
    print(("PASS  " if ok else "FAIL  ") + text)
    if not ok:
        fails += 1


for fg, bg, need, use in PAIRS:
    r = ratio(rgb(fg), rgb(bg))
    report(r >= need, f"{fg:<20} on {bg:<13} {r:5.2f}:1 (need {need:g}) {use}")
for fg, bg, need, use in PAIRS_RGB:
    r = ratio(rgb(fg), bg)
    report(r >= need, f"{fg:<20} on {'#%02X%02X%02X' % bg:<13} {r:5.2f}:1 (need {need:g}) {use}")

# Panels are nearly opaque: re-test the text pairs over the worst-case world (white, black).
alpha = float(resolve("panel-alpha"))
for world_name, world in (("white", (255, 255, 255)), ("black", (0, 0, 0))):
    eff = over(rgb("panel"), world, alpha)
    for fg in ("text", "text-muted"):
        r = ratio(rgb(fg), eff)
        report(r >= NORMAL, f"{fg:<20} on panel@{alpha:g} over {world_name:<5} {r:5.2f}:1 (need {NORMAL:g})")

# --panel-bg must be the panel colour at --panel-alpha.
m = re.fullmatch(r"rgb\((\d+) (\d+) (\d+) / ([\d.]+)\)", resolve("panel-bg"))
ok = bool(m) and tuple(int(m.group(i)) for i in (1, 2, 3)) == rgb("panel") and abs(float(m.group(4)) - alpha) < 1e-6
report(ok, "--panel-bg equals --panel at --panel-alpha")

# Type scale: nothing under 16 px; no pixel font anywhere in the type stacks.
for name in sorted(RAW):
    if name.startswith("text-") and name not in ("text-muted", "text-on-light"):
        px = int(re.fullmatch(r"(\d+)px", resolve(name)).group(1))
        report(px >= 16, f"--{name} = {px}px (body and UI text need >= 16px)")
for name in ("font-body", "font-mono", "font-display"):
    stack = resolve(name).lower()
    report(not re.search(r"pixel|press start|silkscreen|vt323|8-bit", stack), f"--{name} is not a pixel font")
report(resolve("font-body").lower().rstrip().endswith("sans-serif"), "--font-body is a sans-serif stack")
report(resolve("font-mono").lower().rstrip().endswith("monospace"), "--font-mono is a monospace stack")

# Stage and portrait maths.
px = lambda n: int(resolve(n).replace("px", ""))
zoom = int(resolve("world-zoom"))
report(zoom >= 1, f"--world-zoom = {zoom} is a whole number")
report(px("world-w") * zoom == px("stage-w") and px("world-h") * zoom == px("stage-h"), "world x zoom = stage (320x180 x4 = 1280x720)")
report(px("portrait-native") * zoom == px("portrait-size"), "48 px portrait x zoom = --portrait-size (192 px)")

# Role anchors must stay as published unless a change is recorded in UI_KIT_SPEC.md.
PUBLISHED = {"ink": "#182B38", "paper": "#F4F2EC", "teal": "#19AFA2", "coral": "#EC776D", "violet": "#9876D5", "gold": "#E6B750"}
for name, hexv in PUBLISHED.items():
    report(resolve(name).upper() == hexv, f"anchor --{name} is {resolve(name).upper()} (published {hexv})")

# ---- Lint the generated reference page (all screens) ------------------------------------------------
sys.path.insert(0, HERE)
import build_reference  # noqa: E402

HTML = build_reference.page()
STYLE = "".join(re.findall(r"<style>(.*?)</style>", HTML, flags=re.S)) + "".join(re.findall(r'style="([^"]*)"', HTML))
bad = []
for m in re.finditer(r"font-size:\s*([^;}\"]+)", STYLE):
    v = m.group(1).strip()
    if v.startswith("var(--text-"):
        continue
    mm = re.fullmatch(r"(\d+(?:\.\d+)?)px", v)
    if not mm or float(mm.group(1)) < 16:
        bad.append("font-size:" + v)
for m in re.finditer(r"(?<![-\w])font:\s*([^;}\"]+)", STYLE):
    if "var(--text-" not in m.group(1):
        bad.append("font:" + m.group(1))
report(not bad, "every font-size and font shorthand in the page is >= 16 px" + (": " + "; ".join(bad[:4]) if bad else ""))
report(not re.search(r"font-family:\s*(?!var\(--font-)", STYLE), "font-family only through the --font-* tokens (no pixel font)")
report(not re.search(r"(?<![-\w])color:\s*var\(--(teal|coral|violet)\)", STYLE),
       "teal, coral and violet are never a text colour (the lighter --accent-* tokens carry text)")
report(not re.search(r"background(?:-color)?:\s*var\(--violet\)", STYLE), "no text sits on a violet fill (violet is a glyph and outline colour only)")
texts = [m.start() for m in re.finditer(r"you need to press", HTML)]
missing = [i for i in texts if "Hint:" not in HTML[i:i + 420]]
report(texts and not missing, f"hint grammar: all {len(texts)} instructions saying 'you need to press' carry a 'Hint:' (action, key, gesture)")
ids = re.findall(r'<span class="a" id="s-([\w-]+)">', HTML)
report(len(ids) == len(set(ids)) and len(ids) >= 5, f"{len(ids)} screens carry unique #s-<id> targets")
report("<script" not in HTML, "reference page has no script")

print()
print("ALL CHECKS PASSED" if not fails else f"{fails} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
