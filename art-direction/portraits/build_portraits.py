"""Build the portrait outputs: template sheet, character sheet, comparison, dialogue mock, atlas.

Run: python3 build_portraits.py   (needs Pillow + numpy)
Writes into this folder:
  portrait-template.png     construction guides on the standard chibi head, the seven head silhouettes, the notes
  portraits-sheet.png       one row per character: world sprite (S idle) at x4, then each expression at x4
  portraits-compare.png     one row per expression type, all seven characters (the personality check)
  portraits-dialogue.png    each character in a mock dialogue panel with one line from levels.md
  portraits-atlas.png/json  native 48x48 cells: rows are characters, columns neutral, concerned, pleased, signature
"""
import json
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("portraits", "gate1", "cast", "scale-test"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import build_scale_test as bst  # noqa: E402
import chibi  # noqa: E402
from chibi import grid_img, on, sprite_img, up  # noqa: E402,F401  (grid_img is also used by build_mira_patches)
import portrait_ada  # noqa: E402
import portrait_engineer  # noqa: E402
import portrait_hal  # noqa: E402
import portrait_ivo  # noqa: E402
import portrait_mira  # noqa: E402
import portrait_noor  # noqa: E402
import portrait_vale  # noqa: E402

# Atlas row order: the first rows never move (engineer, ivo, mira, mira_patch1..6), then the later characters.
CAST = [("engineer", portrait_engineer), ("ivo", portrait_ivo), ("mira", portrait_mira), ("noor", portrait_noor),
        ("hal", portrait_hal), ("ada", portrait_ada), ("vale", portrait_vale)]
ATLAS_ORDER = ["engineer", "ivo", "mira", "vale", "hal", "ada", "noor"]
STANDARD = list(chibi.STANDARD)
ZOOM = 4          # the world's zoom on 1366x768; portraits are shown at the same factor
BG = "#151C2B"
PLATE = "#343650"  # stand-in dialogue plate; the real plate comes from the UI tokens
PANEL = "#1B2033"
BRASS, TEXT, DIM = "#E1AC62", "#F4F2EC", "#C7B7A0"
BY_NAME = dict(CAST)


def sig_of(mod):
    return mod.SIGNATURES[0] if mod.SIGNATURES else None


def sig_suffix(name, sig):
    return sig[len(name) + 1:]


# ---- mannequin: a neutral stand-in drawn only from the ink and stone ramps -------------------
MAN_PAL = {".": None, "o": "#202337", "1": "#C7B7A0", "2": "#968A85", "r": "#777A8C", "q": "#535971"}


def silhouette(mod, plain=True):
    """The head and shoulders of a character module as a flat two-tone grid (no hair, no face)."""
    g = chibi.blank()
    body = chibi.paint_spans(g, mod.BODY, lambda r, c, a, b: "r")
    chibi.ring(g, body, over_all=False)
    head = chibi.paint_spans(g, mod.HEAD, chibi.skin_token)
    chibi.ring(g, head, over_all=True)
    return ["".join(r) for r in g]


def guides(draw, ox, oy, z, label=True, font=None):
    """Draw the construction guides over a portrait drawn at (ox, oy) with zoom z."""
    F = chibi.FRAME

    def hline(r, color, name, side="r", span=(0, 48)):
        y = oy + r * z
        draw.line([(ox + span[0] * z, y), (ox + span[1] * z, y)], fill=color, width=1)
        if label and font:
            if side == "r":
                draw.text((ox + 48 * z + 8, y - 8), name, font=font, fill=color)
            else:
                draw.text((ox - 8, y - 8), name, font=font, fill=color, anchor="ra")

    def vline(c, color, span=(0, 48)):
        x = ox + c * z
        draw.line([(x, oy + span[0] * z), (x, oy + span[1] * z)], fill=color, width=1)

    for c in range(16, 48, 16):                       # world tile grid
        vline(c, "#535971")
        draw.line([(ox, oy + c * z), (ox + 48 * z, oy + c * z)], fill="#535971", width=1)
    hline(F["hair_top_outline_row"], "#5AA3AE", f"hair top outline  r{F['hair_top_outline_row']}")
    hline(F["head_rows"][0], "#5AA3AE", f"head top  r{F['head_rows'][0]}", "l")
    hline(F["brow_row"], "#B2CE78", f"brows  r{F['brow_row']}")
    hline(F["eye_rows"][0], "#E67A70", f"eye block  r{F['eye_rows'][0]}-{F['eye_rows'][1]}", "l")
    hline(F["blush_rows"][0], "#B2CE78", f"blush  r{F['blush_rows'][0]}-{F['blush_rows'][1]}")
    hline(F["mouth_rows"][0], "#E67A70", f"mouth  r{F['mouth_rows'][0]}-{F['mouth_rows'][1]}", "l")
    hline(F["head_rows"][1] + 1, "#5AA3AE", f"chin  r{F['head_rows'][1]}")
    hline(F["shoulders_from_row"], "#E1AC62", f"shoulders  r{F['shoulders_from_row']}", "l")
    hline(F["crop_row"] + 1, "#E1AC62", f"crop  r{F['crop_row']} (the body runs on)")
    vline(24, "#F5D580")                               # centre axis between columns 23 and 24
    if label and font:
        draw.text((ox + 24 * z + 4, oy + 1), "axis (23|24)", font=font, fill="#F5D580")


def build_template():
    f_t, f_s, f_n, f_h = bst.font(20, bold=True), bst.font(13), bst.font(12), bst.font(15, bold=True)
    z = ZOOM
    pw = 48 * z
    margin = 150
    W = 1500
    sil_z = 2
    H = 70 + pw + 60 + 5 * 22 + 40 + (48 * sil_z + 70)
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((24, 14), "Portrait template · chibi direction C · 48x48 logical px · x4 (the world's zoom)", font=f_t, fill=TEXT)
    man = silhouette(portrait_engineer)
    mim = grid_img(man, MAN_PAL)
    oy = 70
    ox = margin
    sheet.paste(on(mim, PLATE, z).convert("RGB"), (ox, oy))
    guides(d, ox, oy, z, True, f_s)
    d.text((ox, oy + pw + 10), "A  construction guides on the standard head", font=f_h, fill=BRASS)
    bx = ox + pw + margin + 20
    sheet.paste(Image.new("RGB", (pw, pw), PLATE), (bx, oy))
    guides(d, bx, oy, z, False)
    F = chibi.FRAME
    d.rectangle([bx + 6 * z, oy + 3 * z, bx + 41 * z, oy + 37 * z], outline=TEXT)
    d.text((bx + 8 * z, oy + 5 * z), "head box (standard)\ncols 6-41, rows 3-36", font=f_n, fill=TEXT)
    d.text((bx + 10 * z, oy + 40 * z), "tiny shoulders\ncols 8-39, rows 38-47", font=f_n, fill=TEXT)
    d.text((bx, oy + pw + 10), "B  the same guides, blank", font=f_h, fill=BRASS)
    # notes
    ny = oy + pw + 50
    notes = [
        "Head: an oversized round head, rows 3-36 and up to 40 px wide (Hal, broader and shorter; Noor, narrower and longer, chin on row 38). The shoulders are tiny and sit in the bottom ten rows.",
        "Shading: flat. One skin fill and one crescent of shade down the lower right, a one-pixel shade under the fringe. Outline #202337, closed. Light from the upper left.",
        "Eyes: dots with a glint (the glint key is the sprite palette's lightest step, recorded in EXTRA). Mouths are big and readable. Cheeks are round with blush (Vale: none at rest).",
        "Expression: neutral, concerned and pleased for everyone, plus each character's own signature. Eye shape, brow habit, mouth habit, blush and a tic differ per persona (PORTRAIT_PERSONAS.md).",
        "Placement: shown at the world's zoom (x4 on 1366x768 = 192x192 screen px, x6 on 1920x1080), whole numbers only. The panel supplies the plate: the portrait is transparent.",
    ]
    for i, n in enumerate(notes):
        d.text((24, ny + i * 22), n, font=f_s, fill=DIM)
    # the seven head silhouettes, one above the other's identity: width and height in pixels
    sy = ny + 5 * 22 + 24
    d.text((24, sy), "C  the seven heads and shoulders (x2): head width and height change with the persona", font=f_h, fill=BRASS)
    sx = 24
    for name, mod in CAST:
        sim = grid_img(silhouette(mod), MAN_PAL)
        sheet.paste(on(sim, PLATE, sil_z).convert("RGB"), (sx, sy + 26))
        rows = sorted(mod.HEAD)
        wid = max(b - a + 1 for a, b in mod.HEAD.values())
        d.text((sx, sy + 26 + 48 * sil_z + 4), f"{name}: {wid}x{rows[-1] - rows[0] + 1}", font=f_n, fill=DIM)
        sx += 48 * sil_z + 20
    sheet.save(os.path.join(HERE, "portrait-template.png"))


def ramp_swatches(mod, d, x, y, used):
    f = bst.font(11)
    keys = [k for k in sorted(used) if k != "."]
    for i, k in enumerate(keys):
        d.rectangle([x + i * 26, y, x + i * 26 + 22, y + 14], fill=mod.PAL[k], outline="#535971")
        d.text((x + i * 26 + 11, y + 17), k, font=f, fill=DIM, anchor="ma")


def build_sheet():
    f_t, f_h = bst.font(20, bold=True), bst.font(16, bold=True)
    z = ZOOM
    pw = 48 * z
    sh = 24 * z
    cell = pw + 24
    left = 24 + 100
    W = left + 80 + 4 * cell + 20
    row_h = pw + 112
    H = 70 + len(CAST) * row_h
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), "Portraits beside the world sprite · x4 · chibi direction C · every portrait key is a key of the sprite's PAL",
           font=f_t, fill=TEXT)
    y = 56
    for name, mod in CAST:
        d.text((24, y + 6), name.capitalize(), font=f_h, fill=BRASS)
        sheet.paste(on(sprite_img(mod.SPRITE, mod.PAL), PLATE, z).convert("RGB"), (left, y + pw - sh))
        d.text((left, y + pw + 6), "S idle", font=bst.font(11), fill=DIM)
        used = set()
        names = STANDARD + ([sig_of(mod)] if sig_of(mod) else [])
        for i, e in enumerate(names):
            grid = mod.EXPRESSIONS[e]
            used |= {ch for r in grid for ch in r}
            px = left + 80 + i * cell
            sheet.paste(on(grid_img(grid, mod.PAL), PLATE, z).convert("RGB"), (px, y))
            d.text((px, y + pw + 6), e, font=bst.font(14, bold=True), fill=TEXT if i < 3 else BRASS)
        d.text((left + 80, y + pw + 28), mod.TAGLINE, font=bst.font(12), fill=DIM)
        ramp_swatches(mod, d, left + 80, y + pw + 52, used)
        d.text((left + 80, y + pw + 90), "keys used (same hex as the sprite)", font=bst.font(11), fill="#777A8C")
        y += row_h
    sheet.save(os.path.join(HERE, "portraits-sheet.png"))


