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

        // Analyst Overlays: Compactness & Pressure
        if (frame.compactness) {
            Object.entries(frame.compactness).forEach(([team, score]) => {
                const isBlue = team.includes('BLUE');
                const teamPlayers = frame.players.filter(p => p.team === (isBlue ? 'BLUE' : 'RED'));
                if (teamPlayers.length === 0) return;

                const centroidX = teamPlayers.reduce((a, b) => a + b.pos[0], 0) / teamPlayers.length;
                const centroidY = teamPlayers.reduce((a, b) => a + b.pos[1], 0) / teamPlayers.length;

                // Draw Compactness Ring
                ctx.strokeStyle = isBlue ? `rgba(59, 130, 246, ${score * 0.3})` : `rgba(244, 63, 94, ${score * 0.3})`;
                ctx.setLineDash([5, 5]);
                ctx.beginPath();
                ctx.arc(centroidX, centroidY, 60, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);
            });
        }

        if (frame.pressure !== undefined && frame.ball) {
            const bp = frame.ball.pos;
            ctx.strokeStyle = `rgba(255, 255, 255, ${frame.pressure * 0.5})`;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(bp[0], bp[1], 15 + frame.pressure * 20, 0, Math.PI * 2);
            ctx.stroke();
        }

        // Overlays (Attention links)
        if (frame.overlays?.attn && frame.players) {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.lineWidth = 1;
            const players = frame.players;
            // Assuming 14x14 attention map
            for (let i = 0; i < Math.min(players.length, 14); i++) {
                for (let j = i + 1; j < Math.min(players.length, 14); j++) {
                    const row = frame.overlays.attn[i];
                    if (!row) continue;
                    const weight = row[j] || 0;
                    if (weight > 0.3) {
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
