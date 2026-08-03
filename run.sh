#!/bin/bash
# ============================================================
# AROVA Desktop Launcher
# ============================================================
# Usage:
#   chmod +x run.sh
#   ./run.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "[ERROR] Virtual environment not found. Run ./install.sh first."
    exit 1
fi

# Launch AROVA
echo "Starting AROVA AI Healthcare Assistant..."
python app/main.py
