import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import backend from "~backend/client";
import BoardGrid from "../components/BoardGrid";
import PlayerHUD from "../components/PlayerHUD";
import DiceRoller from "../components/DiceRoller";
import { Button } from "@/components/ui/button";

export default function Game() {
  const { matchId } = useParams();
  const [diceResult, setDiceResult] = useState<number[]>([]);
  const [isRolling, setIsRolling] = useState(false);

  const { data: gameState } = useQuery({
    queryKey: ["gameState", matchId],
    queryFn: () => backend.game.getState({ matchId: matchId! }),
    refetchInterval: 2000
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
      const result = await backend.game.rollDice({ matchId, userId: "user_1" });
      setDiceResult(result.dice);
    } catch (err) {
      console.error(err);
    } finally {
      setTimeout(() => setIsRolling(false), 900);
    }
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
      </div>
    </div>
  );
}
