import { dictionariesMock } from "../../../entities/dict/mock";
import { ResponsiveTable, Column } from "../../../widgets/ResponsiveTable";

export function AdminDictionariesPage() {
  const { networks, stores, regions } = dictionariesMock;

  const networkColumns: Column<(typeof networks)[number]>[] = [
    { key: "name", label: "Сеть" },
    { key: "region", label: "Регион" },
  ];
  const storeColumns: Column<(typeof stores)[number]>[] = [
    { key: "name", label: "Магазин" },
    { key: "networkId", label: "Сеть" },
    { key: "city", label: "Город" },
  ];
  const regionColumns: Column<(typeof regions)[number]>[] = [
    { key: "name", label: "Регион" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-800">Справочники</h1>
        <p className="text-sm text-slate-500">Редактирование производится в backend. Здесь только просмотр демо-данных.</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-700">Сети</h2>
          <ResponsiveTable data={networks.map((item) => ({ ...item, id: item.id }))} columns={networkColumns} />
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-700">Регионы</h2>
          <ResponsiveTable data={regions.map((item) => ({ ...item, id: item.id }))} columns={regionColumns} />
        </div>
      </div>
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-700">Магазины</h2>
        <ResponsiveTable data={stores.map((item) => ({ ...item, id: item.id }))} columns={storeColumns} />
      </div>
    </div>
  );
}
