import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";
import type { SensorDataFilters, SensorDataListResponse } from "../types/api";

export function useSensorData(filters: SensorDataFilters) {
  const params = new URLSearchParams();
  params.set("page", String(filters.page));
  params.set("limit", String(filters.limit));

  if (filters.serial_number) params.set("serial_number", filters.serial_number);
  if (filters.mode) params.set("mode", filters.mode);
  if (filters.timestamp_from) params.set("timestamp_from", filters.timestamp_from);
  if (filters.timestamp_to) params.set("timestamp_to", filters.timestamp_to);
  if (filters.created_at_from) params.set("created_at_from", filters.created_at_from);
  if (filters.created_at_to) params.set("created_at_to", filters.created_at_to);

  return useQuery({
    queryKey: ["sensor-data", filters],
    queryFn: () =>
      apiFetch<SensorDataListResponse>(
        `/api/v1/sensor-data?${params.toString()}`
      ),
  });
}
