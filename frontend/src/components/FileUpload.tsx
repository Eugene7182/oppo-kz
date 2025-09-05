import React from 'react';

interface Props {
  onSelect: (file: File) => void;
}

// Simple file upload component
export default function FileUpload({ onSelect }: Props) {
  return (
    <input
      type="file"
      onChange={(e) => {
        const file = e.target.files?.[0];
        if (file) onSelect(file);
      }}
      className="block"
    />
  );
}
