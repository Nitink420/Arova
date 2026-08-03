#!/bin/bash
# ============================================================
# AROVA Jetson Orin Launcher
# ============================================================
# Usage:
#   chmod +x run_jetson.sh
#   ./run_jetson.sh
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "[ERROR] Virtual environment not found. Run ./install_jetson.sh first."
    exit 1
fi

# Export Jetson-specific environment if not already in .env
export ENVIRONMENT=${ENVIRONMENT:-jetson}

# Launch AROVA
echo "Starting AROVA AI Healthcare Assistant (Jetson Orin)..."
python app/main.py
