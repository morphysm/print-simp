# PrintSimp Pro - Windows Screenshot Tool
# Ctrl+Shift+P: drag to select region → auto-save to Pictures/Screenshots + clipboard copy
# Runs silently in background; Escape cancels a selection

import io
import queue
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path

import mss
from pynput import keyboard
from PIL import Image, ImageTk
import win32clipboard

SAVE_FOLDER = Path.home() / "Pictures" / "Screenshots"
SAVE_FOLDER.mkdir(parents=True, exist_ok=True)

_capture_queue = queue.Queue()


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
        self.canvas.configure(bg="white")
        self.root.after(100, lambda: self._finish(end_x, end_y))

    def _finish(self, end_x, end_y):
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

    filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = SAVE_FOLDER / filename
    cropped.save(path)

    _copy_to_clipboard(cropped)


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
        except Exception:
            if attempt < 2:
                time.sleep(0.05)


def main():
    def _on_hotkey():
        _capture_queue.put(True)

    listener = keyboard.GlobalHotKeys({"<ctrl>+<shift>+p": _on_hotkey})
    listener.start()

    # tkinter must run on the main thread on Windows — hotkey pushes a signal,
    # main thread polls and opens the selector here instead of in a daemon thread
    while True:
        try:
            _capture_queue.get(timeout=0.2)
        except queue.Empty:
            continue

        img = ScreenCapture().grab_fullscreen()
        AreaSelector(img).run()


if __name__ == "__main__":
    main()
