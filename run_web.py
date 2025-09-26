#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    web_dir = script_dir / "web"

    # Check if virtual environment exists
    venv_dir = script_dir / "venv"
    if not venv_dir.exists():
        print("Error: Virtual environment not found at", venv_dir)
        print("Please create a virtual environment and install requirements first:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    # Check if web directory exists
    if not web_dir.exists():
        print("Error: Web directory not found at", web_dir)
        sys.exit(1)

    # Check if Flask is installed
    try:
        activate_script = venv_dir / "bin" / "activate"
        if os.name == 'nt':  # Windows
            activate_script = venv_dir / "Scripts" / "activate.bat"

        # Change to web directory and run the Flask app
        os.chdir(web_dir)

        print("=" * 60)
        print("🚀 Starting BSB to USFM Converter Web Interface")
        print("=" * 60)
        print(f"📁 Working directory: {web_dir}")
        print("🌐 Server will be available at: http://localhost:5000")
        print("🔧 Press Ctrl+C to stop the server")
        print("=" * 60)

        # Activate virtual environment and run Flask
        if os.name == 'nt':  # Windows
            cmd = f'"{activate_script}" && python app.py'
            subprocess.run(cmd, shell=True)
        else:  # Unix/Linux/macOS
            cmd = f'source "{activate_script}" && python3 app.py'
            subprocess.run(cmd, shell=True, executable='/bin/bash')

    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Thank you for using BSB to USFM Converter!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
