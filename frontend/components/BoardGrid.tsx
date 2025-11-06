interface PlayerTokens {
  playerId: string;
  positions: number[];
  color: string;
}

interface BoardGridProps {
  totalTiles: number;
  yellowStripSpots: number[];
  playerTokens: PlayerTokens[];
}

export default function BoardGrid({ totalTiles, yellowStripSpots, playerTokens }: BoardGridProps) {
  const cols = 8;
  const rows = Math.ceil(totalTiles / cols);

  const getTileNumber = (row: number, col: number): number => {
    if (row % 2 === 0) {
      return row * cols + col + 1;
    } else {
      return row * cols + (cols - col);
    }
  };

  return (
    <div className="bg-[#1A2332] rounded-2xl p-4 shadow-2xl">
      <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
        {Array.from({ length: totalTiles }).map((_, idx) => {
          const row = Math.floor(idx / cols);
          const col = idx % cols;
          const tileNum = getTileNumber(row, col);
          const isYellow = yellowStripSpots.includes(tileNum);

          return (
            <div
              key={idx}
              className={`
                relative aspect-square rounded-lg border-2 transition-all
                ${isYellow 
                  ? "bg-gradient-to-br from-[#FFEA7A] to-[#FFD700] border-[#FFEA7A]" 
                  : "bg-[#0F1724] border-[#2A3342]"
                }
                hover:border-[#0E6FFF]
              `}
            >
              <div className="absolute top-1 left-1 text-[10px] font-medium text-foreground/60">
                {tileNum}
              </div>
              
              {playerTokens.map((player) =>
                player.positions.map((pos, tokenIdx) => {
                  if (pos === tileNum) {
                    return (
                      <div
                        key={`${player.playerId}-${tokenIdx}`}
                        className="absolute inset-0 flex items-center justify-center"
                      >
                        <div
                          className="w-6 h-6 rounded-full border-2 border-white shadow-lg"
                          style={{ backgroundColor: player.color }}
                        />
                      </div>
                    );
                  }
                  return null;
                })
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
