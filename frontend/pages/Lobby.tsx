import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Bell, Users, Play, ShoppingBag } from "lucide-react";
import backend from "~backend/client";
import MatchSetupModal from "../components/MatchSetupModal";

export default function Lobby() {
  const [searchParams] = useSearchParams();
  const userId = searchParams.get("userId") || "user_1";
  const [showMatchSetup, setShowMatchSetup] = useState(false);
  const navigate = useNavigate();

  const { data: user } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => backend.user.get({ id: userId })
  });

  const { data: mockUsers } = useQuery({
    queryKey: ["mockUsers"],
    queryFn: () => backend.user.mockUsers()
  });

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-foreground">PesaMali Lobby</h1>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon">
              <Bell className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(`/profile/${userId}`)}
            >
              <Users className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <ShoppingBag className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {user && (
          <div className="bg-[#1A2332] rounded-2xl p-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-[#0E6FFF] to-[#28C76F] rounded-full flex items-center justify-center text-2xl">
                👤
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-foreground">{user.username}</h2>
                <p className="text-sm text-muted-foreground capitalize">
                  {user.profession.replace(/_/g, " ")}
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-[#FFEA7A]">{user.pesamaliPoints}</div>
                <div className="text-xs text-muted-foreground">Points</div>
              </div>
            </div>
          </div>
        )}

        <div className="grid gap-4">
          <Button
            onClick={() => setShowMatchSetup(true)}
            className="w-full h-16 bg-[#0E6FFF] hover:bg-[#0D5FE5] text-lg"
          >
            <Play className="h-6 w-6 mr-2" />
            Create New Match
          </Button>
        </div>

        <div className="bg-[#1A2332] rounded-2xl p-6 space-y-4">
          <h3 className="text-lg font-semibold text-foreground">Online Players</h3>
          <div className="space-y-3">
            {mockUsers?.users.filter(u => u.online).map((player) => (
              <div
                key={player.id}
                className="flex items-center justify-between p-3 bg-[#0F1724] rounded-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#28C76F] to-[#0E6FFF] rounded-full flex items-center justify-center">
                    👤
                  </div>
                  <div>
                    <div className="font-medium text-foreground">{player.username}</div>
                    <div className="text-xs text-muted-foreground capitalize">
                      {player.profession.replace(/_/g, " ")}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-[#28C76F] rounded-full" />
                  <span className="text-xs text-muted-foreground">Online</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {showMatchSetup && (
        <MatchSetupModal
          userId={userId}
          onClose={() => setShowMatchSetup(false)}
        />
      )}
    </div>
  );
}
