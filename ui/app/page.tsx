# OUTPUT PART 7 / Y
# Neon Gridiron ULTRA: Next.js Frontend(Dashboard & Live)

# File: ui / package.json
{
    "name": "neon-gridiron-ui",
        "version": "1.0.0",
            "dependencies": {
        "next": "14.0.0",
            "react": "18.2.0",
                "react-dom": "18.2.0",
                    "lucide-react": "^0.284.0",
                        "recharts": "^2.9.0",
                            "clsx": "^2.0.0",
                                "tailwind-merge": "^1.14.0"
    },
    "devDependencies": {
        "autoprefixer": "^10.4.16",
            "postcss": "^8.4.31",
                "tailwindcss": "^3.3.3",
                    "typescript": "^5.2.2"
    }
}
# lines: 20

# File: ui / app / page.tsx
import Link from 'next/link';

export default function Home() {
    return (
        <main className="min-h-screen bg-slate-950 text-cyan-400 p-8 font-mono">
            <h1 className="text-6xl font-black mb-8 border-b-4 border-cyan-500 pb-4 skew-x-[-10deg]">
                NEON GRIDIRON <span className="text-pink-500 italic">ULTRA</span>
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <NavCard title="LIVE MATCH" href="/live" desc="Watch current generation training" color="border-cyan-500" />
                <NavCard title="TRAINING HUB" href="/training" desc="Elo, Diversity, PBT History" color="border-pink-500" />
                <NavCard title="REPLAYS" href="/replays" desc="Match archival and analysis" color="border-purple-500" />
                <NavCard title="EXPLOIT LAB" href="/exploits" desc="Anomalies and detectors" color="border-red-500" />
                <NavCard title="GENERATIONS" href="/generations" desc="Compare agent evolution" color="border-green-500" />
            </div>
        </main>
    );
}

function NavCard({ title, href, desc, color }: any) {
    return (
        <Link href={href} className={`block p-6 bg-slate-900 border-l-8 ${color} hover:bg-slate-800 transition-all group`}>
            <h2 className="text-2xl font-bold group-hover:translate-x-2 transition-transform">{title}</h2>
            <p className="text-slate-400 mt-2">{desc}</p>
        </Link>
    );
}
# lines: 35

# File: ui / app / live / page.tsx
"use client";
import React, { useEffect, useState } from 'react';
import FieldCanvas from '@/components/FieldCanvas';

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
                        <span className="text-pink-500 font-bold">SCORE: {frame.score[0]} - {frame.score[1]}</span>
                        <span className="ml-4 text-slate-500">TICK: {frame.tick}</span>
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
# lines: 35

# END OF PART 7 - to continue output next part.
