import { NavLink, Outlet } from "react-router-dom";
import { useTheme } from "./ThemeProvider";

export function Layout() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="container">
      <header className="header">
        <h1>IoT 모니터링</h1>
        <button
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={theme === "light" ? "다크 모드로 전환" : "라이트 모드로 전환"}
        >
          {theme === "light" ? "🌙 다크" : "☀️ 라이트"}
        </button>
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
