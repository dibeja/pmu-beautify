#!/bin/bash
# First-run setup for pmu-beautify (macOS). Safe to run again: it skips what is already there.
# Installs: ffmpeg + Python 3.12 (Homebrew), a private venv with mediapipe/opencv/numpy,
# and the two face models, checked against their SHA-256.
set -euo pipefail

DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOME_DIR="${PMU_BEAUTIFY_HOME:-$HOME/.pmu-beautify}"
VENV="$HOME_DIR/venv"
MODELS="$HOME_DIR/models"

[ "$(uname)" = Darwin ] || { echo "pmu-beautify setup supports macOS only."; exit 1; }

if ! command -v brew >/dev/null 2>&1; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)" && break; done
fi
if ! command -v brew >/dev/null 2>&1; then
  cat <<'EOF'
Homebrew is missing. It needs your Mac password, so install it yourself in Terminal:

  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

then run this setup again.
EOF
  exit 2
fi

command -v ffmpeg >/dev/null 2>&1 || { echo "Installing ffmpeg..."; brew install ffmpeg; }

PY="$(command -v python3.12 || true)"
if [ -z "$PY" ]; then
  [ -x "$(brew --prefix)/opt/python@3.12/bin/python3.12" ] || { echo "Installing Python 3.12..."; brew install python@3.12; }
  PY="$(brew --prefix)/opt/python@3.12/bin/python3.12"
fi

mkdir -p "$MODELS"
if [ ! -x "$VENV/bin/python" ]; then
  echo "Creating venv in $VENV..."
  "$PY" -m venv "$VENV"
fi
"$VENV/bin/python" -m pip install -q --upgrade pip
"$VENV/bin/python" -m pip install -q -r "$DIR/requirements.txt"

fetch() {  # name url sha256
  local f="$MODELS/$1"
  if [ -f "$f" ] && [ "$(shasum -a 256 "$f" | cut -d' ' -f1)" = "$3" ]; then return; fi
  echo "Downloading $1..."
  curl -fsSL -o "$f.part" "$2"
  [ "$(shasum -a 256 "$f.part" | cut -d' ' -f1)" = "$3" ] || { rm -f "$f.part"; echo "Checksum mismatch for $1"; exit 3; }
  mv "$f.part" "$f"
}
fetch face_landmarker.task \
  https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task \
  64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff
fetch face_recognition_sface_2021dec.onnx \
  https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx \
  0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79

"$VENV/bin/python" -c "import cv2, mediapipe, numpy; cv2.FaceRecognizerSF" >/dev/null
touch "$HOME_DIR/.ready"
echo "pmu-beautify ready. Python: $VENV/bin/python"
