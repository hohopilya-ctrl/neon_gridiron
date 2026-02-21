import yaml
import sys
import os

def validate():
    config_dir = "configs"
    required_files = ["match_rules.yaml", "rewards.yaml", "abilities_core.yaml"]
    
    for f in required_files:
        path = os.path.join(config_dir, f)
        if not os.path.exists(path):
            print(f"CRITICAL: Missing config {f}")
            sys.exit(1)
        
        with open(path, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                print(f"OK: {f} is valid YAML")
            except Exception as e:
                print(f"FAIL: {f} syntax error: {e}")
                sys.exit(1)

if __name__ == "__main__":
    validate()
