import { Button } from "@/components/ui/button";
import { Dices } from "lucide-react";

interface DiceRollerProps {
  dice: number[];
  isRolling: boolean;
  onRoll: () => void;
}

export default function DiceRoller({ dice, isRolling, onRoll }: DiceRollerProps) {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="flex gap-3">
        {dice.length > 0 ? (
          dice.map((value, idx) => (
            <div
              key={idx}
              className={`
                w-16 h-16 bg-white rounded-xl flex items-center justify-center
                text-3xl font-bold text-[#0F1724] shadow-lg
                ${isRolling ? "animate-spin" : ""}
              `}
            >
              {isRolling ? "?" : value}
            </div>
          ))
        ) : (
          <div className="w-16 h-16 bg-[#2A3342] rounded-xl flex items-center justify-center">
            <Dices className="h-8 w-8 text-muted-foreground" />
          </div>
        )}
      </div>
      
      <Button
        onClick={onRoll}
        disabled={isRolling}
        className="bg-[#0E6FFF] hover:bg-[#0D5FE5]"
      >
        {isRolling ? "Rolling..." : "Roll Dice"}
      </Button>
    </div>
  );
}
