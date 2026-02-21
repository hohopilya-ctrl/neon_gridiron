import subprocess
import sys
import time
import signal
from pathlib import Path

def launch():
    print("🚀 N E O N  G R I D I R O N  U L T R A")
    print("--------------------------------------")

    root = Path(__file__).parent.resolve()
    processes = []

    # Cross-platform window flags
    kwargs = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE

    try:
        # 1. Start Telemetry Bridge (FastAPI)
        print("[1/3] Starting API Server...")
        p_api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "server.app:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=root, **kwargs
        )
        processes.append(p_api)

        # Allow server to warm up
        time.sleep(2)

        # 2. Start Training Engine
        print("[2/3] Starting RL Training Engine...")
        p_train = subprocess.Popen(
            [sys.executable, "-m", "ai.training.league"],
            cwd=root, **kwargs
        )
        processes.append(p_train)

        # 3. Start Live Viewer (Pygame)
        print("[3/3] Starting Live Viewer...")
        p_view = subprocess.Popen(
            [sys.executable, "tools/live_viewer.py"],
            cwd=root, **kwargs
        )
        processes.append(p_view)

        print("\n✅ ULTRA STACK DEPLOYED.")
        print("Monitor logs in separate sessions.")
        
        # Keep alive and monitor
        while True:
            time.sleep(1)
            for p in processes:
                if p.poll() is not None:
                    print(f"⚠️ Process {p.pid} exited. Shutting down stack...")
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Ultra Stack...")
        for p in processes:
            p.terminate()
        sys.exit(0)

if __name__ == "__main__":
    launch()
