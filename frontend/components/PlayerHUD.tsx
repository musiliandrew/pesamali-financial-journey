import { Coins, TrendingUp, TrendingDown, Wallet } from "lucide-react";

interface PlayerHUDProps {
  username: string;
  profession: string;
  avatarId: string;
  currentPoints: number;
  savingsPoints: number;
  liabilityPoints: number;
}

export default function PlayerHUD({
  username,
  profession,
  currentPoints,
  savingsPoints,
  liabilityPoints
}: PlayerHUDProps) {
  return (
    <div className="bg-[#1A2332] border-b border-[#2A3342] p-4">
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 bg-gradient-to-br from-[#0E6FFF] to-[#28C76F] rounded-full flex items-center justify-center">
          👤
        </div>
        <div className="flex-1">
          <div className="font-semibold text-foreground">{username}</div>
          <div className="text-xs text-muted-foreground capitalize">
            {profession.replace(/_/g, " ")}
          </div>
        </div>
        <div className="flex gap-3">
          <div className="text-center">
            <div className="flex items-center gap-1 text-foreground">
              <Coins className="h-4 w-4 text-[#FFEA7A]" />
              <span className="text-sm font-bold">{currentPoints}</span>
            </div>
            <div className="text-[10px] text-muted-foreground">Total</div>
          </div>
          <div className="text-center">
            <div className="flex items-center gap-1 text-foreground">
              <Wallet className="h-4 w-4 text-[#28C76F]" />
              <span className="text-sm font-bold">{savingsPoints}</span>
            </div>
            <div className="text-[10px] text-muted-foreground">Savings</div>
          </div>
          <div className="text-center">
            <div className="flex items-center gap-1 text-foreground">
              <TrendingDown className="h-4 w-4 text-[#FF4D4F]" />
              <span className="text-sm font-bold">{liabilityPoints}</span>
            </div>
            <div className="text-[10px] text-muted-foreground">Debt</div>
          </div>
        </div>
      </div>
    </div>
  );
}
