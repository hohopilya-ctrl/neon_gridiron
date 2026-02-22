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

        // 1. Clear & Setup Background
        const w = canvas.width;
        const h = canvas.height;
        ctx.fillStyle = '#020617';
        ctx.fillRect(0, 0, w, h);

        // 2. Cyberpunk Grid
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 0.5;
        for (let i = 0; i < w; i += 40) {
            ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, h); ctx.stroke();
        }
        for (let i = 0; i < h; i += 40) {
            ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(w, i); ctx.stroke();
        }

        // 3. Pitch Lines (Standard Football Ground)
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 2;
        ctx.strokeRect(40, 40, w - 80, h - 80); // Boundary
        ctx.beginPath(); // Center Line
        ctx.moveTo(w / 2, 40);
        ctx.lineTo(w / 2, h - 40);
        ctx.stroke();
        ctx.beginPath(); // Center Circle
        ctx.arc(w / 2, h / 2, 60, 0, Math.PI * 2);
        ctx.stroke();

        // 4. Trace Paths (Historical/Predicted)
        const overlays = (frame as any).o || frame.overlays || {};
        if (overlays.paths) {
            ctx.strokeStyle = 'rgba(34, 211, 238, 0.3)';
            ctx.setLineDash([5, 5]);
            overlays.paths.forEach((path: any) => {
                ctx.beginPath();
                ctx.moveTo(path[0][0], path[0][1]);
                for (let i = 1; i < path.length; i++) {
                    ctx.lineTo(path[i][0], path[i][1]);
                }
                ctx.stroke();
            });
            ctx.setLineDash([]);
        }

        // 5. Render Players (frame.p or frame.players)
        const players = (frame as any).p || frame.players || [];
        players.forEach((p: any) => {
            const isBlue = p.team === 'BLUE' || p.team === 0;
            ctx.fillStyle = isBlue ? '#3b82f6' : '#f43f5e';
            ctx.shadowBlur = 10;
            ctx.shadowColor = ctx.fillStyle;

            ctx.beginPath();
            ctx.arc(p.pos[0], p.pos[1], 8, 0, Math.PI * 2);
            ctx.fill();

            // Player ID Label
            ctx.fillStyle = '#94a3b8';
            ctx.font = '10px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(p.id.split('_')[1] || '', p.pos[0], p.pos[1] - 12);
            ctx.shadowBlur = 0;
        });

        // 6. Render Ball (frame.b.p or frame.ball.pos)
        const ball = (frame as any).b || frame.ball;
        if (ball) {
            const bp = ball.p || ball.pos;
            if (bp) {
                ctx.fillStyle = '#ffffff';
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#ffffff';
                ctx.beginPath();
                ctx.arc(bp[0], bp[1], 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            }
        }

    }, [frame]);

    return (
        <canvas
            ref={canvasRef}
            width={900}
            height={520}
            className="w-full h-auto bg-slate-950 rounded-xl"
        />
    );
}
