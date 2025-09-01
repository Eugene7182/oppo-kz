import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../shared/api/http";

export default function Login() {
  const nav = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      const { data } = await api.auth.login({ username, password });
      const token = data?.access_token;
      const me = data?.user || null;

      if (!token) throw new Error("Пустой токен");
      localStorage.setItem("token", `Bearer ${token}`);
      if (me) localStorage.setItem("me", JSON.stringify(me));

      // роутинг по роли
      const role = (me?.role || "").toLowerCase();
      if (role === "super") nav("/invites", { replace: true });
      else if (role === "promoter") nav("/pos", { replace: true });
      else nav("/", { replace: true });
    } catch (e: any) {
      setErr(e?.response?.data?.detail || e?.message || "Ошибка входа");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 420, margin: "40px auto" }}>
      <h2>Вход</h2>
      <p style={{ color: "#666", marginTop: 4 }}>
        Введите логин и пароль. Логин = <i>username</i> из инвайта (можно e-mail).
      </p>

      <form onSubmit={onSubmit} style={{ marginTop: 16, display: "grid", gap: 12 }}>
        <div>
          <label>Логин</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            placeholder="username или e-mail"
            style={{ width: "100%", padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
        </div>
        <div>
          <label>Пароль</label>
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            required
            placeholder="пароль"
            style={{ width: "100%", padding: 8, borderRadius: 8, border: "1px solid #ddd" }}
          />
        </div>

        {!!err && <div style={{ color: "crimson" }}>{err}</div>}

        <button
          disabled={busy}
          type="submit"
          style={{
            padding: "10px 14px",
            borderRadius: 10,
            border: "1px solid #ccc",
            background: busy ? "#f3f3f3" : "#fff",
            cursor: busy ? "not-allowed" : "pointer",
          }}
        >
          Войти
        </button>

        <div style={{ marginTop: 8 }}>
          <Link to="/">← На главную</Link>
        </div>
      </form>
    </div>
  );
}
