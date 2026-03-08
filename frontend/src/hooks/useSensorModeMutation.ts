import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";
import { SensorMode } from "../types/api";
import type { Sensor } from "../types/api";

export function useSensorModeMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      serialNumber,
      mode,
    }: {
      serialNumber: string;
      mode: SensorMode;
    }) =>
      apiFetch<Sensor>(`/api/v1/sensors/${serialNumber}/mode`, {
        method: "PATCH",
        body: JSON.stringify({ mode }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sensors"] });
    },
  });
}
