#!/bin/bash
cd "$(dirname "$0")"
export PYTHONUNBUFFERED=1
export QT_LOGGING_RULES="*.debug=false;qt.qpa.*=false"

if [ -n "$DISPLAY" ] || [ -e /tmp/.X11-unix/X0 ]; then
  export DISPLAY=${DISPLAY:-:0}
  export QT_QPA_PLATFORM=xcb
  python3 main.py
  exit $?
fi

export QT_QPA_PLATFORM=eglfs
export QT_QPA_EGLFS_ALWAYS_SET_MODE=1
python3 main.py
