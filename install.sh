#!/bin/bash
# ============================================================
# AROVA Desktop Installer
# ============================================================
# Creates a Python virtual environment and installs all
# dependencies for Desktop (Windows WSL / Linux) deployment.
#
# Usage:
#   chmod +x install.sh
#   ./install.sh
# ============================================================

set -e

echo "=============================================="
echo "  AROVA Desktop Installer"
echo "=============================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Check Python version
echo ""
echo "[1/5] Checking Python version..."
PYTHON_CMD=""
for cmd in python3.10 python3 python; do
    if command -v "$cmd" &> /dev/null; then
        version=$("$cmd" --version 2>&1 | awk '{print $2}')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON_CMD="$cmd"
            echo "  Found $PYTHON_CMD ($version)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python 3.10+ is required but not found."
    echo "  Install Python 3.10+ and try again."
    exit 1
fi

# 2. Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists. Skipping creation."
else
    $PYTHON_CMD -m venv venv
    echo "  Virtual environment created at ./venv"
fi

# 3. Activate virtual environment
echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo "  Activated: $(which python)"

# 4. Upgrade pip
echo ""
echo "[4/5] Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet

# 5. Install dependencies
echo ""
echo "[5/5] Installing dependencies..."
pip install -r requirements.txt

# 6. Create .env from template if not exists
if [ ! -f ".env" ]; then
    echo ""
    echo "[INFO] Creating .env from .env.example..."
    cp .env.example .env
    echo "  .env created. Edit it to configure your environment."
fi

echo ""
echo "=============================================="
echo "  Installation Complete!"
echo "=============================================="
echo ""
echo "  Next steps:"
echo "    1. Edit .env for your environment"
echo "    2. Run: source venv/bin/activate"
echo "    3. Run: python app/main.py"
echo ""
