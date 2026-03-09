# 가상 센서 시뮬레이터 개발 계획

## 목적
실제 IoT 센서를 대신하여 백엔드 서버에 주기적으로 환경 데이터를 전송하는 가상 센서 시뮬레이터.
센서 모드 전환, 고장 시뮬레이션 등 제어 API를 제공하여 전체 시스템 E2E 테스트를 가능하게 한다.

## 기술 스택
- **FastAPI** — 센서 제어 API 서버
- **APScheduler** — 센서별 주기적 데이터 전송 스케줄링
- **httpx** — 백엔드 서버로 비동기 HTTP 요청

## 센서 사양 (5개)

| 시리얼 번호 | 위치 | 타임존 포맷 | 초기 모드 |
|---|---|---|---|
| SN-SEOUL-001 | 서울 (37.5665, 126.9780) | KST (+09:00) | NORMAL |
| SN-BUSAN-002 | 부산 (35.1796, 129.0756) | KST (+09:00) | NORMAL |
| SN-JEJU-003 | 제주 (33.4996, 126.5312) | UTC (Z) | NORMAL |
| SN-TOKYO-004 | 도쿄 (35.6762, 139.6503) | UTC (Z) | EMERGENCY |
| SN-NEWYORK-005 | 뉴욕 (40.7128, -74.0060) | UTC (Z) | NORMAL |

> 타임존 혼재 상황 재현: 서울/부산은 KST(`+09:00`), 나머지는 UTC(`Z`)로 timestamp 전송

## 센서 상태 모델

각 가상 센서는 인메모리로 아래 상태를 관리한다:

| 필드 | 타입 | 설명 |
|---|---|---|
| serial_number | str | 센서 식별번호 |
| mode | Enum (NORMAL/EMERGENCY) | 현재 작동 모드 |
| broken | bool | 고장 여부 (True면 데이터 전송 중단) |
| latitude | float | 위도 |
| longitude | float | 경도 |
| tz_offset | str | timestamp 포맷에 사용할 오프셋 (`+09:00` 또는 `Z`) |
| climate | dict | 도시별 기후 특성 (온도/습도/기압/공기질 범위) |

## 전송 주기

과제 명세 기반:
- **NORMAL 모드**: 10분(600초) 간격
- **EMERGENCY 모드**: 10초 간격

모드 변경 시 스케줄러의 해당 센서 job interval을 동적으로 변경한다.

## 데이터 생성 로직

센서별 기후 특성 범위 내에서 랜덤 + 시간 흐름에 따른 미세 변동:
- `temperature`: 기본 범위 ± random(-2, 2)
- `humidity`: 기본 범위 ± random(-5, 5)
- `pressure`: 기본 범위 ± random(-2, 2)
- `air_quality`: 기본 범위 ± random(-10, 10)
- `location`: 고정 좌표 ± random(-0.01, 0.01) 미세 변동

## 서버 시작 시 동작

1. 백엔드 서버(`BACKEND_URL`)에 각 센서를 `POST /api/v1/sensors`로 등록 (409 중복 무시)
2. APScheduler에 센서별 job 등록 (NORMAL: 600초, EMERGENCY: 10초)
3. 각 job은 해당 센서의 데이터를 생성하여 `POST /api/v1/sensor-data`로 단건 전송
4. `broken=True`인 센서는 전송 스킵 → 백엔드에서 MISSING 상태로 판별됨

## API 엔드포인트

### 센서 목록 조회
- `GET /sensors` — 전체 센서 상태 조회 (serial_number, mode, broken)

### 모드 변경
- `PATCH /sensors/{serial_number}/mode` — body: `{ "mode": "EMERGENCY" | "NORMAL" }`
  - 인메모리 상태 변경
  - 백엔드 서버에도 `PATCH /api/v1/sensors/{serial_number}/mode` 동기화
  - APScheduler job interval 변경 (NORMAL→600초, EMERGENCY→10초)

### 고장 시뮬레이션
- `PATCH /sensors/{serial_number}/broken` — body: `{ "broken": true | false }`
  - `broken=true`: 데이터 전송 중단 (스케줄러 job은 유지하되 전송 스킵)
  - `broken=false`: 전송 재개

## 디렉토리 구조

```
sensor/
├── main.py            # FastAPI 앱 + 라이프사이클 + 라우터
├── sensor_manager.py  # 센서 상태 관리 + 데이터 생성 + 전송 로직
├── config.py          # 설정 (백엔드 URL, 포트 등)
├── requirements.txt
├── Dockerfile
├── plan.md
└── README.md
```

## 설정

| 환경변수 | 기본값 | 설명 |
|---|---|---|
| BACKEND_URL | http://127.0.0.1:9000 | 백엔드 서버 주소 |
| SENSOR_PORT | 9001 | 센서 시뮬레이터 포트 |
| NORMAL_INTERVAL | 600 | NORMAL 모드 전송 주기 (초) |
| EMERGENCY_INTERVAL | 10 | EMERGENCY 모드 전송 주기 (초) |

## 검증 시나리오

1. 센서 시뮬레이터 시작 → 백엔드에 5개 센서 자동 등록 확인
2. NORMAL 모드 센서 → 10분 간격 데이터 전송 확인
3. 모드 변경 API 호출 → EMERGENCY 전환 → 10초 간격으로 변경 확인
4. 고장 API 호출(`broken=true`) → 데이터 전송 중단 → 백엔드에서 MISSING 판별 확인
5. 고장 복구(`broken=false`) → 전송 재개 → HEALTHY 복구 확인
6. 타임존 혼재: 서울/부산은 `+09:00`, 나머지는 `Z`로 timestamp 생성 확인
