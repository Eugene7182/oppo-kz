import React, { ReactNode } from 'react';

interface Props {
  label: string;
  children: ReactNode;
}

// Wrapper for form fields with label
export default function FormField({ label, children }: Props) {
  return (
    <label className="block mb-4">
      <span className="block mb-1 text-sm font-medium text-gray-700">{label}</span>
      {children}
    </label>
  );
}
