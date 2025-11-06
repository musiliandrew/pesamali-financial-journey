import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import backend from "~backend/client";
import BoardGrid from "../components/BoardGrid";
import PlayerHUD from "../components/PlayerHUD";
import DiceRoller from "../components/DiceRoller";
import { Button } from "@/components/ui/button";

export default function Game() {
  const { matchId } = useParams();
  const [qs] = useSearchParams();
  const userId = qs.get("userId") || "user_1";
  const [diceResult, setDiceResult] = useState<number[]>([]);
  const [isRolling, setIsRolling] = useState(false);
  const [savingAmount, setSavingAmount] = useState<number>(100);
  const [savingsCardId, setSavingsCardId] = useState<string>("");
  const [spendingCardId, setSpendingCardId] = useState<string>("");
  const [dreamId, setDreamId] = useState<string>("");

  const { data: gameState, refetch: refetchState } = useQuery({
    queryKey: ["gameState", matchId],
    queryFn: () => backend.game.getState({ matchId: matchId! }),
    refetchInterval: 2000
  });

  const API_BASE = import.meta.env.VITE_BACKEND_BASE_URL || "http://localhost:8000";
  const authHeader = () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("jwt") : null;
    return token ? { Authorization: `Bearer ${token}` } : {} as Record<string, string>;
  };

  const { data: savingsCards } = useQuery({
    queryKey: ["savingsCards"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/cards/savings`, { headers: { ...authHeader() } });
      return res.json();
    }
  });
  const { data: spendingCards } = useQuery({
    queryKey: ["spendingCards"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/cards/spending`, { headers: { ...authHeader() } });
      return res.json();
    }
  });
  const { data: dreamsList } = useQuery({
    queryKey: ["dreamsList"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/dreams`, { headers: { ...authHeader() } });
      return res.json();
    }
  });

  useEffect(() => {
    if (!matchId) return;

    let stream: any;
    
    const connect = async () => {
      try {
        stream = await backend.game.streamUpdates({ matchId });
        for await (const update of stream) {
          console.log("Game update:", update);
        }
      } catch (err) {
        console.error("Stream error:", err);
      }
    };

    connect();

    return () => {
      if (stream) {
        stream.close?.();
      }
    };
  }, [matchId]);

  const handleRollDice = async () => {
    if (!matchId) return;
    
    setIsRolling(true);
    try {
      const result = await backend.game.rollDice({ matchId, userId });
      setDiceResult(result.dice);
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => setIsRolling(false), 900);
    }
  };

  const drawPlayingCard = async () => {
    if (!matchId) return;
    await fetch(`${API_BASE}/matches/${matchId}/cards/draw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ userId })
    }).then(r => r.json()).then(j => { console.log('card_draw', j); refetchState(); }).catch(console.error);
  };

  const playSavings = async () => {
    if (!matchId || !savingsCardId || !savingAmount) return;
    await fetch(`${API_BASE}/matches/${matchId}/cards/savings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ userId, cardId: savingsCardId, amount: savingAmount })
    }).then(r => r.json()).then(j => { console.log('savings_play', j); refetchState(); }).catch(console.error);
  };

  const playSpending = async () => {
    if (!matchId || !spendingCardId) return;
    await fetch(`${API_BASE}/matches/${matchId}/cards/spending`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ userId, cardId: spendingCardId })
    }).then(r => r.json()).then(j => { console.log('spending_play', j); refetchState(); }).catch(console.error);
  };

  const purchaseDream = async () => {
    if (!matchId || !dreamId) return;
    await fetch(`${API_BASE}/matches/${matchId}/dreams/purchase`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ userId, dreamId })
    }).then(r => r.json()).then(j => { console.log('dream_purchase', j); refetchState(); }).catch(console.error);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <PlayerHUD
        username="Player 1"
        profession="teacher_campus"
        avatarId="avatar_1"
        currentPoints={1200}
        savingsPoints={0}
        liabilityPoints={0}
      />

      <div className="flex-1 flex items-center justify-center p-4">
        <BoardGrid
          totalTiles={80}
          yellowStripSpots={[1, 80, 5, 76, 11, 70, 19, 62, 25, 56, 32, 49, 38, 43, 48, 33, 54, 27, 59, 22, 66, 15, 71, 10, 77, 4]}
          playerTokens={[
            { playerId: "p1", positions: [0, 0, 0, 0], color: "#FF6B6B" }
          ]}
        />
      </div>

      <div className="p-4 bg-[#1A2332] border-t border-[#2A3342]">
        <div className="max-w-md mx-auto flex items-center justify-center gap-4">
          <DiceRoller
            dice={diceResult}
            isRolling={isRolling}
            onRoll={handleRollDice}
          />
          {diceResult.length > 0 && !isRolling && (
            <div className="text-center">
              <div className="text-2xl font-bold text-foreground">
                {diceResult[0] + diceResult[1]}
              </div>
              <div className="text-xs text-muted-foreground">Total</div>
            </div>
          )}
        </div>
        <div className="max-w-3xl mx-auto mt-6 grid gap-3 md:grid-cols-2">
          <div className="p-3 rounded bg-[#0F1724] space-y-2">
            <div className="font-semibold">Yellow-strip play</div>
            <button className="px-3 py-2 rounded bg-blue-600" onClick={drawPlayingCard}>Draw playing card</button>
          </div>
          <div className="p-3 rounded bg-[#0F1724] space-y-2">
            <div className="font-semibold">Savings card</div>
            {Array.isArray(savingsCards) && savingsCards.length > 0 ? (
              <select className="w-full p-2 rounded bg-[#0B1120]" value={savingsCardId} onChange={e=>setSavingsCardId(e.target.value)}>
                <option value="">Select savings card</option>
                {savingsCards.map((c:any)=> <option key={c.id} value={c.id}>{c.name} (≥{c.save_threshold})</option>)}
              </select>
            ) : (
              <input className="w-full p-2 rounded bg-[#0B1120]" placeholder="Savings Card ID" value={savingsCardId} onChange={e=>setSavingsCardId(e.target.value)} />
            )}
            <input className="w-full p-2 rounded bg-[#0B1120]" placeholder="Amount" type="number" value={savingAmount} onChange={e=>setSavingAmount(parseInt(e.target.value||'0'))} />
            <button className="px-3 py-2 rounded bg-green-600" onClick={playSavings}>Play savings</button>
          </div>
          <div className="p-3 rounded bg-[#0F1724] space-y-2">
            <div className="font-semibold">Spending card</div>
            {Array.isArray(spendingCards) && spendingCards.length > 0 ? (
              <select className="w-full p-2 rounded bg-[#0B1120]" value={spendingCardId} onChange={e=>setSpendingCardId(e.target.value)}>
                <option value="">Select spending card</option>
                {spendingCards.map((c:any)=> <option key={c.id} value={c.id}>{c.name} ({c.total_cost})</option>)}
              </select>
            ) : (
              <input className="w-full p-2 rounded bg-[#0B1120]" placeholder="Spending Card ID" value={spendingCardId} onChange={e=>setSpendingCardId(e.target.value)} />
            )}
            <button className="px-3 py-2 rounded bg-amber-600" onClick={playSpending}>Play spending</button>
          </div>
          <div className="p-3 rounded bg-[#0F1724] space-y-2">
            <div className="font-semibold">Purchase dream</div>
            {Array.isArray(dreamsList) && dreamsList.length > 0 ? (
              <select className="w-full p-2 rounded bg-[#0B1120]" value={dreamId} onChange={e=>setDreamId(e.target.value)}>
                <option value="">Select dream</option>
                {dreamsList.map((d:any)=> <option key={d.id} value={d.id}>{d.name} ({d.cost})</option>)}
              </select>
            ) : (
              <input className="w-full p-2 rounded bg-[#0B1120]" placeholder="Dream ID" value={dreamId} onChange={e=>setDreamId(e.target.value)} />
            )}
            <button className="px-3 py-2 rounded bg-purple-600" onClick={purchaseDream}>Purchase</button>
          </div>
        </div>
      </div>
    </div>
  );
}
