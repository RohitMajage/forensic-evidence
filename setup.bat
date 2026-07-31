@echo off
echo ==================================================
echo Installing Forensic Evidence Project Dependencies
echo ==================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your PATH environment variable.
    echo Please install Python (recommended version 3.9) before running this script.
    pause
    exit /b
)

echo [1/6] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [2/6] Installing Django and core database libraries...
python -m pip install django django-select2 opencv-python numpy scipy Pillow pydub

echo.
echo [3/6] Installing precompiled dlib binary for Windows...
python -m pip install dlib-bin

echo.
echo [4/6] Installing face_recognition...
python -m pip install face-recognition-models
python -m pip install face_recognition --no-deps

echo.
echo [5/6] Installing precompiled webrtcvad binary for Windows...
python -m pip install webrtcvad-wheels

echo.
echo [6/6] Installing torch, librosa, and resemblyzer...
python -m pip install torch librosa
python -m pip install resemblyzer --no-deps

echo.
echo ==================================================
echo Setup completed successfully!
echo You can now use start.bat to run the server.
echo ==================================================
pause
