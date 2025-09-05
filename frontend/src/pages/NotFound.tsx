import React from 'react';
import { Link } from 'react-router-dom';

// Fallback page
export default function NotFound() {
  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">404 - Not Found</h1>
      <Link to="/" className="text-blue-600 underline">
        Go home
      </Link>
    </div>
  );
}
