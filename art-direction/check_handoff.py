"""Check that every file path listed in ART_HANDOFF.md exists.

A path is any `backticked` token ending in a known file extension. Paths resolve against
art-direction/ first, then the repo root. A token containing * is a glob and must match at least
one file. Exit code 1 if anything is missing.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXT = (".png", ".gif", ".json", ".py", ".md", ".css", ".html", ".kbd")

text = open(os.path.join(HERE, "ART_HANDOFF.md"), encoding="utf-8").read()
# Skip templates such as `cast/<name>-atlas.png` and suffix fragments such as `-atlas-silhouette.png`.
tokens = sorted({t for t in re.findall(r"`([^`\s]+)`", text)
                 if t.endswith(EXT) and "<" not in t and t[0] not in "~-."})

missing = []
for t in tokens:
    hits = [m for base in (HERE, ROOT) for m in glob.glob(os.path.join(base, t))]
    if not hits:
        missing.append(t)

for m in missing:
    print("MISSING", m)
print(f"{len(tokens)} listed paths checked, {len(missing)} missing")
sys.exit(1 if missing else 0)
