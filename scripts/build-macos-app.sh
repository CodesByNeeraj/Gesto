#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIRECTORY="$(cd "$(dirname "$0")/.." && pwd)"

python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name Gesto \
  --icon "${PROJECT_DIRECTORY}/assets/icons/Gesto.icns" \
  --osx-bundle-identifier com.gesto.app \
  --add-data "${PROJECT_DIRECTORY}/assets:assets" \
  --add-data "${PROJECT_DIRECTORY}/src:src" \
  --collect-all customtkinter \
  --collect-all mediapipe \
  --hidden-import cv2 \
  --hidden-import joblib \
  --hidden-import numpy \
  --hidden-import sklearn \
  "${PROJECT_DIRECTORY}/src/main.py"

BUNDLE_PATH="${PROJECT_DIRECTORY}/dist/Gesto.app"
/usr/libexec/PlistBuddy -c \
  "Add :NSCameraUsageDescription string Gesto uses your camera to recognize gestures locally on your Mac." \
  "${BUNDLE_PATH}/Contents/Info.plist"
codesign --force --deep --sign - "${BUNDLE_PATH}"
