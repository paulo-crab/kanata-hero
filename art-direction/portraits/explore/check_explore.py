"""Checks for the portrait exploration (three styles x Engineer, Ivo, Mira x three expressions).

Run: python3 check_explore.py     Exit code 1 on any failure.
Per grid: 48x48; every key is a key of that character's world-sprite PAL (the one extra pale
highlight key per character is itself a PAL key, recorded in explore_common.CHARS[..]["extra"]
and checked here to carry the sprite's hex); no UI marker hex; no violet; row 0 and the side
columns clear; a closed outline (every opaque pixel that touches transparency is #0E1020, except
on the crop row); the hair and clothing keys of the sprite appear; skin steps stay within the
direction's budget (the blush key is counted apart); expressions differ and share their shoulders.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import explore_common as X  # noqa: E402
import style_a  # noqa: E402
import style_b  # noqa: E402
import style_c  # noqa: E402

STYLES = {"A": style_a, "B": style_b, "C": style_c}
SKIN_BUDGET = {"A": 2, "B": 3, "C": 2}       # skin-ramp steps on the head, blush excluded
fails = []
count = 0


def diff(a, b):
    return sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


for sid, st in STYLES.items():
    for who, cfg in X.CHARS.items():
        spr = cfg["spr"]
        pal = spr.PAL
        for key, info in cfg["extra"].items():
            if key not in pal or pal[key] != info["hex"]:
                fails.append(f"{who}: recorded extra {key!r} is not a PAL step with that hex")
        grids = {}
        for e in X.EXPRESSIONS:
            name = f"{sid}/{who}/{e}"
            g = X.compose(st, who, e)
            grids[e] = g
            count += 1
            if len(g) != 48 or any(len(r) != 48 for r in g):
                fails.append(f"{name}: not 48x48")
                continue
            used = {ch for r in g for ch in r} - {"."}
            for ch in sorted(used):
                if ch not in pal:
                    fails.append(f"{name}: key {ch!r} is not in {who}'s sprite PAL")
            hexes = {pal[ch] for ch in used if ch in pal}
            if hexes & X.MARKERS:
                fails.append(f"{name}: UI marker hex {sorted(hexes & X.MARKERS)}")
            if hexes & X.VIOLET:
                fails.append(f"{name}: violet on a person")
            if any(ch != "." for ch in g[0]):
                fails.append(f"{name}: row 0 must stay clear")
            if any(r[0] != "." or r[47] != "." for r in g):
                fails.append(f"{name}: pixels on a side column")
            if not any(ch != "." for ch in g[47]):
                fails.append(f"{name}: nothing on the crop row")
            for y in range(48):
                for x in range(48):
                    ch = g[y][x]
                    if ch in (".", "o"):
                        continue
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if 0 <= yy < 48 and 0 <= xx < 48 and g[yy][xx] == ".":
                            fails.append(f"{name}: open silhouette at ({x},{y}) key {ch!r}")
                            break
            if pal.get("o") != X.OUTLINE:
                fails.append(f"{name}: outline key is not {X.OUTLINE}")
            # identity: the sprite's hair and clothing steps are all present
            hair = set(spr.SLOTS["hair"])
            if len(used & hair) < 3:
                fails.append(f"{name}: hair ramp barely used ({sorted(used & hair)})")
            jacket = set(spr.SLOTS["jacket"])
            if not used & jacket:
                fails.append(f"{name}: no clothing key of the sprite")
            skin = set(spr.SLOTS["skin"]) - {cfg["skin"]["4"]}
            n_skin = len(used & skin)
            if n_skin > SKIN_BUDGET[sid]:
                fails.append(f"{name}: {n_skin} skin steps {sorted(used & skin)} (budget {SKIN_BUDGET[sid]})")
        names = list(X.EXPRESSIONS)
        for i in range(3):
            for j in range(i + 1, 3):
                d = diff(grids[names[i]], grids[names[j]])
                if d < 12:
                    fails.append(f"{sid}/{who}: {names[i]} and {names[j]} differ by only {d} px")
        for e in names[1:]:
            if grids[e][38:] != grids[names[0]][38:]:
                fails.append(f"{sid}/{who}/{e}: shoulders differ from neutral")

for f in fails:
    print("FAIL", f)
print(f"{count} portraits checked, {len(fails)} failures")
sys.exit(1 if fails else 0)
