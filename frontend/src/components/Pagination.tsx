import React from 'react';

interface Props {
  page: number;
  total: number;
  onChange: (page: number) => void;
}

// Basic pagination component
export default function Pagination({ page, total, onChange }: Props) {
  return (
    <div className="flex gap-2 items-center">
      <button
        className="px-2 py-1 border rounded disabled:opacity-50"
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
      >
        Prev
      </button>
      <span>{page}</span>
      <button
        className="px-2 py-1 border rounded disabled:opacity-50"
        onClick={() => onChange(page + 1)}
        disabled={page >= total}
      >
        Next
      </button>
    </div>
  );
}
