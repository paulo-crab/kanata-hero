"""Rebuild every generated art file and run every check, in dependency order.

Run from the repo root:  python3 art-direction/build_all.py   (Python 3 with Pillow and numpy;
jsonschema is optional, check_atlas.py falls back to a built-in validator).

PNG, GIF and JSON files under art-direction/ are outputs of these steps and are never hand-edited.
The builds are deterministic: on a clean checkout, a full run leaves `git status` unchanged.
Exit code 1 if any step fails.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAST = ["engineer", "ivo", "mira", "noor", "hal", "ada", "vale"]

STEPS = [
    # (folder, script, args)
    ("palettes", "check_palettes.py", []),
    ("palettes", "build_palettes.py", []),
    ("gate1", "build_gate1.py", []),
    *[("gate1", "check_gate1.py", [f"{c}_sprites"]) for c in CAST],
    *[("cast", "build_cast.py", [c]) for c in CAST],
    ("cast", "build_noor_room.py", []),
    ("cast", "build_hal_room.py", []),
    ("cast", "build_ada_room.py", []),
    ("cast", "build_vale_room.py", []),
    ("gate1", "check_gate1.py", ["bgworker_a_sprites"]),
    ("gate1", "check_gate1.py", ["bgworker_b_sprites"]),
    ("cast", "check_bgworkers.py", []),
    ("cast", "build_bgworkers.py", []),
    ("cast", "check_mira_patches.py", []),
    ("cast", "build_mira_patches.py", []),
    ("glitches", "check_glitches.py", []),
    ("glitches", "build_glitches.py", []),
    ("pace", "check_pace.py", []),
    ("pace", "build_pace.py", []),
    ("portraits", "check_portraits.py", []),
    ("portraits", "build_portraits.py", []),
    ("kit", "build_kit.py", []),          # Orientation atlas, garden states, zero-diff room rebuild
    ("kit", "build_records.py", []),
    ("kit", "build_systems.py", []),
    ("kit", "build_nightshift.py", []),
    ("kit", "build_executive.py", []),
    ("kit", "check_atlas.py", []),        # validates every *-atlas.json and *-reference-room.json
    ("ui-kit", "check_contrast.py", []),
    ("ui-kit", "build_world.py", []),
    ("ui-kit", "build_reference.py", []),
    (".", "check_handoff.py", []),        # every path listed in ART_HANDOFF.md exists
]


def main():
    failed = []
    for folder, script, args in STEPS:
        cwd = os.path.join(HERE, folder)
        label = f"{folder}/{script} {' '.join(args)}".strip()
        r = subprocess.run([sys.executable, script, *args], cwd=cwd, capture_output=True, text=True)
        last = (r.stdout.strip().splitlines() or [""])[-1]
        print(f"{'ok  ' if r.returncode == 0 else 'FAIL'} {label:44} {last[:90]}")
        if r.returncode:
            failed.append(label)
            sys.stdout.write(r.stdout[-2000:] + r.stderr[-2000:])
    print(f"\n{len(STEPS) - len(failed)}/{len(STEPS)} steps passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
