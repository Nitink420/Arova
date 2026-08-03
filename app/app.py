# app/app.py
"""
AROVA Multilingual Application Entry Point (Legacy Wrapper)

Imports and launches the modular main application from app/main.py.
Preserves backward compatibility for direct execution of app/app.py.
"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.main import main

if __name__ == "__main__":
    main()