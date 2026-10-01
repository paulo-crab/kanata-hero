#!/usr/bin/env python3
"""WCAG AA contrast check for tokens.css (task 10.1).

Run with the project interpreter:  PY check_contrast.py
Parses every `--name: value;` in tokens.css, resolves `var()` aliases, then asserts
  - every text-on-panel pair listed in PAIRS (>= 4.5:1 normal text, >= 3:1 large text or UI glyphs),
  - the panel alpha leaves text legible over the worst-case world (white and black),
  - the type scale never drops below 16 px and the body face is not a pixel font,
  - the stage maths (320x180 world at an integer zoom is the 1280x720 stage).
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

print()
print("ALL CHECKS PASSED" if not fails else f"{fails} CHECK(S) FAILED")
sys.exit(1 if fails else 0)
