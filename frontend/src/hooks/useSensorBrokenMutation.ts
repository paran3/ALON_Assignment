import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useSensorBrokenMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      serialNumber,
      broken,
    }: {
      serialNumber: string;
      broken: boolean;
    }) =>
      apiFetch<{ serial_number: string; broken: boolean }>(
        `/api/v1/sensors/${serialNumber}/broken`,
        {
          method: "PATCH",
          body: JSON.stringify({ broken }),
        }
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sensors"] });
    },
  });
}
