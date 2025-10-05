import { User, UserRole } from "./index";

const users: Record<UserRole, User> = {
  admin: {
    id: "u-admin",
    fullName: "Администратор",
    email: "admin@oppo.kz",
    role: "admin",
  },
  office: {
    id: "u-office",
    fullName: "Офис OPPO",
    email: "office@oppo.kz",
    role: "office",
  },
  supervisor: {
    id: "u-supervisor",
    fullName: "Супервизор Регион",
    email: "supervisor@oppo.kz",
    role: "supervisor",
    region: "Алматы",
  },
  promoter: {
    id: "u-promoter",
    fullName: "Промоутер",
    email: "promoter@oppo.kz",
    role: "promoter",
    network: "Sulpak",
  },
};

export function getMockUserByRole(role: UserRole): User {
  return users[role];
}

export function getAllMockUsers(): User[] {
  return Object.values(users);
}
