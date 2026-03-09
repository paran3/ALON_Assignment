/**
 * UTC 시간 문자열을 지정된 타임존으로 변환하여 포맷팅
 */
export function formatInTimezone(utc: string | null, timezone: string): string {
  if (!utc) return "-";
  const date = new Date(utc);
  return date.toLocaleString("ko-KR", {
    timeZone: timezone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}
