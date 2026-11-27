#!/bin/bash
# Full pipeline on a fresh machine / GitHub runner:
#   1. voices (Piper)  2. render all shots  3. audio mix  4. join + mux
# Assumes: python venv at ./venv (or system python with deps), ffmpeg installed,
# Piper voice model extracted at $MODEL_DIR, fonts in ~/vid/fonts.
set -e
cd "$(dirname "$0")"
if [ -x ./venv/bin/python ]; then PY="${PY:-./venv/bin/python}"; else PY="${PY:-python3}"; fi
"$PY" gen_voices.py
"$PY" render.py all
"$PY" audio_mix.py
bash join.sh
echo "DONE: myheritage-final.mp4"
