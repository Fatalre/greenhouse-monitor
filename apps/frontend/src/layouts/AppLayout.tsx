import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  Activity,
  Database,
  FlaskConical,
  Gauge,
  LogOut,
  Menu,
  MonitorCog,
  Moon,
  Sun,
  Thermometer,
} from "lucide-react";
import { useState } from "react";
import { api, clearAccessToken } from "../api/client";

export function AppLayout() {
  const [dark, setDark] = useState(() => localStorage.theme === "dark");
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    localStorage.theme = next ? "dark" : "light";
    document.documentElement.dataset.theme = next ? "dark" : "light";
  };

  const links = [
    ["/", "Панель", Gauge],
    ["/measurements", "Измерения", Database],
    ["/experiments", "Эксперименты", FlaskConical],
    ["/devices", "Устройства", Activity],
    ["/system", "Система", MonitorCog],
  ] as const;

  return (
    <div className="app-shell">
      <aside className={open ? "open" : ""}>
        <div className="brand">
          <Thermometer />
          Greenhouse Monitor
        </div>

        <nav>
          {links.map(([path, label, Icon]) => (
            <NavLink
              key={path}
              to={path}
              onClick={() => setOpen(false)}
            >
              <Icon size={19} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <main>
        <header>
          <button
            className="icon mobile"
            onClick={() => setOpen(!open)}
          >
            <Menu />
          </button>

          <div />

          <button className="icon" onClick={toggleTheme}>
            {dark ? <Sun /> : <Moon />}
          </button>

          <button
            className="icon"
            onClick={async () => {
              try {
                await api("/auth/logout", { method: "POST" });
              } finally {
                clearAccessToken();
                navigate("/login", { replace: true });
              }
            }}
          >
            <LogOut />
          </button>
        </header>

        <section className="content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}