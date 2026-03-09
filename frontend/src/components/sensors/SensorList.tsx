import { useSensors } from "../../hooks/useSensors";
import { SensorCard } from "./SensorCard";

export function SensorList() {
  const { data, isLoading, error } = useSensors();

  if (isLoading) {
    return (
      <div className="sensor-grid">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skeleton skeleton-card" />
        ))}
      </div>
    );
  }
  if (error) return <div className="error-message">센서 목록을 불러오지 못했습니다</div>;
  if (!data?.data.length) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📡</div>
        <p>등록된 센서가 없습니다</p>
      </div>
    );
  }

  return (
    <div className="sensor-grid">
      {data.data.map((sensor) => (
        <SensorCard key={sensor.serial_number} sensor={sensor} />
      ))}
    </div>
  );
}
