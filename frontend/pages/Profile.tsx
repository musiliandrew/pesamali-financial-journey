import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Trophy, Flame, Target } from "lucide-react";
import backend from "~backend/client";

export default function Profile() {
  const { userId } = useParams();
  
  const { data: user } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => backend.user.get({ id: userId! })
  });

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-muted-foreground">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        <Link to="/lobby">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Lobby
          </Button>
        </Link>

        <div className="bg-[#1A2332] rounded-2xl p-6 space-y-6">
          <div className="flex items-center gap-4">
            <div className="w-24 h-24 bg-gradient-to-br from-[#0E6FFF] to-[#28C76F] rounded-full flex items-center justify-center text-4xl">
              👤
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-semibold text-foreground">{user.username}</h1>
              <p className="text-muted-foreground capitalize">
                {user.profession.replace(/_/g, " ")}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#0F1724] rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-[#FFEA7A]">{user.pesamaliPoints}</div>
              <div className="text-xs text-muted-foreground mt-1">Pesa Mali Points</div>
            </div>
            <div className="bg-[#0F1724] rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-[#28C76F]">{user.totalWins}</div>
              <div className="text-xs text-muted-foreground mt-1">Wins</div>
            </div>
            <div className="bg-[#0F1724] rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-[#FF6B6B]">{user.totalGames}</div>
              <div className="text-xs text-muted-foreground mt-1">Games</div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-[#0F1724] rounded-xl">
              <div className="flex items-center gap-3">
                <Flame className="h-5 w-5 text-[#FF6B6B]" />
                <span className="text-sm text-foreground">Current Streak</span>
              </div>
              <span className="font-semibold text-foreground">{user.currentStreak} days</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-[#0F1724] rounded-xl">
              <div className="flex items-center gap-3">
                <Trophy className="h-5 w-5 text-[#FFEA7A]" />
                <span className="text-sm text-foreground">Longest Streak</span>
              </div>
              <span className="font-semibold text-foreground">{user.longestStreak} days</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-[#0F1724] rounded-xl">
              <div className="flex items-center gap-3">
                <Target className="h-5 w-5 text-[#28C76F]" />
                <span className="text-sm text-foreground">Win Rate</span>
              </div>
              <span className="font-semibold text-foreground">
                {user.totalGames > 0 ? Math.round((user.totalWins / user.totalGames) * 100) : 0}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
