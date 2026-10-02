"""Objective glitch-sprite checks. Exit code 1 on any failure.

Run: python3 check_glitches.py      (stdlib only)
Rules (STYLE_BIBLE 3, 7 and GLITCHES_SPEC.md):
  frame      every frame is the archetype's size, a multiple of 16, within 16-32 px;
             no opaque pixel on the left, right or top border (no clipping)
  palette    only the allowed hexes, no UI marker hex, violet only from the 4-step ramp
  contour    every opaque pixel that touches transparency (or the frame edge) is an
             outline or dark step; the darkest violet never fills an interior (all 8 neighbours violet)
  glow       glow pixels (c, d) never touch transparency, so the glow can't erase the
             silhouette; at most two glow steps; a per-frame glow limit
  violet     present in every glitch frame (roam, misregister, repaired); absent from every ordinary prop
  read       the rest frames of the three archetypes differ in greyscale at 1x: a different
             silhouette (overlap <= 0.45 aligned at the base) or a housing luma gap of 0.15
  repaired   exactly one snap frame per archetype, distinct from the roam rest, both misregister frames and the
             ordinary prop; its housing is the ordinary prop's (violet may only replace a few pixels)
  ordinary   exactly one static frame per archetype, no violet and no glow, same size and anchor;
             a blocking collision cell contains opaque pixels
  anchor     base_bc (w/2, h) in the sprite table and in the atlas JSON (archetype and ordinary entry)
  mirror     no glitch frame is mirror-symmetric (never flippable); the chair's ordinary prop is
             symmetric by construction and the atlas says flippable false
  variants   palette variants: four steps in the violet hue band, same lightness order, clear of every UI marker,
             never #9876D5, distinct from the standard ramp; dark_steps keep their contrast on the Night Shift floor.
             Behaviours: roam_ms and holds are multiples of the 40 ms tick, frame indices exist, paths are known
  districts  the five district ids, valid archetypes / palettes / behaviours, first glitch consistent, intensity ramp
             calm -> uncanny -> peak -> quiet -> relief, chair recolour from the district ramp; the table in
             GLITCHES_SPEC.md and the atlas JSON on disk agree with glitch_variants.py
"""
import colorsys
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import glitch_sprites as G  # noqa: E402
import glitch_variants as V  # noqa: E402

ALLOWED = {
    "#202337", "#343650", "#535971", "#777A8C",              # ink / outline ramp
    "#413755", "#67547C", "#9477AF", "#C3A6D6",              # violet, glitches only
    "#C7B7A0", "#E2D6C2", "#F4F2EC",                          # stone + paper ramp (folded form)
    "#B65761", "#E67A70", "#F6B18E",                          # coral chair upholstery (the room's chairs)
}
GLOW_LIMIT = {16: 12, 32: 20}     # glow px per frame by frame width
HOT_LIMIT = 4                     # px of the brightest step "d"
MIN_SNAP_DIFF_ROAM = 12           # px by which the snap frame differs from the roam rest frame
MIN_SNAP_DIFF_ORDINARY = 6        # ... and from the ordinary prop
MIN_SNAP_VIOLET = 8               # violet px in the snap frame, so it reads at x4
HOUSING_SLACK = 12                # interior housing px the snap's violet may replace (the slot, the crease)
FRAME_COUNT = {"roam": (2, 4), "misregister": (1, 2), "repaired": (1, 1), "ordinary": (1, 1)}
TICK = 40
fails = []


