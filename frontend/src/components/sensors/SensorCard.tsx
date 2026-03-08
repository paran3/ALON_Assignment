import { format } from "date-fns";
import type { Sensor } from "../../types/api";
import { SensorStatus } from "../../types/api";
import { ModeToggle } from "./ModeToggle";

const STATUS_LABEL: Record<string, string> = {
  HEALTHY: "정상",
  MISSING: "미응답",
};

const MODE_LABEL: Record<string, string> = {
  NORMAL: "일반",
  EMERGENCY: "긴급",
};

function formatLocalTime(utc: string | null): string {
  if (!utc) return "-";
  return format(new Date(utc), "yyyy-MM-dd HH:mm:ss");
}

interface SensorCardProps {
  sensor: Sensor;
}

export function SensorCard({ sensor }: SensorCardProps) {
  const statusClass =
    sensor.status === SensorStatus.HEALTHY ? "badge-healthy" : "badge-missing";
  const modeClass =
    sensor.mode === "EMERGENCY" ? "badge-emergency" : "badge-normal";

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <strong style={{ fontSize: "0.95rem" }}>{sensor.serial_number}</strong>
        <span className={`badge ${statusClass}`}>{STATUS_LABEL[sensor.status] ?? sensor.status}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: "0.85rem", color: "var(--text-secondary)" }}>
        <div>
          모드: <span className={`badge ${modeClass}`}>{MODE_LABEL[sensor.mode] ?? sensor.mode}</span>
        </div>
        <div>마지막 수신: {formatLocalTime(sensor.last_received_at)}</div>
        <div>
          위치: {sensor.latitude.toFixed(4)}, {sensor.longitude.toFixed(4)}
        </div>
      </div>
      <div style={{ marginTop: 12 }}>
        <ModeToggle serialNumber={sensor.serial_number} currentMode={sensor.mode} />
      </div>
    </div>
  );
}
