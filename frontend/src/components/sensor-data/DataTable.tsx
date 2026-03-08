import { format } from "date-fns";
import type { SensorData } from "../../types/api";

const MODE_LABEL: Record<string, string> = {
  NORMAL: "일반",
  EMERGENCY: "긴급",
};

function formatLocal(utc: string): string {
  return format(new Date(utc), "yyyy-MM-dd HH:mm:ss");
}

interface DataTableProps {
  data: SensorData[];
}

export function DataTable({ data }: DataTableProps) {
  if (!data.length) {
    return <div className="loading">조회된 데이터가 없습니다</div>;
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>시리얼 번호</th>
            <th>측정 시간</th>
            <th>수신 시간</th>
            <th>모드</th>
            <th>온도 (°C)</th>
            <th>습도 (%)</th>
            <th>기압 (hPa)</th>
            <th>공기질</th>
          </tr>
        </thead>
        <tbody>
          {data.map((d) => (
            <tr key={d.id}>
              <td>{d.serial_number}</td>
              <td>{formatLocal(d.timestamp)}</td>
              <td>{formatLocal(d.server_received_at)}</td>
              <td>
                <span
                  className={`badge ${d.mode === "EMERGENCY" ? "badge-emergency" : "badge-normal"}`}
                >
                  {MODE_LABEL[d.mode] ?? d.mode}
                </span>
              </td>
              <td>{d.metrics.temperature.toFixed(1)}</td>
              <td>{d.metrics.humidity.toFixed(1)}</td>
              <td>{d.metrics.pressure.toFixed(1)}</td>
              <td>{d.metrics.air_quality}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
