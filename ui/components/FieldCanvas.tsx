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
        if (frame.ball) {
            ctx.fillStyle = '#ffffff';
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#ffffff';
            ctx.beginPath();
            ctx.arc(frame.ball.pos[0] * 1, frame.ball.pos[1] * 1, 3, 0, Math.PI * 2);
            ctx.fill();
        }

        // Players
        if (frame.p) {
            frame.p.forEach((p: any) => {
                ctx.fillStyle = p.team === 0 ? '#3b82f6' : '#f43f5e';
                ctx.shadowColor = ctx.fillStyle;
                ctx.beginPath();
                ctx.arc(p.pos[0] * 1, p.pos[1] * 1, 5, 0, Math.PI * 2);
                ctx.fill();
            });
        }

        // Overlays (Explainability)
        if (frame.o) {
            // 1. Attention Map (Draw lines between agents)
            if (frame.o.attn) {
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                ctx.lineWidth = 1;
                // Simplified visualization of high-attention links
                const players = frame.p;
                for (let i = 0; i < players.length; i++) {
                    for (let j = i + 1; j < players.length; j++) {
                        const weight = frame.o.attn[i][j] || 0;
                        if (weight > 0.5) {
                            ctx.beginPath();
                            ctx.moveTo(players[i].pos[0] * 1, players[i].pos[1] * 1);
                            ctx.lineTo(players[j].pos[0] * 1, players[j].pos[1] * 1);
                            ctx.stroke();
                        }
                    }
                }
            }

            // 2. Planned Paths (Trajectories)
            if (frame.o.paths) {
                ctx.setLineDash([5, 5]);
                ctx.strokeStyle = '#22d3ee';
                frame.o.paths.forEach((path: any) => {
                    ctx.beginPath();
                    ctx.moveTo(path[0].x * 1, path[0].y * 1);
                    path.slice(1).forEach((pt: any) => ctx.lineTo(pt.x * 1, pt.y * 1));
                    ctx.stroke();
                });
                ctx.setLineDash([]);
            }
        }
    }, [frame]);

    return <canvas ref={canvasRef} width={600} height={400} className="w-full h-full" />;
}
