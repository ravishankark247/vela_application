"""Start the Vela mobile-responsive preview with Python."""

from __future__ import annotations

import subprocess
import sys
import socket


def available_port(start: int = 8501) -> int:
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            if probe.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free preview port found between 8501 and 8520.")


def main() -> None:
    try:
        import streamlit  # noqa: F401
    except ImportError:
        print("Streamlit is not installed. Run: pip install -r requirements.txt")
        raise SystemExit(1)

    port = available_port()
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.headless=true",
        "--browser.serverAddress=localhost",
        f"--server.port={port}",
    ]
    print(f"Starting Vela preview at http://localhost:{port}")
    print("Press Ctrl+C to stop the preview.")
    try:
        subprocess.run(command, check=False)
    except KeyboardInterrupt:
        print("\nVela preview stopped.")


if __name__ == "__main__":
    main()