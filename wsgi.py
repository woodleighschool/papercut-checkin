#!/usr/bin/env python3

from server import create_app
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


app = create_app()

if __name__ == "__main__":
    # For development
    app.run(debug=True, host="0.0.0.0", port=5000)
