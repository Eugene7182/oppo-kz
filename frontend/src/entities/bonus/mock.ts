import { BonusPayout, BonusScheme } from "./index";

export const bonusSchemesMock: BonusScheme[] = [
  {
    id: "b-1",
    name: "Sulpak A-Series",
    type: "fixed",
    skuId: "p-3",
    network: "Sulpak",
    fixedAmount: 1500,
    capAmount: 200000,
    validFrom: "2024-01-01",
  },
  {
    id: "b-2",
    name: "Reno Premium",
    type: "hybrid",
    skuId: "p-1",
    network: "Mechta",
    percent: 4,
    fixedAmount: 2500,
    capAmount: 400000,
    validFrom: "2024-05-01",
  },
];

export const bonusPayoutsMock: BonusPayout[] = [
  { promoterId: "u-promoter", month: "2024-08", amount: 185000, achievedPercent: 112 },
  { promoterId: "u-promoter", month: "2024-09", amount: 152000, achievedPercent: 98 },
];
