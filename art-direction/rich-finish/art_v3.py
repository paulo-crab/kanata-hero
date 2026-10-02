"""Mock 3 art: Mock 2 plus the set-piece density that reference 08 shows (lounge, trolley, parcels,
extra planters). Drawn with Room helpers from gate1/environment.py. DRAFT for board validation."""
import numpy as np

import build_scale_test as bst
import art_v2

H = bst.hx
CHAIR = [H(x) for x in ("#5A2412", "#A8421C", "#D2641F", "#F0944A")]
RUG = [H(x) for x in ("#4E2C18", "#7A4A2A", "#B8742F")]
CART = [H(x) for x in ("#243043", "#41546F", "#7E93AE")]
CARD = [H(x) for x in ("#7A5230", "#B98A55", "#E2BC83")]
TAPE = H("#F2E4C8")


def armchair(r, x, y, facing="r"):
    """Top-down armchair seen from above: dark back, two arms, a lit seat cushion with a highlight."""
    r.cast(x, x + 14, y + 14, rows=1)
    body = r.mask(x, y, x + 14, y + 14)
    r.img[body] = CHAIR[1]
    bx0, bx1 = (x, x + 4) if facing == "r" else (x + 10, x + 14)
    sx0, sx1 = (x + 4, x + 13) if facing == "r" else (x + 1, x + 10)
    r.rect(bx0, y, bx1, y + 14, CHAIR[0])                       # back
    r.rect(bx0 + 1, y + 1, bx1 - 1, y + 3, CHAIR[1])            # back highlight
    r.rect(sx0, y, sx1, y + 3, CHAIR[1])                        # near arm
    r.rect(sx0, y + 11, sx1, y + 14, CHAIR[0])                  # far arm (shaded)
    r.rect(sx0, y + 3, sx1, y + 11, CHAIR[2])                   # cushion
    r.rect(sx0 + 1, y + 4, sx1 - 2, y + 5, CHAIR[3])            # cushion highlight
    r.rect(sx0 + 1, y + 4, sx0 + 2, y + 9, CHAIR[3])
    r.outline(body)


def round_table(r, cx, cy):
    r.cast(cx - 6, cx + 6, cy + 6, rows=1)
    top = r.disc(cx, cy, 6.5, 5.2)
    r.img[top] = H("#8C93A6")
    r.img[top & (r.y < cy - 1)] = H("#C9CEDA")
    r.outline(top)
    art_v2.leaves_v2(r, cx, cy - 2, 4.2, 5, count=5, spread=2)


def rug(r, x0, y0, x1, y1):
    r.rect(x0, y0, x1, y1, RUG[1])
    r.rect(x0, y0, x1, y0 + 2, RUG[2]); r.rect(x0, y1 - 2, x1, y1, RUG[2])
    r.rect(x0, y0, x0 + 2, y1, RUG[2]); r.rect(x1 - 2, y0, x1, y1, RUG[2])
    r.rect(x0 + 4, y0 + 4, x1 - 4, y0 + 5, RUG[0]); r.rect(x0 + 4, y1 - 5, x1 - 4, y1 - 4, RUG[0])
    r.rect(x0 + 4, y0 + 4, x0 + 5, y1 - 4, RUG[0]); r.rect(x1 - 5, y0 + 4, x1 - 4, y1 - 4, RUG[0])
    r.outline(r.mask(x0, y0, x1, y1), RUG[0])


def parcel(r, x, y, w, h):
    box = r.mask(x, y, x + w, y + h)
    r.img[box] = CARD[1]
    r.rect(x, y, x + w, y + 2, CARD[2])
    r.rect(x + w // 2, y, x + w // 2 + 1, y + h, TAPE)
    r.outline(box, CARD[0])


def _unused_trolley(r, x, y):
    """Parcel trolley, as at the mailroom in 08: blue-grey frame, stacked boxes, two wheels."""
    r.cast(x, x + 22, y + 26, rows=1)
    frame = r.mask(x, y + 12, x + 22, y + 26)
    r.img[frame] = CART[1]
    r.rect(x, y + 12, x + 22, y + 14, CART[2])
    r.rect(x + 2, y + 16, x + 20, y + 24, CART[0])
    r.outline(frame)
    r.rect(x + 2, y + 25, x + 5, y + 27, CART[0]); r.rect(x + 17, y + 25, x + 20, y + 27, CART[0])
    parcel(r, x + 2, y + 2, 10, 10)
    parcel(r, x + 11, y + 5, 9, 7)
    parcel(r, x + 6, y - 4, 8, 6)


def extras(c, room):
    rug(room, 8, 118, 76, 150)
    armchair(room, 14, 126, "r")
    armchair(room, 54, 126, "l")
    round_table(room, 41, 133)
    for px, py in ((4, 100), (50, 160)):
        art_v2.pot_v2(room, px, py, 300 + px)
    parcel(room, 262, 154, 8, 7)
    parcel(room, 272, 156, 7, 6)
