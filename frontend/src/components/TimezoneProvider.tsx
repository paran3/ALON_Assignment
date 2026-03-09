import { createContext, useContext, useState } from "react";

export const TIMEZONE_OPTIONS = [
  { value: "Asia/Seoul", label: "한국 (KST)" },
  { value: "Asia/Tokyo", label: "일본 (JST)" },
  { value: "America/New_York", label: "뉴욕 (ET)" },
  { value: "Europe/London", label: "런던 (GMT)" },
  { value: "UTC", label: "UTC" },
] as const;

interface TimezoneContextValue {
  timezone: string;
  setTimezone: (tz: string) => void;
}

const TimezoneContext = createContext<TimezoneContextValue>({
  timezone: "Asia/Seoul",
  setTimezone: () => {},
});

export function useTimezone() {
  return useContext(TimezoneContext);
}

export function TimezoneProvider({ children }: { children: React.ReactNode }) {
  const [timezone, setTimezone] = useState<string>(() => {
    return localStorage.getItem("timezone") || "Asia/Seoul";
  });

  const handleSetTimezone = (tz: string) => {
    setTimezone(tz);
    localStorage.setItem("timezone", tz);
  };

  return (
    <TimezoneContext.Provider value={{ timezone, setTimezone: handleSetTimezone }}>
      {children}
    </TimezoneContext.Provider>
  );
}
