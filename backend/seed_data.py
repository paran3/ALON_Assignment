"""센서 및 측정 데이터 시드 스크립트. 백엔드 서버가 실행 중일 때 사용."""

import asyncio
import random
from datetime import datetime, timedelta, timezone

import aiohttp

BASE_URL = "http://localhost:9000/api/v1"

SENSORS = [
    {"serial_number": "SN-SEOUL-001", "latitude": 37.5665, "longitude": 126.9780, "mode": "NORMAL"},
    {"serial_number": "SN-BUSAN-002", "latitude": 35.1796, "longitude": 129.0756, "mode": "NORMAL"},
    {"serial_number": "SN-JEJU-003", "latitude": 33.4996, "longitude": 126.5312, "mode": "NORMAL"},
    {"serial_number": "SN-TOKYO-004", "latitude": 35.6762, "longitude": 139.6503, "mode": "EMERGENCY"},
    {"serial_number": "SN-NEWYORK-005", "latitude": 40.7128, "longitude": -74.0060, "mode": "NORMAL"},
]

# 도시별 기후 특성
CLIMATE = {
    "SN-SEOUL-001": {"temp": (5, 15), "humidity": (40, 70), "pressure": (1010, 1025), "air_quality": (30, 80)},
    "SN-BUSAN-002": {"temp": (8, 18), "humidity": (50, 80), "pressure": (1008, 1020), "air_quality": (20, 60)},
    "SN-JEJU-003": {"temp": (10, 20), "humidity": (60, 90), "pressure": (1005, 1018), "air_quality": (10, 40)},
    "SN-TOKYO-004": {"temp": (6, 16), "humidity": (45, 75), "pressure": (1010, 1022), "air_quality": (40, 120)},
    "SN-NEWYORK-005": {"temp": (-2, 10), "humidity": (30, 65), "pressure": (1005, 1025), "air_quality": (50, 150)},
}

# 도시별 UTC 오프셋
TZ_OFFSETS = {
    "SN-SEOUL-001": "+09:00",
    "SN-BUSAN-002": "+09:00",
    "SN-JEJU-003": "+09:00",
    "SN-TOKYO-004": "+09:00",
    "SN-NEWYORK-005": "-05:00",
}


def generate_sensor_data(serial_number: str, index: int) -> dict:
    climate = CLIMATE[serial_number]
    sensor = next(s for s in SENSORS if s["serial_number"] == serial_number)
    offset = TZ_OFFSETS[serial_number]

    # 최근 2시간 동안의 데이터, 6분 간격
    base_time = datetime.now(timezone.utc) - timedelta(hours=2)
    timestamp = base_time + timedelta(minutes=6 * index)
    ts_str = timestamp.strftime(f"%Y-%m-%dT%H:%M:%S{offset}")

    temp_range = climate["temp"]
    hum_range = climate["humidity"]
    pres_range = climate["pressure"]
    aq_range = climate["air_quality"]

    # 시간에 따라 약간 변화하는 값 생성
    progress = index / 20
    temperature = round(temp_range[0] + (temp_range[1] - temp_range[0]) * progress + random.uniform(-2, 2), 1)
    humidity = round(hum_range[0] + (hum_range[1] - hum_range[0]) * progress + random.uniform(-5, 5), 1)
    pressure = round(pres_range[0] + (pres_range[1] - pres_range[0]) * progress + random.uniform(-2, 2), 1)
    air_quality = max(0, int(aq_range[0] + (aq_range[1] - aq_range[0]) * progress + random.uniform(-10, 10)))

    # 위치 약간 변동
    lat = sensor["latitude"] + random.uniform(-0.01, 0.01)
    lng = sensor["longitude"] + random.uniform(-0.01, 0.01)

    return {
        "serial_number": serial_number,
        "timestamp": ts_str,
        "mode": sensor["mode"],
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "location": {"lat": round(lat, 4), "lng": round(lng, 4)},
        "air_quality": air_quality,
    }


async def main():
    async with aiohttp.ClientSession() as session:
        # 1. 센서 등록
        print("=== 센서 등록 ===")
        for sensor in SENSORS:
            async with session.post(f"{BASE_URL}/sensors", json=sensor) as resp:
                if resp.status == 201:
                    print(f"  [OK] {sensor['serial_number']} 등록 완료")
                elif resp.status == 409:
                    print(f"  [SKIP] {sensor['serial_number']} 이미 존재")
                else:
                    text = await resp.text()
                    print(f"  [ERR] {sensor['serial_number']} - {resp.status}: {text}")

        # 2. 센서 데이터 배치 전송 (센서별 20건)
        print("\n=== 센서 데이터 전송 ===")
        for sensor in SENSORS:
            sn = sensor["serial_number"]
            batch = [generate_sensor_data(sn, i) for i in range(20)]

            async with session.post(f"{BASE_URL}/sensor-data", json=batch) as resp:
                if resp.status == 202:
                    body = await resp.json()
                    print(f"  [OK] {sn} → 20건 전송 (task_id: {body['task_id'][:8]}...)")
                else:
                    text = await resp.text()
                    print(f"  [ERR] {sn} - {resp.status}: {text}")

        # 잠시 대기 후 결과 확인
        await asyncio.sleep(2)

        # 3. 확인
        print("\n=== 결과 확인 ===")
        async with session.get(f"{BASE_URL}/sensors") as resp:
            body = await resp.json()
            print(f"  등록된 센서: {len(body['data'])}개")
            for s in body["data"]:
                print(f"    - {s['serial_number']}: {s['status']} ({s['mode']})")

        async with session.get(f"{BASE_URL}/sensor-data?limit=1") as resp:
            body = await resp.json()
            print(f"  총 데이터: {body['pagination']['total_count']}건")


if __name__ == "__main__":
    asyncio.run(main())
