"""Palette and variant checks for the background workers. Exit code 1 on any failure.

Run: python3 check_bgworkers.py   (from anywhere; stdlib only)
1. Runs the shared Gate 1 checker on both bodies (default palette).
2. Swaps every PALETTES entry into PAL and re-runs the marker, violet and teal tests, plus the
   muted rules (saturation cap, luminance spread below the named cast, contrast against the floor,
   hair against skin) over every idle, walk and individual-idle frame.
3. Checks the individual idles' frame rules and that the silhouette palette uses ink steps only.
"""
import colorsys
import importlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
sys.path.insert(0, os.path.join(HERE, "..", "kit"))
CHECK = os.path.join(HERE, "..", "gate1", "check_gate1.py")
MARKERS = {"#19AFA2", "#EC776D", "#9876D5", "#E6B750"}
VIOLET = {"#413755", "#67547C", "#9477AF", "#C3A6D6"}
INK = {"#202337", "#343650", "#535971"}
FLOOR = "#E6D3B3"
SAT_CAP = 30          # worker top / trouser / under steps, HSL %
MIN_TOP_FLOOR = 2.0   # worker top fill vs floor, WCAG-style ratio, so figures stay findable
MIN_HAIR_SKIN = 1.25  # any hair step touching any skin step
fails = []


def rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


def hsl(h):
    hh, l, s = colorsys.rgb_to_hls(*rgb(h))
    return hh * 360, s * 100, l * 100


