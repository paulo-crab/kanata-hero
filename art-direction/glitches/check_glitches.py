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
  violet     present in every frame (it is the anomaly cue)
  read       the rest frames of the three archetypes differ in greyscale at 1x: a different
             silhouette (overlap <= 0.45 aligned at the base) or a housing luma gap of 0.15
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glitch_sprites as G  # noqa: E402

ALLOWED = {
    "#202337", "#343650", "#535971", "#777A8C",              # ink / outline ramp
    "#413755", "#67547C", "#9477AF", "#C3A6D6",              # violet, glitches only
    "#C7B7A0", "#E2D6C2", "#F4F2EC",                          # stone + paper ramp (folded form)
    "#B65761", "#E67A70", "#F6B18E",                          # coral chair upholstery (the room's chairs)
}
GLOW_LIMIT = {16: 12, 32: 20}     # glow px per frame by frame width
HOT_LIMIT = 4                     # px of the brightest step "d"
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


def check_frame(name, fr, w, h, lift=0):
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
    if not violet:
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
        for anim in ("roam", "misregister"):
            frs = d["grid"][anim]
            lo, hi = (2, 4) if anim == "roam" else (1, 2)
            if not lo <= len(frs) <= hi:
                fails.append(f"{arch} {anim}: {len(frs)} frames (need {lo}-{hi})")
            if len(set(map(tuple, frs))) != len(frs):
                fails.append(f"{arch} {anim}: duplicate frames")
            for i, fr in enumerate(frs):
                lift = d["roam"]["lift_px"][i] if anim == "roam" else 0
                g = check_frame(f"{arch}_{anim}_{i}", fr, w, h, lift)
                total += 1
                glow_max[arch] = max(glow_max.get(arch, 0), g or 0)
    # Misregister must differ from the roam rest frame by a 1-2 px offset only.
    for arch, d in G.ARCHETYPES.items():
        rest = d["grid"]["roam"][0]
        for i, fr in enumerate(d["grid"]["misregister"]):
            diff = sum(a != b for ra, rb in zip(rest, fr) for a, b in zip(ra, rb))
            if diff == 0:
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
    for f in fails:
        print("FAIL", f)
    print("rest silhouettes (w x h, housing luma):", {k: (f"{v['w']}x{v['h']}", round(v["luma"], 2)) for k, v in sigs.items()})
    print("pairwise overlap:", {f"{a}/{b}": round(iou(sigs[a], sigs[b]), 2) for i, a in enumerate(names) for b in names[i + 1:]})
    print("max glow px per archetype:", glow_max)
    print(f"{total} frames checked, {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