def build_compare():
    """One row per expression type, all seven characters: the check that no two faces look alike."""
    f_t, f_h, f_s = bst.font(20, bold=True), bst.font(16, bold=True), bst.font(12)
    z = ZOOM
    pw = 48 * z
    gap = 10
    left = 124
    rows = [("neutral", "neutral"), ("concerned", "concerned"), ("pleased", "pleased"), ("signature", None)]
    W = left + 7 * (pw + gap) + 20
    H = 62 + len(rows) * (pw + 44)
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), "Seven personalities, one row per expression · x4", font=f_t, fill=TEXT)
    y = 56
    for label, e in rows:
        d.text((24, y + pw // 2 - 8), label, font=f_h, fill=BRASS)
        for i, (name, mod) in enumerate(CAST):
            key = e if e else sig_of(mod)
            x = left + i * (pw + gap)
            if key is None:
                d.rectangle([x, y, x + pw - 1, y + pw - 1], outline="#343650")
                d.text((x + 8, y + pw // 2 - 6), "none specified", font=f_s, fill="#777A8C")
            else:
                sheet.paste(on(grid_img(mod.EXPRESSIONS[key], mod.PAL), PLATE, z).convert("RGB"), (x, y))
            d.text((x + 2, y + pw + 4), f"{name}" + (f" · {key}" if e is None and key else ""), font=f_s, fill=DIM)
        y += pw + 44
    sheet.save(os.path.join(HERE, "portraits-compare.png"))


# One line per character, from levels.md (the key line, then the hint line), with a different expression each.
LINES = [
    ("engineer", "concerned", "Engineer (journal)", "Unissued badge: its old department name differs from the current sign.", ""),
    ("ivo", "neutral", "Ivo", "To walk to the west desk, you need to press Left Arrow.", "Hint: Left Arrow is tap-hold Caps (nav) + H."),
    ("mira", "mira_grin", "Mira", "To type \"jk\" in the label, you need to press J, then K.", "Hint: tap J, tap K. A same-hand roll stays text."),
    ("noor", "noor_unimpressed", "Noor", "To step back over the drifted word, you need to press Option + Left.", "Hint: Option + Left is tap-hold Caps + B."),
    ("hal", "hal_puzzled", "Hal", "To enter digit 7 of the ID, you need to press 7.", "Hint: 7 is tap-hold Space (numbers-symbols) + J."),
    ("ada", "pleased", "Ada", "To walk north along the lit route, you need to press Up Arrow.", "Hint: Physical arrows and Right Command are XX on practice. Use tap-hold Caps + K."),
    ("vale", "vale_softened", "Vale", "Restore the department's original name.", ""),
]


def wrap(d, text, font, width):
    words, line, out = text.split(), "", []
    for w in words:
        if d.textlength((line + " " + w).strip(), font=font) > width:
            out.append(line.strip())
            line = ""
        line += " " + w
    out.append(line.strip())
    return out


def build_dialogue():
    f_t, f_h, f_b, f_s = bst.font(20, bold=True), bst.font(17, bold=True), bst.font(15), bst.font(12)
    z = ZOOM
    pw = 48 * z
    pad = 14
    panel_w, panel_h = pw + 2 * pad + 400, pw + 2 * pad
    left, gap = 24, 22
    cols = 2
    rows = (len(LINES) + cols - 1) // cols
    W = left * 2 + cols * panel_w + (cols - 1) * gap
    H = 70 + rows * (panel_h + gap)
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((left, 16), "Portraits in a dialogue panel · x4 · one line from levels.md each, a different expression each", font=f_t, fill=TEXT)
    for i, (who, expr, label, text, hint) in enumerate(LINES):
        mod = BY_NAME[who]
        px = left + (i % cols) * (panel_w + gap)
        y = 56 + (i // cols) * (panel_h + gap)
        d.rectangle([px, y, px + panel_w - 1, y + panel_h - 1], fill=PANEL, outline="#535971", width=2)
        d.rectangle([px + pad - 2, y + pad - 2, px + pad + pw + 1, y + pad + pw + 1], fill=PLATE, outline="#535971")
        sheet.paste(on(grid_img(mod.EXPRESSIONS[expr], mod.PAL), PLATE, z).convert("RGB"), (px + pad, y + pad))
        tx = px + pad + pw + 20
        d.text((tx, y + 22), label, font=f_h, fill=BRASS)
        ly = y + 56
        for line in wrap(d, text, f_b, panel_w - (tx - px) - 18):
            d.text((tx, ly), line, font=f_b, fill=TEXT)
            ly += 22
        if hint:
            ly += 6
            for line in wrap(d, hint, f_b, panel_w - (tx - px) - 18):
                d.text((tx, ly), line, font=f_b, fill=DIM)
                ly += 22
        d.text((tx, y + panel_h - 30), f"[{expr}]", font=f_s, fill="#777A8C")
    sheet.save(os.path.join(HERE, "portraits-dialogue.png"))


def build_atlas():
    rows = []
    for name in ATLAS_ORDER:
        mod = BY_NAME[name]
        rows.append((name, mod, 0))
        if name == "mira":
            rows += [(f"mira_patch{k}", mod, k) for k in range(1, 7)]
    columns = STANDARD + ["signature"]
    atlas = Image.new("RGBA", (48 * len(columns), 48 * len(rows)), (0, 0, 0, 0))
    entries = {}
    for r, (name, mod, k) in enumerate(rows):
        base = "mira" if k else name
        names = STANDARD + [sig_of(mod)]
        for c, e in enumerate(names):
            if e is None:
                continue
            grid, pal = mod.EXPRESSIONS[e], mod.PAL
            if k:
                grid, pal = mod.with_patches(grid, k), mod.PATCH_PAL
            atlas.paste(grid_img(grid, pal), (c * 48, r * 48))
            key = f"{name}_{e}" if c < 3 else f"{name}_{sig_suffix(base, e)}"
            entries[key] = {"x": c * 48, "y": r * 48, "w": 48, "h": 48}
    atlas.save(os.path.join(HERE, "portraits-atlas.png"))
    meta = {
        "frame": {"w": 48, "h": 48},
        "style": "chibi icon: oversized round head, tiny shoulders, flat shading, dot eyes; per-character head, hair and expressions",
        "columns": columns,
        "signature_column": 3,
        "signatures": {name: sig_of(BY_NAME[name]) for name, _ in CAST if sig_of(BY_NAME[name])},
        "rows": [name for name, _, _ in rows],
        "zoom": "same integer factor as the world (x4 at 1366x768, x6 at 1920x1080); never fractional",
        "origin": "top-left of the 48x48 cell sits on the dialogue panel's portrait slot; background is transparent",
        "mira_patch_rows": "mira_patchK is Mira wearing patches 1..K (the row 'mira' is K = 0)",
        "signature_keys": "a signature entry is <row>_<name>, for example ivo_laugh or mira_patch3_grin; characters without one leave the cell empty",
        "portraits": entries,
    }
    with open(os.path.join(HERE, "portraits-atlas.json"), "w") as fh:
        json.dump(meta, fh, indent=2)


if __name__ == "__main__":
    build_template()
    build_sheet()
    build_compare()
    build_dialogue()
    build_atlas()
    print("built portrait-template.png, portraits-sheet.png, portraits-compare.png, portraits-dialogue.png, portraits-atlas.png/json")
