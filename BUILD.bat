@echo off
echo ============================================
echo  PrintSimp Pro - Build Script
echo ============================================
echo.

echo [1/2] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: pip install failed. Make sure Python is installed and on your PATH.
    pause
    exit /b 1
)

echo.
echo [2/2] Building executable...
pyinstaller --onefile --noconsole --name PrintSimpPro ^
  --hidden-import win32clipboard ^
  --hidden-import win32api ^
  --hidden-import pywintypes ^
  print_simp_pro_windows_screenshot_tool.py
if %errorlevel% neq 0 (
    echo ERROR: Build failed. See output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Done! Your file is at:  dist\PrintSimpPro.exe
echo  Copy it anywhere and double-click to run.
echo  Press Ctrl+Shift+P to take a screenshot.
echo  Screenshots go to: Pictures\Screenshots\
echo ============================================
pause
