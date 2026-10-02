#!/usr/bin/env python3
"""Renders every UI kit screen of reference.html to a 1366 x 768 PNG with headless Edge or Chrome.

Not part of build_all.py (it needs a browser). Run after build_reference.py when a screen changes:

    python3 render_screens.py              # all screens
    python3 render_screens.py layout-nav   # one screen (the #s-<id> target)

Each screen section has two targets: #s-<id> (colour) and #s-<id>-grey (forced greyscale, the
colour-blind check). Colour renders go to screens/<id>-1366x768.png; the screens in GREY are also
rendered to screens/<id>-grey-1366x768.png. The stage inside is 1280 x 720 (world x4), letterboxed.
Set KH_BROWSER to the browser executable if it is not found.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screens")
CANDIDATES = [
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
# Screens whose meaning is carried by shape and text rather than colour: also rendered in greyscale.
GREY = {"layout-practice", "setup-calibration", "input-feedback", "glitch-duel", "elevator-map", "seal-award"}


def browser():
    for c in [os.environ.get("KH_BROWSER", "")] + CANDIDATES:
        if c and os.path.exists(c):
            return c
    sys.exit("no Edge or Chrome found; set KH_BROWSER")


def shoot(exe, frag, path):
    url = "file://" + os.path.join(HERE, "reference.html") + "#" + frag
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1366,768", "--virtual-time-budget=2000", "--screenshot=" + path, url],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    html = open(os.path.join(HERE, "reference.html"), encoding="utf-8").read()
    ids = re.findall(r'<span class="a" id="s-([\w-]+)">', html)
    want = sys.argv[1:] or ids
    os.makedirs(OUT, exist_ok=True)
    exe = browser()
    for sid in want:
        if sid not in ids:
            sys.exit("unknown screen " + sid)
        shoot(exe, f"s-{sid}", os.path.join(OUT, f"{sid}-1366x768.png"))
        print("rendered", sid)
        if sid in GREY:
            shoot(exe, f"s-{sid}-grey", os.path.join(OUT, f"{sid}-grey-1366x768.png"))
            print("rendered", sid, "(greyscale)")


if __name__ == "__main__":
    main()
