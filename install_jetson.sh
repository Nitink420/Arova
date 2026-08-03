#!/bin/bash
# ============================================================
# AROVA Jetson Orin Installer
# ============================================================
# For AIProff Jetson Orin with JetPack 6.1
#
# CRITICAL: This script NEVER installs torch, torchvision,
# or torchaudio. They are pre-installed via NVIDIA JetPack.
#
# Usage:
#   chmod +x install_jetson.sh
#   ./install_jetson.sh
# ============================================================

set -e

echo "=============================================="
echo "  AROVA Jetson Orin Installer"
echo "=============================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Verify CUDA PyTorch
echo ""
echo "[1/6] Verifying CUDA PyTorch installation..."
PYTHON_CMD=""
for cmd in python3.10 python3 python; do
    if command -v "$cmd" &> /dev/null; then
        PYTHON_CMD="$cmd"
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERROR] Python 3 not found."
    exit 1
fi

# Check that torch is installed and CUDA is available
TORCH_CHECK=$($PYTHON_CMD -c "
try:
    import torch
    print(f'torch={torch.__version__}')
    print(f'cuda={torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'gpu={torch.cuda.get_device_name(0)}')
except ImportError:
    print('torch=NOT_INSTALLED')
    print('cuda=False')
" 2>&1)

echo "$TORCH_CHECK"

if echo "$TORCH_CHECK" | grep -q "torch=NOT_INSTALLED"; then
    echo ""
    echo "[ERROR] PyTorch is NOT installed."
    echo "  On Jetson Orin, PyTorch must be installed via NVIDIA JetPack wheels."
    echo "  DO NOT install torch from pip — it will not have CUDA support."
    echo ""
    echo "  Install from: https://forums.developer.nvidia.com/t/pytorch-for-jetson/"
    exit 1
fi

if echo "$TORCH_CHECK" | grep -q "cuda=False"; then
    echo ""
    echo "[WARNING] PyTorch is installed but CUDA is NOT available."
    echo "  This may indicate a JetPack installation issue."
    echo "  AROVA will fall back to CPU mode."
fi

# 2. Verify torchvision
echo ""
echo "[2/6] Verifying torchvision..."
TV_CHECK=$($PYTHON_CMD -c "
try:
    import torchvision
    print(f'torchvision={torchvision.__version__}')
except ImportError:
    print('torchvision=NOT_INSTALLED')
" 2>&1)

echo "$TV_CHECK"

if echo "$TV_CHECK" | grep -q "NOT_INSTALLED"; then
    echo ""
    echo "[ERROR] torchvision is NOT installed."
    echo "  Install it from NVIDIA JetPack wheels (matching your torch version)."
    exit 1
fi

# 3. Create virtual environment with system packages (to inherit torch)
echo ""
echo "[3/6] Creating virtual environment (with system packages)..."
if [ -d "venv" ]; then
    echo "  Virtual environment already exists. Skipping creation."
else
    $PYTHON_CMD -m venv venv --system-site-packages
    echo "  Virtual environment created with system site-packages."
fi

# 4. Activate virtual environment
echo ""
echo "[4/6] Activating virtual environment..."
source venv/bin/activate
echo "  Activated: $(which python)"

# 5. Upgrade pip (without touching torch)
echo ""
echo "[5/6] Upgrading pip..."
pip install --upgrade pip setuptools wheel --quiet

# 6. Install Jetson dependencies (NO torch, NO torchvision)
echo ""
echo "[6/6] Installing Jetson dependencies..."
pip install -r requirements-jetson.txt

# Verify critical imports
echo ""
echo "Verifying critical imports..."
python -c "
import sys
modules = [
    ('torch', True),
    ('torchvision', True),
    ('cv2', True),
    ('gradio', True),
    ('requests', True),
    ('dotenv', True),
    ('numpy', True),
    ('pandas', True),
    ('fpdf', True),
]
all_ok = True
for name, required in modules:
    try:
        __import__(name)
        print(f'  ✅ {name}')
    except ImportError:
        status = '❌ MISSING (required)' if required else '⚠️ MISSING (optional)'
        print(f'  {status} {name}')
        if required:
            all_ok = False

if not all_ok:
    print()
    print('[ERROR] Some required modules are missing.')
    sys.exit(1)
else:
    print()
    print('[OK] All critical imports verified.')
"

# Create .env from template if not exists
if [ ! -f ".env" ]; then
    echo ""
    echo "[INFO] Creating .env from .env.example..."
    cp .env.example .env
    echo "  .env created. Edit OLLAMA_API_URL for your Jetson network."
fi

echo ""
echo "=============================================="
echo "  Jetson Installation Complete!"
echo "=============================================="
echo ""
echo "  Next steps:"
echo "    1. Edit .env:"
echo "       ENVIRONMENT=jetson"
echo "       OLLAMA_API_URL=http://172.xx.xx.xx:11434"
echo "    2. Run: source venv/bin/activate"
echo "    3. Run: python app/main.py"
echo ""
