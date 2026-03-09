import { SensorMode } from "../../types/api";
import { useSensorModeMutation } from "../../hooks/useSensorModeMutation";
import { BULK_SENSORS } from "../../constants/sensors";

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

  const handleClick = () => {
    if (BULK_SENSORS.has(serialNumber)) {
      const confirmed = window.confirm(
        `${serialNumber}은(는) 벌크 전송 센서입니다.\n` +
        `${MODE_LABEL[nextMode]} 모드로 전환하면 전송 방식이 변경됩니다.\n\n` +
        `• 일반: 10분마다 10건 벌크 전송\n` +
        `• 긴급: 10초마다 1건 단일 전송\n\n` +
        `전환하시겠습니까?`
      );
      if (!confirmed) return;
    }
    mutation.mutate({ serialNumber, mode: nextMode });
  };

  return (
    <button
      className="btn btn-sm"
      disabled={mutation.isPending}
      onClick={handleClick}
      aria-label={`${serialNumber} 모드를 ${MODE_LABEL[nextMode]}(으)로 전환`}
    >
      {mutation.isPending ? "전환 중…" : `${MODE_LABEL[nextMode]} 모드로 전환`}
    </button>
  );
}
