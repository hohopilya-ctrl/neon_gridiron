import os
import json

def compare_replays(path_a, path_b):
    with open(path_a, 'r') as f: ra = json.load(f)
    with open(path_b, 'r') as f: rb = json.load(f)
    
    if len(ra['frames']) != len(rb['frames']):
        return False, "Length mismatch"
        
    for i in range(len(ra['frames'])):
        if ra['frames'][i]['b'] != rb['frames'][i]['b']:
            return False, f"Ball mismatch at frame {i}"
            
    return True, "Identical"

if __name__ == "__main__":
    # Example usage
    pass
