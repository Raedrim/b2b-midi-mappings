#!/bin/bash
# Starts the DDJ-FLX4 bridge on macOS: sets up a private Python environment on first run, then runs it.
# Double-click this file in Finder. Leave the window open while you use B2B Studio.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found."
    echo "Install it from https://www.python.org/downloads/ (or run: xcode-select --install) and try again."
    [ -z "$NOPAUSE" ] && read -n 1 -s -r -p "Press any key to close."
    exit 1
fi

if [ ! -d .venv ]; then
    python3 -m venv .venv || { echo "Could not create the Python environment."; exit 1; }
fi
.venv/bin/python -m pip install --quiet --disable-pip-version-check -r requirements.txt \
    || { echo "Could not install the dependencies. Check your internet connection and try again."; exit 1; }

.venv/bin/python flx4_bridge.py "$@"
echo
[ -z "$NOPAUSE" ] && read -n 1 -s -r -p "Press any key to close."
