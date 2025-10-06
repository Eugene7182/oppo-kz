import rawData from "../../ops/demo/demo_data.json";

export type DemoData = typeof rawData;

export interface RegionSeed {
  key: string;
  id: string;
  name: string;
}

export interface StoreSeed {
  key: string;
  id: string;
  name: string;
  networkKey: string;
  networkId: string;
  regionId: string;
}

export interface UserSeed {
  key: string;
  id: string;
  email: string;
  fullName: string;
  role: string;
  regionId: string | null;
}

export interface ProductSeed {
  key: string;
  id: string;
  sku: string;
  name: string;
}

export interface SaleSeed {
  key: string;
  id: string;
  promoterKey: string;
  promoterId: string;
  storeKey: string;
  storeId: string;
  skuKey: string;
  skuId: string;
  qty: number;
  price: number;
  date: Date;
  locked: boolean;
  tags: string[];
}

export interface CorrectionSeed {
  saleId: string;
  deltaQty: number;
  deltaPrice: number;
}

const data: DemoData = rawData;

function makeUTC(year: number, monthIndex: number, day: number): Date {
  return new Date(Date.UTC(year, monthIndex, day));
}

function daysInMonth(year: number, monthIndex: number): number {
  return new Date(Date.UTC(year, monthIndex + 1, 0)).getUTCDate();
}

function addMonths(value: Date, offset: number): Date {
  const year = value.getUTCFullYear();
  const month = value.getUTCMonth() + offset;
  const targetYear = year + Math.floor(month / 12);
  const targetMonth = ((month % 12) + 12) % 12;
  const day = Math.min(value.getUTCDate(), daysInMonth(targetYear, targetMonth));
  return makeUTC(targetYear, targetMonth, day);
}

function startOfMonth(value: Date): Date {
  return makeUTC(value.getUTCFullYear(), value.getUTCMonth(), 1);
}

function startOfWeek(value: Date): Date {
  const day = value.getUTCDay();
  const delta = (day + 6) % 7; // monday = 0
  return makeUTC(value.getUTCFullYear(), value.getUTCMonth(), value.getUTCDate() - delta);
}

function addDays(value: Date, offset: number): Date {
  return new Date(value.getTime() + offset * 86_400_000);
}

const referenceDate = makeUTC(
  Number(data.reference_date.slice(0, 4)),
  Number(data.reference_date.slice(5, 7)) - 1,
  Number(data.reference_date.slice(8, 10)),
);

const anchors: Record<string, Date> = {
  reference_date: referenceDate,
  today: referenceDate,
  current_week_start: startOfWeek(referenceDate),
  last_week_start: addDays(startOfWeek(referenceDate), -7),
  two_weeks_ago_start: addDays(startOfWeek(referenceDate), -14),
  current_month_start: startOfMonth(referenceDate),
  previous_month_start: addMonths(startOfMonth(referenceDate), -1),
  two_months_ago_start: addMonths(startOfMonth(referenceDate), -2),
  current_month_start_last_year: addMonths(startOfMonth(referenceDate), -12),
  previous_month_start_last_year: addMonths(addMonths(startOfMonth(referenceDate), -1), -12),
};

function resolveDate(spec: { anchor?: string; offset_days?: number } | null | undefined): Date {
  if (!spec || !spec.anchor) {
    return new Date(referenceDate.getTime());
  }
  const anchor = anchors[spec.anchor];
  if (!anchor) {
    throw new Error(`Unknown anchor ${spec.anchor}`);
  }
  const offset = spec.offset_days ?? 0;
  return addDays(anchor, offset);
}

const regions: RegionSeed[] = data.regions.map((region) => ({
  key: region.key,
  id: region.id,
  name: region.name,
}));

const regionByKey = new Map(regions.map((region) => [region.key, region]));

const networks = data.networks.map((network) => ({
  key: network.key,
  id: network.id,
  name: network.name,
}));

const stores: StoreSeed[] = data.networks.flatMap((network) =>
  network.stores.map((store) => ({
    key: store.key,
    id: store.id,
    name: store.name,
    networkKey: network.key,
    networkId: network.id,
    regionId: regionByKey.get(store.region_key)!.id,
  })),
);

const storeByKey = new Map(stores.map((store) => [store.key, store]));

const users: UserSeed[] = data.users.map((user) => ({
  key: user.key,
  id: user.id,
  email: user.email,
  fullName: user.full_name,
  role: user.role,
  regionId: user.region_key ? regionByKey.get(user.region_key)!.id : null,
}));

const userByKey = new Map(users.map((user) => [user.key, user]));

const products: ProductSeed[] = data.products.map((product) => ({
  key: product.key,
  id: product.id,
  sku: product.sku,
  name: product.name,
}));

const productByKey = new Map(products.map((product) => [product.key, product]));

const sales: SaleSeed[] = data.sales.map((sale) => ({
  key: sale.key,
  id: sale.id,
  promoterKey: sale.promoter_key,
  promoterId: userByKey.get(sale.promoter_key)!.id,
  storeKey: sale.store_key,
  storeId: storeByKey.get(sale.store_key)!.id,
  skuKey: sale.sku_key,
  skuId: productByKey.get(sale.sku_key)!.id,
  qty: sale.qty,
  price: sale.price,
  date: resolveDate(sale.date),
  locked: Boolean(sale.locked),
  tags: sale.tags ?? [],
}));

export const password = data.password;
export const demoReferenceDate = referenceDate;
export const demoNetworks = networks;
export const demoUsers = users;
export const demoStores = stores;
export const demoProducts = products;
export const demoSales = sales;

export function formatDate(value: Date): string {
  return value.toISOString().slice(0, 10);
}

export function createSaleState(): Map<string, SaleSeed> {
  return new Map(demoSales.map((sale) => [sale.id, { ...sale }]));
}

export function findSaleByTag(tag: string): SaleSeed {
  const found = demoSales.find((sale) => sale.tags.includes(tag));
  if (!found) {
    throw new Error(`Sale with tag ${tag} not found`);
  }
  return found;
}

export function getSaleByKey(key: string): SaleSeed {
  const found = demoSales.find((sale) => sale.key === key);
  if (!found) {
    throw new Error(`Sale with key ${key} not found`);
  }
  return found;
}

export function getNetworkId(key: string): string {
  const found = demoNetworks.find((network) => network.key === key);
  if (!found) {
    throw new Error(`Network ${key} not found`);
  }
  return found.id;
}

export function getUserByKey(key: string): UserSeed {
  const user = userByKey.get(key);
  if (!user) {
    throw new Error(`User ${key} not found`);
  }
  return user;
}

export function getStoreByKey(key: string): StoreSeed {
  const store = storeByKey.get(key);
  if (!store) {
    throw new Error(`Store ${key} not found`);
  }
  return store;
}

export function getProductByKey(key: string): ProductSeed {
  const product = productByKey.get(key);
  if (!product) {
    throw new Error(`Product ${key} not found`);
  }
  return product;
}

export function startOfWeekUtc(value: Date): Date {
  return startOfWeek(value);
}

export function startOfMonthUtc(value: Date): Date {
  return startOfMonth(value);
}

export function addMonthsUtc(value: Date, offset: number): Date {
  return addMonths(value, offset);
}

export function addDaysUtc(value: Date, offset: number): Date {
  return addDays(value, offset);
}
