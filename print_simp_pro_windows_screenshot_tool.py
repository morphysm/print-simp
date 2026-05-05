# PrintSimp Pro - Windows Screenshot Tool
# Ctrl+Shift+P: drag to select region → auto-save to Pictures/Screenshots + clipboard copy
# Runs silently in background; Escape cancels a selection

import ctypes
import io
import logging
import os
import queue
import subprocess
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path

import mss
import pystray
from pynput import keyboard
from PIL import Image, ImageDraw, ImageTk
import win32clipboard

logging.basicConfig(level=logging.ERROR)

SAVE_FOLDER = Path.home() / "Pictures" / "Screenshots"
SAVE_FOLDER.mkdir(parents=True, exist_ok=True)

_capture_queue = queue.Queue()
_is_selecting = False


def _set_dpi_aware():
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
    except (AttributeError, OSError):
        ctypes.windll.user32.SetProcessDPIAware()


class ScreenCapture:
    def grab_fullscreen(self):
        with mss.mss() as sct:
            monitor = sct.monitors[0]  # monitors[0] = all screens combined
            shot = sct.grab(monitor)
            return Image.frombytes("RGB", shot.size, shot.rgb)


class AreaSelector:
    def __init__(self, image):
        self.image = image
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.canvas = tk.Canvas(self.root, cursor="cross", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        # Dark tint overlay to signal the tool is active
        w, h = image.width, image.height
        self.canvas.create_rectangle(0, 0, w, h, fill="black", stipple="gray25", outline="")

        self.start_x = self.start_y = 0
        self.rect = None

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def _on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )

    def _on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def _on_release(self, event):
        end_x, end_y = event.x, event.y
        self.root.destroy()
        _save_and_copy(self.image, self.start_x, self.start_y, end_x, end_y)

    def run(self):
        self.root.mainloop()


def _save_and_copy(image, x1, y1, x2, y2):
    x, y = min(x1, x2), min(y1, y2)
    w, h = abs(x2 - x1), abs(y2 - y1)
    if w < 5 or h < 5:
        return

    cropped = image.crop((x, y, x + w, y + h))

    filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S_%f.png")
    path = SAVE_FOLDER / filename
    try:
        cropped.save(path)
    except Exception as e:
        logging.error("Failed to save screenshot: %s", e)

    try:
        _copy_to_clipboard(cropped)
    except Exception as e:
        logging.error("Failed to copy to clipboard: %s", e)


def _copy_to_clipboard(img):
    output = io.BytesIO()
    img.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]  # strip 14-byte BMP file header, keep the DIB payload
    output.close()

    for attempt in range(3):
        try:
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            finally:
                win32clipboard.CloseClipboard()
            return
        except Exception as e:
            if attempt < 2:
                time.sleep(0.05)
    logging.error("Failed to copy image to clipboard after 3 attempts")


def _make_scissors_icon():
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = (180, 180, 180, 255)
    draw.ellipse((1, 1, 13, 13), outline=c, width=2)   # top finger ring
    draw.ellipse((1, 19, 13, 31), outline=c, width=2)  # bottom finger ring
    draw.ellipse((14, 14, 18, 18), fill=c)             # pivot dot
    draw.line((7, 7, 31, 1), fill=c, width=2)          # top blade
    draw.line((7, 25, 31, 31), fill=c, width=2)        # bottom blade
    return img


def _start_tray(listener):
    def take_screenshot(icon, item):
        if not _is_selecting:
            _capture_queue.put(True)

    def open_folder(icon, item):
        subprocess.Popen(["explorer", str(SAVE_FOLDER)])

    def quit_app(icon, item):
        icon.stop()
        listener.stop()
        os._exit(0)

    icon = pystray.Icon(
        "PrintSimp Pro",
        _make_scissors_icon(),
        "PrintSimp Pro",
        menu=pystray.Menu(
            pystray.MenuItem("Take Screenshot", take_screenshot),
            pystray.MenuItem("Open Screenshots Folder", open_folder),
            pystray.MenuItem("Quit", quit_app),
        ),
    )
    icon.run()


def main():
    global _is_selecting

    _set_dpi_aware()

    def _on_hotkey():
        if not _is_selecting:
            _capture_queue.put(True)

    listener = keyboard.GlobalHotKeys({"<ctrl>+<shift>+p": _on_hotkey})
    listener.start()

    threading.Thread(target=_start_tray, args=(listener,), daemon=True).start()

    # tkinter must run on the main thread on Windows — hotkey pushes a signal,
    # main thread polls and opens the selector here instead of in a daemon thread
    while True:
        try:
            _capture_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        _is_selecting = True
        img = ScreenCapture().grab_fullscreen()
        AreaSelector(img).run()
        _is_selecting = False


if __name__ == "__main__":
    main()