def luma(hexs):
    r, g, b = (int(hexs[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def check_palette():
    used = {v for v in G.PAL.values() if v}
    if used - ALLOWED:
        fails.append(f"palette: hexes outside the allowed set {sorted(used - ALLOWED)}")
    if used & G.UI_MARKERS:
        fails.append(f"palette: UI marker hex {sorted(used & G.UI_MARKERS)}")
    violet = {G.PAL[k] for k in G.VIOLET_KEYS}
    if violet != {"#413755", "#67547C", "#9477AF", "#C3A6D6"}:
        fails.append("palette: violet keys are not the four-step anomaly ramp")
    if len(G.GLOW_KEYS) > 2:
        fails.append("glow: more than two glow steps")


def neighbours(fr, x, y):
    h, w = len(fr), len(fr[0])
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        yield (fr[ny][nx] if 0 <= nx < w and 0 <= ny < h else ".")


def neighbours8(fr, x, y):
    h, w = len(fr), len(fr[0])
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                nx, ny = x + dx, y + dy
                yield (fr[ny][nx] if 0 <= nx < w and 0 <= ny < h else ".")


def check_frame(name, fr, w, h, lift=0, ordinary=False):
    if len(fr) != h or any(len(r) != w for r in fr):
        fails.append(f"{name}: not {w}x{h}")
        return
    if any(r[0] != "." or r[-1] != "." for r in fr) or any(ch != "." for ch in fr[0]):
        fails.append(f"{name}: opaque pixel on the left, right or top border")
    if lift <= 1 and all(ch == "." for ch in fr[h - 1]) and all(ch == "." for ch in fr[h - 2]):
        fails.append(f"{name}: nothing rests on the bottom two rows")
    glow = hot = violet = 0
    for y, row in enumerate(fr):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if ch not in G.PAL:
                fails.append(f"{name}: unknown key {ch!r}")
                continue
            touches_clear = "." in neighbours(fr, x, y)
            if touches_clear and ch not in G.CONTOUR_KEYS and ch != "b":
                fails.append(f"{name}: ({x},{y}) {ch!r} on the silhouette is not an outline/dark step")
            if ch == "b" and touches_clear and _violet_block(fr, x, y):
                fails.append(f"{name}: ({x},{y}) violet fill on the silhouette (a ghost outline is 1 px)")
            if ch in G.GLOW_KEYS:
                glow += 1
                if touches_clear:
                    fails.append(f"{name}: ({x},{y}) glow {ch!r} touches transparency")
            if ch == "d":
                hot += 1
            if ch in G.VIOLET_KEYS:
                violet += 1
            if ch == "a" and all(n in G.VIOLET_KEYS for n in neighbours8(fr, x, y)):
                fails.append(f"{name}: ({x},{y}) darkest violet used as interior fill")
    if ordinary:
        if violet:
            fails.append(f"{name}: {violet} violet px in an ordinary prop (violet is for the glitch states only)")
    elif not violet:
        fails.append(f"{name}: no violet in the frame")
    if glow > GLOW_LIMIT[w]:
        fails.append(f"{name}: {glow} glow px (limit {GLOW_LIMIT[w]})")
    if hot > HOT_LIMIT:
        fails.append(f"{name}: {hot} hot px (limit {HOT_LIMIT})")
    return glow


def _violet_block(fr, x, y):
    """True when (x, y) belongs to a 2x2 block of violet pixels: a fill, not a 1 px ghost line."""
    h, w = len(fr), len(fr[0])
    for ox in (-1, 0):
        for oy in (-1, 0):
            cells = [(x + ox + i, y + oy + j) for i in (0, 1) for j in (0, 1)]
            if all(0 <= cx < w and 0 <= cy < h and fr[cy][cx] in G.VIOLET_KEYS for cx, cy in cells):
                return True
    return False


def signature(fr):
    """Housing silhouette (the object without its violet cue), bounding box and housing luma of a rest frame."""
    allp = {(x, y) for y, r in enumerate(fr) for x, ch in enumerate(r) if ch != "." and ch not in "abcd"}
    xs = [p[0] for p in allp]
    ys = [p[1] for p in allp]
    w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
    pts = [G.PAL[ch] for r in fr for ch in r if ch != "." and ch not in "abcd"]
    mean = sum(luma(p) for p in pts) / len(pts)
    return {"w": w, "h": h, "luma": mean, "mask": allp, "cx": (max(xs) + min(xs)) / 2, "bottom": max(ys)}


def iou(a, b):
    """Silhouette overlap with the two aligned at bottom centre (how they sit on the floor)."""
    ma = {(round(x - a["cx"]), y - a["bottom"]) for x, y in a["mask"]}
    mb = {(round(x - b["cx"]), y - b["bottom"]) for x, y in b["mask"]}
    return len(ma & mb) / len(ma | mb)


def diff(a, b):
    return sum(pa != pb for ra, rb in zip(a, b) for pa, pb in zip(ra, rb))


def mirrored(fr):
    return [r[::-1] for r in fr]


# ------------------------------------------------------------------ repaired and ordinary

def check_states(arch, d, w, h):
    g = d["grid"]
    rest, rep, ordi = g["roam"][0], g["repaired"][0], g["ordinary"][0]
    # the snap frame must read as neither a roam frame nor the ordinary prop
    if diff(rep, rest) < MIN_SNAP_DIFF_ROAM:
        fails.append(f"{arch}_repaired: only {diff(rep, rest)} px from the roam rest frame (need {MIN_SNAP_DIFF_ROAM})")
    if diff(rep, ordi) < MIN_SNAP_DIFF_ORDINARY:
        fails.append(f"{arch}_repaired: only {diff(rep, ordi)} px from the ordinary prop (need {MIN_SNAP_DIFF_ORDINARY})")
    for i, fr in enumerate(g["misregister"]):
        if rep == fr:
            fails.append(f"{arch}_repaired: identical to misregister frame {i}")
    for i, fr in enumerate(g["roam"]):
        if rep == fr:
            fails.append(f"{arch}_repaired: identical to roam frame {i}")
    violet = sum(ch in G.VIOLET_KEYS for r in rep for ch in r)
    if violet < MIN_SNAP_VIOLET:
        fails.append(f"{arch}_repaired: only {violet} violet px (need {MIN_SNAP_VIOLET} to read at x4)")
    # housing: the snap's non-violet pixels are the ordinary prop's; violet may replace only a few housing pixels
    wrong, replaced, on_edge = 0, 0, 0
    for y, (ry, oy_) in enumerate(zip(rep, ordi)):
        for x, (pr, po) in enumerate(zip(ry, oy_)):
            if pr not in G.VIOLET_KEYS and pr != po:
                wrong += 1
            if pr in G.VIOLET_KEYS and po != ".":
                replaced += 1
                if "." in neighbours(ordi, x, y):
                    on_edge += 1
    if wrong:
        fails.append(f"{arch}_repaired: {wrong} non-violet pixels differ from the ordinary prop (the snap is the prop plus violet)")
    if on_edge:
        fails.append(f"{arch}_repaired: violet covers {on_edge} pixels of the ordinary prop's silhouette edge (violet never covers the silhouette)")
    if replaced > HOUSING_SLACK:
        fails.append(f"{arch}_repaired: violet replaces {replaced} interior housing pixels (limit {HOUSING_SLACK})")
    # ordinary: no violet / glow is covered by check_frame; the key set must be office colours only
    keys = {ch for r in ordi for ch in r} - {"."}
    if keys & set(G.VIOLET_KEYS):
        fails.append(f"{arch}_ordinary: uses violet keys {sorted(keys & set(G.VIOLET_KEYS))}")
    # collision: one string per footprint row, one char per cell; a blocking cell must hold pixels
    fw, fh = g["footprint"]
    col = d["ordinary"]["collision"]
    if len(col) != fh or any(len(r) != fw or set(r) - {"0", "1"} for r in col):
        fails.append(f"{arch}_ordinary: collision {col} does not match the {fw}x{fh} footprint")
    else:
        for cy, row in enumerate(col):
            for cx, c in enumerate(row):
                if c == "1" and not any(ordi[y][x] != "." for y in range(cy * 16, cy * 16 + 16)
                                        for x in range(cx * 16, cx * 16 + 16)):
                    fails.append(f"{arch}_ordinary: collision blocks cell ({cx},{cy}) that holds no pixels")
    # anchor
    if tuple(d["anchor"]) != (w // 2, h):
        fails.append(f"{arch}: anchor {d['anchor']} is not base_bc ({w // 2}, {h})")
    # never mirrored: every glitch frame has a left/right asymmetry; the chair's ordinary prop is symmetric
    for kind in ("roam", "misregister", "repaired", "ordinary"):
        for i, fr in enumerate(g[kind]):
            if fr == mirrored(fr) and not (arch == "chair" and kind == "ordinary"):
                fails.append(f"{arch}_{kind}_{i}: mirror-symmetric, so a flipped copy would be indistinguishable")


# ------------------------------------------------------------------ colour maths for the variants

def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rel_lum(h):
    r, g, b = (_lin(c) for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((rel_lum(a), rel_lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


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


def hls(h):
    return colorsys.rgb_to_hls(*(c / 255 for c in rgb(h)))


def check_variants():
    markers = V.dp.MARKERS
    std = V.PALETTE_VARIANTS["standard"]
    if std["steps"] != V.STANDARD_VIOLET or std["steps"] != [G.PAL[k] for k in "abcd"]:
        fails.append("variants: the standard variant is not the ramp the sprites are drawn in")
    if set(V.PALETTE_VARIANTS) != {"standard", "plum", "dusk"}:
        fails.append(f"variants: palette ids {sorted(V.PALETTE_VARIANTS)}")
    if {v["duel"] for v in V.PALETTE_VARIANTS.values()} != {"token", "route", "code"}:
        fails.append("variants: the three palettes must signal the three duel kinds (token, route, code)")
    dark_floor_ok = {}
    for vid, v in V.PALETTE_VARIANTS.items():
        for key in ("steps", "dark_steps"):
            steps = v[key]
            if len(steps) != 4 or len(set(steps)) != 4:
                fails.append(f"variants: {vid}.{key} must be four distinct steps")
                continue
            ls = [rel_lum(s) for s in steps]
            if ls != sorted(ls):
                fails.append(f"variants: {vid}.{key} is not ordered dark to light")
            for s in steps:
                hue = hls(s)[0] * 360
                if not V.VIOLET_HUE_BAND[0] <= hue <= V.VIOLET_HUE_BAND[1]:
                    fails.append(f"variants: {vid}.{key} {s} hue {hue:.0f} is outside the violet band {V.VIOLET_HUE_BAND}")
                if s.upper() == markers["violet"].upper():
                    fails.append(f"variants: {vid}.{key} uses the UI marker #9876D5")
                for mk, mh in markers.items():
                    if de(s, mh) < V.MIN_DE_MARKER:
                        fails.append(f"variants: {vid}.{key} {s} is dE {de(s, mh):.1f} from the {mk} marker (need {V.MIN_DE_MARKER})")
            if len({c for c in steps} & ALLOWED - set(V.STANDARD_VIOLET)):
                fails.append(f"variants: {vid}.{key} collides with an office colour")
        if vid != "standard":
            for i in (1, 2):   # the fill and the glow step must be distinguishable from the standard ramp
                if de(v["steps"][i], std["steps"][i]) < V.MIN_DE_VARIANT:
                    fails.append(f"variants: {vid} step {i} is only dE {de(v['steps'][i], std['steps'][i]):.1f} from standard")
    names = list(V.PALETTE_VARIANTS)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            for k in (1, 2):
                a, b = V.PALETTE_VARIANTS[names[i]]["steps"][k], V.PALETTE_VARIANTS[names[j]]["steps"][k]
                if de(a, b) < V.MIN_DE_VARIANT:
                    fails.append(f"variants: {names[i]} and {names[j]} step {k} are only dE {de(a, b):.1f} apart")
    for vid, v in V.PALETTE_VARIANTS.items():
        b, c = v["dark_steps"][1], v["dark_steps"][2]
        got = (contrast(b, V.DARK_FLOORS["fill"]), contrast(b, V.DARK_FLOORS["mid"]), contrast(c, V.DARK_FLOORS["fill"]))
        need = (V.DARK_MIN_CONTRAST["fill_b"], V.DARK_MIN_CONTRAST["mid_b"], V.DARK_MIN_CONTRAST["fill_c"])
        if any(a < n for a, n in zip(got, need)):
            fails.append(f"variants: {vid}.dark_steps contrast on the Night Shift floor {[round(x, 2) for x in got]} < {list(need)}")
        dark_floor_ok[vid] = [round(x, 2) for x in got]
    return dark_floor_ok


def check_behaviours():
    arch_frames = {a: len(d["grid"]["misregister"]) for a, d in G.ARCHETYPES.items()}
    for bid, b in V.BEHAVIOURS.items():
        if set(b["roam_ms"]) != set(G.ARCHETYPES):
            fails.append(f"behaviours: {bid}.roam_ms must list {sorted(G.ARCHETYPES)}")
        for a, ms in b["roam_ms"].items():
            if ms % TICK or not 80 <= ms <= 400:
                fails.append(f"behaviours: {bid}.roam_ms[{a}] = {ms} is not a multiple of {TICK} in 80-400")
        p = b["path"]
        if p["shape"] not in ("hover", "line", "edge") or p["lane_px"] % 4 or p["lane_px"] < 16:
            fails.append(f"behaviours: {bid}.path {p} (shape hover|line|edge, lane_px a multiple of 4, at least 16)")
        pa = b["pause"]
        if pa is not None and (not isinstance(pa["after_cycles"], int) or pa["after_cycles"] < 1 or pa["hold_ms"] % TICK):
            fails.append(f"behaviours: {bid}.pause {pa} (whole cycles, hold in {TICK} ms ticks)")
        m = b["misregister"]
        if m["amplitude"] not in V.AMPLITUDE_FRAMES:
            fails.append(f"behaviours: {bid}.misregister.amplitude {m['amplitude']!r}")
        else:
            for a, n in arch_frames.items():
                if max(V.AMPLITUDE_FRAMES[m["amplitude"]]) >= n:
                    fails.append(f"behaviours: {bid} amplitude {m['amplitude']} uses a misregister frame {a} does not have")
        ev = m["every_ms"]
        if ev is not None and (len(ev) != 2 or ev[0] >= ev[1] or any(x % TICK for x in ev)):
            fails.append(f"behaviours: {bid}.misregister.every_ms {ev}")
        if m["on_pause"] and pa is None:
            fails.append(f"behaviours: {bid} misregisters on pause but never pauses")
        if b["tone"] not in ("calm", "uncanny", "quiet", "relief"):
            fails.append(f"behaviours: {bid}.tone {b['tone']!r}")
    if any(max(V.CONTACT_FRAMES) >= n for n in arch_frames.values()):
        fails.append("behaviours: contact frames index a missing misregister frame")


# ------------------------------------------------------------------ districts

DISTRICT_IDS = ["orientation", "records", "systems", "nightshift", "executive"]
RAMP = [("orientation", 1, "calm"), ("records", 2, "uncanny"), ("systems", 3, "uncanny"),
        ("nightshift", 4, "quiet"), ("executive", 1, "relief")]
DUEL_OF_PALETTE = {"standard": "token", "plum": "route", "dusk": "code"}


def check_districts():
    if list(V.DISTRICTS) != DISTRICT_IDS:
        fails.append(f"districts: ids {list(V.DISTRICTS)} must be {DISTRICT_IDS} in story order")
        return
    prev_end = 0
    for did, intensity, tone in RAMP:
        d = V.DISTRICTS[did]
        if d["intensity"] != intensity or d["tone"] != tone:
            fails.append(f"districts: {did} intensity/tone {d['intensity']}/{d['tone']} must be {intensity}/{tone} (calm -> uncanny -> peak -> quiet -> relief)")
        lo, hi = d["levels"]
        if lo != prev_end + 1 or hi < lo:
            fails.append(f"districts: {did} levels {d['levels']} do not follow the previous district")
        prev_end = hi
        if bool(d.get("dark_floor")) != (did == "nightshift"):
            fails.append(f"districts: {did}.dark_floor must be true for Night Shift only")
        arch = d["archetypes"]
        if not arch or set(arch) - set(G.ARCHETYPES):
            fails.append(f"districts: {did} archetypes {sorted(arch)}")
            continue
        if d["max_per_room"] < 1:
            fails.append(f"districts: {did}.max_per_room")
        pal_used = {p for a in arch.values() for p in a["palettes"]}
        beh_used = {b for a in arch.values() for b in a["behaviours"]}
        if pal_used - set(V.PALETTE_VARIANTS) or beh_used - set(V.BEHAVIOURS):
            fails.append(f"districts: {did} names an unknown palette or behaviour")
        if set(d["palette_from_level"]) != pal_used or set(d["behaviour_from_level"]) != beh_used:
            fails.append(f"districts: {did} palette_from_level / behaviour_from_level must list exactly the palettes and behaviours in use")
        for table in ("palette_from_level", "behaviour_from_level"):
            for k, lv in d[table].items():
                if not lo <= lv <= hi:
                    fails.append(f"districts: {did}.{table}[{k}] = {lv} is outside levels {lo}-{hi}")
        for a, e in arch.items():
            if not lo <= e["from_level"] <= hi:
                fails.append(f"districts: {did}.{a}.from_level {e['from_level']} is outside levels {lo}-{hi}")
        fg = d["first_glitch"]
        earliest = min(e["from_level"] for e in arch.values())
        if fg["level"] != earliest:
            fails.append(f"districts: {did}.first_glitch.level {fg['level']} is not the earliest from_level {earliest}")
        e = arch.get(fg["archetype"])
        if not e or fg["palette"] not in e["palettes"] or fg["behaviour"] not in e["behaviours"] or fg["level"] < e["from_level"]:
            fails.append(f"districts: {did}.first_glitch {fg} is not allowed by the archetype's own entry")
        elif d["palette_from_level"][fg["palette"]] > fg["level"] or d["behaviour_from_level"][fg["behaviour"]] > fg["level"]:
            fails.append(f"districts: {did}.first_glitch uses a palette or behaviour held back past its level")
        for q in d["quiet_levels"]:
            if not lo <= q < fg["level"]:
                fails.append(f"districts: {did} quiet level {q} must come before the first glitch (level {fg['level']})")
        for a, e in arch.items():
            for p in e["palettes"]:
                if d["palette_from_level"][p] > hi:
                    fails.append(f"districts: {did}.{a} palette {p} never appears")
        # each behaviour's tone belongs to the district's tone
        for b in beh_used:
            bt = V.BEHAVIOURS[b]["tone"]
            ok = {"calm": {"calm"}, "uncanny": {"calm", "uncanny"}, "quiet": {"quiet", "uncanny"}, "relief": {"relief"}}[tone]
            if bt not in ok:
                fails.append(f"districts: {did} ({tone}) allows behaviour {b} of tone {bt}")
        # chair recolour: coral steps 1..3 become steps 1..3 of the district ramp named in glitch_variants
        sw = V.chair_swap(did)
        if did == "orientation":
            if sw:
                fails.append("districts: orientation keeps the coral chair (no swap)")
        else:
            ramp = V.dp.DISTRICTS[did][V.CHAIR_RAMP[did]]
            if list(sw.keys()) != V.CHAIR_SWAP_FROM or list(sw.values()) != ramp[1:4]:
                fails.append(f"districts: {did} chair swap is not coral 1..3 -> {V.CHAIR_RAMP[did]} 1..3")
    # the level designers' anchors from levels.md
    o = V.DISTRICTS["orientation"]
    fg = o["first_glitch"]
    if (fg["level"], fg["archetype"], fg["behaviour"]) != (1, "form", "drift") or "chair" in o["archetypes"]:
        fails.append("districts: Orientation's first glitch must be level 01's harmless paper-fold (form, drift), with no chair shadow")
    ns = V.DISTRICTS["nightshift"]
    if 17 not in ns["quiet_levels"] or min(e["from_level"] for e in ns["archetypes"].values()) <= 17:
        fails.append("districts: Night Shift level 17 (safe break room) must hold no glitch")
    ex = V.DISTRICTS["executive"]
    br = ex.get("branches", {})
    if sorted(br.values()) != sorted(G.ARCHETYPES) or any(
            ex["archetypes"][a]["palettes"] != [p] for a, p in
            (("form", "standard"), ("chair", "plum"), ("stapler", "dusk"))):
        fails.append("districts: Executive needs one archetype per branch, each in the palette of its duel (token, route, code)")


# ------------------------------------------------------------------ spec and atlas agree with the data

def check_spec_and_atlas():
    spec_path = os.path.join(HERE, "GLITCHES_SPEC.md")
    with open(spec_path) as fh:
        spec = fh.read()
    m = re.search(r"<!-- districts:start -->(.*?)<!-- districts:end -->", spec, re.S)
    if not m:
        fails.append("spec: GLITCHES_SPEC.md has no <!-- districts:start --> ... <!-- districts:end --> table")
        return
    rows = {}
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        mm = re.match(r"`(\w+)`$", cells[0]) if cells else None
        if mm and len(cells) >= 6:
            rows[mm.group(1)] = cells
    for did, d in V.DISTRICTS.items():
        cells = rows.get(did)
        if not cells:
            fails.append(f"spec: district table has no row for `{did}`")
            continue
        text = " | ".join(cells)
        lo, hi = d["levels"]
        want = [f"L{lo}-{hi}" if lo != hi else f"L{lo}", d["tone"], f"intensity {d['intensity']}", f"max {d['max_per_room']}"]
        fg = d["first_glitch"]
        want.append(f"L{fg['level']:02d} {fg['archetype']} {fg['palette']} {fg['behaviour']}")
        for a, e in d["archetypes"].items():
            want.append(f"{a} from L{e['from_level']:02d}")
            want += [f"`{p}`" for p in e["palettes"]] + [f"`{b}`" for b in e["behaviours"]]
        for t in want:
            if t not in text:
                fails.append(f"spec: row `{did}` is missing {t!r}")
        absent = set(G.ARCHETYPES) - set(d["archetypes"])
        for a in absent:
            if re.search(rf"\b{a} from L", text):
                fails.append(f"spec: row `{did}` lists {a}, which the data does not allow")
    for vid, v in V.PALETTE_VARIANTS.items():
        for hexs in v["steps"] + v["dark_steps"]:
            if hexs not in spec:
                fails.append(f"spec: palette variant {vid} step {hexs} is not in GLITCHES_SPEC.md")
    for bid, b in V.BEHAVIOURS.items():
        if f"`{bid}`" not in spec:
            fails.append(f"spec: behaviour `{bid}` is not in GLITCHES_SPEC.md")
        for a, ms in b["roam_ms"].items():
            if str(ms) not in spec:
                fails.append(f"spec: behaviour `{bid}` roam_ms {ms} is not in GLITCHES_SPEC.md")
    # the atlas JSON on disk must be the data (a stale build is a failure: rebuild with build_glitches.py)
    path = os.path.join(HERE, "glitches-atlas.json")
    if not os.path.exists(path):
        fails.append("atlas: glitches-atlas.json is missing (run build_glitches.py)")
        return
    with open(path) as fh:
        atlas = json.load(fh)
    if set(atlas.get("animations", {})) != {f"{a}_{k}" for a, k in G.ANIMATIONS}:
        fails.append("atlas: animations in glitches-atlas.json do not match the sprite table (stale build?)")
    for a, d in G.ARCHETYPES.items():
        w, h = d["grid"]["size"]
        arch = atlas.get("archetypes", {}).get(a)
        if not arch:
            fails.append(f"atlas: archetype {a} missing")
            continue
        for label, node in (("archetype", arch), ("ordinary", arch.get("ordinary", {}))):
            an = node.get("anchor", {})
            if (an.get("name"), an.get("x"), an.get("y")) != ("base_bc", w // 2, h):
                fails.append(f"atlas: {a} {label} anchor {an} is not base_bc ({w // 2}, {h})")
            if node.get("flippable") is not False:
                fails.append(f"atlas: {a} {label} must be flippable false")
        o = arch.get("ordinary", {})
        if o.get("collision") != d["ordinary"]["collision"] or o.get("footprint", {}).get("cells") != list(d["grid"]["footprint"]):
            fails.append(f"atlas: {a} ordinary footprint/collision do not match the sprite table")
        rep = atlas["animations"].get(f"{a}_repaired", {})
        if rep.get("frames") != 1 or rep.get("ms") != G.REPAIRED_MS or rep.get("loop") is not False or rep.get("play") != "once" \
                or rep.get("then") != f"{a}_ordinary":
            fails.append(f"atlas: {a}_repaired must be 1 frame, {G.REPAIRED_MS} ms, play once, then {a}_ordinary")
        if atlas["animations"].get(f"{a}_ordinary", {}).get("static") is not True:
            fails.append(f"atlas: {a}_ordinary must be static")
    av = atlas.get("variants", {})
    for vid, v in V.PALETTE_VARIANTS.items():
        e = av.get("palettes", {}).get(vid, {})
        if e.get("steps") != v["steps"] or e.get("dark_steps") != v["dark_steps"] or e.get("duel") != v["duel"]:
            fails.append(f"atlas: palette variant {vid} differs from glitch_variants.py (stale build?)")
        elif e.get("swap") != V.palette_swap(vid) or e.get("swap_dark") != V.palette_swap(vid, dark=True):
            fails.append(f"atlas: palette variant {vid} swap tables are wrong")
    for bid, b in V.BEHAVIOURS.items():
        e = av.get("behaviours", {}).get(bid, {})
        if e.get("roam_ms") != b["roam_ms"] or e.get("path") != b["path"] or e.get("pause") != b["pause"] \
                or e.get("misregister", {}).get("frames") != V.AMPLITUDE_FRAMES[b["misregister"]["amplitude"]] \
                or e.get("misregister", {}).get("every_ms") != b["misregister"]["every_ms"]:
            fails.append(f"atlas: behaviour {bid} differs from glitch_variants.py (stale build?)")
    ad = atlas.get("districts", {})
    for did, d in V.DISTRICTS.items():
        e = ad.get(did)
        if not e:
            fails.append(f"atlas: district {did} missing")
            continue
        for key in ("levels", "tone", "intensity", "max_per_room", "archetypes", "first_glitch", "palette_from_level",
                    "behaviour_from_level", "quiet_levels"):
            if e.get(key) != d[key]:
                fails.append(f"atlas: district {did}.{key} differs from glitch_variants.py (stale build?)")
        if e.get("chair_recolour") != V.chair_swap(did):
            fails.append(f"atlas: district {did}.chair_recolour is wrong")
        if e.get("palette_steps") != ("dark_steps" if d.get("dark_floor") else "steps"):
            fails.append(f"atlas: district {did}.palette_steps is wrong")


def main():
    check_palette()
    total, glow_max = 0, {}
    for arch, d in G.ARCHETYPES.items():
        w, h = d["grid"]["size"]
        if w % 16 or h % 16 or not (16 <= w <= 32 and 16 <= h <= 32):
            fails.append(f"{arch}: size {w}x{h} is not on the 16 px grid within 16-32")
        fw, fh = d["grid"]["footprint"]
        if (fw * 16, fh * 16) != (w, h):
            fails.append(f"{arch}: footprint {fw}x{fh} cells does not match the frame")
        for anim in G.KINDS:
            frs = d["grid"][anim]
            lo, hi = FRAME_COUNT[anim]
            if not lo <= len(frs) <= hi:
                fails.append(f"{arch} {anim}: {len(frs)} frames (need {lo}-{hi})")
            if len(set(map(tuple, frs))) != len(frs):
                fails.append(f"{arch} {anim}: duplicate frames")
            for i, fr in enumerate(frs):
                lift = d["roam"]["lift_px"][i] if anim == "roam" else 0
                g = check_frame(f"{arch}_{anim}_{i}", fr, w, h, lift, ordinary=anim == "ordinary")
                total += 1
                glow_max[arch] = max(glow_max.get(arch, 0), g or 0)
        if d["repaired"]["play"] != "once" or d["repaired"]["ms"] != G.REPAIRED_MS or G.REPAIRED_MS % TICK:
            fails.append(f"{arch}: the repaired frame must play once at {G.REPAIRED_MS} ms (a multiple of {TICK})")
        check_states(arch, d, w, h)
    # Misregister must differ from the roam rest frame by a 1-2 px offset only.
    for arch, d in G.ARCHETYPES.items():
        rest = d["grid"]["roam"][0]
        for i, fr in enumerate(d["grid"]["misregister"]):
            if diff(rest, fr) == 0:
                fails.append(f"{arch}_misregister_{i}: identical to the roam rest frame")
    # Greyscale read at 1x: the rest silhouettes must differ in size and overlap little.
    sigs = {a: signature(d["grid"]["roam"][0]) for a, d in G.ARCHETYPES.items()}
    names = list(sigs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            s1, s2 = sigs[names[i]], sigs[names[j]]
            o = iou(s1, s2)
            dl = abs(s1["luma"] - s2["luma"])
            if (o > 0.45 and dl < 0.15) or (abs(s1["w"] - s2["w"]) < 3 and abs(s1["h"] - s2["h"]) < 3 and dl < 0.15):
                fails.append(f"read: {names[i]} and {names[j]} are too alike (overlap {o:.2f}, "
                             f"{s1['w']}x{s1['h']} vs {s2['w']}x{s2['h']}, luma gap {dl:.2f})")
    dark = check_variants()
    check_behaviours()
    check_districts()
    check_spec_and_atlas()
    for f in fails:
        print("FAIL", f)
    print("rest silhouettes (w x h, housing luma):", {k: (f"{v['w']}x{v['h']}", round(v["luma"], 2)) for k, v in sigs.items()})
    print("pairwise overlap:", {f"{a}/{b}": round(iou(sigs[a], sigs[b]), 2) for i, a in enumerate(names) for b in names[i + 1:]})
    print("max glow px per archetype:", glow_max)
    print("snap frame px from the roam rest / the ordinary prop:",
          {a: (diff(d["grid"]["repaired"][0], d["grid"]["roam"][0]), diff(d["grid"]["repaired"][0], d["grid"]["ordinary"][0]))
           for a, d in G.ARCHETYPES.items()})
    print("dark_steps contrast on the Night Shift floor (b on fill, b on mid, c on fill):", dark)
    print(f"{total} frames checked, {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
