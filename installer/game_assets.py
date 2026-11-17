"""Read art, fonts and sounds straight out of the player's own Left 4 Dead 2 install.

Nothing from the game is bundled with the installer; if the game isn't found, the UI falls back to plain colors.
"""
import io
import os
import struct

import vpk
from PIL import Image

VFONT_MAGIC, VFONT_TRICK = b"VFONT1", 167
# VTF image format id -> (Pillow decoder args, bytes per 4x4 block or per pixel, is_block_compressed)
VTF_FORMATS = {
    0: (("raw", "RGBA"), 4, False), 2: (("raw", "RGB"), 3, False), 3: (("raw", "BGR"), 3, False),
    12: (("raw", "BGRA"), 4, False), 13: (("bcn", 1), 8, True), 14: (("bcn", 2), 16, True),
    15: (("bcn", 3), 16, True),
}


def decode_vfont(data: bytes) -> bytes:
    """Undo Valve's VFONT1 obfuscation (port of ValveResourceFormat's ValveFont.Decode)."""
    if not data.endswith(VFONT_MAGIC):
        raise ValueError("not a VFONT1 file")
    count = data[-len(VFONT_MAGIC) - 1]
    salt = data[-len(VFONT_MAGIC) - count:-len(VFONT_MAGIC) - 1]
    magic = VFONT_TRICK
    for b in salt:
        magic ^= (b + VFONT_TRICK) % 256
    out = bytearray(data[:len(data) - len(VFONT_MAGIC) - count])
    for i, b in enumerate(out):
        out[i] = b ^ magic
        magic = (b + VFONT_TRICK) % 256
    return bytes(out)


def decode_vtf(data: bytes) -> Image.Image:
    """Largest mip of frame 0. shortcut: assumes the high-res image block ends the file (true for 2D UI art)."""
    if data[:4] != b"VTF\0":
        raise ValueError("not a VTF file")
    width, height = struct.unpack_from("<HH", data, 16)
    frames = struct.unpack_from("<H", data, 24)[0]
    fmt = struct.unpack_from("<i", data, 52)[0]
    if fmt not in VTF_FORMATS:
        raise ValueError(f"unsupported VTF format {fmt}")
    args, unit, blocks = VTF_FORMATS[fmt]
    size = ((width + 3) // 4) * ((height + 3) // 4) * unit if blocks else width * height * unit
    start = len(data) - size * frames
    mode = "RGB" if args[0] == "raw" and len(args[1]) == 3 else "RGBA"
    return Image.frombytes(mode, (width, height), data[start:start + size], *args)


class GameAssets:
    def __init__(self, game_dir: str):
        self.root = os.path.join(game_dir, "left4dead2")
        self.pak = vpk.open(os.path.join(self.root, "pak01_dir.vpk"))

    def image(self, path: str) -> Image.Image:
        return decode_vtf(self.pak.get_file(path).read())

    def font_file(self, name: str, out_dir: str) -> str:
        """Decode resource/<name>.vfont to a .ttf in out_dir and return its path."""
        with open(os.path.join(self.root, "resource", name + ".vfont"), "rb") as f:
            ttf = decode_vfont(f.read())
        out = os.path.join(out_dir, name + ".ttf")
        with open(out, "wb") as f:
            f.write(ttf)
        return out

    def sound(self, name: str) -> bytes | None:
        path = os.path.join(self.root, "sound", "ui", name)
        if os.path.isfile(path):
            return open(path, "rb").read()
        try:
            return self.pak.get_file(f"sound/ui/{name}").read()
        except KeyError:
            return None


if __name__ == "__main__":  # self-check: decode the art we use and dump PNGs for a look
    import sys
    assets = GameAssets(sys.argv[1])
    out = sys.argv[2]
    for p in ["materials/vgui/resource/logo_game.vtf", "materials/console/background_menu_widescreen.vtf",
              "materials/console/background01_widescreen.vtf", "materials/vgui/loadingscreen_nomercy.vtf",
              "materials/vgui/loadingscreen_default.vtf"]:
        img = assets.image(p)
        img.save(os.path.join(out, os.path.basename(p) + ".png"))
        print(p, img.size, img.mode)
    from PIL import ImageFont
    ttf = assets.font_file("tgb", out)
    assert ImageFont.truetype(ttf, 20).getname()[0], "font did not decode"
    print("font:", ImageFont.truetype(ttf, 20).getname())
    print("click sound bytes:", len(assets.sound("menu_click01.wav") or b""))
