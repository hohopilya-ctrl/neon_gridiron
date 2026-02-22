from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES: dict[str, str] = {
    "ai/env/__init__.py": """\
\"\"\"Environment package for Neon Gridiron.\"\"\"\n\nfrom ai.env.neon_env import NeonFootballEnv\n\n__all__ = [\"NeonFootballEnv\"]\n""",
    "ai/env/neon_env.py": """\
from __future__ import annotations\n\nfrom typing import Any\n\nimport gymnasium as gym\nimport numpy as np\nfrom gymnasium import spaces\n\nfrom sim.core.rng import DeterministicRNG\nfrom sim.core.rules import RulesEngine\nfrom sim.core.state import BallState, MatchState, PlayerState, TeamID\n\n\nclass NeonFootballEnv(gym.Env[np.ndarray, np.ndarray]):\n    \"\"\"Minimal deterministic 7v7 environment used by tests and training stubs.\"\"\"\n\n    metadata = {\"render_modes\": []}\n\n    def __init__(self, config: dict[str, Any] | None = None):\n        super().__init__()\n        self.config = config or {}\n        self.seed_value = int(self.config.get(\"seed\", 42))\n        self.rng = DeterministicRNG(self.seed_value)\n\n        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(28,), dtype=np.float32)\n        self.observation_space = spaces.Box(\n            low=-np.inf,\n            high=np.inf,\n            shape=(64,),\n            dtype=np.float32,\n        )\n\n        self.rules = RulesEngine((600.0, 400.0))\n        self.state = MatchState(players=[], ball=BallState())\n        self.max_steps = 600\n        self._step_count = 0\n\n    def reset(\n        self,\n        *,\n        seed: int | None = None,\n        options: dict[str, Any] | None = None,\n    ) -> tuple[np.ndarray, dict[str, Any]]:\n        del options\n        if seed is not None:\n            self.seed_value = int(seed)\n        self.rng.reset(self.seed_value)\n        self._step_count = 0\n\n        self.state.tick = 0\n        self.state.score = {TeamID.BLUE: 0, TeamID.RED: 0}\n        self.state.events = []\n        self.state.ball = BallState(\n            pos=np.array([300.0, 200.0], dtype=np.float32),\n            vel=np.zeros(2, dtype=np.float32),\n        )\n\n        self.state.players = []\n        for idx in range(7):\n            self.state.players.append(\n                PlayerState(\n                    id=f\"blue_{idx}\",\n                    team=TeamID.BLUE,\n                    pos=np.array([120.0 + idx * 20.0, 60.0 + idx * 40.0], dtype=np.float32),\n                    vel=np.zeros(2, dtype=np.float32),\n                )\n            )\n        for idx in range(7):\n            self.state.players.append(\n                PlayerState(\n                    id=f\"red_{idx}\",\n                    team=TeamID.RED,\n                    pos=np.array([480.0 - idx * 20.0, 60.0 + idx * 40.0], dtype=np.float32),\n                    vel=np.zeros(2, dtype=np.float32),\n                )\n            )\n\n        return self._build_observation(), {\"seed\": self.seed_value}\n\n    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:\n        action = np.asarray(action, dtype=np.float32).reshape(self.action_space.shape)\n\n        self.state.tick += 1\n        self._step_count += 1\n\n        for idx, player in enumerate(self.state.players):\n            base = idx * 2\n            force = action[base : base + 2]\n            player.vel = np.clip(force * 6.0, -6.0, 6.0)\n            player.pos = player.pos + player.vel\n            player.pos[0] = np.clip(player.pos[0], 0.0, 600.0)\n            player.pos[1] = np.clip(player.pos[1], 0.0, 400.0)\n\n        impulse = float(np.mean(action))\n        self.state.ball.vel = np.array([impulse * 1.5, -impulse * 1.5], dtype=np.float32)\n        self.state.ball.pos = np.clip(\n            self.state.ball.pos + self.state.ball.vel,\n            np.array([0.0, 0.0], dtype=np.float32),\n            np.array([600.0, 400.0], dtype=np.float32),\n        )\n\n        reward = float(-np.linalg.norm(self.state.ball.pos - np.array([300.0, 200.0], dtype=np.float32)) / 1000.0)\n\n        goal_team = self.rules.check_goal(self.state.ball.pos)\n        terminated = goal_team is not None\n        if goal_team is TeamID.BLUE:\n            self.state.score[TeamID.BLUE] += 1\n            reward += 1.0\n        elif goal_team is TeamID.RED:\n            self.state.score[TeamID.RED] += 1\n            reward -= 1.0\n\n        truncated = self._step_count >= self.max_steps\n\n        return self._build_observation(), reward, bool(terminated), bool(truncated), {}\n\n    def _build_observation(self) -> np.ndarray:\n        obs = np.zeros(64, dtype=np.float32)\n        obs[0:2] = self.state.ball.pos / np.array([600.0, 400.0], dtype=np.float32)\n        obs[2:4] = self.state.ball.vel / 10.0\n\n        cursor = 4\n        for player in self.state.players[:14]:\n            obs[cursor : cursor + 2] = player.pos / np.array([600.0, 400.0], dtype=np.float32)\n            cursor += 2\n            if cursor >= 64:\n                break\n        return obs\n""",
    "ui/lib/frame.ts": """\
export type PlayerFrame = {\n  id: string;\n  team: string;\n  pos: [number, number];\n  vel: [number, number];\n};\n\nexport type Frame = {\n  tick: number;\n  score: [number, number];\n  ball: { pos: [number, number]; vel?: [number, number] };\n  players: PlayerFrame[];\n  overlays?: { attn?: number[][] };\n};\n\nexport function normalizeFrame(raw: Record<string, unknown>): Frame {\n  const scoreRaw = Array.isArray(raw.s) ? raw.s : [0, 0];\n  const ballPos = Array.isArray(raw.b) ? raw.b : [300, 200];\n  const playersRaw = Array.isArray(raw.p) ? raw.p : [];\n\n  const players = playersRaw.map((p) => {\n    const player = p as Record<string, unknown>;\n    return {\n      id: String(player.id ?? \"unknown\"),\n      team: String(player.team ?? \"BLUE\"),\n      pos: (Array.isArray(player.pos) ? player.pos : [0, 0]) as [number, number],\n      vel: (Array.isArray(player.vel) ? player.vel : [0, 0]) as [number, number],\n    };\n  });\n\n  return {\n    tick: Number(raw.t ?? 0),\n    score: [Number(scoreRaw[0] ?? 0), Number(scoreRaw[1] ?? 0)],\n    ball: { pos: [Number(ballPos[0] ?? 300), Number(ballPos[1] ?? 200)] },\n    players,\n    overlays: (raw.o as { attn?: number[][] } | undefined) ?? {},\n  };\n}\n""",
    "ui/lib/ws.ts": """\
import { Frame, normalizeFrame } from \"./frame\";\n\nexport class UltraWSClient {\n  private ws: WebSocket | null = null;\n\n  constructor(\n    private readonly url: string,\n    private readonly onFrame: (frame: Frame) => void,\n  ) {}\n\n  connect(): void {\n    this.ws = new WebSocket(this.url);\n    this.ws.onmessage = (event) => {\n      try {\n        const parsed = JSON.parse(event.data) as Record<string, unknown>;\n        this.onFrame(normalizeFrame(parsed));\n      } catch {\n        // Ignore malformed frames.\n      }\n    };\n  }\n\n  close(): void {\n    this.ws?.close();\n    this.ws = null;\n  }\n}\n""",
}


