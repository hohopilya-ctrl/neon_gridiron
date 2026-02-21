import typer
import subprocess
import os
import sys
from typing import Optional
from pathlib import Path

app = typer.Typer(help="Neon Gridiron ULTRA: Unified CLI")

@app.command()
def ultra():
    """Launch the full stack (API + Training + Viewer)."""
    typer.echo("🚀 Launching Neon Gridiron ULTRA Stack...")
    # This will refer to run_ultra.py which I will refactor next
    subprocess.run([sys.executable, "run_ultra.py"])

@app.command()
def train():
    """Start the RL training league."""
    typer.echo("🏆 Starting RL Training League...")
    subprocess.run([sys.executable, "-m", "ai.training.league"])

@app.command()
def server():
    """Start the Telemetry API server (Uvicorn)."""
    typer.echo("📡 Starting Telemetry Server...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", "server.app:app", 
        "--host", "127.0.0.1", "--port", "8000"
    ])

@app.command()
def check():
    """Run all quality checks (Ruff, MyPy, Pytest)."""
    typer.echo("🛡️ Running Security & Quality Audit...")
    
    typer.echo("\n1. Linting (Ruff)...")
    subprocess.run(["python", "-m", "ruff", "check", "."])
    
    typer.echo("\n2. Formatting Check (Ruff)...")
    subprocess.run(["python", "-m", "ruff", "format", "--check", "."])
    
    typer.echo("\n3. Type Checking (MyPy)...")
    subprocess.run(["python", "-m", "mypy", "."])
    
    typer.echo("\n4. Unit Tests (Pytest)...")
    subprocess.run(["python", "-m", "pytest"])

@app.command()
def replay(file1: str, file2: Optional[str] = None):
    """View or compare replay files."""
    if file2:
        typer.echo(f"🧐 Comparing {file1} and {file2}...")
        subprocess.run([sys.executable, "tools/replay_diff.py", file1, file2])
    else:
        typer.echo(f"📺 Playing replay {file1}...")
        # Placeholder for playback tool
        
if __name__ == "__main__":
    app()
