import socket
import json
import os


class UDPSender:
    def __init__(self, ip="127.0.0.1", port=4242):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_state(self, env):
        """
        Extracts position data from the Pymunk environment and sends it to Godot.
        """
        ball_pos = env.ball_body.position

        players_pos = []
        for p in env.players:
            pos = p["body"].position
            is_dashing = int(p.get("is_dashing", False))
            players_pos.append(
                {
                    "x": float(pos.x),
                    "y": float(pos.y),
                    "dash": is_dashing,
                    "stm": float(p.get("stamina", 100.0) / 100.0),
                    "goalie": int(p.get("is_goalie", False)),
                    "pp": float(p.get("p_points", 0.0)),
                    "tags": p.get("active_tags", []),
                }
            )

        # Load leaderboard from history or latest gen
        leaderboard = []
        history_path = "models/pbt/history.json"
        if os.path.exists(history_path):
            with open(history_path, "r") as f:
                history = json.load(f)
                if history:
                    last_gen = history[-1]
                    leaderboard.append({"name": "AVG_ELO", "val": last_gen["avg_elo"]})
                    leaderboard.append({"name": "MAX_ELO", "val": last_gen["max_elo"]})

        state_dict = {
            "ball": {"x": float(ball_pos.x), "y": float(ball_pos.y), "spin": float(env.ball_spin)},
            "players": players_pos,
            "score": [env.match_score[0], env.match_score[1]]
            if hasattr(env, "match_score")
            else [0, 0],
            "time": float(env.match_time) if hasattr(env, "match_time") else 0.0,
            "spec": float(env.spectacle_score) if hasattr(env, "spectacle_score") else 0.0,
            "trait": str(env.patch_version),
            "lb": leaderboard,
        }

        payload = json.dumps(state_dict).encode("utf-8")
        try:
            self.sock.sendto(payload, (self.ip, self.port))
        except Exception as e:
            print(f"Error sending telemetry: {e}")
