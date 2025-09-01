// frontend/src/pages/Invites.tsx
import { useState } from "react";
import * as auth from "../shared/api/auth";

export default function Invites() {
  // auth
  const [u, setU] = useState("");
  const [p, setP] = useState("");
  const [authMsg, setAuthMsg] = useState<string>("");

  // invite form
  const [role, setRole] = useState<"promoter" | "super">("promoter");
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [storeId, setStoreId] = useState<number | "">("");
  const [network, setNetwork] = useState("");
  const [expires, setExpires] = useState<number>(72);

  const [result, setResult] = useState<{ code: string; link: string } | null>(
    null
  );
  const [err, setErr] = useState<string>("");

  const doLogin = async () => {
    setAuthMsg("");
    try {
      await auth.login(u.trim(), p);
      setAuthMsg("Успешный вход. Можно создавать инвайты.");
    } catch (e: any) {
      setAuthMsg(
        e?.response?.data?.detail || e?.message || "Ошибка авторизации"
      );
    }
  };

  const create = async () => {
    setErr("");
    setResult(null);

    if (!username.trim()) {
      setErr("Укажи логин (username). Если хочешь логин по e-mail — просто укажи e-mail.");
      return;
    }

    try {
      const body: any = {
        role,
        username: username.trim(),
        full_name: fullName.trim() || undefined,
        expires_hours: expires || undefined,
      };
      if (storeId !== "") body.store_id = Number(storeId);
      if (network.trim()) body.network = network.trim();

      const { code } = await auth.createInvite(body);

      const link =
        window.location.origin + "/register?code=" + encodeURIComponent(code);

      setResult({ code, link });
    } catch (e: any) {
      setErr(e?.response?.data?.detail || e?.message || "Ошибка создания инвайта");
    }
  };

  return (
    <div style={{ maxWidth: 680, margin: "40px auto", padding: 16 }}>
      <h2>Инвайты (супервайзер)</h2>

      {/* AUTH */}
      <div
        style={{
          border: "1px solid #e3e3e3",
          borderRadius: 12,
          padding: 16,
          background: "#fafafa",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Авторизация</h3>
        <div style={{ display: "grid", gap: 8, gridTemplateColumns: "1fr 1fr auto" }}>
          <input
            placeholder="Логин (username)"
            value={u}
            onChange={(e) => setU(e.target.value)}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
          />
          <input
            type="password"
            placeholder="Пароль"
            value={p}
            onChange={(e) => setP(e.target.value)}
            style={{ padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
          />
          <button onClick={doLogin} style={{ padding: "10px 16px", borderRadius: 10 }}>
            Войти
          </button>
        </div>
        {authMsg && <p style={{ marginTop: 8 }}>{authMsg}</p>}
      </div>

      {/* INVITE FORM */}
      <div style={{ marginTop: 20 }}>
        <h3>Создать приглашение</h3>

        <div
          style={{
            display: "grid",
            gap: 10,
            gridTemplateColumns: "1fr 1fr",
            alignItems: "center",
          }}
        >
          <label>
            Роль
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as any)}
              style={{
                width: "100%",
                padding: 10,
                borderRadius: 8,
                border: "1px solid #ddd",
                marginTop: 6,
              }}
            >
              <option value="promoter">promoter</option>
              <option value="super">super</option>
            </select>
          </label>

          <label>
            Срок действия (часы)
            <input
              type="number"
              min={1}
              value={expires}
              onChange={(e) => setExpires(Number(e.target.value))}
              style={{
                width: "100%",
                padding: 10,
                borderRadius: 8,
                border: "1px solid #ddd",
                marginTop: 6,
              }}
            />
          </label>

          <label>
            Логин (username)
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="например, e-mail"
              style={{
                width: "100%",
                padding: 10,
                borderRadius: 8,
                border: "1px solid #ddd",
                marginTop: 6,
              }}
            />
          </label>

          <label>
            ФИО (необязательно)
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              style={{
                width: "100%",
                padding: 10,
                borderRadius: 8,
                border: "1px solid #ddd",
                marginTop: 6,
              }}
            />
          </label>

          <label>
            Привязка к магазину (store_id)
            <input
              type="number"
              value={storeId}
              onChange={(e) =>
                setStoreId(e.target.value === "" ? "" : Number(e.target.value))
              }
              placeholder="опционально"
              style={{
                width: "100%",
                padding: 10,
                borderRadius: 8,
                border: "1px solid #ddd",
                marginTop: 6,
              }}
            />
          </label>

          <label>
            Сеть (network)
            <input
              value={network}
              onChange={(e) => setNetwork(e.target.value)}
              placeholder="например, Sulpak (опционально)"
              style={{
                width: "100%",
                padding: 10,
                borderRadius: 8,
                border: "1px solid #ddd",
                marginTop: 6,
              }}
            />
          </label>
        </div>

        {err && <div style={{ color: "#b00020", marginTop: 10 }}>{err}</div>}

        <button
          onClick={create}
          style={{
            marginTop: 12,
            padding: "10px 16px",
            borderRadius: 10,
            border: "1px solid #2b6",
            background: "#28a745",
            color: "white",
            cursor: "pointer",
          }}
        >
          Создать инвайт
        </button>

        {result && (
          <div
            style={{
              marginTop: 14,
              border: "1px solid #e3e3e3",
              borderRadius: 12,
              padding: 14,
              background: "#fafafa",
            }}
          >
            <div>Код: <b>{result.code}</b></div>
            <div style={{ marginTop: 6 }}>
              Ссылка регистрации:{" "}
              <a href={result.link} target="_blank" rel="noreferrer">
                {result.link}
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
