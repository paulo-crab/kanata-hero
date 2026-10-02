"""Board sheets for the detail round: the four 16 px mocks, the two-grid garden comparison, the camera diagram."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import base, m2, hr

F = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 26, index=1)
F2 = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 21)
BG, GOLD, MUTE = '#171B2C', '#E6B750', '#B9C1D6'
pad, top = 24, 66

frames = [('Mock 2 (what the board picked)', 'colour, light, leafy foliage', m2.build()),
          ('Mock 2.1: organic detail', 'bark, limbs, ripples, mossy rocks', m2.build(organic=True)),
          ('Mock 2.2: material detail', 'wood grain, bricks, screens, lamps', m2.build(materials=True)),
          ('Mock 2.3: both', 'same objects, more drawn on each', m2.build(organic=True, materials=True))]
W, Hh = 640, 360
sheet = Image.new('RGB', (2 * W + 3 * pad, 2 * (Hh + top) + 3 * pad), BG); d = ImageDraw.Draw(sheet)
for i, (t, sub, a) in enumerate(frames):
    x = pad + (i % 2) * (W + pad); y = pad + (i // 2) * (Hh + top + pad)
    d.text((x, y), t, font=F, fill=GOLD); d.text((x, y + 32), sub, font=F2, fill=MUTE)
    sheet.paste(Image.fromarray(a[:180, :320]).resize((W, Hh), Image.NEAREST), (x, y + top))
sheet.save('detail-mocks.png')

# same garden, 16 px grid vs 32 px grid, equal size on screen
a23 = frames[3][2]
left = Image.fromarray(a23[56:156, 70:200]).resize((130 * 6, 100 * 6), Image.NEAREST)
right = Image.fromarray(hr.lit(hr.draw())).resize((260 * 3, 200 * 3), Image.NEAREST)
sheet2 = Image.new('RGB', (2 * 780 + 3 * pad, 600 + top + 2 * pad), BG); d2 = ImageDraw.Draw(sheet2)
for i, (t, sub, im) in enumerate((('Mock 2.3 on today\'s 16 px grid', 'what we can draw now', left),
                                  ('Mock 2.4 on a finer 32 px grid', 'same garden, four times the pixels', right))):
    x = pad + i * (780 + pad); d2.text((x, pad), t, font=F, fill=GOLD); d2.text((x, pad + 32), sub, font=F2, fill=MUTE)
    sheet2.paste(im, (x, pad + top))
sheet2.save('detail-two-grids.png')

# camera: default 320x180 at x4 vs wide 427x240 at x3, same 1280x720 screen
S = 640 / 320.0
default = Image.fromarray(a23[:180, :320]).resize((640, 360), Image.NEAREST)
scale = 3 / 4.0
inner = Image.fromarray(a23[:180, :320]).resize((int(640 * scale), int(360 * scale)), Image.NEAREST)
wide = Image.new('RGB', (640, 360), '#2A3150'); wd = ImageDraw.Draw(wide)
for k in range(-360, 640, 14):
    wd.line([(k, 360), (k + 360, 0)], fill='#323A5C', width=2)
wide.paste(inner, (0, 0))
wd.rectangle([0, 0, inner.width - 1, inner.height - 1], outline=GOLD, width=3)
cam = Image.new('RGB', (2 * 640 + 3 * pad, 360 + top + 3 * pad + 90), BG); dc = ImageDraw.Draw(cam)
dc.text((pad, pad), 'Default: 320x180 at x4', font=F, fill=GOLD)
dc.text((pad, pad + 32), '20 x 11 tiles. People are 96 px tall on a 1280x720 stage', font=F2, fill=MUTE)
cam.paste(default, (pad, pad + top))
dc.text((2 * pad + 640, pad), 'Wider: 427x240 at x3', font=F, fill=GOLD)
dc.text((2 * pad + 640, pad + 32), '26 x 15 tiles. People are 72 px tall; the hatched area is new', font=F2, fill=MUTE)
cam.paste(wide, (2 * pad + 640, pad + top))
dc.text((pad, pad + top + 360 + 20), 'Both fill the same 1280x720 stage. The wider view shows 1.33x more across and down (1.78x the area),', font=F2, fill='#F3EFE4')
dc.text((pad, pad + top + 360 + 50), 'and draws everything 25% smaller. Reference 08 shows about 24 x 13 tiles, between the two.', font=F2, fill='#F3EFE4')
cam.save('camera-default-vs-wide.png')
for n, a in (('m2_1_organic', frames[1][2]), ('m2_2_materials', frames[2][2]), ('m2_3_both', frames[3][2])):
    base.save_x4(a, n + '.png')
print('ok')
