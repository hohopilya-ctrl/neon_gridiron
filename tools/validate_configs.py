import os
import sys

import yaml


def validate():
    config_dir = "configs"
    required_files = ["match_rules.yaml", "rewards.yaml", "abilities_core.yaml"]

    for file_name in required_files:
        path = os.path.join(config_dir, file_name)
        if not os.path.exists(path):
            print(f"CRITICAL: Missing config {file_name}")
            continue

        with open(path, "r") as stream:
            try:
                yaml.safe_load(stream)
                print(f"OK: {file_name} is valid YAML")
            except Exception as exc:
                print(f"FAIL: {file_name} syntax error: {exc}")
                sys.exit(1)


if __name__ == "__main__":
    validate()
