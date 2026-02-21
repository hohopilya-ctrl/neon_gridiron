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
    
    # 1. Start Telemetry Bridge (FastAPI)
    print("[1/3] Starting API Server...")
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.app:app", "--host", "127.0.0.1", "--port", "8000"], 
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=root
    )
    
    # Allow server to warm up
    time.sleep(2)
    
    # 2. Start Training Engine
    print("[2/3] Starting RL Training Engine...")
    subprocess.Popen(
        [sys.executable, "-m", "ai.training.league"], 
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=root
    )
    
    # 3. Start Live Viewer (Pygame)
    print("[3/3] Starting Live Viewer...")
    subprocess.Popen(
        [sys.executable, "tools/live_viewer.py"], 
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=root
    )
    
    print("\n✅ ULTRA STACK DEPLOYED.")
    print("Monitor logs in the separate console windows.")
    print("Open Godot Client to view in 3D.")

if __name__ == "__main__":
    try:
        launch()
    except KeyboardInterrupt:
        print("\nShutdown requested.")
