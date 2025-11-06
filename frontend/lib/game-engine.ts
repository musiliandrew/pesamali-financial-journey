export function seededRandom(seed: string, iteration: number): number {
  let x = Math.sin(seed.split('').reduce((a, b) => a + b.charCodeAt(0), 0) + iteration) * 10000;
  return x - Math.floor(x);
}

export function rollDice(seed: string, iteration: number): [number, number] {
  const dice1 = Math.floor(seededRandom(seed, iteration * 2) * 6) + 1;
  const dice2 = Math.floor(seededRandom(seed, iteration * 2 + 1) * 6) + 1;
  return [dice1, dice2];
}

export function getValidMoves(
  tokenPositions: number[],
  diceTotal: number,
  maxPosition: number
): number[] {
  return tokenPositions
    .map((pos, idx) => {
      const newPos = pos + diceTotal;
      return newPos <= maxPosition ? idx : -1;
    })
    .filter(idx => idx !== -1);
}

export function checkWinConditions(player: any): boolean {
  return (
    player.assets.length >= 2 &&
    player.savingsPoints >= 500 &&
    player.liabilityPoints === 0 &&
    player.cards.every((c: any) => c.played) &&
    player.dreamBought
  );
}

export function isYellowStrip(position: number, yellowSpots: number[]): boolean {
  return yellowSpots.includes(position);
}

export function canPurchaseAsset(position: number): boolean {
  return position >= 12 && position <= 20 || position >= 41 && position <= 50;
}

export function canCollectReturn(position: number): boolean {
  const returnPhases = [
    { min: 21, max: 30 },
    { min: 60, max: 61 }
  ];
  
  return returnPhases.some(phase => 
    position >= phase.min && 
    position <= phase.max && 
    position % 2 === 1
  );
}
