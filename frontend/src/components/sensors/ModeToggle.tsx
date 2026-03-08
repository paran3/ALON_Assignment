import { SensorMode } from "../../types/api";
import { useSensorModeMutation } from "../../hooks/useSensorModeMutation";

const MODE_LABEL: Record<string, string> = {
  NORMAL: "일반",
  EMERGENCY: "긴급",
};

interface ModeToggleProps {
  serialNumber: string;
  currentMode: SensorMode;
}

export function ModeToggle({ serialNumber, currentMode }: ModeToggleProps) {
  const mutation = useSensorModeMutation();
  const nextMode =
    currentMode === SensorMode.NORMAL
      ? SensorMode.EMERGENCY
      : SensorMode.NORMAL;

  return (
    <button
      className="btn btn-sm"
      disabled={mutation.isPending}
      onClick={() => mutation.mutate({ serialNumber, mode: nextMode })}
      aria-label={`${serialNumber} 모드를 ${MODE_LABEL[nextMode]}(으)로 전환`}
    >
      {mutation.isPending ? "전환 중…" : `${MODE_LABEL[nextMode]} 모드로 전환`}
    </button>
  );
}
