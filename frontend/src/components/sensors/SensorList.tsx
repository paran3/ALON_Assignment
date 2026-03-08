import { useSensors } from "../../hooks/useSensors";
import { SensorCard } from "./SensorCard";

export function SensorList() {
  const { data, isLoading, error } = useSensors();

  if (isLoading) return <div className="loading">센서 목록을 불러오는 중…</div>;
  if (error) return <div className="error-message">센서 목록을 불러오지 못했습니다</div>;
  if (!data?.data.length) return <div className="loading">등록된 센서가 없습니다</div>;

  return (
    <div className="sensor-grid">
      {data.data.map((sensor) => (
        <SensorCard key={sensor.serial_number} sensor={sensor} />
      ))}
    </div>
  );
}
