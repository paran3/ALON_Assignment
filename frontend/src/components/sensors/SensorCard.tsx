import { useNavigate } from "react-router-dom";
import type { Sensor } from "../../types/api";
import { SensorStatus } from "../../types/api";
import { ModeToggle } from "./ModeToggle";
import { useSensorBrokenMutation } from "../../hooks/useSensorBrokenMutation";
import { useTimezone } from "../TimezoneProvider";
import { formatInTimezone } from "../../utils/formatTime";
import { BULK_SENSORS } from "../../constants/sensors";

const STATUS_LABEL: Record<string, string> = {
  HEALTHY: "정상",
  MISSING: "미응답",
};

const MODE_LABEL: Record<string, string> = {
  NORMAL: "일반",
  EMERGENCY: "긴급",
};

interface SensorCardProps {
  sensor: Sensor;
}

export function SensorCard({ sensor }: SensorCardProps) {
  const navigate = useNavigate();
  const brokenMutation = useSensorBrokenMutation();
  const { timezone } = useTimezone();

  const statusClass =
    sensor.status === SensorStatus.HEALTHY ? "badge-healthy" : "badge-missing";
  const modeClass =
    sensor.mode === "EMERGENCY" ? "badge-emergency" : "badge-normal";

  const handleCardClick = () => {
    navigate(`/sensor-data?serial_number=${encodeURIComponent(sensor.serial_number)}`);
  };

  const handleBrokenToggle = () => {
    brokenMutation.mutate({
      serialNumber: sensor.serial_number,
      broken: !sensor.broken,
    });
  };

  return (
    <div
      className={`card card-clickable ${sensor.status === SensorStatus.HEALTHY ? "card-status-healthy" : "card-status-missing"}`}
      onClick={handleCardClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") handleCardClick(); }}
      aria-label={`${sensor.serial_number} 측정 데이터 보기`}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <strong style={{ fontSize: "0.95rem" }}>{sensor.serial_number}</strong>
        <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
          {sensor.broken && <span className="badge badge-broken">고장</span>}
          <span className={`badge ${statusClass}`}>{STATUS_LABEL[sensor.status] ?? sensor.status}</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: "0.85rem", color: "var(--text-secondary)" }}>
        <div>
          ⚡ 모드: <span className={`badge ${modeClass}`}>{MODE_LABEL[sensor.mode] ?? sensor.mode}</span>
          {BULK_SENSORS.has(sensor.serial_number) && <span className="badge badge-bulk">벌크</span>}
        </div>
        <div>🕐 마지막 수신: {formatInTimezone(sensor.last_received_at, timezone)}</div>
        <div>
          📍 위치: {sensor.latitude.toFixed(4)}, {sensor.longitude.toFixed(4)}
        </div>
      </div>
      <div style={{ marginTop: 12, display: "flex", gap: 8 }} onClick={(e) => e.stopPropagation()}>
        <ModeToggle serialNumber={sensor.serial_number} currentMode={sensor.mode} />
        <button
          className={`btn btn-sm ${sensor.broken ? "btn-broken-active" : "btn-broken"}`}
          disabled={brokenMutation.isPending}
          onClick={handleBrokenToggle}
          aria-label={`${sensor.serial_number} 고장 시뮬레이션 ${sensor.broken ? "해제" : "설정"}`}
        >
          {brokenMutation.isPending ? "처리 중…" : sensor.broken ? "고장 해제" : "고장 시뮬레이션"}
        </button>
      </div>
    </div>
  );
}
