export type SaleStatus = "draft" | "submitted" | "locked" | "corrected";

export type Sale = {
  id: string;
  storeId: string;
  storeName: string;
  network: string;
  skuId: string;
  skuName: string;
  soldAt: string;
  qty: number;
  amount: number;
  promoterId: string;
  status: SaleStatus;
  version: number;
};

export type SaleCorrection = {
  saleId: string;
  deltaQty: number;
  reason: string;
  createdAt: string;
};