def lum(h):
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4  # noqa: E731
    r, g, b = (f(c) for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def frames_of(mod):
    out = {f"idle_{f}_{i}": fr for f, fs in mod.IDLE.items() for i, fr in enumerate(fs)}
    out.update({f"walk_{f}_{i}": fr for f, fs in mod.WALK.items() for i, fr in enumerate(fs)})
    out.update({f"{k}_{i}": fr for k, fs in mod.IDLE_VARIANTS.items() for i, fr in enumerate(fs)})
    out.update({f"seated_{k}_{i}": fr for k, fs in mod.SEATED.items() for i, fr in enumerate(fs)})
    return out


def occluder_hidden():
    """Pixels of the 16x24 seated frame covered by the real desk-front occluder (kit atlas, seat offsets)."""
    import numpy as np
    import kitlib
    at = kitlib.Atlas(os.path.join(HERE, "..", "kit", "orientation-atlas.json"))
    out = {}
    for desk in ("desk_a", "desk_b"):
        e = at.entries[desk + "_front"]
        spr = at.sprite(desk + "_front")
        ox, oy = e["footprint"]["origin_px"]
        mask = np.zeros((24, 16), bool)
        for y in range(spr.shape[0]):
            for x in range(spr.shape[1]):
                fy, fx = (y - oy) + 20 - 0 - 0, (x - ox) - 8   # occluder px relative to desk origin -> frame px
                if spr[y, x, 3] and 0 <= fy < 24 and 0 <= fx < 16:
                    mask[fy, fx] = True
        out[desk] = mask
    return out


# Named-cast references for "lower contrast, recede": Engineer jacket, Ivo cardigan, Mira ochre panel.
cast = {}
for n, keys in (("engineer_sprites", "pqrs"), ("ivo_sprites", "pqrs"), ("mira_sprites", "wxyz")):
    m = importlib.import_module(n)
    cols = [m.PAL[k] for k in keys]
    cast[n] = (max(hsl(c)[1] for c in cols), max(lum(c) for c in cols) - min(lum(c) for c in cols))
CAST_SAT = min(v[0] for v in cast.values())
CAST_SPREAD = min(v[1] for v in cast.values())

for body in ("bgworker_a_sprites", "bgworker_b_sprites"):
    r = subprocess.run([sys.executable, CHECK, body], capture_output=True, text=True)
    print(f"[{body}] gate1: {r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()}")
    if r.returncode:
        fails.append(f"{body}: check_gate1 failed\n{r.stdout}")

    mod = importlib.import_module(body)
    frames = frames_of(mod)
    # structure of every frame, including the individual idles (check_gate1 does not see those)
    for name, fr in frames.items():
        if len(fr) != 24 or any(len(x) != 16 for x in fr):
            fails.append(f"{body} {name}: not 16x24")
            continue
        if not any(c != "." for c in fr[23]):
            fails.append(f"{body} {name}: nothing on row 23")
        left = sum(c != "." for x in fr for c in x[:8])
        right = sum(c != "." for x in fr for c in x[8:])
        if abs(left - right) / (left + right) > 0.2:
            fails.append(f"{body} {name}: mass off anchor (L {left} / R {right})")
        head = set(mod.SLOTS["hair"] + mod.SLOTS["skin"] + "o.")
        for y, x in enumerate(fr[:10]):
            if set(x) - head:
                fails.append(f"{body} {name}: row {y} head uses {sorted(set(x) - head)}")
        for y, x in enumerate(fr):
            for xx, c in enumerate(x):
                if c == "A" and 0 < xx < 15 and 0 < y < 23 and {x[xx - 1], x[xx + 1], fr[y - 1][xx], fr[y + 1][xx]} <= set(mod.SLOTS["hair"]):
                    fails.append(f"{body} {name}: darkest hair step used as fill at ({y},{xx})")
        if name.startswith("walk_") and any(x[0] != "." or x[15] != "." for x in fr[18:]):
            fails.append(f"{body} {name}: stride touches the frame edge")
    if len(mod.WALK["s"]) != 4 or any(len(v) != 4 for v in mod.WALK.values()):
        fails.append(f"{body}: walk must be 4 frames per facing")
    if any(len(v) != 2 for v in mod.IDLE.values()) or any(len(v) != 2 for v in mod.IDLE_VARIANTS.values()):
        fails.append(f"{body}: idles must be 2 frames")

    # seated sets: everything readable above the occluder, columns 0 and 15 empty below row 14, 2 frames,
    # and the real desk-front occluders cover no pixel of rows 0-14
    hidden = occluder_hidden()
    if set(mod.SEATED) != {"idle", "typing", "phone", "coffee"}:
        fails.append(f"{body}: SEATED needs idle, typing, phone, coffee")
    for k, fs in mod.SEATED.items():
        if len(fs) != 2 or fs[0] == fs[1]:
            fails.append(f"{body}: seated {k} must be 2 distinct frames")
        for i, fr in enumerate(fs):
            nm = f"seated_{k}_{i}"
            if any(x[0] != "." or x[15] != "." for x in fr[15:]):
                fails.append(f"{nm}: {body} columns 0/15 used below row 14 (visible beside the occluder)")
            if any(c in "ghjefi" for x in fr[15:] for c in x):
                fails.append(f"{nm}: {body} prop key below row 14 (hidden by the occluder)")
            for desk, mask in hidden.items():
                for y in range(15):
                    if any(m and c != "." for m, c in zip(mask[y], fr[y])) and y < 15:
                        fails.append(f"{nm}: {body} {desk} occluder covers a pixel in row {y}")
                        break
            if k in ("phone", "coffee") and not any(c in "ghjefi" for x in fr[:15] for c in x):
                fails.append(f"{nm}: {body} prop not visible in rows 0-14")
    print(f"[{body}] seated: 4 sets x 2 frames, occluder rows 15-23 hidden, rows 0-14 clear (checked vs the kit atlas)")

    seen = []
    for pname in mod.PALETTES:
        pal = mod.make_pal(pname)
        mod.PAL.clear()
        mod.PAL.update(pal)  # swap PAL in place, as the brief asks, so every check reads the swap
        used = {pal[c] for fr in frames.values() for x in fr for c in x if c != "."}
        if used & MARKERS:
            fails.append(f"{body}/{pname}: marker hex {used & MARKERS}")
        if used & VIOLET:
            fails.append(f"{body}/{pname}: violet on a person")
        for slot in ("jacket", "under", "trousers"):
            for k in mod.SLOTS[slot]:
                h, s, _l = hsl(pal[k])
                if 160 <= h <= 200 and s > 60:
                    fails.append(f"{body}/{pname}: {slot} {pal[k]} teal-hued at {s:.0f}% saturation")
                if s > SAT_CAP:
                    fails.append(f"{body}/{pname}: {slot} {pal[k]} saturation {s:.0f}% > {SAT_CAP}%")
        fills = [pal[k] for k in "qrs"]
        spread = max(map(lum, fills)) - min(map(lum, fills))
        if spread >= CAST_SPREAD:
            fails.append(f"{body}/{pname}: top luminance spread {spread:.3f} not below the cast's {CAST_SPREAD:.3f}")
        if ratio(pal["r"], FLOOR) < MIN_TOP_FLOOR:
            fails.append(f"{body}/{pname}: top mid vs floor {ratio(pal['r'], FLOOR):.2f} < {MIN_TOP_FLOOR}")
        if ratio(pal["P"], FLOOR) < 4:
            fails.append(f"{body}/{pname}: trousers vs floor under 4")
        if not all(pal[k] for slot in mod.SLOTS.values() for k in slot):
            fails.append(f"{body}/{pname}: a slot key is transparent")
        hs = set(mod.SLOTS["hair"]); sk = set(mod.SLOTS["skin"])
        worst = 99
        for name, fr in frames.items():
            for y, x in enumerate(fr):
                for xx, c in enumerate(x):
                    for dy, dx in ((1, 0), (0, 1)):
                        if y + dy < 24 and xx + dx < 16:
                            d = fr[y + dy][xx + dx]
                            if (c in hs and d in sk) or (c in sk and d in hs):
                                worst = min(worst, ratio(pal[c], pal[d]))
        if worst < MIN_HAIR_SKIN:
            fails.append(f"{body}/{pname}: hair touches skin at contrast {worst:.2f} < {MIN_HAIR_SKIN}")
        seen.append(pal["r"])
        print(f"[{body}] palette {pname}: top max sat {max(hsl(pal[k])[1] for k in 'pqrs'):.0f}%, "
              f"spread {spread:.3f} (cast {CAST_SPREAD:.3f}), top/floor {ratio(pal['r'], FLOOR):.2f}, "
              f"hair/skin min {worst:.2f}")
    mod.PAL.clear()
    mod.PAL.update(mod.make_pal("slate"))
    if len(set(seen)) != len(seen):
        fails.append(f"{body}: two palettes share the same top")

    # silhouette: ink steps only, and a lit-edge frame stays inside the same colour set
    sil = {mod.SILHOUETTE_PAL[c] for fr in frames.values() for x in fr for c in x if c != "."}
    lit = {mod.SILHOUETTE_LIT_PAL[c] for fr in frames.values() for x in mod.silhouette_lit(fr) for c in x if c != "."}
    if not sil <= INK or not lit <= INK:
        fails.append(f"{body}: silhouette uses non-ink colours {sil | lit}")

for f in fails:
    print("FAIL", f)
print(f"check_bgworkers: {len(fails)} failures (cast reference: sat {CAST_SAT:.0f}%, spread {CAST_SPREAD:.3f})")
sys.exit(1 if fails else 0)
