import pathlib
import shutil


def cleanup():
    """Purge transient artifacts, caches and temporary files."""
    root = pathlib.Path(__file__).parent.parent.resolve()
    print(f"🧹 Starting cleanup in {root}...")

    # Directories to remove
    trash_dirs = [
        "**/__pycache__",
        "logs",
        "replays",
        "artifacts",
        "models",
        "ppo_neon_tensorboard",
        "ml_environment/venv",
        "ml_environment/env",
        "ml_environment/replays",
        "ml_environment/models",
        "ml_environment/ppo_neon_tensorboard",
        "godot_client/.godot",
        ".godot",
    ]

    # Files to remove
    trash_files = [
        "**/*.pyc",
        "**/*.pyo",
        "ml_environment/*.txt",
        "*.log",
        "diag_ultra.py",  # Local diagnostic tool
        "run_ultra.bat",  # Replaced by better scripts later
    ]

    for pattern in trash_dirs:
        for path in root.glob(pattern):
            if path.is_dir():
                print(f"Removing directory: {path.relative_to(root)}")
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    print(f"Failed to remove {path}: {e}")

    for pattern in trash_files:
        for path in root.glob(pattern):
            if path.is_file():
                print(f"Removing file: {path.relative_to(root)}")
                try:
                    path.unlink()
                except Exception as e:
                    print(f"Failed to remove {path}: {e}")

    print("✅ Cleanup complete.")


if __name__ == "__main__":
    cleanup()
