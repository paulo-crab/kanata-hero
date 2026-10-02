"""Build the portrait-direction review images.

Run: python3 build_explore.py   (needs Pillow + numpy)
Writes into this folder:
  portrait-directions.png           one row per character: the world sprite (S idle) at x4, then for
                                    each direction the three expressions at x4
  portrait-directions-dialogue.png  one expression per direction inside a mock dialogue panel at x4
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import explore_common as X  # noqa: E402
import style_a  # noqa: E402
import style_b  # noqa: E402
import style_c  # noqa: E402

bst = X.bst
STYLES = [style_a, style_b, style_c]
BLURB = {
    "A": "boxy head, 2x3 block eyes, two skin tones",
    "B": "rounded-square bust, 3x3 eyes, tiny nose",
    "C": "oversized head, dot eyes, tiny shoulders",
}
Z = 4
BG = "#151C2B"
PLATE = "#343650"        # stand-in dialogue plate, as in build_portraits.py
PANEL = "#1B2033"


def portrait(style, who, expr):
    return X.grid_img(X.compose(style, who, expr), X.pal_of(who))


def build_directions():
    f_t, f_h, f_s = bst.font(20, bold=True), bst.font(17, bold=True), bst.font(12)
    pw = 48 * Z
    gap, group_gap, left = 8, 34, 24
    label_w = 120
    sprite_w = 16 * Z + 24
    group_w = 3 * pw + 2 * gap
    W = left + label_w + sprite_w + 3 * group_w + 2 * group_gap + 24 + left
    row_h = pw + 44
    H = 120 + 3 * row_h
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((left, 14), "Portrait directions: Engineer, Ivo, Mira  ·  x4  ·  48x48, sprite palettes only", font=f_t, fill="#F4F2EC")
    x0 = left + label_w + sprite_w
    d.text((left + label_w, 84), "world sprite", font=f_s, fill="#C7B7A0")
    for gi, st in enumerate(STYLES):
        gx = x0 + gi * (group_w + group_gap)
        d.text((gx, 44), st.NAME, font=f_h, fill="#E1AC62")
        d.text((gx, 68), BLURB[st.NAME[0]], font=f_s, fill="#C7B7A0")
    y = 104
    for who, cfg in X.CHARS.items():
        d.text((left, y + pw // 2 - 10), cfg["label"], font=f_h, fill="#E1AC62")
        sp = X.on(X.sprite_img(who), PLATE, Z).convert("RGB")
        sheet.paste(sp, (left + label_w, y + pw - sp.height))
        for gi, st in enumerate(STYLES):
            gx = x0 + gi * (group_w + group_gap)
            for ei, e in enumerate(X.EXPRESSIONS):
                px = gx + ei * (pw + gap)
                sheet.paste(X.on(portrait(st, who, e), PLATE, Z).convert("RGB"), (px, y))
                d.text((px + 2, y + pw + 6), e, font=f_s, fill="#C7B7A0")
        y += row_h
    sheet.save(os.path.join(HERE, "portrait-directions.png"))


LINES = {
    "engineer": ("concerned", "Engineer", "That chord did not register. Try the hold again, slower."),
    "ivo": ("neutral", "Ivo", "Welcome to Orientation. Please take a visitor badge."),
    "mira": ("pleased", "Mira", "Route fixed. Nice work, you are quick."),
}


def build_dialogue():
    f_t, f_h, f_b, f_s = bst.font(20, bold=True), bst.font(17, bold=True), bst.font(15), bst.font(12)
    pw = 48 * Z
    pad = 14
    panel_w, panel_h = pw + 2 * pad + 360, pw + 2 * pad
    left, gap = 24, 22
    W = left * 2 + 3 * panel_w + 2 * gap
    H = 100 + 3 * (panel_h + gap) + 10
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    d.text((left, 14), "Portraits in a dialogue panel  ·  x4  ·  one expression per character", font=f_t, fill="#F4F2EC")
    for gi, st in enumerate(STYLES):
        d.text((left + gi * (panel_w + gap), 56), st.NAME, font=f_h, fill="#E1AC62")
    y = 90
    for who, (expr, name, text) in LINES.items():
        for gi, st in enumerate(STYLES):
            px = left + gi * (panel_w + gap)
            d.rectangle([px, y, px + panel_w - 1, y + panel_h - 1], fill=PANEL, outline="#535971", width=2)
            d.rectangle([px + pad - 2, y + pad - 2, px + pad + pw + 1, y + pad + pw + 1], fill=PLATE, outline="#535971")
            sheet.paste(X.on(portrait(st, who, expr), PLATE, Z).convert("RGB"), (px + pad, y + pad))
            tx = px + pad + pw + 20
            d.text((tx, y + 26), name, font=f_h, fill="#E1AC62")
            words, line, ly = text.split(), "", y + 62
            for w in words:                                  # simple word wrap
                if d.textlength(line + " " + w, font=f_b) > panel_w - (tx - px) - 18:
                    d.text((tx, ly), line.strip(), font=f_b, fill="#F4F2EC")
                    line, ly = "", ly + 22
                line += " " + w
            d.text((tx, ly), line.strip(), font=f_b, fill="#F4F2EC")
            d.text((tx, y + panel_h - 32), f"[{expr}]", font=f_s, fill="#777A8C")
        y += panel_h + gap
    sheet.save(os.path.join(HERE, "portrait-directions-dialogue.png"))


if __name__ == "__main__":
    build_directions()
    build_dialogue()
    print("built portrait-directions.png and portrait-directions-dialogue.png")
