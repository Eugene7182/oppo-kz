export type BonusSchemeType = "fixed" | "percent" | "hybrid";

export type BonusScheme = {
  id: string;
  name: string;
  type: BonusSchemeType;
  skuId?: string;
  network?: string;
  percent?: number;
  fixedAmount?: number;
  capAmount?: number;
  validFrom: string;
  validTo?: string;
};

export type BonusPayout = {
  promoterId: string;
  month: string;
  amount: number;
  achievedPercent: number;
};
