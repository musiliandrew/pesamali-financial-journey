import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPoints(points: number): string {
  return new Intl.NumberFormat().format(points);
}

export function getProfessionDisplay(profession: string): string {
  return profession.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
}

export function getPlayerColor(seatPosition: number): string {
  const colors = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#A8E6CF"];
  return colors[seatPosition] || "#999999";
}
