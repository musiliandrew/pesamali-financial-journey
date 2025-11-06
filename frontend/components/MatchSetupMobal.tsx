import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Switch } from "@/components/ui/switch";
import backend from "~backend/client";
import { useToast } from "@/components/ui/use-toast";

interface MatchSetupModalProps {
  userId: string;
  onClose: () => void;
}

export default function MatchSetupModal({ userId, onClose }: MatchSetupModalProps) {
  const [numPlayers, setNumPlayers] = useState("2");
  const [vsAI, setVsAI] = useState(false);
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleCreateMatch = async () => {
    try {
      const { matchId } = await backend.game.createMatch({
        numPlayers: parseInt(numPlayers),
        matchType: vsAI ? "vs_ai" : "multiplayer"
      });

      await backend.game.joinMatch({
        matchId,
        userId,
        isAi: false,
        seatPosition: 0
      });

      if (vsAI) {
        for (let i = 1; i < parseInt(numPlayers); i++) {
          await backend.game.joinMatch({
            matchId,
            userId: `ai_${i}`,
            isAi: true,
            seatPosition: i
          });
        }
      }

      await backend.game.startMatch({ matchId });
      
      navigate(`/game/${matchId}`);
    } catch (err) {
      console.error(err);
      toast({
        title: "Error",
        description: "Failed to create match",
        variant: "destructive"
      });
    }
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="bg-[#1A2332] border-[#2A3342]">
        <DialogHeader>
          <DialogTitle className="text-foreground">Create Match</DialogTitle>
        </DialogHeader>
        <div className="space-y-6 py-4">
          <div className="space-y-3">
            <Label className="text-foreground">Number of Players</Label>
            <RadioGroup value={numPlayers} onValueChange={setNumPlayers}>
              {["2", "3", "4"].map((n) => (
                <div key={n} className="flex items-center space-x-2">
                  <RadioGroupItem value={n} id={`players-${n}`} />
                  <Label htmlFor={`players-${n}`} className="text-foreground cursor-pointer">
                    {n} Players
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>

          <div className="flex items-center justify-between">
            <Label htmlFor="vs-ai" className="text-foreground">Play vs AI</Label>
            <Switch
              id="vs-ai"
              checked={vsAI}
              onCheckedChange={setVsAI}
            />
          </div>

          <Button
            onClick={handleCreateMatch}
            className="w-full bg-[#0E6FFF] hover:bg-[#0D5FE5]"
          >
            Start Game
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
