import { test, expect } from "@playwright/test";
import type { APIRequestContext } from "@playwright/test";
import crypto from "node:crypto";

import {
  password,
  demoReferenceDate,
  createSaleState,
  findSaleByTag,
  getSaleByKey,
  getNetworkId,
  getUserByKey,
  getStoreByKey,
  getProductByKey,
  formatDate,
  addMonthsUtc,
  addDaysUtc,
  startOfMonthUtc,
  startOfWeekUtc,
} from "../support/demoData";

interface RangeMetrics {
  baseQty: number;
  baseRevenue: number;
  correctionQty: number;
  correctionRevenue: number;
  factQty: number;
  factRevenue: number;
}

interface PeriodSummary {
  current: RangeMetrics;
  previous: RangeMetrics;
  changePct: number | null;
}

const saleState = createSaleState();
const corrections: { saleId: string; deltaQty: number; deltaPrice: number }[] = [];

function toNumber(value: unknown): number {
  if (value === null || value === undefined) {
    return 0;
  }
  if (typeof value === "number") {
    return value;
  }
  if (typeof value === "string") {
    return Number(value);
  }
  throw new Error(`Unexpected numeric value: ${String(value)}`);
}

function isWithin(date: Date, start: Date, end: Date): boolean {
  return date.getTime() >= start.getTime() && date.getTime() <= end.getTime();
}

function aggregateRange(start: Date, end: Date, storeFilter?: Set<string>): RangeMetrics {
  let baseQty = 0;
  let baseRevenue = 0;
  let correctionQty = 0;
  let correctionRevenue = 0;
  for (const sale of saleState.values()) {
    if (isWithin(sale.date, start, end) && (!storeFilter || storeFilter.has(sale.storeKey))) {
      baseQty += sale.qty;
      baseRevenue += sale.qty * sale.price;
    }
  }
  for (const correction of corrections) {
    const sale = saleState.get(correction.saleId);
    if (!sale) continue;
    if (isWithin(sale.date, start, end) && (!storeFilter || storeFilter.has(sale.storeKey))) {
      correctionQty += correction.deltaQty;
      correctionRevenue += correction.deltaPrice;
    }
  }
  return {
    baseQty,
    baseRevenue,
    correctionQty,
    correctionRevenue,
    factQty: baseQty + correctionQty,
    factRevenue: baseRevenue + correctionRevenue,
  };
}

function toPeriodValue(metrics: RangeMetrics): RangeMetrics {
  return { ...metrics };
}

function percentageChange(current: RangeMetrics, previous: RangeMetrics): number | null {
  if (previous.factRevenue === 0) {
    return null;
  }
  return ((current.factRevenue - previous.factRevenue) / previous.factRevenue) * 100;
}

