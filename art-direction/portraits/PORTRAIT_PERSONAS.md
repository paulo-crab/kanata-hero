# Portrait personas (chibi direction C)

**Status:** Candidate, pending director review. Player decision 2026-10-02: the first portraits were "too serious, too real", so the cast moves to the **Chibi icon** direction, and "each person should have their own emotion/reactions, so they have personality". This sheet records, per character, the physical cues, the emotional profile taken from the docs, and the concrete pixel choices that make their neutral, concerned and pleased looks differ. The code is `chibi.py` plus `portrait_<name>.py`; the rules are in [PORTRAIT_RULES.md](PORTRAIT_RULES.md).

**Sources:** `design/characters/{engineer,ivo,mira,noor,hal,ada,vale}.md`, `design/characters/README.md`, `levels.md` (cast table and the levels each character appears in), `docs/game-design.md` ("Characters and UI"). Where a doc says nothing the sheet says "not specified" and picks a mild, kind default. Nobody is mean or hostile.

## Shared vocabulary (all in the C style)

Head 34-36 px wide and 32-36 px tall; tiny shoulders in rows 38-47; flat shading (fill plus one crescent); outline `#202337`. Eyes are dots with a glint; blush is two small patches. Pixel coordinates are portrait (col, row), 0-indexed, left eye first. "Glance" means the eyes shift one pixel sideways.

| | Head (w x h) | Eyes | Brows | Mouth habit | Blush | Tic |
| --- | --- | --- | --- | --- | --- | --- |
| Engineer | 36x34, standard round | round dot 4x4 | even, left a pixel high | wide gentle smile | 4x2 | one brow rides high |
| Ivo | 36x34, wide soft jaw | small oval 4x3 | fine, exactly level | narrow tidy smile | 3x2 | laugh lines at the mouth |
| Mira | 36x34, pointed chin | tall oval 4x5, two sparkles | right brow cocked | lopsided smirk | 4x2 | the bun, the wink |
| Noor | 32x36, tall and narrow | half-lid 4x3, flat upper lid | never match | flat, one corner | 2x2 pale pink | deadpan |
| Hal | 40x32, broad and low | round 4x4, big 5x5 when anxious | slant in | short, pursed | 4x2 | sweat bead |
| Ada | 34x34, soft round | shaded heavy lid over a dot | low, even, 5 px | straight, small lower lip | 3x2 (5x2 when pleased) | serene closed eyes |
| Vale | 36x34, square, flat top and chin | small squared 4x3 | straight, 5 px | dead level, 8 px | none at rest | stiffness |

## Engineer (the baseline)

**(a) Physical.** The standard round head (rows 3-36, cols 6-41). Brown swept hair: crown tufts, a long right-hand fringe in short points, a short left temple. Teal jacket with a cream collar V; the brass badge on its lanyard at the lower right.

**(b) Emotional profile.** "Observant and competent; mostly defined by the player's choices" (engineer.md); "their journal records evidence rather than speeches" (levels.md cast table). So the Engineer is the unmarked reference every other face deviates from: standard dot eyes, standard mouths, one small habit.

**(c) Looks.**
- Neutral: round eyes at (14,22) and (30,22); brows 4 px, the left on row 18 and the right on row 19 (observant); a smile of `o` at (20,28), (27,28) over cols 21-26 on row 29; blush 4x2 at (9,27), (35,27).
- Concerned: brows tilt up in the middle in three steps; the mouth is a small open ring on rows 29-31, cols 22-25.
- Pleased: closed arc eyes on rows 23-24; arched brows; an open smile on rows 28-30, cols 20-27.

**(d) Signature.** Not specified. None.

## Ivo

**(a) Physical.** The softest, oldest head: a wide, rounded jaw (rows 30-36 stay wide). Silver hair in three clusters with ink notches on top, side tufts that bulge past the head, a toothed fringe with a centre forelock. The widest shoulders in the cast (cols 5-42), terracotta cardigan with the ochre strip, the tablet at the lower right.

**(b) Emotional profile.** "Precise. Believes clear instructions help people; begins to question the repeated onboarding scripts" (ivo.md). His lines are exact ("To walk to the west desk, you need to press **Left Arrow**"). Greeting wave "becomes an unscripted laugh after the review" (levels.md).

