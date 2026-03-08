import { SensorList } from "../components/sensors/SensorList";

export function SensorsPage() {
  return (
    <div>
      <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: 16 }}>
        센서 현황
      </h2>
      <SensorList />
    </div>
  );
}
