import { bonusPayoutsMock, bonusSchemesMock } from "../../entities/bonus/mock";
import { dictionariesMock } from "../../entities/dict/mock";
import { plansMock } from "../../entities/plan/mock";
import { salesMock } from "../../entities/sale/mock";
import { insightSampleResponse } from "../../entities/insight/mock";
import { getAllMockUsers } from "../../entities/user/mock";

export const mockApi = {
  health: async () => ({ data: { status: "mock" } }),
  version: async () => ({ data: { version: "0.0.0-demo" } }),
  invites: {
    list: async () => ({ data: getAllMockUsers().filter((u) => u.role === "promoter") }),
  },
  sales: {
    list: async () => ({ data: salesMock }),
  },
  plans: {
    list: async () => ({ data: plansMock }),
  },
  dict: {
    networks: async () => ({ data: dictionariesMock.networks }),
    stores: async () => ({ data: dictionariesMock.stores }),
    regions: async () => ({ data: dictionariesMock.regions }),
  },
  bonus: {
    schemes: async () => ({ data: bonusSchemesMock }),
    payouts: async () => ({ data: bonusPayoutsMock }),
  },
  insights: {
    summarize: async () => ({ data: insightSampleResponse }),
  },
};