**(c) Looks.**
- Neutral (polite, scripted): small oval eyes on rows 23-25; fine brows exactly level and mirrored on row 20; a narrow tidy smile (`o` at (21,29) and (26,29), cols 22-25 on row 30) with a one-pixel laugh line either side at (19,29) and (28,29). Everything symmetric: it is the script.
- Concerned (questioning): the eyes open wide (4x4); the left brow stays level, the right arches high on rows 17-18; a flat doubtful mouth on row 29 with one end lifted at (26,28). Questioning, not worried.
- Pleased (the warm smile before the laugh): soft closed arcs, small arched brows, a deep closed smile (ends two rows up) with the laugh lines and bigger blush.

**(d) Signature: `ivo_laugh`.** Eyes squeezed shut on rows 22-23, brows lifted to row 18, a 10 px open mouth with a row of teeth (the hair's lightest step) over a dark inside. Source: the unscripted laugh in the cast table.

## Mira

**(a) Physical.** Round head with a slightly pointed chin. Dark hair: a dome with a fringe and parting, and the bun on her left (screen right), drawn as a ball with its own ink arc so a V notch separates it from the dome. Two-panel jacket (green on screen left, ochre right), the coral strap diagonal from the upper left to the lower middle. The bag is off-frame.

**(b) Emotional profile.** "Playful at first; later admits she kept copies of routes Pace tried to erase" (mira.md); "Mira jokes that the building seems convinced everyone has only one useful hand" (level 05). Quick, bright, a little cheeky; honest when it matters.

**(c) Looks.**
- Neutral (ready to go): big tall-oval eyes with a second sparkle pixel; the left brow level, the right cocked (rows 17-18); a lopsided smirk rising to the right (row 30 cols 20-22, row 29 cols 23-25, row 28 cols 26-27); blush 4x2.
- Concerned (earnest, the erased-routes admission): the eyes drop and slide one pixel down and left (a glance away); the brows climb steeply on the inner ends; a small pressed mouth off centre at (19,29), (18,30). No grin anywhere.
- Pleased (proud): closed arc eyes, both brows lifted to row 17, a toothy smile (teeth in the paper's lightest step).

**(d) Signature: `mira_grin`.** A wink (left eye open, right a closed arc), the right brow higher still, a wide open grin with the tongue out (coral `d`). Source: the "playful grin" portrait in mira.md.

## Noor

**(a) Physical.** The tall, narrow cast member: the longest, narrowest head (cols 8-39, chin on row 38) and the narrowest shoulders (cols 10-37). Blue-black crop with two crown tufts of different size and a notch between, a heavy left lock and a stepped right hairline. Linen shirt with a V neck and a dark neck line. The coral folder is held against her left (screen-left) shoulder, overlapping the shirt edge. Noor uses she/her (player decision, 2026-10-02).

**(b) Emotional profile.** "Precise, with dry humor; quietly defiant" (noor.md); "Pace insists the copy is equivalent" and Noor corrects it anyway (level 11). Understated: the feelings are small and sideways.

**(c) Looks.**
- Neutral (dry): half-lidded eyes (flat upper lid on row 24, iris row 25, `.oo.` on row 26); brows that never match, the left on row 21 and the right on row 20; a flat mouth on row 31 (cols 21-25) with one corner up at (26,30); a tiny pale-pink 2x2 blush.
- Concerned (skeptical, defiant): the left brow drops toward the nose, the right arches high; the mouth is flat with one corner pulled down at (26,32). A frown on one side only.
- Pleased (quietly satisfied): the squint-smile (lids rise to meet: `oooo` over `.oo.`); a one-sided closed smile that climbs at (25,30) and (26,29); no teeth.

**(d) Signature: `noor_unimpressed`.** The lids go flat (two rows), the glance slides one pixel right, both brows sit flat and low, the mouth is dead flat, no blush. Source: "(a) dry, unimpressed" in noor.md.

## Hal

**(a) Physical.** Compact: the broadest, lowest head (40 px wide, rows 5-36). Sandy mop with three outline-capped crown spikes, a fringe that dips to uneven points, side locks that stop above the ears. Cobalt vest with stone sleeves at both edges, a stone shirt V, a chest pocket on the left. The orange tool roll with two steel tips at the lower right.

**(b) Emotional profile.** "Practical and hands-on; anxious when the system misbehaves, focused once a fix is in sight" (hal.md); portraits "Anxious (before the Alarm Glyphs fix)", "Focused (after)", puzzled. His tells are the brows and the eyes.

**(c) Looks.**
- Neutral (focused, practical): round 4x4 eyes; brows slant in toward the nose (2 px steps on rows 19-20); a short pursed line on row 29 (cols 21-26); blush 4x2.
- Concerned (anxious): the eyes grow to 5x5 with two glints; the brows climb steeply; a wobbling mouth (alternating rows 29-30); a bead of sweat (the vest's light blue) at (38,19). Wide eyes, not tears.
- Pleased (settled focus): the eyes stay open, the lower lid rises (4x3 with a flat bottom); brows level and low; a lopsided confident smile climbing at (26,28) and (27,27). The only pleased look in the cast with open eyes.

**(d) Signature: `hal_puzzled`.** One big 5x5 eye and one small 4x3 eye, one brow high (rows 16-17) and one low (row 21), a squiggle mouth off centre. Source: the "Puzzled" reaction and portrait in hal.md.

## Ada

**(a) Physical.** A soft round head under a warm-white cloud: three scalloped bumps with ink notches, strand lines where clusters meet, an uneven fringe. Deepest skin ramp in the cast. Moss coat with a skin V neck, lapel creases, two buttons; the lantern's top at the lower right. The warm lantern is the "warm light on one side" cue (decision 9 in PORTRAITS_SPEC); no face rim is drawn.

**(b) Emotional profile.** "Direct, kind, practical about recovery. Calm" (ada.md); "a locked tool need not mean a locked route" (level 18). She states things plainly and is warm underneath.

**(c) Looks.**
- Neutral (calm): a heavy shaded upper lid over each dot (the skin shade on row 23) for a steady, unhurried gaze; low even 5 px brows on row 20; a straight serene mouth on row 29 with a small lower lip at (23,30); blush 3x2.
- Concerned (serious, instructive): the lids lift (full 4x4 eyes); brows 5 px, level and low; a firm level 8 px line on row 30. Firm, not afraid.
- Pleased (warm): serene closed eyes (resting lids, `o..o` over `.oo.`); a wide gentle smile (ends at (19,28) and (28,28), cols 20-27 on row 29); the broadest blush in the cast (5x2).

**(d) Signature.** None specified beyond the three standard looks (the docs name calm, instructive and warm only).

## Vale

**(a) Physical.** Squarer and stiffer: flat top, flat 24 px chin, the only flat square shoulders (full width from row 38). Graphite hair: a cowlick, a short skin-coloured side part left of centre, diagonal strand lines, a long centre lock. Navy suit with seams, a pale shirt V, the green tie, the copper badge.

**(b) Emotional profile.** "Wants a defensible audit once shown the evidence. Starts rigid, softens across the three final repairs" (vale.md). Composed, then unsettled by the evidence, then resolved. The arc must show in the face.

**(c) Looks.**
- Neutral (composed, rigid): small squared 4x3 eyes; straight 5 px brows on row 20; a dead-level 8 px mouth on row 30; **no blush**.
- Concerned (unsettled): the eyes widen to round 4x4; the brows pinch up in four steps; the line gives way into a small frown (ends at (21,32) and (26,32)). Still no blush: he is not embarrassed, he is shaken.
- Pleased (restrained): the same squared eyes, the brows lift one pixel, the corners of the mouth rise by one pixel, a faint 2x1 blush appears. An almost-smile.

**(d) Signature: `vale_softened`.** The first real softening: the lids ease (`oooo` over `o5oo` over `.oo.`), the brows relax into arches, a real closed-lip smile (ends two rows up, cols 20-27), a full 3x2 blush. Source: "softens across the three final repairs" and "Vale releases the raw audit" (levels.md level 20).

## How the set reads at x4

`portraits-compare.png` puts one expression type per row. At x4 no two characters share a concerned or a pleased face: the concerned set differs by brow shape (inner-up, single arch, steep, drop-and-lift, pinch, level), eye size and mouth (ring, dash, pressed, one-corner-down, wobble, firm line, frown). The checker also requires every pair to differ by at least 14 feature pixels (ink, brow, glint) in each standard expression.
