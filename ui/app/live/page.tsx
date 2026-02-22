"use client";
import React, { useEffect, useState } from 'react';
import FieldCanvas from '../../components/FieldCanvas';

export default function LiveMatch() {
    const [frame, setFrame] = useState(null);

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8000/ws/live");
        ws.onmessage = (e) => setFrame(JSON.parse(e.data));
        return () => ws.close();
    }, []);

    return (
        <div className="min-h-screen bg-black p-4">
            <div className="flex justify-between items-center mb-4">
                <div className="text-3xl font-bold text-cyan-400 tracking-tighter">LIVE BROADCAST</div>
                {frame && (
                    <div className="bg-slate-900 p-2 rounded border border-cyan-800">
                        <span className="text-pink-500 font-bold">SCORE: {frame.s[0]} - {frame.s[1]}</span>
                        <span className="ml-4 text-slate-500">TICK: {frame.t}</span>
                    </div>
                )}
            </div>

            <div className="aspect-video w-full bg-slate-950 border-2 border-slate-800 rounded-lg overflow-hidden relative">
                <FieldCanvas frame={frame} />
                {/* Overlays for explainability can go here */}
            </div>
        </div>
    );
}
