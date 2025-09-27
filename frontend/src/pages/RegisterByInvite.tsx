// frontend/src/pages/RegisterByInvite.tsx
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import * as auth from "../shared/api/auth";

type InviteInfo =
  | {
      valid: true;
      username: string;
      role: "promoter" | "super";
      full_name?: string | null;
      store_id?: number | null;
      network?: string | null;
      expires_at?: string;
    }
  | {
      valid: false;
      reason?: "not_found" | "used" | "expired";
    };

export default function RegisterByInvite() {
  const [sp] = useSearchParams();
  const navigate = useNavigate();
  const code = sp.get("code") || "";

  const [loading, setLoading] = useState(true);
  const [invite, setInvite] = useState<InviteInfo | null>(null);
  const [error, setError] = useState<string>("");

  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [fullName, setFullName] = useState("");

  useEffect(() => {
    if (!code) {
      setInvite({ valid: false, reason: "not_found" });
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const info = await api.auth.checkInvite(code);
        if (info.valid) {
          setInvite({
            valid: true,
            username: info.username!,
            role: info.role!,
            full_name: info.full_name ?? "",
            store_id: info.store_id ?? null,
            network: info.network ?? null,
            expires_at: info.expires_at,
          });
          setFullName(info.full_name ?? "");
        } else {
          setInvite({ valid: false, reason: info.reason });
        }
      } catch (e: any) {
        setError(e?.message || "Ошибка проверки инвайта");
      } finally {
        setLoading(false);
      }
    })();
  }, [code]);

  const doRegister = async () => {
    setError("");
    if (!invite || invite.valid !== true) return;
    if (!password || password.length < 6) {
      setError("Пароль должен быть не короче 6 символов.");
      return;
    }
    if (password !== password2) {
      setError("Пароли не совпадают.");
      return;
    }
    try {
      // вернётся токен — мы его сохраним внутри api.auth.registerByInvite
      await api.auth.registerByInvite(code, password, fullName || undefined);
      // после успеха — на главную (или куда нужно)
      navigate("/", { replace: true });
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || "Ошибка регистрации");
    }
  };

  const ReasonText = () => {
    if (!invite || invite.valid) return null;
    const r = invite.reason;
    if (r === "expired") return <span>Код приглашения истёк.</span>;
    if (r === "used") return <span>Код уже был использован.</span>;
    return <span>Код не найден.</span>;
  };

  return (
    <div style={{ maxWidth: 520, margin: "40px auto", padding: 16 }}>
      <h2>Регистрация по приглашению</h2>

      {!code && <p>Не передан параметр <code>code</code>.</p>}

      {loading && <p>Проверяем код…</p>}

      {!loading && invite && invite.valid && (
        <>
          <div
            style={{
              border: "1px solid #e3e3e3",
              borderRadius: 12,
              padding: 16,
              marginTop: 10,
              background: "#fafafa",
            }}
          >
            <p style={{ margin: "6px 0" }}>
              Логин: <b>{invite.username}</b>
            </p>
            <p style={{ margin: "6px 0" }}>
              Роль: <b>{invite.role === "promoter" ? "Промоутер" : "Супервайзер"}</b>
            </p>
            {invite.network ? (
              <p style={{ margin: "6px 0" }}>
                Сеть: <b>{invite.network}</b>
              </p>
            ) : null}
            {invite.store_id ? (
              <p style={{ margin: "6px 0" }}>
                Привязка к магазину ID: <b>{invite.store_id}</b>
              </p>
            ) : null}
            {invite.expires_at ? (
              <p style={{ margin: "6px 0", color: "#666" }}>
                Действительно до: {new Date(invite.expires_at).toLocaleString()}
              </p>
            ) : null}
          </div>

          <div style={{ marginTop: 16 }}>
            <label style={{ display: "block", marginBottom: 6 }}>ФИО (необязательно)</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Ваше имя"
              style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
            />
          </div>

          <div style={{ marginTop: 16 }}>
            <label style={{ display: "block", marginBottom: 6 }}>Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Пароль"
              style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
            />
          </div>

          <div style={{ marginTop: 12 }}>
            <label style={{ display: "block", marginBottom: 6 }}>Повтор пароля</label>
            <input
              type="password"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
              placeholder="Повтор пароля"
              style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ddd" }}
            />
          </div>

          {error && (
            <div style={{ color: "#b00020", marginTop: 12 }}>
              {error}
            </div>
          )}

          <div style={{ marginTop: 16 }}>
            <button
              onClick={doRegister}
              style={{
                padding: "10px 16px",
                borderRadius: 10,
                border: "1px solid #2b6",
                background: "#28a745",
                color: "white",
                cursor: "pointer",
              }}
            >
              Зарегистрироваться
            </button>
          </div>
        </>
      )}

      {!loading && invite && !invite.valid && (
        <>
          <div style={{ marginTop: 10, color: "#b00020" }}>
            <ReasonText />
          </div>
        </>
      )}
    </div>
  );
}
