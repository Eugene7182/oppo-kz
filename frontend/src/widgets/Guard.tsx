import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../shared/context/AuthContext';
import type { Role } from '../shared/context/AuthContext';
import EmptyState from './EmptyState';

interface GuardProps {
  children: JSX.Element;
  roles?: Role[];
}

// Route guard that checks authentication and roles
export default function Guard({ children, roles }: GuardProps) {
  const { me } = useAuth();
  const location = useLocation();

  // Нет токена — отправляем пользователя на страницу логина
  if (!me) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  // Есть пользователь, но роль не подходит — показываем дружелюбное сообщение
  if (roles && !roles.includes(me.role)) {
    return <EmptyState title="403" description="Недостаточно прав" />;
  }
  return children;
}
