export type WeightClass =
  | "Strawweight"
  | "Minimumweight"
  | "Light Flyweight"
  | "Flyweight"
  | "Super Flyweight"
  | "Bantamweight"
  | "Super Bantamweight"
  | "Featherweight"
  | "Super Featherweight"
  | "Lightweight"
  | "Super Lightweight"
  | "Welterweight"
  | "Super Welterweight"
  | "Middleweight"
  | "Super Middleweight"
  | "Light Heavyweight"
  | "Cruiserweight"
  | "Heavyweight";

export type Fighter = {
  id: string;
  name: string;
  weightClass: WeightClass;
  wins: number;
  losses: number;
  draws: number;
  knockouts: number;
  /** Public URL to the Ghibli portrait (Supabase Storage). null while mock. */
  avatarUrl: string | null;
  /** CSS gradient stand-in used until real portraits are wired. */
  placeholderGradient: string;
};
