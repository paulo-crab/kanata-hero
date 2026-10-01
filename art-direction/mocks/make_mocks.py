"""Mock: proposed 3/4-overhead 20x26 Engineer vs the current Gate 1 16x24 sprite."""
import sys, random
sys.path.insert(0, "/private/tmp/claude-502/-Users-paulo-sebastiao-workspace-kanata-hero/3af7cccc-686d-48c4-bb8a-206766ce02d4/scratchpad/lib")
sys.path.insert(0, "../gate1")
from PIL import Image, ImageDraw
import engineer_sprites as old

PAL = {".": None, "o": "#2a1d2b", "O": "#1a1220",
 "h": "#4a2e2e", "H": "#7a4a34", "G": "#b0703f", "g": "#d79a58",
 "s": "#e3ad7d", "t": "#b97a55", "u": "#f5cfa4", "r": "#d9876b", "m": "#8a3b3b",
 "e": "#1f1a2e", "w": "#ffffff",
 "j": "#2f8f90", "J": "#63c9bb", "k": "#1d5560", "c": "#f4f0e6", "l": "#f0c040",
 "p": "#3d4f86", "P": "#28335c", "b": "#8a5236", "B": "#c07c52"}

HALF = [
".....ooooo", "...ooHHGGG", "..oHHGGGgG", ".oHHGGGGGg", ".ohHHGGHHH",
".ohHHHhhHH", ".ohhHsssss", ".ohtuussss", ".ohtsewsss", ".ohtseesss",
"..ottssssm", "...ottssss", "....oooooo", "....oocccc", "..ookjjJcc",
".okkjjjJJl", ".okkjjjjJl", ".okkjjjjjl", ".ossojjjjj", "..oootjjjj",
"....oPPppp", "....oPpppo", "....oPpppo", "....oPpppo", "...ooBBBBo",
"..oobBBBBo", "...oooooo.",
]
S = [r + r[::-1] for r in HALF]
S[10] = list(S[10]); S[10][9] = S[10][10] = "m"; S[10] = "".join(S[10])
S[11] = S[11][:9] + "ss" + S[11][11:]
S[11] = S[11].replace("sssssssss", "ssssssssu") if False else S[11]

def setpx(g, y, x, c):
    r = list(g[y]); r[x] = c; g[y] = "".join(r)

# E: face turned right, hair covers the back of head, nose bump, lanyard shifts
E = list(S)
for y in range(6, 12):
    for x in range(3, 10):
        if E[y][x] in "stuMmer w": setpx(E, y, x, "H" if y < 10 else "t")
for y in (8, 9):
    for x in (5, 6, 13, 14): setpx(E, y, x, "s")
for (x, c) in ((11, "e"), (12, "w")): setpx(E, 8, x, c)
for (x, c) in ((11, "e"), (12, "e")): setpx(E, 9, x, c)
for (x, c) in ((15, "w"), (16, "e")): setpx(E, 8, x, c)
for (x, c) in ((15, "e"), (16, "e")): setpx(E, 9, x, c)
setpx(E, 9, 17, "u"); setpx(E, 10, 17, "t")
for x in (9, 10): setpx(E, 10, x, "s")
setpx(E, 10, 13, "m"); setpx(E, 10, 14, "m")
for y in range(14, 18):
    for x in (9, 10):
        setpx(E, y, x, "j")
    setpx(E, y, 12, "l")
setpx(E, 15, 12, "l"); setpx(E, 16, 12, "l")
W = [r[::-1] for r in E]

# N: back of head, no face, no lanyard/collar V
N = list(S)
for y in range(6, 12):
    for x in range(2, 18):
        if N[y][x] in "stuMmer w": setpx(N, y, x, "H" if (x + y) % 5 else "h")
for y in range(6, 12):
    for x in range(3, 17):
        if N[y][x] == "H" and (x * 7 + y * 3) % 6 == 0: setpx(N, y, x, "G")
for y in range(12, 18):
    for x in range(2, 18):
        if N[y][x] in "clu": setpx(N, y, x, "j")
for x in range(7, 13): setpx(N, 12, x, "k")
for x in range(8, 12): setpx(N, 13, x, "j")

