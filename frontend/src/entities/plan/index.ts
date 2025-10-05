export type Plan = {
  id: string;
  scope: "national" | "network" | "store" | "team" | "individual";
  target: number;
  achieved: number;
  period: string;
  ownerId?: string;
  ownerName?: string;
};
