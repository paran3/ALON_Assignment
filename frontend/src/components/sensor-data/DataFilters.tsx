import { useState } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import { SensorMode } from "../../types/api";
import type { SensorDataFilters } from "../../types/api";
import { useSensors } from "../../hooks/useSensors";
import { format } from "date-fns";

interface DataFiltersProps {
  filters: SensorDataFilters;
  onChange: (filters: SensorDataFilters) => void;
}

function toDate(value: string | undefined): Date | undefined {
  if (!value) return undefined;
  return new Date(value);
}

function fromDate(date: Date | null): string | undefined {
  if (!date) return undefined;
  return format(date, "yyyy-MM-dd'T'HH:mm:ss");
}

export function DataFilters({ filters, onChange }: DataFiltersProps) {
  const [collapsed, setCollapsed] = useState(false);
  const { data: sensorsData } = useSensors();
  const sensors = sensorsData?.data || [];

  const update = (patch: Partial<SensorDataFilters>) =>
    onChange({ ...filters, ...patch, page: 1 });

  const handleReset = () =>
    onChange({ page: 1, limit: filters.limit });

  const hasActiveFilters =
    filters.serial_number ||
    filters.mode ||
    filters.timestamp_from ||
    filters.timestamp_to ||
    filters.created_at_from ||
    filters.created_at_to;

  return (
    <div className={`filters-container ${collapsed ? "collapsed" : ""}`}>
      <button
        className="btn btn-sm filter-collapse-btn"
        onClick={() => setCollapsed((c) => !c)}
        aria-label={collapsed ? "필터 펼치기" : "필터 접기"}
      >
        {collapsed ? "▼ 필터 펼치기" : "▲ 필터 접기"}
      </button>
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="filter-sensor">센서</label>
          <select
            id="filter-sensor"
            value={filters.serial_number || ""}
            onChange={(e) =>
              update({ serial_number: e.target.value || undefined })
            }
          >
            <option value="">전체</option>
            {sensors.map((s) => (
              <option key={s.serial_number} value={s.serial_number}>
                {s.serial_number}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="filter-mode">모드</label>
          <select
            id="filter-mode"
            value={filters.mode || ""}
            onChange={(e) =>
              update({ mode: (e.target.value as SensorMode) || undefined })
            }
          >
            <option value="">전체</option>
            <option value={SensorMode.NORMAL}>일반</option>
            <option value={SensorMode.EMERGENCY}>긴급</option>
          </select>
        </div>
      </div>

      <fieldset className="filter-fieldset">
        <legend>측정 시간</legend>
        <div className="filter-row">
          <div className="filter-group">
            <label>시작</label>
            <DatePicker
              selected={toDate(filters.timestamp_from)}
              onChange={(date: Date | null) => update({ timestamp_from: fromDate(date) })}
              showTimeSelect
              timeIntervals={10}
              timeFormat="HH:mm"
              dateFormat="yyyy-MM-dd HH:mm"
              placeholderText="날짜 선택…"
              isClearable
              selectsStart
              startDate={toDate(filters.timestamp_from)}
              endDate={toDate(filters.timestamp_to)}
              className="datepicker-input"
            />
          </div>
          <span className="filter-separator">~</span>
          <div className="filter-group">
            <label>종료</label>
            <DatePicker
              selected={toDate(filters.timestamp_to)}
              onChange={(date: Date | null) => update({ timestamp_to: fromDate(date) })}
              showTimeSelect
              timeIntervals={10}
              timeFormat="HH:mm"
              dateFormat="yyyy-MM-dd HH:mm"
              placeholderText="날짜 선택…"
              isClearable
              selectsEnd
              startDate={toDate(filters.timestamp_from)}
              endDate={toDate(filters.timestamp_to)}
              minDate={toDate(filters.timestamp_from)}
              className="datepicker-input"
            />
          </div>
        </div>
      </fieldset>

      <fieldset className="filter-fieldset">
        <legend>서버 수신 시간</legend>
        <div className="filter-row">
          <div className="filter-group">
            <label>시작</label>
            <DatePicker
              selected={toDate(filters.created_at_from)}
              onChange={(date: Date | null) => update({ created_at_from: fromDate(date) })}
              showTimeSelect
              timeIntervals={10}
              timeFormat="HH:mm"
              dateFormat="yyyy-MM-dd HH:mm"
              placeholderText="날짜 선택…"
              isClearable
              selectsStart
              startDate={toDate(filters.created_at_from)}
              endDate={toDate(filters.created_at_to)}
              className="datepicker-input"
            />
          </div>
          <span className="filter-separator">~</span>
          <div className="filter-group">
            <label>종료</label>
            <DatePicker
              selected={toDate(filters.created_at_to)}
              onChange={(date: Date | null) => update({ created_at_to: fromDate(date) })}
              showTimeSelect
              timeIntervals={10}
              timeFormat="HH:mm"
              dateFormat="yyyy-MM-dd HH:mm"
              placeholderText="날짜 선택…"
              isClearable
              selectsEnd
              startDate={toDate(filters.created_at_from)}
              endDate={toDate(filters.created_at_to)}
              minDate={toDate(filters.created_at_from)}
              className="datepicker-input"
            />
          </div>
        </div>
      </fieldset>

      {hasActiveFilters ? (
        <button className="btn btn-sm filter-reset" onClick={handleReset}>
          필터 초기화
        </button>
      ) : null}
    </div>
  );
}
