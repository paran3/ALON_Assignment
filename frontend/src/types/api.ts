export const SensorMode = {
  NORMAL: "NORMAL",
  EMERGENCY: "EMERGENCY",
} as const;
export type SensorMode = (typeof SensorMode)[keyof typeof SensorMode];

export const SensorStatus = {
  HEALTHY: "HEALTHY",
  MISSING: "MISSING",
} as const;
export type SensorStatus = (typeof SensorStatus)[keyof typeof SensorStatus];

export interface Sensor {
  serial_number: string;
  mode: SensorMode;
  status: SensorStatus;
  last_received_at: string | null;
  latitude: number;
  longitude: number;
  created_at: string;
  updated_at: string;
}

export interface SensorListResponse {
  success: boolean;
  data: Sensor[];
}

export interface Location {
  lat: number;
  lng: number;
}

export interface Metrics {
  temperature: number;
  humidity: number;
  pressure: number;
  air_quality: number;
}

export interface SensorData {
  id: number;
  serial_number: string;
  timestamp: string;
  server_received_at: string;
  mode: SensorMode;
  metrics: Metrics;
  location: Location;
}

export interface Pagination {
  total_count: number;
  current_page: number;
  limit: number;
  total_pages: number;
  has_next_page: boolean;
  has_prev_page: boolean;
}

export interface SensorDataListResponse {
  success: boolean;
  data: SensorData[];
  pagination: Pagination;
}

export interface SensorDataFilters {
  serial_number?: string;
  mode?: SensorMode;
  timestamp_from?: string;
  timestamp_to?: string;
  created_at_from?: string;
  created_at_to?: string;
  page: number;
  limit: number;
}