function computeExpected(asOf: Date): { mtd: RangeMetrics; mtdLfl: PeriodSummary; wow: PeriodSummary; mom: PeriodSummary; yoy: PeriodSummary } {
  const monthStart = startOfMonthUtc(asOf);
  const mtd = aggregateRange(monthStart, asOf);

  const currentStoreIds = new Set<string>();
  for (const sale of saleState.values()) {
    if (isWithin(sale.date, monthStart, asOf)) {
      currentStoreIds.add(sale.storeKey);
    }
  }

  const lflStart = addMonthsUtc(monthStart, -12);
  const lflEnd = addMonthsUtc(asOf, -12);
  const lfl = aggregateRange(lflStart, lflEnd, currentStoreIds);

  const currentWeekStart = startOfWeekUtc(asOf);
  const lastWeekStart = addDaysUtc(currentWeekStart, -7);
  const lastWeekEnd = addDaysUtc(currentWeekStart, -1);
  const prevWeekStart = addDaysUtc(lastWeekStart, -7);
  const prevWeekEnd = addDaysUtc(lastWeekStart, -1);
  const weekCurrent = aggregateRange(lastWeekStart, lastWeekEnd);
  const weekPrevious = aggregateRange(prevWeekStart, prevWeekEnd);

  const prevMonthStart = addMonthsUtc(monthStart, -1);
  const prevMonthEnd = addDaysUtc(monthStart, -1);
  const twoMonthsAgoStart = addMonthsUtc(prevMonthStart, -1);
  const twoMonthsAgoEnd = addDaysUtc(prevMonthStart, -1);
  const monthCurrent = aggregateRange(prevMonthStart, prevMonthEnd);
  const monthPrevious = aggregateRange(twoMonthsAgoStart, twoMonthsAgoEnd);

  const prevMonthLastYearStart = addMonthsUtc(prevMonthStart, -12);
  const prevMonthLastYearEnd = addDaysUtc(addMonthsUtc(prevMonthLastYearStart, 1), -1);
  const yoyPrevious = aggregateRange(prevMonthLastYearStart, prevMonthLastYearEnd);

  return {
    mtd,
    mtdLfl: {
      current: toPeriodValue(mtd),
      previous: toPeriodValue(lfl),
      changePct: percentageChange(mtd, lfl),
    },
    wow: {
      current: toPeriodValue(weekCurrent),
      previous: toPeriodValue(weekPrevious),
      changePct: percentageChange(weekCurrent, weekPrevious),
    },
    mom: {
      current: toPeriodValue(monthCurrent),
      previous: toPeriodValue(monthPrevious),
      changePct: percentageChange(monthCurrent, monthPrevious),
    },
    yoy: {
      current: toPeriodValue(monthCurrent),
      previous: toPeriodValue(yoyPrevious),
      changePct: percentageChange(monthCurrent, yoyPrevious),
    },
  };
}

async function loginAs(request: APIRequestContext, email: string): Promise<{ headers: Record<string, string>; token: string }> {
  const response = await request.post("/auth/login", {
    data: { username: email, password },
  });
  expect(response.ok()).toBeTruthy();
  const body = await response.json();
  const token = body.access_token as string;
  return {
    headers: {
      Authorization: `Bearer ${token}`,
      "content-type": "application/json",
    },
    token,
  };
}

function decimalCloseTo(actual: unknown, expected: number, precision = 6) {
  expect(toNumber(actual)).toBeCloseTo(expected, precision);
}

function expectChange(actual: unknown, expected: number | null) {
  if (expected === null) {
    expect(actual).toBeNull();
  } else {
    decimalCloseTo(actual, expected, 6);
  }
}

