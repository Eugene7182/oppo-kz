// ... остальной код страницы без изменений
{result && (
  <div style={{ marginTop: 16 }}>
    <h3>Результат</h3>
    <pre style={{ background: '#111', color: '#eee', padding: 12, borderRadius: 8 }}>
{JSON.stringify(result, null, 2)}
    </pre>
    {'code' in result && (
      <div style={{ marginTop: 8 }}>
        <div>Ссылка для регистрации:</div>
        <code>
          {`${window.location.origin}/register/${result.code}`}
        </code>
        <div style={{ marginTop: 6, fontSize: 12, opacity: 0.8 }}>
          Отправьте её пользователю. Он задаст пароль и затем войдёт.
        </div>
      </div>
    )}
  </div>
)}
