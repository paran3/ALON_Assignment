import { useState } from "react";
import { useSensorData } from "../hooks/useSensorData";
import { DataFilters } from "../components/sensor-data/DataFilters";
import { DataTable } from "../components/sensor-data/DataTable";
import { DataChart } from "../components/sensor-data/DataChart";
import { Pagination } from "../components/sensor-data/Pagination";
import type { SensorDataFilters } from "../types/api";

type ViewMode = "table" | "chart";

const LIMIT_OPTIONS = [10, 20, 50, 100];

export function SensorDataPage() {
  const [filters, setFilters] = useState<SensorDataFilters>({
    page: 1,
    limit: 10,
  });
  const [view, setView] = useState<ViewMode>("table");
  const { data, isLoading, error } = useSensorData(filters);

  return (
    <div>
      <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: 16 }}>
        측정 데이터
      </h2>

      <DataFilters filters={filters} onChange={setFilters} />

      <div className="data-toolbar">
        <div className="view-toggle">
          <button
            className={view === "table" ? "active" : ""}
            onClick={() => setView("table")}
          >
            테이블
          </button>
          <button
            className={view === "chart" ? "active" : ""}
            onClick={() => setView("chart")}
          >
            차트
          </button>
        </div>
        <select
          className="pagination-limit"
          value={filters.limit}
          onChange={(e) =>
            setFilters((f) => ({ ...f, limit: Number(e.target.value), page: 1 }))
          }
          aria-label="페이지당 표시 건수"
        >
          {LIMIT_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>
              {opt}건씩
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="loading">데이터를 불러오는 중…</div>
      ) : error ? (
        <div className="error-message">데이터를 불러오지 못했습니다</div>
      ) : data ? (
        <>
          {view === "table" ? (
            <DataTable data={data.data} />
          ) : (
            <DataChart data={data.data} />
          )}
          <Pagination
            pagination={data.pagination}
            onPageChange={(page) => setFilters((f) => ({ ...f, page }))}
          />
        </>
      ) : null}
    </div>
  );
}
