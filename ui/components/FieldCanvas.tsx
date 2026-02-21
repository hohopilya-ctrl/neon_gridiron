# OUTPUT PART 8 / Y
# Neon Gridiron ULTRA: Frontend Components and Styles

# File: ui / components / FieldCanvas.tsx
"use client";
import React, { useRef, useEffect } from 'react';

export default function FieldCanvas({ frame }: { frame: any }) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || !frame) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Background
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Grid
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 1;
        for (let i = 0; i < canvas.width; i += 40) {
            ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
        }
        for (let i = 0; i < canvas.height; i += 40) {
            ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); ctx.stroke();
        }

        // Ball
        ctx.fillStyle = '#ffffff';
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#ffffff';
        ctx.beginPath();
        ctx.arc(frame.ball.x * 10, frame.ball.y * 10, 3, 0, Math.PI * 2);
        ctx.fill();

        // Players
        frame.players.forEach((p: any) => {
            ctx.fillStyle = p.team === 0 ? '#3b82f6' : '#f43f5e';
            ctx.shadowColor = ctx.fillStyle;
            ctx.beginPath();
            ctx.arc(p.pos[0] * 10, p.pos[1] * 10, 5, 0, Math.PI * 2);
            ctx.fill();
        });
    }, [frame]);

    return <canvas ref={canvasRef} width={600} height={400} className="w-full h-full" />;
}
# lines: 45

# File: ui / styles / globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
    --neon - cyan: #22d3ee;
    --neon - pink: #f43f5e;
}

body {
    @apply bg - slate - 950 text - slate - 200;
    background - image: radial - gradient(circle at 50 % 50 %, #1e1b4b 0 %, #020617 100 %);
}

.neon - border {
    @apply border - 2 border - cyan - 500 shadow - [0_0_15px_rgba(34, 211, 238, 0.5)];
}

.neon - text {
    @apply text - cyan - 400 drop - shadow - [0_0_8px_rgba(34, 211, 238, 0.8)];
}
# lines: 25

# File: tools / validate_configs.py
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
# lines: 25

# File: pyproject.toml
[tool.ruff]
line - length = 100
target - version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"

[project]
name = "neon-gridiron-ultra"
version = "1.0.0"
dependencies = [
    "gymnasium>=0.29.0",
    "pymunk>=6.5.0",
    "torch>=2.1.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "pyyaml>=6.0.0",
    "numpy>=1.26.0"
]
# lines: 30

# END OF PART 8 - to continue output next part.
