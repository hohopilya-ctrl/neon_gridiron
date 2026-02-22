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
