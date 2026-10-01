"""Checks for Mira's patch states (mira_patches.py). Exit code 1 on any failure.

For each state 0..6 it (1) runs the unmodified Gate 1 person checker on the patched frames,
(2) tests the patch rules: every patch pixel sits on a jacket pixel of the approved frame,
patches stay clear of the head rows, light keys stay small, and each state differs from the
one before it in every facing and in every frame.
Run: python3 check_mira_patches.py
"""
import contextlib
import io
import os
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import mira_patches as mp  # noqa: E402
import mira_sprites as spr  # noqa: E402

fails = []
CHECKER = os.path.join(HERE, "..", "gate1", "check_gate1.py")
LIGHT = set("ijgab")


def gate1(k):
    """Run check_gate1.py unmodified on state k by registering it as a sprite module."""
    name = f"mira_patch_state_{k}"
    sys.modules[name] = mp.module_for_state(k)
    argv, sys.argv = sys.argv, ["check_gate1.py", name]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            runpy.run_path(CHECKER, run_name="__main__")
        code = 0
    except SystemExit as e:
        code = e.code or 0
    finally:
        sys.argv = argv
    for line in buf.getvalue().splitlines():
        if line.startswith("FAIL"):
            fails.append(f"state {k}: {line}")
    return code, buf.getvalue().strip().splitlines()[-1]


summary = []
for k in range(7):
    code, last = gate1(k)
    summary.append(f"state {k}: {last}")

# Patch placement rules, on the approved frames (idle 0 for dy=0, idle 1 for dy=1 coordinates).
for n, patch in enumerate(mp.PATCHES, 1):
    for f, px in patch["world"].items():
        keys = [key for _, _, key in px]
        if not 1 <= len(px) <= 2:
            fails.append(f"patch {n} {f}: {len(px)} px (must be 1-2)")
        for x, y, key in px:
            if y < 10:
                fails.append(f"patch {n} {f}: pixel ({x},{y}) on the head rows")
            base = spr.IDLE[f][0][y][x]
            if base not in mp.JACKET:
                fails.append(f"patch {n} {f}: pixel ({x},{y}) lies on {base!r}, not on the jacket")
            if key not in mp.PAL:
                fails.append(f"patch {n} {f}: unknown key {key!r}")
# Patches never overlap each other within a facing, and keep a 1 px gap from a different patch.
for f in "snew":
    owner = {}
    for n, patch in enumerate(mp.PATCHES, 1):
        for x, y, _ in patch["world"][f]:
            if (x, y) in owner:
                fails.append(f"{f}: patches {owner[(x, y)]} and {n} overlap at ({x},{y})")
            owner[(x, y)] = n
    for (x, y), n in owner.items():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            m = owner.get((x + dx, y + dy))
            if m and m != n:
                fails.append(f"{f}: patches {n} and {m} touch at ({x},{y})")

# Each state differs from the previous in every facing and frame, and light colours stay small.
def frames(k):
    idle, walk = mp.state_frames(k)
    out = {}
    for f in "snew":
        for i, fr in enumerate(idle[f]):
            out[f"idle_{f}_{i}"] = fr
        for i, fr in enumerate(walk[f]):
            out[f"walk_{f}_{i}"] = fr
    return out

prev = frames(0)
for k in range(1, 7):
    cur = frames(k)
    for name, fr in cur.items():
        diff = sum(a != b for ra, rb in zip(fr, prev[name]) for a, b in zip(ra, rb))
        if not 1 <= diff <= 2:
            fails.append(f"state {k} {name}: differs from state {k - 1} by {diff} px (need 1-2)")
        light = sum(row.count(c) for row in fr for c in LIGHT)
        brass = sum(row.count(c) for row in fr for c in "ab")
        if light > 9:
            fails.append(f"state {k} {name}: {light} light patch px (limit 9)")
        if brass > 4:
            fails.append(f"state {k} {name}: {brass} brass px (limit 4)")
    prev = cur

# State 0 is the approved sprite, untouched.
idle0, walk0 = mp.state_frames(0)
assert idle0 == spr.IDLE and walk0 == spr.WALK, "state 0 must equal the approved frames"

for line in summary:
    print(line)
for f in fails:
    print("FAIL", f)
print(f"{len(fails)} patch failures")
sys.exit(1 if fails else 0)
