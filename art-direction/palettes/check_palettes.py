"""Objective palette checks for the district sheets and the new cast ramps (tasks 5.1, 5.2).

Run: python3 check_palettes.py            (needs numpy only; exit code 1 on any failure)
  (a) markers     no step equals or sits within dE(CIE76) < 10 of #19AFA2 #EC776D #9876D5 #E6B750;
                  the violet ramp is the glitch family: it may sit near violet, never equal #9876D5
  (b) teal        hue 160-200 degrees steps stay <= 60% HSL saturation on non-device ramps
  (c) floor       WCAG-style luminance contrast >= 3:1 of the person outline against the floor
                  mid and fill steps (light floors); the cast's mid tones are tabulated, and at
                  least 45% of each sprite's body pixels must reach 3:1 against the floor fill.
                  Dark Night Shift floor: the edge-light rule instead (rim, pool, shadow tests)
  (g) violet      no floor or wall step in hue 260-320 degrees with saturation > 12%; floor mid dE from #9477AF is reported
  (f) ramps       adjacent steps of every district ramp are dE >= 8 apart
  (d) shared      ink and violet ramps are identical in every district
  (e) cast        new skin/hair ramps: corresponding mid steps >= 12 dE from every other cast
                  member, hair separated from skin, ramps clear of markers and violet
Orientation is the approved palette: it is reported (INFO) but not failed.
"""
import colorsys
import itertools
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import district_palettes as dp  # noqa: E402

OUTLINE = "#202337"
MIN_DE_MARKER = 10.0
MIN_DE_CAST = 12.0
MIN_CONTRAST = 3.0
MIN_DL_HAIR_SKIN = 12.0  # L* gap between a hair fill step and the skin step it touches


# ------------------------------------------------------------------ colour maths

def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lab(h):
    r, g, b = (_lin(c) for c in rgb(h))
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116  # noqa: E731
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def de(a, b):
    return sum((p - q) ** 2 for p, q in zip(lab(a), lab(b))) ** 0.5


