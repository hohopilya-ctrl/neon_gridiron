import json
import sys
import numpy as np
from pathlib import Path

def compare_replays(file1: str, file2: str):
    """Compares two JSONL replay files and reports the divergence tick."""
    print(f"🧐 Comparing:\n  1: {file1}\n  2: {file2}")
    
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        for i, (line1, line2) in enumerate(zip(f1, f2)):
            d1 = json.loads(line1)
            d2 = json.loads(line2)
            
            # Check for divergence in ball position
            p1 = np.array(d1['b']['p'])
            p2 = np.array(d2['b']['p'])
            
            if not np.allclose(p1, p2, atol=1e-5):
                print(f"❌ DIVERGENCE DETECTED at tick {d1.get('t', i)}")
                print(f"  File 1 position: {p1}")
                print(f"  File 2 position: {p2}")
                print(f"  Delta: {np.linalg.norm(p1 - p2)}")
                return False
                
    print("✅ Replays are identical (within tolerance).")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/replay_diff.py <replay1.jsonl> <replay2.jsonl>")
    else:
        compare_replays(sys.argv[1], sys.argv[2])
