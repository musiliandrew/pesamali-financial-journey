import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Trophy, TrendingUp, Coins, Share2 } from "lucide-react";

export default function PostGame() {
  const { matchId } = useParams();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center space-y-4 pt-8">
          <div className="text-6xl">🎉</div>
          <h1 className="text-3xl font-bold text-foreground">Victory!</h1>
          <p className="text-muted-foreground">You achieved your dream!</p>
        </div>

        <div className="bg-[#1A2332] rounded-2xl p-6 space-y-4">
          <h2 className="text-xl font-semibold text-foreground">Game Summary</h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-[#0F1724] rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Trophy className="h-5 w-5 text-[#FFEA7A]" />
                <span className="text-sm text-muted-foreground">Final Score</span>
              </div>
              <div className="text-2xl font-bold text-foreground">2,450</div>
            </div>
            <div className="bg-[#0F1724] rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-5 w-5 text-[#28C76F]" />
                <span className="text-sm text-muted-foreground">Asset Returns</span>
              </div>
              <div className="text-2xl font-bold text-foreground">+640</div>
            </div>
            <div className="bg-[#0F1724] rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <Coins className="h-5 w-5 text-[#0E6FFF]" />
                <span className="text-sm text-muted-foreground">Savings</span>
              </div>
              <div className="text-2xl font-bold text-foreground">650</div>
            </div>
            <div className="bg-[#0F1724] rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-5 w-5 text-[#FF6B6B]" />
                <span className="text-sm text-muted-foreground">Rank</span>
              </div>
              <div className="text-2xl font-bold text-foreground">#1</div>
            </div>
          </div>

          <div className="space-y-2">
            <h3 className="font-medium text-foreground">Achievements Unlocked</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2 p-2 bg-[#0F1724] rounded-lg">
                <div className="text-xl">🎯</div>
                <span className="text-sm text-foreground">Dream Achiever</span>
              </div>
              <div className="flex items-center gap-2 p-2 bg-[#0F1724] rounded-lg">
                <div className="text-xl">💰</div>
                <span className="text-sm text-foreground">Savings Master</span>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <Button className="w-full bg-[#0E6FFF] hover:bg-[#0D5FE5]">
            <Share2 className="h-4 w-4 mr-2" />
            Share Results
          </Button>
          <Button
            variant="outline"
            className="w-full"
            onClick={() => navigate("/lobby")}
          >
            Back to Lobby
          </Button>
        </div>
      </div>
    </div>
  );
}
