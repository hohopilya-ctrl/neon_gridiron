"""
Neon Gridiron ULTRA: Professional Entry Point
Used to launch the simulation, server, and visualizer stack.
"""

import subprocess
import sys
import time
from pathlib import Path


def launch():
    print("🚀 N E O N  G R I D I R O N  U L T R A")
    print("--------------------------------------")

    root = Path(__file__).parent.resolve()

    # Cross-platform window flags
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE

    # 1. Start Telemetry Bridge (FastAPI)
    print("[1/3] Starting API Server...")
    processes.append(
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "server.app:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
            ],
            cwd=root,
            **kwargs,
        )
    )

    # Allow server to warm up
    time.sleep(2)

    # 2. Start Training Engine
    print("[2/3] Starting RL Training Engine...")
    processes.append(
        subprocess.Popen(
            [sys.executable, "-m", "ai.training.league"],
            cwd=root,
            **kwargs,
        )
    )

    # 3. Start Live Viewer (Pygame)
    print("[3/3] Starting Live Viewer...")
    processes.append(
        subprocess.Popen(
            [sys.executable, "tools/live_viewer.py"],
            cwd=root,
            **kwargs,
        )
    )

    print("\n✅ ULTRA STACK DEPLOYED.")
    print("Monitor logs in the separate console windows.")
    print("Open Godot Client to view in 3D.")


    processes = []
    
    # ... (subprocess calls above)

    try:
        while True:
            time.sleep(1)
            # Check if any process died
            for p in processes:
                if p.poll() is not None:
                    print(f"⚠️ Process {p.pid} terminated unexpectedly.")
                    raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Ultra Stack...")
        for p in processes:
            p.terminate()
        sys.exit(0)
