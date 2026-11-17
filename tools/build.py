"""Build dist/l4d2.apworld, dist/archipelago.vpk and dist/L4D2 Archipelago Installer.exe.

Needs: pip install vpk pyinstaller pillow
Usage: python tools/build.py [--no-exe]
"""
import json
import os
import subprocess
import sys
import zipfile

import vpk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
WORLD = os.path.join(ROOT, "apworld", "l4d2")


def build_apworld() -> str:
    out = os.path.join(DIST, "l4d2.apworld")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for folder, dirs, files in os.walk(WORLD):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in files:
                path = os.path.join(folder, name)
                arc = os.path.join("l4d2", os.path.relpath(path, WORLD))
                if name == "archipelago.json":
                    manifest = json.load(open(path, encoding="utf-8"))
                    manifest.update(version=7, compatible_version=7)  # APContainer format, see worlds/Files.py
                    z.writestr(arc, json.dumps(manifest, indent=2))
                else:
                    z.write(path, arc)
    return out


def build_vpk() -> str:
    out = os.path.join(DIST, "archipelago.vpk")
    pak = vpk.new(os.path.join(ROOT, "addon"))
    pak.version = 1  # L4D2 only loads VPK v1 ("Unknown version 2 for vpk"); the library defaults to v2
    pak.save(out)
    with open(out, "rb") as f:
        assert f.read(8) == b"\x34\x12\xaa\x55\x01\x00\x00\x00", "archipelago.vpk is not VPK v1"
    return out


def build_exe() -> str:
    sep = os.pathsep
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", "--windowed",
        "--name", "L4D2 Archipelago Installer",
        "--distpath", DIST, "--workpath", os.path.join(ROOT, "build"), "--specpath", os.path.join(ROOT, "build"),
        "--add-data", f"{os.path.join(DIST, 'l4d2.apworld')}{sep}.",
        "--add-data", f"{os.path.join(DIST, 'archipelago.vpk')}{sep}.",
        os.path.join(ROOT, "installer", "installer.py"),
    ])
    return os.path.join(DIST, "L4D2 Archipelago Installer.exe")


if __name__ == "__main__":
    os.makedirs(DIST, exist_ok=True)
    print(build_apworld())
    print(build_vpk())
    if "--no-exe" not in sys.argv:
        print(build_exe())
