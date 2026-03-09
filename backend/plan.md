# Backend 개발 계획

## Context
IoT 센서 환경 데이터 모니터링 시스템의 백엔드를 FastAPI로 구축한다. assignment.md 요구사항 기반.

## 디렉토리 구조 (full-stack-fastapi-template 참고)
```
backend/
├── app/
│   ├── main.py                # FastAPI 앱, 라이프사이클
│   ├── models.py              # SQLAlchemy 모델
│   ├── schemas.py             # Pydantic 스키마
│   ├── crud.py                # DB CRUD 함수
│   ├── api/
│   │   ├── deps.py            # DB 세션 등 의존성
│   │   ├── main.py            # 라우터 통합
│   │   └── routes/
│   │       ├── sensor_data.py # 데이터 수집/조회
│   │       ├── sensors.py     # 센서 상태/제어
│   │       └── tasks.py       # 백그라운드 태스크 상태 조회
│   ├── core/
│   │   ├── config.py          # Settings (Pydantic BaseSettings)
│   │   └── db.py              # SQLAlchemy 엔진/세션
│   └── services/
│       ├── data_ingestion.py  # 데이터 수집 백그라운드 처리
│       └── health_checker.py  # 센서 상태 검증 (APScheduler)
├── alembic/                   # DB 마이그레이션
├── alembic.ini
├── pyproject.toml
├── Dockerfile
└── README.md
```

## DB 스키마 (SQLite + SQLAlchemy, 시간은 전부 UTC 저장)

### sensor_data (센서 측정 데이터)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | Integer PK | 자동 증가 |
| serial_number | String, indexed | 센서 식별번호 |
| timestamp | DateTime(UTC) | 센서 기준 생성시간 (UTC 정규화) |
| created_at | DateTime(UTC) | 서버 수신 시간 |
| mode | String | NORMAL / EMERGENCY |
| temperature | Float | 온도 |
| humidity | Float | 습도 |
| pressure | Float | 기압 |
| latitude | Float | 위도 |
| longitude | Float | 경도 |
| air_quality | Integer | 공기질 지수 |
| task_id | String, nullable | 배치 처리 태스크 ID |

### sensors (센서 마스터 - 센서가 등록 API로 직접 등록)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| serial_number | String PK | 센서 식별번호 |
| mode | String | 현재 모드 (NORMAL/EMERGENCY) |
| status | String | HEALTHY / MISSING |
| last_received_at | DateTime(UTC), nullable | 마지막 데이터 수신 시간 (등록 시 null) |
| latitude | Float | 위도 (등록 시 필수) |
| longitude | Float | 경도 (등록 시 필수) |
| created_at | DateTime(UTC) | 최초 등록 시간 |
| updated_at | DateTime(UTC) | 최종 갱신 시간 |

### background_tasks (백그라운드 태스크 추적)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | String PK | UUID |
| status | String | PENDING / PROCESSING / COMPLETED / FAILED |
| total_count | Integer | 전체 데이터 수 |
| processed_count | Integer | 처리 완료 수 |
| error_message | String, nullable | 에러 메시지 |
| created_at | DateTime(UTC) | 생성 시간 |
| completed_at | DateTime(UTC), nullable | 완료 시간 |

## API 엔드포인트

### 데이터 수집
- `POST /api/v1/sensor-data` — 단일/배치 수신 → 백그라운드 태스크 처리, task_id 반환 (202)

### 데이터 조회
- `GET /api/v1/sensor-data` — 필터: serial_number, mode, timestamp_from/to, created_at_from/to + 페이지네이션

### 센서 관리
- `POST /api/v1/sensors` — 센서 등록 (serial_number 중복 시 409 Conflict)
  - 요청: `{ serial_number, latitude, longitude, mode(기본 NORMAL) }`
- `GET /api/v1/sensors` — 전체 센서 목록 + 상태
- `GET /api/v1/sensors/{serial_number}` — 단일 센서 상세
- `PATCH /api/v1/sensors/{serial_number}/mode` — 모드 변경 (NORMAL ↔ EMERGENCY), 센서 시뮬레이터 동기화

### 태스크 조회
- `GET /api/v1/tasks/{task_id}` — 백그라운드 태스크 상태 조회

## 핵심 로직

### 1. 타임존 정규화
- 수신 시 timestamp 파싱 → UTC로 통일 저장
- ISO8601: `+09:00`이면 KST→UTC 변환, `Z`면 그대로

### 2. 백그라운드 데이터 수집
- POST 수신 → 즉시 task_id 반환 (202 Accepted)
- asyncio 태스크에서 데이터 검증/정규화/저장
- 미등록 센서의 데이터는 개별 실패 처리 (등록된 건만 저장, 미등록 건은 스킵 후 에러 기록)
- sensors 테이블 update (last_received_at, mode, 위치 갱신)

### 3. 센서 상태 검증 (APScheduler)
- **APScheduler AsyncIOScheduler** 주기적 검사 (5초 간격)
- 로직: `now - last_received_at > expected_interval + tolerance(30초)` → MISSING
- NORMAL: 600초, EMERGENCY: 10초
- API 조회 시에도 on-demand 상태 계산 (이중 안전장치)

### 4. 데이터 유효성 검증
- 필수 필드 존재 여부, 타입 체크, 타임스탬프 파싱 가능 여부 (Pydantic)

### 5. 센서 시뮬레이터 연동
- 모드 변경 시 센서 시뮬레이터(`SENSOR_SIMULATOR_URL`)에 httpx로 동기화
- `SENSOR_SIMULATOR_URL`이 빈 문자열이면 동기화 비활성 (기본값)
- 동기화 실패해도 백엔드 동작에 영향 없음 (fire-and-forget, 경고 로그만 기록)

## 주요 라이브러리
- fastapi, uvicorn
- sqlalchemy, alembic
- pydantic, pydantic-settings
- apscheduler
- httpx (센서 시뮬레이터 연동)
- python-dateutil (타임스탬프 파싱)

## 검증 방법
1. 센서 등록 → 201 확인, 동일 serial_number 재등록 → 409 확인
2. 미등록 센서로 데이터 전송 → 태스크 완료 후 해당 건 실패 확인
3. 단일/배치 POST → task_id 반환 확인
4. GET task 상태 → COMPLETED 확인, processed_count/total_count 비교
5. GET sensor-data 필터링 동작 확인
6. 타임존 혼재 데이터 → UTC 정규화 확인
7. 데이터 미전송 → 센서 상태 MISSING 전환 확인
8. 모드 변경 → 센서 시뮬레이터 동기화 확인 (SENSOR_SIMULATOR_URL 설정 시)
