# PrintSimp Pro: User Guide

PrintSimp Pro is a lightweight, open-source productivity tool for Windows designed to streamline screen capturing. It eliminates the extra steps of traditional snipping tools by allowing you to instantly select a region, save it to your drive, and copy it to your clipboard with a single keyboard shortcut.

- Speed-Focused: Triggered instantly via Ctrl + Shift + P.

- Dual-Action: Simultaneously saves a high-quality PNG to your Pictures/Screenshots folder and stores the image in your clipboard for immediate pasting.

- Minimalist Design: Runs silently in the background with no intrusive windows or complex menus.

- Smart Selection: Features a visual crosshair and a red-boundary selector for pixel-perfect captures.

--------------------------------
1. Installation & Setup

    Run the Executable: Open the PrintSimp.exe file. The program runs silently in the background and does not open a visible window upon startup.

    Storage Location: All captured screenshots are automatically saved to your standard Windows Pictures folder:
    C:\Users\[YourName]\Pictures\Screenshots

2. How to Capture

    Trigger: Press Ctrl + Shift + P on your keyboard.

    Select: Your screen will freeze into a static image and your cursor will change to a crosshair.

    Draw: Click and hold the Left Mouse Button, then drag to draw a red box around the area you wish to save.

    Finalize: Release the mouse button to complete the capture.

3. Key Features

    Auto-Save: The selected area is immediately saved as a timestamped PNG file.

    Instant Paste: The image is simultaneously copied to your clipboard. You can immediately press Ctrl + V to paste it into Discord, Slack, Word, or any other application.

    Cancel Capture: If you trigger the tool by mistake, press the Escape (Esc) key to exit selection mode without saving.

4. Technical Notes

    Background Operation: The tool uses minimal system resources while waiting for the hotkey.

    Multi-Monitor Support: The tool captures the entire desktop area across all connected monitors.

    Selection Safety: Very small selections (less than 5x5 pixels) are ignored to prevent accidental "empty" files.
