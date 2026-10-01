"""Objective person-sprite checks (Gate 1 rules) for any cast sprite module. Exit code 1 on any failure."""
import colorsys
import sys

import importlib
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cast"))
# Usage: check_gate1.py [sprite_module]   (default: engineer_sprites)
eng = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "engineer_sprites")

MARKERS = {"#19AFA2", "#EC776D", "#9876D5", "#E6B750"}
VIOLET = {"#413755", "#67547C", "#9477AF", "#C3A6D6"}
fails = []


def hsl(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, s * 100


frames = {f"idle_{f}_{i}": fr for f, fs in eng.IDLE.items() for i, fr in enumerate(fs)}
frames.update({f"walk_{f}_{i}": fr for f, fs in eng.WALK.items() for i, fr in enumerate(fs)})

for name, fr in frames.items():
    if len(fr) != 24 or any(len(r) != 16 for r in fr):
        fails.append(f"{name}: not 16x24")
        continue
    if not any(ch != "." for ch in fr[23]):
        fails.append(f"{name}: nothing rests on row 23")
    left = sum(ch != "." for r in fr for ch in r[:8])
    right = sum(ch != "." for r in fr for ch in r[8:])
    if abs(left - right) / (left + right) > 0.2:
        fails.append(f"{name}: mass off anchor (L {left} / R {right})")
    head_keys = set(eng.SLOTS["hair"] + eng.SLOTS["skin"] + "o.")
    for y, r in enumerate(fr[:10]):
        bad = set(r) - head_keys
        if bad:
            fails.append(f"{name}: row {y} head uses non-hair/skin keys {sorted(bad)}")
    # The darkest hair step may sit on contours and occlusion edges (hair against skin),
    # never as fill: flag it only where hair surrounds it on all four sides.
    hair = set(eng.SLOTS["hair"])
    if any(ch == "A" and 0 < x < 15 and 0 < y < 23
           and {r[x - 1], r[x + 1], fr[y - 1][x], fr[y + 1][x]} <= hair
           for y, r in enumerate(fr) for x, ch in enumerate(r)):
        fails.append(f"{name}: darkest hair step used as interior fill")
    if getattr(eng, "HAIR_SKIN_SEPARATED", False):
        skin = set(eng.SLOTS["skin"]) - {eng.SLOTS["skin"][0]}
        light_hair = set(eng.SLOTS["hair"][1:])
        touch = [(y, x) for y, r in enumerate(fr) for x, ch in enumerate(r) if ch in light_hair
                 and any(0 <= y + dy < 24 and 0 <= x + dx < 16 and fr[y + dy][x + dx] in skin
                         for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
        if touch:
            fails.append(f"{name}: light hair touches skin at {touch[:4]}")
    used = {eng.PAL[ch] for r in fr for ch in r if ch != "."}
    if used & MARKERS:
        fails.append(f"{name}: UI marker hex {used & MARKERS}")
    if used & VIOLET:
        fails.append(f"{name}: violet on a person")

for key in eng.SLOTS["jacket"]:
    h, s = hsl(eng.PAL[key])
    if 160 <= h <= 200 and s > 60:
        fails.append(f"jacket {eng.PAL[key]}: {s:.0f}% saturation > 60%")

# Customization must never change the silhouette: every slot key stays opaque.
assert all(eng.PAL[k] for slot in eng.SLOTS.values() for k in slot)

for f in fails:
    print("FAIL", f)
print(f"{len(frames)} frames checked, {len(fails)} failures")
sys.exit(1 if fails else 0)
