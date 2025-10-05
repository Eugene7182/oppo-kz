import { Sale } from "./index";

export const salesMock: Sale[] = [
  {
    id: "s-1",
    storeId: "store-1",
    storeName: "Sulpak Mega",
    network: "Sulpak",
    skuId: "p-1",
    skuName: "OPPO Reno 12",
    soldAt: new Date().toISOString(),
    qty: 3,
    amount: 3 * 249990,
    promoterId: "u-promoter",
    status: "submitted",
    version: 1,
  },
  {
    id: "s-2",
    storeId: "store-2",
    storeName: "Mechta Dostyk",
    network: "Mechta",
    skuId: "p-3",
    skuName: "OPPO A79",
    soldAt: new Date().toISOString(),
    qty: 5,
    amount: 5 * 149990,
    promoterId: "u-promoter",
    status: "locked",
    version: 4,
  },
];
