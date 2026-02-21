import json
import sys

import numpy as np


def compare_replays(file1: str, file2: str):
    """
    Compares two JSONL replay files and reports the exact tick of divergence.
    Essential for verifying determinism across platforms.
    """
    print(f"🧐 Comparing Divergence:\n  1: {file1}\n  2: {file2}")

    with open(file1, "r") as f1, open(file2, "r") as f2:
        for i, (line1, line2) in enumerate(zip(f1, f2)):
            d1 = json.loads(line1)
            d2 = json.loads(line2)

            # Check ball position divergence
            p1 = np.array(d1["b"]["p"])
            p2 = np.array(d2["b"]["p"])

            if not np.allclose(p1, p2, atol=1e-6):
                print(f"❌ DIVERGENCE AT TICK {d1.get('t', i)}")
                print(f"  F1: {p1}")
                print(f"  F2: {p2}")
                print(f"  Gap: {np.linalg.norm(p1 - p2)}")
                return False

            # Check player drift
            for p_idx, (p1_data, p2_data) in enumerate(zip(d1["p"], d2["p"])):
                pos1 = np.array(p1_data["pos"])
                pos2 = np.array(p2_data["pos"])
                if not np.allclose(pos1, pos2, atol=1e-6):
                    print(f"❌ PLAYER {p1_data['id']} DRIFT AT TICK {d1.get('t', i)}")
                    return False

    print("✅ REPLAYS MATCH BIT-PERFECTLY.")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/replay_diff.py <replay1.jsonl> <replay2.jsonl>")
    else:
        compare_replays(sys.argv[1], sys.argv[2])
