import { ReactNode } from "react";
import { X } from "lucide-react";

export function ModalSheet({ open, title, onClose, children }: { open: boolean; title: string; onClose: () => void; children: ReactNode }) {
  if (!open) return null;

  const isMobile = window.matchMedia("(max-width: 768px)").matches;

  if (isMobile) {
    return (
      <div className="fixed inset-0 z-50 flex flex-col justify-end bg-slate-900/50">
        <div className="rounded-t-3xl bg-white p-4 shadow-xl">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-semibold text-slate-600">{title}</span>
            <button onClick={onClose} className="rounded-full p-1 text-slate-400">
              <X size={16} />
            </button>
          </div>
          {children}
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50">
      <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-base font-semibold text-slate-700">{title}</span>
          <button onClick={onClose} className="rounded-full p-2 text-slate-400 hover:bg-slate-100">
            <X size={16} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
