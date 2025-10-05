import { ReactNode } from "react";

export type Column<T> = {
  key: keyof T;
  label: string;
  render?: (item: T) => ReactNode;
};

export function ResponsiveTable<T extends { id: string }>({ data, columns }: { data: T[]; columns: Column<T>[] }) {
  return (
    <div className="w-full">
      <div className="grid gap-3 lg:hidden">
        {data.map((item) => (
          <div key={item.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            {columns.map((column) => (
              <div key={String(column.key)} className="flex justify-between py-1 text-sm text-slate-600">
                <span className="font-medium text-slate-500">{column.label}</span>
                <span className="text-right text-slate-700">
                  {column.render ? column.render(item) : String(item[column.key])}
                </span>
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="hidden lg:block">
        <table className="min-w-full divide-y divide-slate-200 rounded-3xl bg-white shadow-sm">
          <thead className="bg-slate-50">
            <tr>
              {columns.map((column) => (
                <th key={String(column.key)} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50">
                {columns.map((column) => (
                  <td key={String(column.key)} className="px-4 py-3 text-sm text-slate-600">
                    {column.render ? column.render(item) : String(item[column.key])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
