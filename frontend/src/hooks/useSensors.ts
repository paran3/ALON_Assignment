import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";
import type { SensorListResponse } from "../types/api";

export function useSensors() {
  return useQuery({
    queryKey: ["sensors"],
    queryFn: () => apiFetch<SensorListResponse>("/api/v1/sensors"),
    refetchInterval: 5000,
  });
}
