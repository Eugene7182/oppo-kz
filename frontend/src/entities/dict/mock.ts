import { Dictionaries } from "./index";

export const dictionariesMock: Dictionaries = {
  networks: [
    { id: "net-1", name: "Sulpak", region: "Алматы" },
    { id: "net-2", name: "Mechta", region: "Нур-Султан" },
  ],
  stores: [
    { id: "store-1", name: "Sulpak Mega", networkId: "net-1", city: "Алматы" },
    { id: "store-2", name: "Sulpak Dostyk", networkId: "net-1", city: "Алматы" },
    { id: "store-3", name: "Mechta Esentai", networkId: "net-2", city: "Нур-Султан" },
  ],
  regions: [
    { id: "region-1", name: "Алматы" },
    { id: "region-2", name: "Нур-Султан" },
    { id: "region-3", name: "Шымкент" },
  ],
};
