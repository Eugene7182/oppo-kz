import { useState } from "react";
import { Upload } from "lucide-react";

export function PlanBulkUpload({ onUpload }: { onUpload: (file: File) => void }) {
  const [fileName, setFileName] = useState<string>("");

  return (
    <div className="space-y-3 rounded-3xl border border-indigo-200 bg-indigo-50 p-6 text-indigo-900">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wide">
        <Upload size={14} /> Массовая загрузка планов
      </div>
      <label className="flex flex-col items-center gap-2 rounded-2xl border border-dashed border-indigo-300 bg-white/70 px-4 py-6 text-sm text-center">
        <input
          type="file"
          accept=".xlsx,.csv"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) {
              setFileName(file.name);
              onUpload(file);
            }
          }}
        />
        <span className="text-sm text-indigo-500">Перетащите файл или нажмите для выбора</span>
        {fileName && <span className="text-xs text-indigo-700">Выбран: {fileName}</span>}
      </label>
      <p className="text-xs text-indigo-600">
        Формат: period, scope, target, owner. Планы применяются к магазинам и командам без перезагрузки страницы.
      </p>
    </div>
  );
}
