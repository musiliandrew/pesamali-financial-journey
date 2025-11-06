import { useEffect, useState } from "react";
import backend from "~backend/client";

interface GameUpdate {
  type: string;
  matchId: string;
  data: any;
  timestamp: Date;
}

export function useGameStream(matchId: string | undefined) {
  const [updates, setUpdates] = useState<GameUpdate[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!matchId) return;

    let stream: any;
    
    const connect = async () => {
      try {
        stream = await backend.game.streamUpdates({ matchId });
        setConnected(true);
        
        for await (const update of stream) {
          setUpdates(prev => [...prev, update]);
        }
      } catch (err) {
        console.error("Stream error:", err);
        setConnected(false);
      }
    };

    connect();

    return () => {
      if (stream) {
        stream.close?.();
      }
      setConnected(false);
    };
  }, [matchId]);

  return { updates, connected };
}
