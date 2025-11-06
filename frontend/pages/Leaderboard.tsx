import { useState } from "react";
import { useGlobalLeaderboard, useProfessionLeaderboard } from "../hooks/useLeaderboard";

const professions = [
  "teacher","farmer","engineer","doctor","artist","entrepreneur","writer","athlete"
];

export default function Leaderboard() {
  const [tab, setTab] = useState<'global'|'profession'>('global');
  const [profession, setProfession] = useState<string>('teacher');

  const global = useGlobalLeaderboard();
  const byProf = useProfessionLeaderboard(tab === 'profession' ? profession : null);

  const active = tab === 'global' ? global : byProf;

  return (
    <div className="min-h-screen p-6 max-w-3xl mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Leaderboard</h1>

      <div className="flex gap-2">
        <button className={`px-3 py-2 rounded ${tab==='global'?'bg-blue-600':''}`} onClick={()=>setTab('global')}>Global</button>
        <button className={`px-3 py-2 rounded ${tab==='profession'?'bg-blue-600':''}`} onClick={()=>setTab('profession')}>By Profession</button>
        {tab==='profession' && (
          <select className="ml-2 bg-[#0F1724] p-2 rounded" value={profession} onChange={e=>setProfession(e.target.value)}>
            {professions.map(p=> <option key={p} value={p}>{p}</option>)}
          </select>
        )}
      </div>

      {active.loading && <div>Loading...</div>}
      {active.error && <div className="text-red-400">{active.error}</div>}

      <div className="space-y-2">
        {active.data.map((row:any)=> (
          <div key={row.userId} className="flex items-center justify-between p-3 bg-[#0F1724] rounded">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#28C76F] to-[#0E6FFF]" />
              <div>
                <div className="font-semibold">#{row.rank} {row.username}</div>
                <div className="text-xs opacity-70 capitalize">{row.profession}</div>
              </div>
            </div>
            <div className="text-[#FFEA7A] font-bold">{row.pesaPoints}</div>
          </div>
        ))}
      </div>

      {active.meta && (
        <div className="flex items-center gap-2 pt-2">
          <button className="px-3 py-1 rounded bg-gray-700" disabled={active.page<=1} onClick={()=>active.setPage(active.page-1)}>Prev</button>
          <div className="text-sm">Page {active.meta.page} / {Math.ceil(active.meta.total / active.meta.page_size) || 1}</div>
          <button className="px-3 py-1 rounded bg-gray-700" disabled={(active.meta.page*active.meta.page_size)>=active.meta.total} onClick={()=>active.setPage(active.page+1)}>Next</button>
        </div>
      )}
    </div>
  );
}
