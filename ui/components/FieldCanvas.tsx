"use client";
import React, { useRef, useEffect } from 'react';
import { Frame } from '../lib/frame';

export default function FieldCanvas({ frame }: { frame: Frame | null }) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas || !frame) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear and setup
        const w = canvas.width;
        const h = canvas.height;
        ctx.fillStyle = '#020617';
        ctx.fillRect(0, 0, w, h);

        // Grid (Cyberpunk style)
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 0.5;
        for (let i = 0; i < w; i += 40) {
            ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, h); ctx.stroke();
        }
        for (let i = 0; i < h; i += 40) {
            ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(w, i); ctx.stroke();
        }

        // Center line
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.moveTo(w / 2, 0); ctx.lineTo(w / 2, h); ctx.stroke();

        // Players (v2.2.0: frame.players)
        if (frame.players) {
            frame.players.forEach((p) => {
                const isBlue = p.team === 'BLUE';
                ctx.fillStyle = isBlue ? '#3b82f6' : '#f43f5e';
                ctx.shadowBlur = 15;
                ctx.shadowColor = ctx.fillStyle;

                ctx.beginPath();
                ctx.arc(p.pos[0], p.pos[1], 6, 0, Math.PI * 2);
                ctx.fill();

                // Direction indicator
                if (Math.abs(p.vel[0]) > 0.1 || Math.abs(p.vel[1]) > 0.1) {
                    ctx.strokeStyle = isBlue ? '#60a5fa' : '#fb7185';
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.moveTo(p.pos[0], p.pos[1]);
                    ctx.lineTo(p.pos[0] + p.vel[0] * 0.2, p.pos[1] + p.vel[1] * 0.2);
                    ctx.stroke();
                }
            });
        }

        // Ball (v2.2.0: frame.ball)
        if (frame.ball) {
            const bp = frame.ball.pos;
            ctx.fillStyle = '#ffffff';
            ctx.shadowBlur = 20;
            ctx.shadowColor = '#ffffff';
            ctx.beginPath();
            ctx.arc(bp[0], bp[1], 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        }

        // Overlays (Phase 26 logic)
        if (frame.overlays?.attn && frame.players) {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
            ctx.lineWidth = 1;
            const players = frame.players;
            for (let i = 0; i < players.length; i++) {
                for (let j = i + 1; j < players.length; j++) {
                    const weight = frame.overlays.attn[i][j] || 0;
                    if (weight > 0.5) {
                        ctx.beginPath();
                        ctx.moveTo(players[i].pos[0], players[i].pos[1]);
                        ctx.lineTo(players[j].pos[0], players[j].pos[1]);
                        ctx.stroke();
                    }
                }
            }
        }
    }, [frame]);

    return <canvas ref={canvasRef} width={600} height={400} className="w-full h-full" />;
}
