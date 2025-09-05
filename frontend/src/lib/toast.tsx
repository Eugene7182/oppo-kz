import React, { createContext, useContext, useState, ReactNode } from 'react';
import { createPortal } from 'react-dom';

export type ToastType = 'success' | 'error';
interface Toast { id: number; message: string; type: ToastType; }

// Храним ссылку на функцию показа тостов для вызова вне реакта (например, в интерцепторах)
let externalToast: (msg: string, type?: ToastType) => void = () => {
  console.warn('Toast context not ready');
};

const ToastContext = createContext<(msg: string, type?: ToastType) => void>(
  (msg, type) => externalToast(msg, type),
);

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = (message: string, type: ToastType = 'success') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, message, type }]);
    // Auto-remove after 3 seconds
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3000);
  };

  // делаем функцию доступной вне реакта
  externalToast = addToast;

  return (
    <ToastContext.Provider value={addToast}>
      {children}
      {createPortal(
        <div className="fixed top-4 right-4 space-y-2 z-50">
          {toasts.map((t) => (
            <div
              key={t.id}
              className={`px-4 py-2 rounded shadow text-white transition-opacity ${
                t.type === 'error' ? 'bg-red-500' : 'bg-green-500'
              }`}
            >
              {t.message}
            </div>
          ))}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  );
};

export const useToast = () => useContext(ToastContext);

// Упрощённый хелпер для вызова тостов без хука
export const toast = (msg: string, type: ToastType = 'success') =>
  externalToast(msg, type);
