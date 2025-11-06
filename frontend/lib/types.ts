export type Profession = 
  | "teacher_highschool" 
  | "teacher_campus" 
  | "teacher_professor"
  | "writer_poet" 
  | "writer_novelist"
  | "doctor"
  | "engineer"
  | "artist_painter"
  | "artist_musician"
  | "artist_designer"
  | "athlete_footballer"
  | "athlete_runner"
  | "entrepreneur";

export interface UserProfile {
  id: string;
  username: string;
  avatarId: string;
  profession: Profession;
  professionCategory?: string;
  society?: string;
  pesamaliPoints: number;
  currentStreak: number;
  longestStreak: number;
  totalGames: number;
  totalWins: number;
  createdAt: Date;
  lastActive: Date;
}

export interface Asset {
  id: string;
  name: string;
  cost: number;
  returnAmount: number;
  description: string;
}

export interface Card {
  id: string;
  type: "spending" | "savings" | "playing";
  name: string;
  amount: number;
  description: string;
}

export type GameStatus = "waiting" | "asset_selection" | "in_progress" | "ended";

export interface PlayerState {
  userId: string;
  isAi: boolean;
  seatPosition: number;
  color: string;
  currentPoints: number;
  incomePoints: number;
  liabilityPoints: number;
  assetReturnPoints: number;
  savingsPoints: number;
  tokenPositions: number[];
  assets: string[];
  cards: Card[];
  dreamBought: boolean;
}

export interface GameState {
  matchId: string;
  status: GameStatus;
  currentTurn: number;
  currentPlayerId: string;
  players: PlayerState[];
  rngSeed: string;
  lastDiceRoll?: number[];
  yellowStripSpots: number[];
}
