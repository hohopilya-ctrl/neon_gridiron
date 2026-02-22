import os

def normalize_frame_for_ui(payload: dict) -> dict:
    """
    Normalizes a simulation frame for the UI, ensuring consistent data structures.
    - Converts score dict {"BLUE": x, "RED": y} to list [x, y].
    - Ensures version "2.1.0" is present.
    - Preserves b, p, e, t keys.
    """
    # 1. Ensure version
    payload["v"] = payload.get("v", "2.1.0")

    # 2. Normalize Score (s)
    score = payload.get("s", {})
    if isinstance(score, dict):
        # Convert {"BLUE": 0, "RED": 0} -> [0, 0]
        blue = score.get("BLUE", 0)
        red = score.get("RED", 0)
        payload["s"] = [blue, red]
    elif not isinstance(score, list):
        payload["s"] = [0, 0]

    # 3. Ensure essential keys exist
    if "t" not in payload:
        payload["t"] = 0
    if "b" not in payload:
        payload["b"] = {"p": [300, 200], "v": [0, 0]}
    if "p" not in payload:
        payload["p"] = []
    if "e" not in payload:
        payload["e"] = []
    
    return payload

def get_udp_port() -> int:
    """Returns the unified UDP port from environment or default."""
    return int(os.environ.get("NEON_UDP_PORT", 4242))