test.describe.serial("Business scenarios", () => {
  test("Admin manages bonus schemes and product lifecycle", async ({ request }) => {
    const admin = getUserByKey("user_admin");
    const { headers: adminHeaders } = await loginAs(request, admin.email);
    const technodomId = getNetworkId("network_technodom");
    const nextMonthStart = addMonthsUtc(startOfMonthUtc(demoReferenceDate), 1);

    const createResp = await request.post("/bonus-schemes", {
      headers: adminHeaders,
      data: {
        network_id: technodomId,
        valid_from: formatDate(nextMonthStart),
        valid_to: null,
        rules: [
          { selector_type: "series", selector_value: "Reno", amount: 20000 },
        ],
      },
    });
    expect(createResp.status()).toBe(201);
    const createdScheme = await createResp.json();
    expect(createdScheme.status).toBe("draft");
    const schemeId = createdScheme.id as string;

    const publishResp = await request.post(`/bonus-schemes/${schemeId}/publish`, {
      headers: adminHeaders,
    });
    expect(publishResp.ok()).toBeTruthy();
    const published = await publishResp.json();
    expect(published.status).toBe("published");

    const product = getProductByKey("product_reno10");
    const patchResp = await request.patch(`/products/${product.id}`, {
      headers: adminHeaders,
      data: { status: "eol" },
    });
    expect(patchResp.ok()).toBeTruthy();
    const patched = await patchResp.json();
    expect(patched.status).toBe("eol");
  });

  test("Office bulk plans and closing period locks edits", async ({ request }) => {
    const officeUser = getUserByKey("user_office");
    const { headers: officeHeaders } = await loginAs(request, officeUser.email);

    const periodYm = `${demoReferenceDate.getUTCFullYear()}-${String(demoReferenceDate.getUTCMonth() + 1).padStart(2, "0")}`;
    const planResp = await request.post("/plans/promoter-month/bulk", {
      headers: officeHeaders,
      data: [
        {
          period_ym: periodYm,
          promoter_id: getUserByKey("user_promoter_aidos").id,
          store_id: getStoreByKey("store_technodom_mega").id,
          target_units: 50,
          target_revenue: 9000000,
          source: "import",
          reason: "September revision",
        },
        {
          period_ym: periodYm,
          promoter_id: getUserByKey("user_promoter_assel").id,
          store_id: getStoreByKey("store_sulpak_dostyk").id,
          target_units: 32,
          target_revenue: 5200000,
          source: "import",
          reason: "September revision",
        },
      ],
    });
    expect(planResp.status()).toBe(201);

    const prevMonthStart = addMonthsUtc(startOfMonthUtc(demoReferenceDate), -1);
    const prevMonthEnd = addDaysUtc(startOfMonthUtc(demoReferenceDate), -1);
    const region = getUserByKey("user_supervisor_almaty").regionId!;
    const closeResp = await request.post("/periods/close", {
      headers: officeHeaders,
      data: {
        from_date: formatDate(prevMonthStart),
        to_date: formatDate(prevMonthEnd),
        scope: "region",
        scope_id: region,
      },
    });
    expect(closeResp.status()).toBe(201);

    const lockedSale = findSaleByTag("promoter_lock_target");
    const promoterId = lockedSale.promoterId;
    const salesListResp = await request.get(`/sales?promoter_id=${promoterId}`, {
      headers: officeHeaders,
    });
    expect(salesListResp.ok()).toBeTruthy();
    const salesList = await salesListResp.json();
    const targetSale = (salesList.items as any[]).find((item) => item.id === lockedSale.id);
    expect(targetSale).toBeTruthy();

    const editResp = await request.patch(`/sales/${lockedSale.id}`, {
      headers: { ...officeHeaders, "If-Match": String(targetSale.version) },
      data: { qty: targetSale.qty + 1 },
    });
    expect(editResp.status()).toBe(409);
    const detail = await editResp.json();
    expect(detail.detail.code ?? detail.detail?.code ?? detail.detail).toContain("locked");
  });

  test("Supervisor invites promoter and updates sale", async ({ request }) => {
    const supervisor = getUserByKey("user_supervisor_almaty");
    const { headers: supervisorHeaders } = await loginAs(request, supervisor.email);

    const inviteResp = await request.post("/invites", {
      headers: supervisorHeaders,
      data: {
        email: "new.promoter@oppo.kz",
        role_requested: "promoter",
      },
    });
    expect(inviteResp.status()).toBe(201);

    const editableSale = getSaleByKey("sale_open_current");
    const promoterId = editableSale.promoterId;
    const salesResp = await request.get(`/sales?promoter_id=${promoterId}`, { headers: supervisorHeaders });
    expect(salesResp.ok()).toBeTruthy();
    const salesData = await salesResp.json();
    const sale = (salesData.items as any[]).find((item) => item.id === editableSale.id);
    expect(sale).toBeTruthy();

    const updatedQty = sale.qty + 1;
    const patchResp = await request.patch(`/sales/${editableSale.id}`, {
      headers: { ...supervisorHeaders, "If-Match": String(sale.version) },
      data: { qty: updatedQty, reason: "Stock recount" },
    });
    expect(patchResp.ok()).toBeTruthy();
    const patchedSale = await patchResp.json();
    expect(Number(patchedSale.qty)).toBe(updatedQty);
    const saleEntry = saleState.get(editableSale.id)!;
    saleEntry.qty = updatedQty;
  });

  test("Promoter syncs offline sale and submits correction", async ({ request }) => {
    const promoter = getUserByKey("user_promoter_assel");
    const { headers: promoterHeaders } = await loginAs(request, promoter.email);

    const offlineSaleId = crypto.randomUUID();
    const store = getStoreByKey("store_sulpak_dostyk");
    const sku = getProductByKey("product_reno10");
    const saleDate = addDaysUtc(demoReferenceDate, -5);
    const offlineQty = 2;
    const offlinePrice = 259990;
    const createResp = await request.post("/sales", {
      headers: promoterHeaders,
      data: {
        sale_id: offlineSaleId,
        date: formatDate(saleDate),
        store_id: store.id,
        sku_id: sku.id,
        qty: offlineQty,
        price: offlinePrice,
      },
    });
    expect(createResp.status()).toBe(201);
    const created = await createResp.json();
    expect(created.locked).toBeFalsy();
    saleState.set(offlineSaleId, {
      key: "offline_add",
      id: offlineSaleId,
      promoterKey: promoter.key,
      promoterId: promoter.id,
      storeKey: store.key,
      storeId: store.id,
      skuKey: sku.key,
      skuId: sku.id,
      qty: offlineQty,
      price: offlinePrice,
      date: saleDate,
      locked: false,
      tags: ["mtd"],
    });

    const lockedSale = findSaleByTag("promoter_lock_target");
    const salesResp = await request.get(`/sales?promoter_id=${promoter.id}`, { headers: promoterHeaders });
    expect(salesResp.ok()).toBeTruthy();
    const salesData = await salesResp.json();
    const locked = (salesData.items as any[]).find((item) => item.id === lockedSale.id);
    expect(locked.locked).toBeTruthy();

    const patchResp = await request.patch(`/sales/${lockedSale.id}`, {
      headers: { ...promoterHeaders, "If-Match": String(locked.version) },
      data: { qty: locked.qty + 1 },
    });
    expect(patchResp.status()).toBe(409);

    const correctionResp = await request.post(`/sales/${lockedSale.id}/corrections`, {
      headers: promoterHeaders,
      data: {
        delta_qty: 1,
        delta_price: 299990,
        reason: "Retro adjustment",
      },
    });
    expect(correctionResp.status()).toBe(201);
    corrections.push({ saleId: lockedSale.id, deltaQty: 1, deltaPrice: 299990 });
  });

  test("BI summary reflects corrections and growth", async ({ request }) => {
    const officeUser = getUserByKey("user_office");
    const { headers: officeHeaders } = await loginAs(request, officeUser.email);

    const summaryResp = await request.get(`/analytics/sales/summary?as_of=${formatDate(demoReferenceDate)}`, {
      headers: officeHeaders,
    });
    expect(summaryResp.ok()).toBeTruthy();
    const summary = await summaryResp.json();

    const expected = computeExpected(demoReferenceDate);

    expect(toNumber(summary.mtd.base_qty)).toBe(expected.mtd.baseQty);
    expect(toNumber(summary.mtd.correction_qty)).toBe(expected.mtd.correctionQty);
    expect(toNumber(summary.mtd.fact_qty)).toBe(expected.mtd.factQty);
    expect(toNumber(summary.mtd.base_revenue)).toBe(expected.mtd.baseRevenue);
    expect(toNumber(summary.mtd.correction_revenue)).toBe(expected.mtd.correctionRevenue);
    expect(toNumber(summary.mtd.fact_revenue)).toBe(expected.mtd.factRevenue);

    expectChange(summary.mtd_lfl.change_pct, expected.mtdLfl.changePct);
    expectChange(summary.wow.change_pct, expected.wow.changePct);
    expectChange(summary.mom.change_pct, expected.mom.changePct);
    expectChange(summary.yoy.change_pct, expected.yoy.changePct);

    expect(toNumber(summary.mtd_lfl.current.qty)).toBe(expected.mtdLfl.current.factQty);
    expect(toNumber(summary.mtd_lfl.previous.qty)).toBe(expected.mtdLfl.previous.factQty);
    expect(toNumber(summary.mtd_lfl.current.revenue)).toBe(expected.mtdLfl.current.factRevenue);
    expect(toNumber(summary.mtd_lfl.previous.revenue)).toBe(expected.mtdLfl.previous.factRevenue);
  });
});
