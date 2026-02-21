import typer
import subprocess
import os
import sys
from pathlib import Path

app = typer.Typer(help="Neon Gridiron ULTRA: Unified CLI")


@app.command()
def ultra():
    """Launch the full stack (API + Training + Viewer)."""
    typer.echo("🚀 Launching Neon Gridiron ULTRA Stack...")
    subprocess.run([sys.executable, "run_ultra.py"])


@app.command()
def train():
    """Start the RL training league."""
    typer.echo("🏆 Starting League Training...")
    subprocess.run([sys.executable, "-m", "ai.training.league"])


@app.command()
def server():
    """Run the FastAPI telemetry server."""
    typer.echo("🌐 Starting API Server...")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
    )


@app.command()
def sim():
    """Run a standalone simulation (headless or windowed)."""
    typer.echo("🏟️ Starting Standalone Simulation...")
    # This will be expanded as we add more sim options
    subprocess.run([sys.executable, "-m", "ai.env.neon_env"])


@app.command()
def check():
    """Run quality checks (lint, format, typecheck, tests)."""
    typer.echo("🔍 Running quality checks...")
    subprocess.run(["python", "-m", "ruff", "check", "."])
    subprocess.run(["python", "-m", "ruff", "format", "--check", "."])
    subprocess.run(["python", "-m", "mypy", "."])
    subprocess.run(["python", "-m", "pytest"])

@app.command()
def replay(file1: str, file2: str):
    """Compare two replay files for divergence."""
    typer.echo(f"🧐 Comparing {file1} and {file2}...")
    subprocess.run([sys.executable, "tools/replay_diff.py", file1, file2])


if __name__ == "__main__":
    app()
