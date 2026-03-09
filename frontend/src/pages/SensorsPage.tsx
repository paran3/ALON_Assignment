import { SensorList } from "../components/sensors/SensorList";
import { useSensors } from "../hooks/useSensors";
import { SensorStatus, SensorMode } from "../types/api";

export function SensorsPage() {
  const { data } = useSensors();
  const sensors = data?.data || [];
  const total = sensors.length;
  const healthy = sensors.filter((s) => s.status === SensorStatus.HEALTHY).length;
  const missing = sensors.filter((s) => s.status === SensorStatus.MISSING).length;
  const emergency = sensors.filter((s) => s.mode === SensorMode.EMERGENCY).length;

  return (
    <div className="page-enter">
      <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: 16 }}>
        센서 현황
      </h2>
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📡</div>
          <div className="stat-value">{total}</div>
          <div className="stat-label">전체 센서</div>
        </div>
        <div className="stat-card stat-card-healthy">
          <div className="stat-icon">✅</div>
          <div className="stat-value">{healthy}</div>
          <div className="stat-label">정상</div>
        </div>
        <div className="stat-card stat-card-missing">
          <div className="stat-icon">⚠️</div>
          <div className="stat-value">{missing}</div>
          <div className="stat-label">미응답</div>
        </div>
        <div className="stat-card stat-card-emergency">
          <div className="stat-icon">🚨</div>
          <div className="stat-value">{emergency}</div>
          <div className="stat-label">긴급 모드</div>
        </div>
      </div>
      <SensorList />
    </div>
  );
}
