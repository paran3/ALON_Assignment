# Backend - IoT 환경 데이터 모니터링 시스템

## 기술 스택
- **Framework**: FastAPI
- **아키텍처**: [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) 기반

## 주요 기능
- 센서 데이터 수집 API (단일/배치 전송)
- 타임존 정규화 (UTC/KST 혼재 처리)
- 조회 API (시리얼 넘버, 모드, 기간별 필터링)
- 센서 상태 검증 (데이터 누락 판단)
- 고장 시뮬레이션 (`broken` 플래그 DB 저장 + 센서 시뮬레이터 동기화)
- 모드 변경 양방향 동기화 (백엔드 ↔ 센서 시뮬레이터)

## 센서 상태 검증 (APScheduler)
- 5초 간격으로 모든 센서의 `last_received_at`을 검사하여 데이터 누락(고장) 자동 감지
- NORMAL: 10분, EMERGENCY: 10초 주기 + 30초 허용치 초과 시 `MISSING` 처리
- API 호출 없이도 고장 센서를 놓치지 않기 위한 백그라운드 검사

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./iot_monitoring.db` | DB 접속 URL |
| `SENSOR_SIMULATOR_URL` | `http://sensor:8001` | 센서 시뮬레이터 URL (설정 시 모드 변경 양방향 동기화) |

## 실행 방법

### 로컬

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker (단독)

```bash
cd backend
docker build -t iot-backend .
docker run -p 8000:8000 iot-backend
```

### Docker Compose (백엔드 + 센서 시뮬레이터)

프로젝트 루트에서:
```bash
# 첫 실행 또는 코드 변경 후 재빌드 + 실행
docker compose up --build

# 백그라운드 실행
docker compose up --build -d

# 이미 빌드된 이미지로 실행 (코드 변경 없을 때)
docker compose up

# 로그 확인 (백그라운드 실행 시)
docker compose logs -f

# 특정 서비스 로그만 확인
docker compose logs -f backend

# 중지
docker compose down

# 중지 + 볼륨 삭제 (DB 초기화)
docker compose down -v
```
- 백엔드: http://localhost:8000
- 센서 시뮬레이터: http://localhost:8001
- 양방향 모드 동기화 자동 설정

API 문서: http://localhost:8000/docs
