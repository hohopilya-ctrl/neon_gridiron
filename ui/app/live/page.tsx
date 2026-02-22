"use client";
import React, { useEffect, useState } from 'react';
import FieldCanvas from '../../components/FieldCanvas';
import { UltraWSClient } from '../../lib/ws';
import { Frame } from '../../lib/frame';

export default function LiveMatch() {
    const [frame, setFrame] = useState<Frame | null>(null);

    useEffect(() => {
        const client = new UltraWSClient("ws://localhost:8000/ws/live", (newFrame) => {
            setFrame(newFrame);
        });
        client.connect();
        return () => client.close();
    }, []);

    return (
        <div className="min-h-screen bg-black p-4 font-mono">
            <div className="flex justify-between items-center mb-4">
                <div className="text-3xl font-extrabold text-cyan-400 tracking-tighter">
                    NEON ULTRA <span className="text-slate-600">v2.2.0</span>
                </div>
                {frame && (
                    <div className="flex gap-4">
                        <div className="bg-slate-900 px-4 py-2 rounded-lg border border-cyan-500/30">
                            <span className="text-slate-500 text-xs block">MATCH STATUS</span>
                            <span className="text-pink-500 font-bold text-xl">
                                {frame.score[0]} <span className="text-slate-700">-</span> {frame.score[1]}
                            </span>
                        </div>
                        <div className="bg-slate-900 px-4 py-2 rounded-lg border border-slate-700">
                            <span className="text-slate-500 text-xs block">PRESSURE INDEX</span>
                            <span className="text-cyan-400 font-bold text-xl">{(frame.pressure || 0).toFixed(2)}</span>
                        </div>
                        <div className="bg-slate-900 px-4 py-2 rounded-lg border border-slate-700">
                            <span className="text-slate-500 text-xs block">SIM TICK</span>
                            <span className="text-slate-400 font-bold text-xl">#{frame.tick}</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="aspect-video w-full bg-slate-950 border-2 border-slate-800 rounded-2xl overflow-hidden relative shadow-[0_0_50px_rgba(0,0,0,1)]">
                <FieldCanvas frame={frame} />
                <div className="absolute top-4 right-4 pointer-events-none opacity-50">
                    <div className="text-[10px] text-cyan-500 text-right">BROADCAST_SECURE</div>
                    <div className="h-1 w-24 bg-cyan-900 rounded-full mt-1 overflow-hidden">
                        <div className="h-full bg-cyan-400 animate-pulse w-2/3"></div>
                    </div>
                </div>
            </div>
        </div>
    );
}
