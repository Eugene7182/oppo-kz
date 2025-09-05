import React from 'react';
import { useRoutes } from 'react-router-dom';
import { routes } from './routes';

// Render routes defined in routes.tsx
export default function App() {
  return useRoutes(routes);
}
