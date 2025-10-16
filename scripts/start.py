"""
Production Server Script

Run the FastAPI production server.
"""

import uvicorn
import sys


def main():
    """Start production server"""
    # Try to set UTF-8 encoding for Windows console
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    print("=" * 60)
    print("  Starting Kerykeion-Kabalah Production Server")
    print("=" * 60)
    print("\nServer: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("\nMode: PRODUCTION")
    print("\nPress CTRL+C to stop\n")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
