import os
from typing import List, Optional

import msgpack

from telemetry.frame import TelemetryFrame


class ReplayRecorder:
    """
    Standard match archival for Neon Gridiron ULTRA.
    Records sequences of TelemetryFrames and saves them as compressed msgpack files.
    """

    def __init__(self, match_id: str, save_dir: str = "data/replays"):
        self.match_id = match_id
        self.save_dir = save_dir
        self.frames: List[dict] = []
        os.makedirs(self.save_dir, exist_ok=True)

    def record_frame(self, frame: TelemetryFrame):
        self.frames.append(frame.to_dict())

    def save(self):
        filename = f"{self.match_id}_{int(os.path.getmtime('.'))}.neon_replay"
        path = os.path.join(self.save_dir, filename)
        with open(path, "wb") as f:
            f.write(msgpack.packb(self.frames, use_bin_type=True))
        print(f"Replay saved: {path} ({len(self.frames)} frames)")


class ReplayLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        with open(file_path, "rb") as f:
            self.frames = msgpack.unpackb(f.read(), raw=False)

    def get_frame(self, tick: int) -> Optional[dict]:
        if 0 <= tick < len(self.frames):
            return self.frames[tick]
        return None
