import { Plan } from "./index";

export const plansMock: Plan[] = [
  { id: "plan-national", scope: "national", target: 15000, achieved: 12400, period: "2024-09" },
  { id: "plan-network-sulpak", scope: "network", target: 6000, achieved: 5200, period: "2024-09", ownerName: "Sulpak" },
  { id: "plan-store-1", scope: "store", target: 1200, achieved: 980, period: "2024-09", ownerId: "store-1", ownerName: "Sulpak Mega" },
  { id: "plan-team-supervisor", scope: "team", target: 3000, achieved: 2600, period: "2024-09", ownerId: "u-supervisor", ownerName: "Команда Алматы" },
  { id: "plan-promoter", scope: "individual", target: 450, achieved: 420, period: "2024-09", ownerId: "u-promoter", ownerName: "Промоутер" },
];
