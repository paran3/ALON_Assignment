import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { format } from "date-fns";
import type { SensorData } from "../../types/api";

interface DataChartProps {
  data: SensorData[];
}

export function DataChart({ data }: DataChartProps) {
  if (!data.length) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📈</div>
        <p>차트에 표시할 데이터가 없습니다</p>
      </div>
    );
  }

  const chartData = [...data]
    .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
    .map((d) => ({
      time: format(new Date(d.timestamp), "MM/dd HH:mm"),
      temperature: d.metrics.temperature,
      humidity: d.metrics.humidity,
      pressure: d.metrics.pressure,
      air_quality: d.metrics.air_quality,
    }));

  return (
    <div style={{ width: "100%", height: 400 }}>
      <ResponsiveContainer>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis dataKey="time" fontSize={12} stroke="var(--text-secondary)" />
          <YAxis fontSize={12} stroke="var(--text-secondary)" />
          <Tooltip
            contentStyle={{
              background: "var(--card-bg)",
              border: "1px solid var(--border)",
              borderRadius: 8,
              color: "var(--text)",
            }}
          />
          <Legend />
          <Line type="monotone" dataKey="temperature" stroke="#ef4444" name="온도 (°C)" dot={false} />
          <Line type="monotone" dataKey="humidity" stroke="#3b82f6" name="습도 (%)" dot={false} />
          <Line type="monotone" dataKey="air_quality" stroke="#22c55e" name="공기질" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
