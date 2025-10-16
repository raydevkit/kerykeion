#!/usr/bin/env python3
"""
Quick Development Server Launcher

Usage: python dev.py
       (Will automatically use Poetry environment)
"""

import subprocess
import sys
import os

if __name__ == "__main__":
    # Check if we're in a Poetry environment
    in_poetry = os.environ.get('POETRY_ACTIVE') == '1'

    if not in_poetry:
        # Run using Poetry
        print("Starting server using Poetry environment...\n")
        try:
            subprocess.run([
                sys.executable, "-m", "poetry", "run",
                "python", "-c",
                "from scripts.dev import main; main()"
            ], check=True)
        except subprocess.CalledProcessError:
            print("\nError: Could not start server. Make sure Poetry is installed.")
            print("Install Poetry: pip install poetry")
            sys.exit(1)
    else:
        # Already in Poetry environment
        from scripts.dev import main
        main()
