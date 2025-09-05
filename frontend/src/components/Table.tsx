import React from 'react';
import EmptyState from './EmptyState';

export interface Column<T> {
  key: keyof T;
  header: string;
}

// Generic table component
export default function Table<T extends object>({
  columns,
  data,
}: {
  columns: Column<T>[];
  data: T[];
}) {
  if (!data.length) {
    return <EmptyState />;
  }
  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          {columns.map((col) => (
            <th key={String(col.key)} className="px-4 py-2 text-left text-sm font-medium text-gray-700">
              {col.header}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {data.map((row, i) => (
          <tr key={i} className="hover:bg-gray-50">
            {columns.map((col) => (
              <td key={String(col.key)} className="px-4 py-2 text-sm text-gray-900">
                {String(row[col.key])}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
