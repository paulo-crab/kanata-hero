"""Build the board comparison sheets from the mocks (run: python3 sheets.py)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import base, m1, m2

a0 = base.baseline()[:180]; a1 = m1.build()[:180]; a2 = m2.build()[:180]; a3 = m2.build(dense=True)[:180]
ref = Image.open('../references/08-approved-overhead-direction.png').convert('RGB')
f = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 26, index=1)
f2 = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 21)
W, H, pad, top = 520, 293, 24, 70
panels = [
    ('Reference 08', 'the target', ref.resize((W, int(W * 931 / 1690)), Image.LANCZOS).resize((W, H))),
    ('Today', 'approved, 32 colours', Image.fromarray(a0).resize((W, H), Image.NEAREST)),
    ('Mock 1: light', 'same art, shadows and glow', Image.fromarray(a1).resize((W, H), Image.NEAREST)),
    ('Mock 2: colour', 'vivid palette, leafy foliage', Image.fromarray(a2).resize((W, H), Image.NEAREST)),
    ('Mock 3: density', 'adds lounge, parcels, plants', Image.fromarray(a3).resize((W, H), Image.NEAREST)),
]
sheet = Image.new('RGB', (3 * W + 4 * pad, 2 * (H + top) + 3 * pad), '#171B2C'); d = ImageDraw.Draw(sheet)
for i, (t, sub, im) in enumerate(panels):
    x = pad + (i % 3) * (W + pad); y = pad + (i // 3) * (H + top + pad)
    d.text((x, y), t, font=f, fill='#E6B750'); d.text((x, y + 32), sub, font=f2, fill='#B9C1D6'); sheet.paste(im, (x, y + top))
sheet.save('richness-comparison.png')
cw, ch = 102 * 4, 84 * 4
det = Image.new('RGB', (4 * cw + 5 * pad, ch + top + 2 * pad), '#171B2C'); dd = ImageDraw.Draw(det)
for i, (t, a) in enumerate((('Today', a0), ('Mock 1', a1), ('Mock 2', a2), ('Reference 08', None))):
    x = pad + i * (cw + pad); dd.text((x, pad), t, font=f, fill='#E6B750')
    if a is not None:
        det.paste(Image.fromarray(a[56:140, 88:190]).resize((cw, ch), Image.NEAREST), (x, pad + top))
    else:
        det.paste(ref.crop((560, 200, 1130, 660)).resize((cw, ch), Image.LANCZOS), (x, pad + top))
det.save('richness-garden-detail.png')
base.save_x4(m1.build(), 'm1_light.png'); base.save_x4(m2.build(), 'm2_colour.png'); base.save_x4(m2.build(dense=True), 'm3_density.png'); base.save_x4(base.baseline(), 'm0_today.png')
