export type UserRole = "admin" | "office" | "supervisor" | "promoter";

export type User = {
  id: string;
  fullName: string;
  email: string;
  role: UserRole;
  region?: string;
  network?: string;
};

export type TeamMember = User & {
  storeId?: string;
};
