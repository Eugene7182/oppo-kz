import { BrowserRouter, Routes, Route, Link, NavLink, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "./shared/api/http";

import "./lib/i18n";
import Audit from "./pages/Audit";
import CampaignDetails from "./pages/CampaignDetails";
import TransfersApply from "./pages/TransfersApply";
import AnomaliesForecast from "./pages/AnomaliesForecast";

import Directories from "./pages/Directories";
import UploadSales from "./pages/UploadSales";
import Reconciliation from "./pages/Reconciliation";
import FinalSales from "./pages/FinalSales";
import Invites from "./pages/Invites";
import RegisterByInvite from "./pages/RegisterByInvite";
import Login from "./pages/Login";
import PromoterPOS from "./pages/PromoterPOS";
import BonusGrids from "./pages/BonusGrids"; // <-- новое

const ALink = ({ to, children }: { to: string; children: any }) => (
  <NavLink
    to={to}
    style={({ isActive }) => ({
      textDecoration: "none",
      padding: "6px 10px",
      borderRadius: 8,
      border: "1px solid #ddd",
      background: isActive ? "#f2f2f2" : "transparent",
    })}
  >
    {children}
  </NavLink>
);

function Home() {
  const [status, setStatus] = useState("...");
  const [version, setVersion] = useState("");

  useEffect(() => {
    api.health()
      .then(({ data }) => setStatus(JSON.stringify(data)))
      .catch((e) => setStatus("Ошибка: " + (e?.message || "unknown")));
    api.version()
      .then(({ data }) => setVersion(data?.version || ""))
      .catch(() => {});
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h1>Платформа OPPO KZ {version ? `· v${version}` : ""}</h1>
      <p style={{ color: "#555" }}>Статус API: {status}</p>

      <p style={{ marginTop: 16 }}>
        Начните со <Link to="/directories">Справочников</Link>: магазины/сети и SKU, затем загрузка продаж и сверка. Создание
        приглашений — «Инвайты». Бонусные правила — «Бонусы».
      </p>
    </div>
  );
}

function TopNav() {
  const nav = useNavigate();
  const [me, setMe] = useState<{ username?: string; role?: string } | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("me");
      setMe(raw ? JSON.parse(raw) : null);
    } catch {
      setMe(null);
    }
  }, []);

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("me");
    setMe(null);
    nav("/login");
  }

  const role = (me?.role || "").toLowerCase();

  return (
    <div
      style={{
        padding: "10px 16px",
        display: "flex",
        alignItems: "center",
        gap: 10,
        flexWrap: "wrap",
        borderBottom: "1px solid #eee",
      }}
    >
      <ALink to="/">Главная</ALink>
      <ALink to="/directories">Справочники</ALink>
      <ALink to="/upload">Загрузка</ALink>
      <ALink to="/recon">Сверка</ALink>
      <ALink to="/final">Итог</ALink>
      {role === "super" && <ALink to="/invites">Инвайты</ALink>}
      {role === "super" && <ALink to="/bonus">Бонусы</ALink>}
<ALink to="/audit">Аудит</ALink>
<ALink to="/campaigns/:id">Кампания (детали)</ALink>
<ALink to="/transfers/apply">Перемещения (apply)</ALink>
<ALink to="/analytics/anom-forecast">Аномалии/Прогноз</ALink>
      {role === "promoter" && <ALink to="/pos">POS</ALink>}

      <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
        {me ? (
          <>
            <span style={{ color: "#666" }}>
              {me.username} · {me.role}
            </span>
            <button
              onClick={logout}
              style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #ddd", background: "#fff", cursor: "pointer" }}
            >
              Выйти
            </button>
          </>
        ) : (
          <ALink to="/login">Войти</ALink>
        )}
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <TopNav />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/directories" element={<Directories />} />
        <Route path="/upload" element={<UploadSales />} />
        <Route path="/recon" element={<Reconciliation />} />
        <Route path="/final" element={<FinalSales />} />
        <Route path="/invites" element={<Invites />} />
        <Route path="/register" element={<RegisterByInvite />} />
        <Route path="/login" element={<Login />} />
        <Route path="/pos" element={<PromoterPOS />} />
        <Route path="/bonus" element={<BonusGrids />} /> {/* новое */}
        <Route path="/audit" element={<Audit />} />
        <Route path="/campaigns/:id" element={<CampaignDetails />} />
        <Route path="/campaign-details" element={<CampaignDetails />} />
        <Route path="/transfers/apply" element={<TransfersApply />} />
        <Route path="/analytics/anom-forecast" element={<AnomaliesForecast />} />

        <Route path="*" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}
