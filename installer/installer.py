"""One-click installer + launcher for the Left 4 Dead 2 Archipelago mod.

Installs l4d2.apworld into Archipelago/custom_worlds and archipelago.vpk into left4dead2/addons,
points Archipelago's host.yaml at the game, and offers buttons to start the client and the game.
The look (menu background, Trade Gothic font, UI sounds) is read from the player's own L4D2 install.
"""
import ctypes
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
import tkinter.font
import winsound
from tkinter import filedialog

from PIL import Image, ImageChops, ImageTk

from game_assets import GameAssets

APWORLD = "l4d2.apworld"
VPK = "archipelago.vpk"
BACKGROUND = "materials/console/background_menu_widescreen.vtf"
SETTINGS = os.path.join(os.environ.get("LOCALAPPDATA", tempfile.gettempdir()), "L4D2Archipelago", "launcher.json")

ITEM, ITEM_HOVER, ITEM_OFF = "#b4b4b4", "#ffffff", "#5a5a5a"
MUTED, OK, BAD, WAIT = "#9a9a9a", "#7fcf6a", "#e0453a", "#d9a400"
GAME_FONT, LOGO_FONT, FALLBACK_FONT = "Trade Gothic Bold", "Future Rot", "Segoe UI Semibold"


def payload(name: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist"))
    return os.path.join(base, name)


def steam_path() -> str | None:
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            return os.path.normpath(winreg.QueryValueEx(key, "SteamPath")[0])
    except OSError:
        return None


def find_l4d2() -> str:
    steam = steam_path()
    libraries = [steam] if steam else []
    try:
        with open(os.path.join(steam, "steamapps", "libraryfolders.vdf"), encoding="utf-8") as f:
            libraries += [p.replace("\\\\", "\\") for p in re.findall(r'"path"\s+"([^"]+)"', f.read())]
    except (OSError, TypeError):
        pass
    libraries.append(r"C:\Program Files (x86)\Steam")
    for lib in libraries:
        game = os.path.join(lib, "steamapps", "common", "Left 4 Dead 2")
        if is_l4d2(game):
            return game
    return ""


def find_archipelago() -> str:
    for path in (r"C:\ProgramData\Archipelago", os.path.expandvars(r"%LOCALAPPDATA%\Archipelago")):
        if is_archipelago(path):
            return path
    return ""


def is_l4d2(path: str) -> bool:
    return bool(path) and os.path.isdir(os.path.join(path, "left4dead2"))


def is_archipelago(path: str) -> bool:
    return bool(path) and os.path.isfile(os.path.join(path, "ArchipelagoLauncher.exe"))


def set_host_yaml(ap_dir: str, game_dir: str) -> None:
    """Tell the Archipelago client where L4D2 is, so it never has to ask."""
    host = os.path.join(ap_dir, "host.yaml")
    text = open(host, encoding="utf-8").read() if os.path.isfile(host) else ""
    block = f'l4d2_options:\n  game_folder: "{game_dir.replace(os.sep, "/")}"\n'
    if re.search(r"^l4d2_options:\n(  .*\n?)*", text, re.M):
        text = re.sub(r"^l4d2_options:\n(  .*\n?)*", block, text, flags=re.M)
    else:
        text += ("" if text.endswith("\n") or not text else "\n") + block
    with open(host, "w", encoding="utf-8") as f:
        f.write(text)


def install(ap_dir: str, game_dir: str) -> None:
    shutil.copy2(payload(APWORLD), os.path.join(ap_dir, "custom_worlds", APWORLD))
    shutil.copy2(payload(VPK), os.path.join(game_dir, "left4dead2", "addons", VPK))
    set_host_yaml(ap_dir, game_dir)


def is_installed(ap_dir: str, game_dir: str) -> bool:
    return (is_archipelago(ap_dir) and is_l4d2(game_dir)
            and os.path.isfile(os.path.join(ap_dir, "custom_worlds", APWORLD))
            and os.path.isfile(os.path.join(game_dir, "left4dead2", "addons", VPK)))


def client_command(ap_dir: str, server: str, slot: str, password: str) -> list[str]:
    """Run the Left 4 Dead 2 Client from the user's Archipelago install, without its window."""
    exe = os.path.join(ap_dir, "ArchipelagoLauncherDebug.exe")  # console build, so its output can be piped
    if not os.path.isfile(exe):
        exe = os.path.join(ap_dir, "ArchipelagoLauncher.exe")
    args = [exe, "Left 4 Dead 2 Client", "--", "--nogui", "--connect", server, "--name", slot]
    return args + ["--password", password] if password else args


def load_settings() -> dict:
    try:
        with open(SETTINGS, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_settings(data: dict) -> None:
    os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
    with open(SETTINGS, "w", encoding="utf-8") as f:
        json.dump(data, f)  # server + slot only; the password is never written to disk


class App(tk.Tk):
    """Single canvas styled like the L4D2 main menu; render() redraws everything after each state change."""

    def __init__(self):
        super().__init__()
        self.title("Left 4 Dead 2 - Archipelago")
        self.resizable(False, False)
        self.s = self.winfo_fpixels("1i") / 96  # Windows display scaling
        self.w, self.h = self.px(960), self.px(540)
        self.canvas = tk.Canvas(self, width=self.w, height=self.h, highlightthickness=0, bg="#000")
        self.canvas.pack()
        self.tmp = tempfile.mkdtemp(prefix="l4d2ap_")
        self.game_dir, self.ap_dir = find_l4d2(), find_archipelago()
        self.message, self.message_color = "", MUTED
        self.client, self.connected, self.client_line, self.lines = None, False, "", queue.Queue()
        saved = load_settings()
        self.server = tk.StringVar(value=saved.get("server", "archipelago.gg:"))
        self.slot = tk.StringVar(value=saved.get("slot", ""))
        self.password = tk.StringVar()
        self.load_assets()
        self.entries = [self.make_entry(self.server), self.make_entry(self.slot), self.make_entry(self.password, "*")]
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.render()
        self.after(300, self.poll_client)

    def px(self, v: float) -> int:
        return int(v * self.s)

    # --- game assets -------------------------------------------------------------------------------------------
    def load_assets(self):
        self.art, self.font, self.logo_font, self.sounds = None, FALLBACK_FONT, FALLBACK_FONT, {}
        try:
            assets = GameAssets(self.game_dir)
            self.art = assets.image(BACKGROUND)
            for file, family, attr in (("tgb", GAME_FONT, "font"), ("futurot", LOGO_FONT, "logo_font")):
                ttf = assets.font_file(file, self.tmp)
                if ctypes.windll.gdi32.AddFontResourceExW(ttf, 0x10, 0) and family in tkinter.font.families():
                    setattr(self, attr, family)  # 0x10 = FR_PRIVATE: only this process sees the font
            for key, name in (("hover", "buttonrollover.wav"), ("click", "buttonclick.wav")):
                data = assets.sound(name)
                if data:
                    path = os.path.join(self.tmp, name)
                    with open(path, "wb") as f:
                        f.write(data)
                    self.sounds[key] = path
        except Exception:  # purely cosmetic: no game found or unexpected files -> plain look
            pass
        try:
            self.iconbitmap(os.path.join(self.game_dir, "left4dead2.exe"))  # Tk can read an .exe's icon
        except tk.TclError:
            pass
        self.bg_img, self.bar_img = self.background(), self.hover_bar()
        self.panel_img = ImageTk.PhotoImage(Image.new("RGBA", (self.px(290), self.px(250)), (0, 0, 0, 150)))

    def play(self, key: str):
        if key in self.sounds:
            winsound.PlaySound(self.sounds[key], winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)

    def background(self) -> ImageTk.PhotoImage:
        if self.art:
            img = self.art.convert("RGB").resize((self.w, self.h), Image.LANCZOS)  # widescreen art is stored squashed
        else:
            img = Image.new("RGB", (self.w, self.h), "#0b0c0e")
        ramp = Image.linear_gradient("L")
        left = ramp.rotate(90).resize((self.w, self.h)).point(lambda v: max(0, 235 - int(v * 1.5)))
        bottom = ramp.resize((self.w, self.h)).point(lambda v: max(0, (v - 150) * 2))
        shade = ImageChops.lighter(left, bottom)
        return ImageTk.PhotoImage(Image.composite(Image.new("RGB", img.size), img, shade))

    def hover_bar(self) -> ImageTk.PhotoImage:
        w, h = self.px(380), self.px(36)
        alpha = Image.linear_gradient("L").rotate(90).resize((w, h)).point(lambda v: int(150 * (1 - v / 255)))
        bar = Image.new("RGBA", (w, h), (150, 20, 20, 0))
        bar.putalpha(alpha)
        return ImageTk.PhotoImage(bar)

    def make_entry(self, var: tk.StringVar, show: str = "") -> tk.Entry:
        entry = tk.Entry(self, textvariable=var, show=show, bg="#111214", fg="#ececec", insertbackground="#ececec",
                         relief="flat", highlightthickness=1, highlightbackground="#3a3a3a", highlightcolor="#9c1c1c")
        entry.bind("<Return>", lambda _: self.client or self.toggle_client())
        return entry

    # --- drawing -----------------------------------------------------------------------------------------------
    def text(self, x, y, s, size, color, anchor="w", tags=(), family=None):
        font = (family or self.font, -self.px(size))
        self.canvas.create_text(x + self.px(2), y + self.px(2), text=s, font=font, fill="#000", anchor=anchor,
                                tags=tags)
        return self.canvas.create_text(x, y, text=s, font=font, fill=color, anchor=anchor, tags=tags)

    def render(self):
        c = self.canvas
        c.delete("all")
        c.create_image(0, 0, image=self.bg_img, anchor="nw")

        # under the game logo, which sits top-right in the menu art
        if not self.art:
            self.text(self.px(745), self.px(118), "LEFT 4 DEAD 2", 44, "#c0201a", "center")
        self.text(self.px(745), self.px(164), "ARCHIPELAGO", 30, "#ececec", "center", family=self.logo_font)
        self.text(self.px(745), self.px(194), "MULTIWORLD RANDOMIZER", 14, "#bdbdbd", "center", family=self.logo_font)

        ready = is_l4d2(self.game_dir) and is_archipelago(self.ap_dir)
        installed = is_installed(self.ap_dir, self.game_dir)
        items = [
            ("REINSTALL / UPDATE" if installed else "INSTALL", self.do_install, ready),
            ("DISCONNECT" if self.client else "CONNECT", self.toggle_client, installed),
            ("PLAY ARCHIPELAGO", self.start_game, installed and steam_path() is not None),
            ("SET GAME FOLDER", lambda: self.browse("game"), True),
            ("SET ARCHIPELAGO FOLDER", lambda: self.browse("ap"), True),
            ("QUIT", self.quit_app, True),
        ]
        bar = c.create_image(0, 0, image=self.bar_img, anchor="w", state="hidden")
        for i, (label, action, enabled) in enumerate(items):
            x, y, tag = self.px(64), self.px(178 + i * 42), f"item{i}"
            self.text(x, y, label, 26, ITEM if enabled else ITEM_OFF, tags=(tag,))
            if enabled:
                self.bind_item(tag, action, bar, x, y)

        message, color = self.message, self.message_color
        if not message:
            message, color = (
                ("Enter your room, connect, then play. Keep this window open while you play.", OK) if installed else
                ("Ready to install." if ready else "Set both folders to continue.", MUTED if ready else BAD))
        self.text(self.px(64), self.px(452), message, 15, color)
        self.render_connection()
        for row, (name, path, ok) in enumerate((("LEFT 4 DEAD 2", self.game_dir, is_l4d2(self.game_dir)),
                                                 ("ARCHIPELAGO", self.ap_dir, is_archipelago(self.ap_dir)))):
            y = self.px(486 + row * 24)
            c.create_oval(self.px(64), y - self.px(4), self.px(72), y + self.px(4), fill=OK if ok else BAD, width=0)
            self.text(self.px(82), y, name, 13, ITEM)
            self.text(self.px(230), y, path or "not found", 13, MUTED)

    def render_connection(self):
        """Room details panel under the title, with the hidden client's live status."""
        c, x = self.canvas, self.px(620)
        c.create_image(self.px(600), self.px(222), image=self.panel_img, anchor="nw")
        for i, (label, entry) in enumerate(zip(("SERVER", "SLOT NAME", "PASSWORD"), self.entries)):
            y = self.px(244 + i * 58)
            self.text(x, y, label, 13, MUTED)
            entry.config(font=(self.font, -self.px(15)), state="disabled" if self.client else "normal",
                         disabledbackground="#0c0d0e", disabledforeground="#8a8a8a")
            c.create_window(x, y + self.px(22), window=entry, anchor="w", width=self.px(250), height=self.px(28))
        if self.connected:
            status, color = f"CONNECTED AS {self.slot.get().upper()}", OK
        elif self.client:
            status, color = "CONNECTING...", WAIT
        else:
            status, color = "NOT CONNECTED", BAD
        y = self.px(424)
        c.create_oval(x, y - self.px(4), x + self.px(8), y + self.px(4), fill=color, width=0)
        self.text(x + self.px(16), y, status, 15, color)
        line = self.client_line if len(self.client_line) <= 44 else self.client_line[:43] + "..."
        self.text(x, self.px(450), line, 12, MUTED)

    def bind_item(self, tag, action, bar, x, y):
        c = self.canvas

        def enter(_):
            for item in c.find_withtag(tag)[1::2]:
                c.itemconfig(item, fill=ITEM_HOVER)
            c.coords(bar, x - self.px(20), y)
            c.itemconfig(bar, state="normal")
            c.tag_raise(tag)
            c.config(cursor="hand2")
            self.play("hover")

        def leave(_):
            for item in c.find_withtag(tag)[1::2]:
                c.itemconfig(item, fill=ITEM)
            c.itemconfig(bar, state="hidden")
            c.config(cursor="")

        def click(_):
            self.play("click")
            self.message = ""
            action()

        c.tag_bind(tag, "<Enter>", enter)
        c.tag_bind(tag, "<Leave>", leave)
        c.tag_bind(tag, "<Button-1>", click)

    # --- actions -----------------------------------------------------------------------------------------------
    def say(self, text, color=MUTED):
        self.message, self.message_color = text, color
        self.render()

    def browse(self, which: str):
        current = self.game_dir if which == "game" else self.ap_dir
        path = filedialog.askdirectory(initialdir=current or None)
        if not path:
            return self.render()
        if which == "game":
            self.game_dir = os.path.normpath(path)
            self.load_assets()
        else:
            self.ap_dir = os.path.normpath(path)
        self.render()

    def do_install(self):
        try:
            install(self.ap_dir, self.game_dir)
        except OSError as e:
            return self.say(f"Install failed: {e}. Close the game and Archipelago, then try again.", BAD)
        self.say("Installed! Restart the Archipelago Launcher if it was open.", OK)

    def toggle_client(self):
        if self.client:
            self.stop_client()
            return self.say("Disconnected.")
        server, slot = self.server.get().strip(), self.slot.get().strip()
        if not server or not slot or server.endswith(":"):
            return self.say("Enter the server address (with port) and your slot name first.", BAD)
        save_settings({"server": server, "slot": slot})
        self.client = subprocess.Popen(
            client_command(self.ap_dir, server, slot, self.password.get()), cwd=self.ap_dir,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", creationflags=subprocess.CREATE_NO_WINDOW)
        threading.Thread(target=self.read_client, args=(self.client,), daemon=True).start()
        self.connected, self.client_line = False, "Starting the Archipelago client..."
        self.say("Connecting in the background. Keep this window open while you play.")

    def read_client(self, proc: subprocess.Popen):
        """Background thread: forward the hidden client's output to the UI thread."""
        for line in proc.stdout:
            self.lines.put((proc, line.strip()))
        self.lines.put((proc, None))

    def poll_client(self):
        changed = False
        while not self.lines.empty():
            proc, line = self.lines.get()
            if proc is not self.client:
                continue  # leftover output from a client we already stopped
            changed = True
            if line is None:
                self.client, self.connected = None, False
                self.client_line = self.client_line or "The client stopped."
            elif line.strip("-") and "Warning" not in line:
                self.client_line = line
                if f"{self.slot.get().strip()} (Team" in line and "has joined" in line:
                    self.connected = True
                    self.message, self.message_color = "Connected! Now PLAY ARCHIPELAGO. Keep this window open.", OK
                elif line.startswith(("Disconnected", "Connection refused")) or "rror" in line:
                    self.connected = False
        if changed:
            self.render()
        self.after(300, self.poll_client)

    def stop_client(self):
        proc, self.client, self.connected = self.client, None, False
        if proc and proc.poll() is None:
            try:
                proc.stdin.write("/exit\n")
                proc.stdin.flush()
                proc.wait(3)
            except (OSError, subprocess.TimeoutExpired):
                proc.kill()

    def quit_app(self):
        self.stop_client()
        self.destroy()

    def start_game(self):
        # Just open the game: the mod works in any Co-op campaign, and a normal lobby lets friends join.
        subprocess.Popen([os.path.join(steam_path(), "steam.exe"), "-applaunch", "550"])
        self.say("Launching Left 4 Dead 2... start any Co-op campaign. Locked ones send you to one you have.", OK)


if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # crisp text on high-DPI screens
    except (AttributeError, OSError):
        pass
    app = App()
    app.update()
    try:  # dark title bar (Windows 10 20H1+)
        hwnd = ctypes.windll.user32.GetParent(app.winfo_id())
        ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(ctypes.c_int(1)), 4)
    except (AttributeError, OSError):
        pass
    app.mainloop()