DREAMER_IMPORT = "import torch.nn.functional as F\n"

REWARDS_FILE = "ai/training/rewards.py"
REWARDS_CONTENT = """\
from typing import Any, Dict, List\n\nimport numpy as np\n\nfrom sim.core.state import TeamID\n\n\nclass RewardShaper:\n    \"\"\"\n    Advanced Meta-Reward Shaper for ULTRA Phase 2.\n    Combines sparse goals with dense hierarchical metrics.\n    \"\"\"\n\n    def __init__(self, config: Dict[str, Any] | None = None):\n        self.cfg = config or {}\n        self.w_goal = self.cfg.get(\"w_goal\", 10.0)\n        self.w_ball_dist = self.cfg.get(\"w_ball_dist\", 0.01)\n        self.w_possession = self.cfg.get(\"w_possession\", 0.1)\n        self.w_spectacle = self.cfg.get(\"w_spectacle\", 0.05)\n\n    def compute_meta_reward(self, state: Any, events: List[Any]) -> Dict[str, float]:\n        rewards = {\"total\": 0.0, \"goal\": 0.0, \"dense\": 0.0, \"spec\": 0.0}\n\n        for ev in events:\n            if getattr(ev, \"event_type\", None) == \"GOAL\":\n                rewards[\"goal\"] += self.w_goal\n\n        if getattr(state, \"players\", None):\n            ball_pos = np.asarray(state.ball.pos, dtype=np.float32)\n            min_dist = min(float(np.linalg.norm(np.asarray(p.pos) - ball_pos)) for p in state.players)\n            rewards[\"dense\"] += self.w_ball_dist * (1.0 / (1.0 + min_dist / 100.0))\n\n        if getattr(state.ball, \"last_touch_team\", None) == TeamID.BLUE:\n            rewards[\"dense\"] += self.w_possession\n\n        rewards[\"spec\"] += float(getattr(state, \"spectacle_score\", 0.0)) * self.w_spectacle\n\n        rewards[\"total\"] = rewards[\"goal\"] + rewards[\"dense\"] + rewards[\"spec\"]\n        return rewards\n"""


def write_file(rel_path: str, content: str) -> None:
    path = ROOT / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    print(f"updated {rel_path}")


def patch_dreamer() -> None:
    path = ROOT / "ai/training/dreamer.py"
    text = path.read_text(encoding="utf-8")
    if DREAMER_IMPORT in text:
        print("dreamer.py already includes torch.nn.functional import")
        return
    insert_after = "import torch\n"
    if insert_after not in text:
        raise RuntimeError("Unexpected dreamer.py format; cannot apply import patch.")
    text = text.replace(insert_after, insert_after + DREAMER_IMPORT, 1)
    path.write_text(text, encoding="utf-8")
    print("patched ai/training/dreamer.py")


def main() -> None:
    for rel_path, content in FILES.items():
        write_file(rel_path, content)

    patch_dreamer()
    write_file(REWARDS_FILE, REWARDS_CONTENT)

    print("\nDone. Next steps:")
    print("  python -m ruff check .")
    print("  python -m pytest -q")


if __name__ == "__main__":
    main()
