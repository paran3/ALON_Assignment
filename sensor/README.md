# Sensor - IoT 가상 센서 시뮬레이터

백엔드 서버에 주기적으로 환경 데이터를 전송하는 가상 센서 시뮬레이터.

## 기능
- 센서 5개가 서버 시작 시 백엔드에 자동 등록 후 주기적 데이터 전송
- NORMAL 모드: 10분 간격, EMERGENCY 모드: 10초 간격
- 타임존 혼재 재현 (서울/부산 → KST `+09:00`, 나머지 → UTC `Z`)
- 모드 변경 API (백엔드 동기화 + 전송 주기 자동 변경)
- 고장 시뮬레이션 API (데이터 전송 중단 → 백엔드에서 MISSING 감지)

## 추가 기능 (과제 명세 외)
- **고장 시뮬레이션**: `broken` 플래그로 특정 센서의 데이터 전송을 중단시켜 백엔드의 MISSING 상태 판별 로직을 E2E 테스트할 수 있다.
- **모드 변경 시 백엔드 동기화**: 센서 측에서 모드를 변경하면 백엔드에도 자동 반영되어 양방향 모드 제어가 가능하다.

## API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/sensors` | 전체 센서 상태 조회 |
| PATCH | `/sensors/{serial_number}/mode` | 모드 변경 (`{"mode": "EMERGENCY"}`) |
| PATCH | `/sensors/{serial_number}/broken` | 고장 시뮬레이션 (`{"broken": true}`) |

## 실행 방법

### 로컬
```bash
pip install -r requirements.txt
python main.py
```

### Docker
```bash
docker build -t iot-sensor .
docker run -e BACKEND_URL=http://host.docker.internal:8000 -p 8001:8001 iot-sensor
```

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `BACKEND_URL` | `http://127.0.0.1:8000` | 백엔드 서버 주소 |
| `SENSOR_PORT` | `8001` | 시뮬레이터 포트 |
| `NORMAL_INTERVAL` | `600` | NORMAL 모드 전송 주기 (초) |
| `EMERGENCY_INTERVAL` | `10` | EMERGENCY 모드 전송 주기 (초) |