def render(grid, pal=PAL, jacket=None):
    p = dict(pal)
    if jacket: p.update(jacket)
    im = Image.new("RGBA", (len(grid[0]), len(grid)), (0, 0, 0, 0))
    for y, row in enumerate(grid):
        for x, k in enumerate(row):
            c = p.get(k)
            if c: im.putpixel((x, y), Image.new("RGB", (1, 1), c).getpixel((0, 0)) + (255,))
    return im

def with_shadow(spr):
    w, h = spr.size
    out = Image.new("RGBA", (w, h + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.ellipse((2, h - 4, w - 3, h + 1), fill=(40, 25, 50, 90))
    out.alpha_composite(spr, (0, 0))
    return out

def old_sprite():
    im = Image.new("RGBA", (16, 24), (0, 0, 0, 0))
    for y, row in enumerate(old.S):
        for x, k in enumerate(row):
            c = old.PAL.get(k)
            if c: im.putpixel((x, y), tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) + (255,))
    return im

# ---------- comparison sheet ----------
FLOOR = (222, 205, 170)
def tile_bg(w, h, ts=16):
    im = Image.new("RGB", (w, h), FLOOR)
    d = ImageDraw.Draw(im)
    random.seed(3)
    for y in range(0, h, ts):
        for x in range(0, w, ts):
            for _ in range(5):
                d.point((x + random.randrange(ts), y + random.randrange(ts)), fill=(210, 192, 156))
            d.line((x, y, x + ts, y), fill=(196, 178, 142)); d.line((x, y, x, y + ts), fill=(196, 178, 142))
    return im

Z = 10
W_, H_ = 800, 420
sheet = Image.new("RGB", (W_, H_), (26, 28, 44))
bg = tile_bg(W_ // Z, 30 + 0).resize((W_, 30 * Z), Image.NEAREST)
cells = [("CURRENT  16x24 front elevation", [old_sprite()], 0)]
sprites_new = [render(g) for g in (S, E, N, W)]
sheet_d = ImageDraw.Draw(sheet)
def paste_scaled(spr, x, y):
    big = spr.resize((spr.width * Z, spr.height * Z), Image.NEAREST)
    sheet.paste(big, (x, y), big)
stage = tile_bg(W_ // Z, 31).resize((W_, 310), Image.NEAREST)
sheet.paste(stage, (0, 100))
sheet_d.text((14, 12), "CURRENT Gate 1  16x24 (front elevation, uniform ink outline, muted)", fill=(240, 200, 110))
sheet_d.text((14, 56), "PROPOSED  20x26 (3/4 overhead, big head, selective outline, shadow, warm ramps)  S / E / N / W", fill=(240, 200, 110))
paste_scaled(with_shadow(old_sprite()), 20, 30 - 30 + 100 - 0) if False else None
# old on left strip
old_big = with_shadow(old_sprite())
old_img = old_big.resize((old_big.width * 4, old_big.height * 4), Image.NEAREST)
sheet.paste(old_img, (W_ - 120, 8), old_img)
for i, sp in enumerate(sprites_new):
    paste_scaled(with_shadow(sp), 40 + i * 190, 120)
sheet.save("mock-engineer-compare.png")

# ---------- scene mock (320x180 native) ----------
VW, VH = 320, 180
sc = Image.new("RGBA", (VW, VH), FLOOR + (255,))
d = ImageDraw.Draw(sc)
random.seed(5)
for y in range(0, VH, 16):
    for x in range(0, VW, 16):
        for _ in range(6):
            d.point((x + random.randrange(16), y + random.randrange(16)), fill=(208, 190, 154))
        d.line((x, y, x + 16, y), fill=(194, 176, 140)); d.line((x, y, x, y + 16), fill=(194, 176, 140))
# plaza inlay
d.rectangle((70, 40, 250, 150), fill=(190, 176, 150)); d.rectangle((74, 44, 246, 146), outline=(168, 154, 128))
# glass wall top
d.rectangle((0, 0, VW, 26), fill=(40, 46, 66))
for x in range(4, VW, 40):
    d.rectangle((x, 4, x + 34, 20), fill=(86, 176, 196)); d.rectangle((x, 4, x + 34, 7), fill=(150, 220, 226))
    d.line((x + 12, 4, x + 6, 20), fill=(130, 205, 215))
d.line((0, 22, VW, 22), fill=(80, 220, 235)); d.rectangle((0, 24, VW, 26), fill=(30, 34, 52))

def tree(cx, cy, r):
    d.ellipse((cx - r, cy - r + 3, cx + r, cy + r + 3), fill=(30, 76, 52))
    for _ in range(r * 5):
        a = random.random() * 6.283; rr = random.random() * r
        x = cx + int(rr * __import__("math").cos(a)); y = cy + int(rr * __import__("math").sin(a))
        c = random.choice([(54, 128, 66), (82, 170, 80), (120, 205, 96), (38, 98, 58)])
        d.rectangle((x, y, x + 2, y + 1), fill=c)
    d.rectangle((cx - 2, cy + r - 2, cx + 2, cy + r + 5), fill=(112, 70, 44))
def planter(x, y):
    d.rectangle((x, y + 8, x + 11, y + 15), fill=(60, 68, 96)); d.rectangle((x, y + 8, x + 11, y + 9), fill=(100, 112, 146))
    for i, (dx, dy, c) in enumerate([(2, 0, (72, 160, 76)), (6, -2, (110, 200, 92)), (8, 2, (46, 118, 62)), (3, 4, (96, 184, 84)), (0, 3, (46, 118, 62))]):
        d.ellipse((x + dx, y + dy, x + dx + 6, y + dy + 6), fill=c)
def desk(x, y):
    d.rectangle((x, y, x + 40, y + 15), fill=(126, 82, 52)); d.rectangle((x, y, x + 40, y + 3), fill=(176, 120, 76))
    d.rectangle((x + 4, y - 8, x + 16, y), fill=(52, 60, 88)); d.rectangle((x + 6, y - 6, x + 14, y - 2), fill=(90, 220, 235))
    d.rectangle((x + 22, y + 4, x + 32, y + 8), fill=(240, 232, 210))
def lamp(x, y):
    d.rectangle((x, y, x + 4, y + 8), fill=(56, 58, 78)); d.rectangle((x, y - 3, x + 4, y), fill=(255, 214, 120))
    glow = Image.new("RGBA", (VW, VH), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((x - 14, y - 12, x + 18, y + 16), fill=(255, 210, 120, 38))
    sc.alpha_composite(glow)
tree(160, 92, 30)
d.rectangle((90, 100, 98, 130), fill=(120, 82, 52)); d.rectangle((222, 100, 230, 130), fill=(120, 82, 52))
d.ellipse((150, 108, 170, 120), fill=(70, 160, 200)); 
for (x, y) in ((74, 44), (178 + 66, 44), (74, 128), (246, 128)): lamp(x, y)
for (x, y) in ((10, 34), (298, 34), (60, 150), (250, 150), (20, 120), (292, 110)): planter(x, y)
desk(24, 60); desk(256, 64)

def place(grid, x, y, jk=None, hair=None):
    p = dict(PAL)
    if jk: p.update(jk)
    if hair: p.update(hair)
    spr = with_shadow(render(grid, p))
    sc.alpha_composite(spr, (x, y))
place(S, 150, 148)                                       # player
place(E, 112, 70, jk={"j": "#b0522f", "J": "#d9794e", "k": "#74301c"}, hair={"H": "#b8b8c0", "G": "#e8e8ee", "h": "#7c7c88"})  # grey NPC
place(W, 214, 80, jk={"j": "#d9d4c4", "J": "#f4f0e6", "k": "#9a9484", "l": "#6aa0d8"}, hair={"H": "#2e2428", "G": "#4a3a40", "h": "#1a1218"})
place(N, 240, 112, jk={"j": "#3a4a7a", "J": "#5a70b0", "k": "#222c52"}, hair={"H": "#7a4a34"})
# speech bubble above grey NPC
d.rectangle((115, 58, 129, 68), fill=(238, 98, 84)); d.polygon([(120, 68), (123, 68), (121, 71)], fill=(238, 98, 84))
for x in (118, 122, 126): d.point((x, 63), fill=(255, 255, 255))
sc.convert("RGB").save("mock-scene-native.png")
sc.convert("RGB").resize((VW * 4, VH * 4), Image.NEAREST).save("mock-scene-x4.png")
