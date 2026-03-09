import logging
import random
from datetime import datetime, timezone, timedelta
from enum import Enum

import httpx

from config import settings

logger = logging.getLogger(__name__)


class SensorMode(str, Enum):
    NORMAL = "NORMAL"
    EMERGENCY = "EMERGENCY"


class VirtualSensor:
    def __init__(
        self,
        serial_number: str,
        lat: float,
        lng: float,
        tz_offset: str,
        mode: SensorMode,
        climate: dict,
    ):
        self.serial_number = serial_number
        self.latitude = lat
        self.longitude = lng
        self.tz_offset = tz_offset
        self.mode = mode
        self.broken = False
        self.climate = climate

    def generate_data(self) -> dict:
        now = datetime.now(timezone.utc)

        if self.tz_offset == "+09:00":
            local = now + timedelta(hours=9)
            ts = local.strftime("%Y-%m-%dT%H:%M:%S+09:00")
        else:
            ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        c = self.climate
        return {
            "serial_number": self.serial_number,
            "timestamp": ts,
            "mode": self.mode.value,
            "temperature": round(random.uniform(*c["temp"]), 1),
            "humidity": round(random.uniform(*c["humidity"]), 1),
            "pressure": round(random.uniform(*c["pressure"]), 1),
            "location": {
                "lat": round(self.latitude + random.uniform(-0.01, 0.01), 4),
                "lng": round(self.longitude + random.uniform(-0.01, 0.01), 4),
            },
            "air_quality": max(0, int(random.uniform(*c["air_quality"]))),
        }


SENSOR_DEFS = [
    VirtualSensor("SN-SEOUL-001", 37.5665, 126.9780, "+09:00", SensorMode.NORMAL,
                  {"temp": (3, 17), "humidity": (35, 75), "pressure": (1008, 1027), "air_quality": (20, 90)}),
    VirtualSensor("SN-BUSAN-002", 35.1796, 129.0756, "+09:00", SensorMode.NORMAL,
                  {"temp": (6, 20), "humidity": (45, 85), "pressure": (1006, 1022), "air_quality": (15, 65)}),
    VirtualSensor("SN-JEJU-003", 33.4996, 126.5312, "Z", SensorMode.NORMAL,
                  {"temp": (8, 22), "humidity": (55, 95), "pressure": (1003, 1020), "air_quality": (5, 45)}),
    VirtualSensor("SN-TOKYO-004", 35.6762, 139.6503, "Z", SensorMode.EMERGENCY,
                  {"temp": (4, 18), "humidity": (40, 80), "pressure": (1008, 1024), "air_quality": (30, 130)}),
    VirtualSensor("SN-NEWYORK-005", 40.7128, -74.0060, "Z", SensorMode.NORMAL,
                  {"temp": (-4, 12), "humidity": (25, 70), "pressure": (1003, 1027), "air_quality": (40, 160)}),
]


class SensorManager:
    def __init__(self):
        self.sensors: dict[str, VirtualSensor] = {s.serial_number: s for s in SENSOR_DEFS}

    async def register_all(self):
        api = f"{settings.BACKEND_URL}/api/v1/sensors"
        async with httpx.AsyncClient(timeout=10) as client:
            for s in self.sensors.values():
                body = {
                    "serial_number": s.serial_number,
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                    "mode": s.mode.value,
                }
                try:
                    resp = await client.post(api, json=body)
                    if resp.status_code == 201:
                        logger.info("[등록] %s 완료", s.serial_number)
                    elif resp.status_code == 409:
                        logger.info("[등록] %s 이미 존재", s.serial_number)
                    else:
                        logger.warning("[등록] %s 실패: %s", s.serial_number, resp.text)
                except httpx.HTTPError as e:
                    logger.error("[등록] %s 연결 실패: %s", s.serial_number, e)

    async def send_data(self, serial_number: str):
        sensor = self.sensors.get(serial_number)
        if not sensor:
            return
        if sensor.broken:
            logger.debug("[스킵] %s 고장 상태", serial_number)
            return

        data = sensor.generate_data()
        api = f"{settings.BACKEND_URL}/api/v1/sensor-data"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                resp = await client.post(api, json=data)
                logger.info("[전송] %s → %s", serial_number, resp.status_code)
            except httpx.HTTPError as e:
                logger.error("[전송] %s 실패: %s", serial_number, e)

    async def change_mode(self, serial_number: str, mode: SensorMode):
        sensor = self.sensors.get(serial_number)
        if not sensor:
            return False
        sensor.mode = mode

        # 백엔드 동기화
        api = f"{settings.BACKEND_URL}/api/v1/sensors/{serial_number}/mode"
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                await client.patch(api, json={"mode": mode.value})
            except httpx.HTTPError as e:
                logger.error("[모드 동기화] %s 실패: %s", serial_number, e)

        return True

    def set_broken(self, serial_number: str, broken: bool) -> bool:
        sensor = self.sensors.get(serial_number)
        if not sensor:
            return False
        sensor.broken = broken
        return True

    def get_interval(self, serial_number: str) -> int:
        sensor = self.sensors.get(serial_number)
        if not sensor:
            return settings.NORMAL_INTERVAL
        if sensor.mode == SensorMode.EMERGENCY:
            return settings.EMERGENCY_INTERVAL
        return settings.NORMAL_INTERVAL


manager = SensorManager()
