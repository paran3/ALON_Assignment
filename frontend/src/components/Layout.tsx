import { NavLink, Outlet } from "react-router-dom";
import { useTheme } from "./ThemeProvider";
import { useTimezone, TIMEZONE_OPTIONS } from "./TimezoneProvider";

export function Layout() {
  const { theme, toggleTheme } = useTheme();
  const { timezone, setTimezone } = useTimezone();

  return (
    <div className="container">
      <header className="header">
        <h1>IoT 환경 모니터링</h1>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <select
            className="theme-toggle"
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
            aria-label="타임존 선택"
          >
            {TIMEZONE_OPTIONS.map((tz) => (
              <option key={tz.value} value={tz.value}>
                {tz.label}
              </option>
            ))}
          </select>
          <button
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={theme === "light" ? "다크 모드로 전환" : "라이트 모드로 전환"}
          >
            {theme === "light" ? "🌙 다크" : "☀️ 라이트"}
          </button>
        </div>
      </header>
      <nav className="nav-tabs">
        <NavLink
          to="/sensors"
          className={({ isActive }) =>
            `nav-tab${isActive ? " active" : ""}`
          }
        >
          센서 현황
        </NavLink>
        <NavLink
          to="/sensor-data"
          className={({ isActive }) =>
            `nav-tab${isActive ? " active" : ""}`
          }
        >
          측정 데이터
        </NavLink>
      </nav>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
