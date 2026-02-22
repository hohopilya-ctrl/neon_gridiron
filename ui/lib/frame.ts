export type PlayerFrame = {
  id: string;
  team: string;
  pos: [number, number];
  vel: [number, number];
};

export type Frame = {
  tick: number;
  score: [number, number];
  ball: { pos: [number, number]; vel?: [number, number] };
  players: PlayerFrame[];
  overlays?: { attn?: number[][] };
};

export function normalizeFrame(raw: Record<string, unknown>): Frame {
  const scoreRaw = Array.isArray(raw.s) ? raw.s : [0, 0];
  const ballPos = Array.isArray(raw.b) ? raw.b : [300, 200];
  const playersRaw = Array.isArray(raw.p) ? raw.p : [];

  const players = playersRaw.map((p) => {
    const player = p as Record<string, unknown>;
    return {
      id: String(player.id ?? "unknown"),
      team: String(player.team ?? "BLUE"),
      pos: (Array.isArray(player.pos) ? player.pos : [0, 0]) as [number, number],
      vel: (Array.isArray(player.vel) ? player.vel : [0, 0]) as [number, number],
    };
  });

  return {
    tick: Number(raw.t ?? 0),
    score: [Number(scoreRaw[0] ?? 0), Number(scoreRaw[1] ?? 0)],
    ball: { pos: [Number(ballPos[0] ?? 300), Number(ballPos[1] ?? 200)] },
    players,
    overlays: (raw.o as { attn?: number[][] } | undefined) ?? {},
  };
}
