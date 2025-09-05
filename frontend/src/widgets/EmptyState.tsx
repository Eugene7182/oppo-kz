import React from 'react';

interface Props {
  /**
   * Заголовок пустого состояния
   */
  title?: string;
  /**
   * Дополнительное описание
   */
  description?: string;
}

// Простейший компонент пустого состояния/сообщений об ошибке
export default function EmptyState({
  title = 'Нет данных',
  description,
}: Props) {
  return (
    <div className="p-4 text-center text-gray-500">
      <h2 className="text-lg font-semibold">{title}</h2>
      {description && <p className="mt-1 text-sm">{description}</p>}
    </div>
  );
}
