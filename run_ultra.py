import subprocess
import sys
import time
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
        print("[1/3] Starting Telemetry Bridge...")
        p_api = subprocess.Popen(
            [
                sys.executable,
                "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"
            ],
            cwd=root,
            **kwargs,
        )
        processes.append(p_api)

        # Allow server to warm up
        time.sleep(3)

        # 2. Start Live Simulation Runner
        print("[2/3] Starting ULTRA Live Runner...")
        p_sim = subprocess.Popen([sys.executable, "scripts/live_runner.py"], cwd=root, **kwargs)
        processes.append(p_sim)

        # 3. Instruction for UI
        print("[3/3] ULTRA Stack is live!")
        print("    -> Telemetry Bridge: http://127.0.0.1:8000")
        print("    -> Live Dashboard: http://localhost:3000")
        print("\nPress Ctrl+C to stop the stack.")

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