def lum(h):
    r, g, b = (_lin(c) for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def hsl(h):
    r, g, b = (c / 255 for c in rgb(h))
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, s * 100, l * 100


def ramp_steps(ramps):
    for name, steps in ramps.items():
        for i, h in enumerate(steps):
            yield name, i, h


# ------------------------------------------------------------------ sprite mid tones

def mid_tones(mod):
    """Mid steps of every 4-step body ramp in a sprite module (hair, skin, clothes), plus
    the short trouser ramps in full: {label: hex}."""
    out = {}
    for slot, keys in mod.SLOTS.items():
        groups = [keys[i:i + 4] for i in range(0, len(keys), 4)]
        for gi, g in enumerate(groups):
            sel = g[1:3] if len(g) >= 4 else g
            for k in sel:
                out[f"{slot}{gi if len(groups) > 1 else ''}:{k}"] = mod.PAL[k]
    return out


def rim_hex():
    d, ramp, i = dp.NIGHT_RIM
    return dp.DISTRICTS[d][ramp][i]


def is_dark_floor(d):
    return contrast(OUTLINE, dp.DISTRICTS[d]["floor"][dp.FLOOR_MID]) < MIN_CONTRAST


def coverage(mod, floor_hex):
    """Share of a sprite's body pixels (idle S frame 0, outline excluded) with >= 3:1 against a floor."""
    fr = mod.IDLE["s"][0]
    px = [mod.PAL[ch] for r in fr for ch in r if ch not in ".o"]
    return sum(contrast(h, floor_hex) >= MIN_CONTRAST for h in px) / len(px)


MIN_COVERAGE = 0.45


def floor_rows(cast):
    """Per district and sprite: (outline contrast vs steps 2 and 3, worst mid tone, #mid tones < 3:1)."""
    rows = []
    for d, pal in dp.DISTRICTS.items():
        fl = pal["floor"]
        floors = (fl[dp.FLOOR_MID], fl[dp.FLOOR_FILL])
        for name, mod in cast.items():
            mt = mid_tones(mod)
            worst = min(((min(contrast(h, f) for f in floors), k) for k, h in mt.items()))
            low = sum(1 for h in mt.values() if min(contrast(h, f) for f in floors) < MIN_CONTRAST)
            rows.append(dict(district=d, sprite=name,
                             cov=coverage(mod, fl[dp.FLOOR_FILL]), cov_mid=coverage(mod, fl[dp.FLOOR_MID]),
                             outline=min(contrast(OUTLINE, f) for f in floors),
                             rim=min(contrast(rim_hex(), f) for f in floors),
                             worst=worst[0], worst_key=worst[1], low=low, n=len(mt)))
    return rows


# ------------------------------------------------------------------ cast ramps

def hair_skin_gaps(hair, skin):
    """L* gaps for the contacts a head has: hair fill steps B C D against skin fill steps l m n."""
    gaps = {}
    for (hi, hh), (si, sh) in itertools.product(enumerate(hair), enumerate(skin)):
        if hi >= 1 and si >= 1:
            gaps[("ABCD"[hi], "klmn"[si])] = abs(lab(hh)[0] - lab(sh)[0])
    return gaps


# ------------------------------------------------------------------ the checks

def run(verbose=True):
    fails, info = [], []
    out = print if verbose else (lambda *a, **k: None)

    # (d) shared ramps
    for d, pal in dp.DISTRICTS.items():
        for shared, ref in (("ink", dp.INK), ("violet", dp.VIOLET)):
            if pal[shared] != ref:
                fails.append(f"(d) {d}: {shared} ramp differs from the shared ramp")
        for name, steps in pal.items():
            if len(steps) != 4 or len(set(steps)) != 4:
                fails.append(f"(d) {d}.{name}: needs 4 distinct steps")
            if list(steps) != sorted(steps, key=lambda h: lab(h)[0]) and name not in ("violet",):
                fails.append(f"(d) {d}.{name}: steps are not ordered shadow -> light by lightness")
    if set(dp.DISTRICTS) != {"orientation", "records", "systems", "nightshift", "executive"}:
        fails.append("(d) district set is not the five districts")
    for d, pal in dp.DISTRICTS.items():
        if tuple(pal) != dp.ROLES:
            fails.append(f"(d) {d}: ramps are {tuple(pal)}, expected {dp.ROLES}")

    # (g) violet-family guard: floors and walls must never sit in the glitch hue range
    out("\n(g) Violet-family guard (hue 260-320 and saturation > 12% forbidden on floor and wall); floor mid dE from #9477AF")
    for d, pal in dp.DISTRICTS.items():
        for name in ("floor", "wall"):
            for i, h in enumerate(pal[name]):
                hue, sat, _ = hsl(h)
                if 260 <= hue <= 320 and sat > 12:
                    fails.append(f"(g) {d}.{name}[{i}] {h} is violet-family (hue {hue:.0f}, {sat:.0f}% saturation)")
        out(f"  {dp.NAMES[d]:12} floor mid {pal['floor'][dp.FLOOR_MID]}  dE {de(pal['floor'][dp.FLOOR_MID], '#9477AF'):5.1f}")

    # (f) adjacent steps stay distinguishable
    for d, pal in dp.DISTRICTS.items():
        for name, steps in pal.items():
            for i in range(3):
                if de(steps[i], steps[i + 1]) < 8 and d != "orientation":
                    fails.append(f"(f) {d}.{name}[{i}->{i + 1}] only dE {de(steps[i], steps[i + 1]):.1f}")

    # (a) markers and (b) teal saturation, per district
    marker_hexes = dp.MARKERS.values()
    pools = {d: dict(pal) for d, pal in dp.DISTRICTS.items()}
    pools["orientation"].update(dp.ORIENTATION_EXTRA)
    for d, pal in pools.items():
        bucket = info if d == "orientation" else fails
        for name, i, h in ramp_steps(pal):
            for mk, mh in dp.MARKERS.items():
                if name == "violet":
                    if h.upper() == dp.MARKERS["violet"].upper():
                        fails.append(f"(a) {d}.violet[{i}] {h} equals the violet marker")
                    continue
                dist = de(h, mh)
                if h.upper() == mh.upper() or dist < MIN_DE_MARKER:
                    bucket.append(f"(a) {d}.{name}[{i}] {h} is dE {dist:.1f} from the {mk} marker {mh}")
            if name not in dp.DEVICE_RAMPS.get(d, ()):
                hue, sat, _ = hsl(h)
                if 160 <= hue <= 200 and sat > 60:
                    bucket.append(f"(b) {d}.{name}[{i}] {h} teal-hued at {sat:.0f}% saturation")
        # glitch-family separation: nothing else should be mistaken for the violet ramp
        for name, i, h in ramp_steps({k: v for k, v in pal.items() if k != "violet"}):
            for vi, vh in enumerate(dp.VIOLET):
                if de(h, vh) < 8 and name != "ink":
                    bucket.append(f"(a2) {d}.{name}[{i}] {h} is dE {de(h, vh):.1f} from violet[{vi}] (glitch family)")

    # (c) floor contrast
    cast = dp.existing_cast()
    rows = floor_rows(cast)
    out("\n(c) Floor contrast: person outline #202337, rim, and cast mid tones vs floor steps 2 and 3 (WCAG ratio)")
    out(f"{'district':12} {'sprite':9} {'outline':>8} {'rim':>6} {'worst mid':>10} {'mid<3:1':>8} {'body px>=3:1 fill/mid':>22}")
    for r in rows:
        out(f"{dp.NAMES[r['district']]:12} {r['sprite']:9} {r['outline']:8.2f} {r['rim']:6.2f} "
            f"{r['worst']:7.2f} ({r['worst_key']:10}) {r['low']}/{r['n']}  {r['cov'] * 100:6.0f}% / {r['cov_mid'] * 100:3.0f}%")
        bucket = info if r["district"] == "orientation" else fails
        if is_dark_floor(r["district"]):
            if r["rim"] < MIN_CONTRAST:
                bucket.append(f"(c) {r['district']}: rim {rim_hex()} only {r['rim']:.2f}:1 against the floor")
        else:
            if r["outline"] < MIN_CONTRAST:
                bucket.append(f"(c) {r['district']}: outline only {r['outline']:.2f}:1 against the floor")
            if r["cov"] < MIN_COVERAGE:
                bucket.append(f"(c) {r['district']} {r['sprite']}: only {r['cov'] * 100:.0f}% of body pixels reach 3:1 on the floor fill")
    for d, pal in dp.DISTRICTS.items():
        if not is_dark_floor(d):
            continue
        pool = pal["accent"][1]  # lamp pool: accent step 1 is the pool floor, step 0 its edge
        for name, mod in cast.items():
            if contrast(OUTLINE, pool) < MIN_CONTRAST:
                fails.append(f"(c) {d}: person outline only {contrast(OUTLINE, pool):.2f}:1 inside a lamp pool")
        sh = contrast(pal["floor"][0], pal["floor"][dp.FLOOR_FILL])
        out(f"\n(c) {dp.NAMES[d]} edge-light rule: rim {rim_hex()} vs floor fill {contrast(rim_hex(), pal['floor'][dp.FLOOR_FILL]):.2f}:1, "
            f"outline in a lamp pool ({pool}) {contrast(OUTLINE, pool):.2f}:1, shadow step vs fill {sh:.2f}:1")
        if sh < 1.3:
            fails.append(f"(c) {d}: contact-shadow step (floor[0]) only {sh:.2f}:1 against the floor fill")
    for d in dp.DISTRICTS:
        want_dark = d == "nightshift"
        if is_dark_floor(d) != want_dark:
            fails.append(f"(c) {d}: floor should be {'dark (edge-light rule)' if want_dark else 'light (outline carries)'}")

    # (e) cast ramps
    allc = dp.all_cast_ramps()
    out("\n(e) Cast ramps: dE between corresponding steps (min over the other six)")
    out(f"{'':9}" + "".join(f"{s:>8}" for s in ("hair B", "hair C", "skin l", "skin m")))
    for name in dp.CAST_ORDER:
        cells = []
        for slot, idx in (("hair", 1), ("hair", 2), ("skin", 1), ("skin", 2)):
            m = min(de(allc[name][slot][idx], allc[o][slot][idx]) for o in dp.CAST_ORDER if o != name)
            cells.append(m)
            if name in dp.CAST_RAMPS and m < MIN_DE_CAST:
                fails.append(f"(e) {name}.{slot}[{idx}] only dE {m:.1f} from another cast member")
        out(f"{name:9}" + "".join(f"{c:8.1f}" for c in cells))
    for name in dp.CAST_RAMPS:
        for slot in ("hair", "skin"):
            steps = allc[name][slot]
            if sorted(steps, key=lambda h: lab(h)[0]) != list(steps):
                fails.append(f"(e) {name}.{slot} is not ordered shadow -> light")
            for i, h in enumerate(steps):
                for mk, mh in dp.MARKERS.items():
                    if de(h, mh) < MIN_DE_MARKER:
                        fails.append(f"(e) {name}.{slot}[{i}] {h} within dE {de(h, mh):.1f} of the {mk} marker")
                if any(de(h, v) < 8 for v in dp.VIOLET):
                    fails.append(f"(e) {name}.{slot}[{i}] {h} reads as violet")
        # nobody wears violet-hued hair or skin
    out("\n(e) Hair against skin: smallest L* gap between a hair fill step (B C D) and a skin fill step (l m n)")
    for name in dp.CAST_ORDER:
        g = hair_skin_gaps(allc[name]["hair"], allc[name]["skin"])
        k, v = min(g.items(), key=lambda kv: kv[1])
        sep = getattr(dp.existing_cast().get(name), "HAIR_SKIN_SEPARATED", False)
        ok = v >= MIN_DL_HAIR_SKIN
        out(f"  {name:9} min {k[0]}-{k[1]} gap {v:5.1f}  {'ok' if ok else ('documented separator pixel' if sep else 'approved sprite: frame keys keep them apart') if name not in dp.CAST_RAMPS else 'separator pixel rule applies'}")
        if name in dp.CAST_RAMPS and not ok:
            info.append(f"(e) {name}: hair {k[0]} vs skin {k[1]} only {v:.1f} L*; separator pixel rule applies")
    # at 1x: skin and hair must read as different people, so no new character may match an
    # existing one on both ramps at once
    for a, b in itertools.combinations(dp.CAST_ORDER, 2):
        dh = de(allc[a]["hair"][2], allc[b]["hair"][2])
        ds = de(allc[a]["skin"][2], allc[b]["skin"][2])
        if min(dh, ds) < MIN_DE_CAST and (a in dp.CAST_RAMPS or b in dp.CAST_RAMPS):
            fails.append(f"(e) {a}/{b}: hair dE {dh:.1f}, skin dE {ds:.1f}")

    out("")
    for line in info:
        out("INFO", line)
    for line in fails:
        out("FAIL", line)
    out(f"{len(fails)} failures, {len(info)} informational notes")
    return fails, info


if __name__ == "__main__":
    f, _ = run()
    sys.exit(1 if f else 0)
