# Frontend - IoT 환경 데이터 모니터링 시스템

## 기술 스택
- **Framework**: React 19 + TypeScript
- **빌드**: Vite 7
- **서버 상태 관리**: TanStack Query (5초 간격 자동 리페치)
- **라우팅**: React Router v7
- **차트**: Recharts
- **시간 처리**: date-fns (UTC → 브라우저 로컬 타임존 변환)

## 주요 기능

### 센서 상태 모니터링 (Sensors 탭)
- 등록된 센서 목록을 카드 형태로 표시
- 센서별 상태(HEALTHY/MISSING) 배지 표시
- 모드 전환(NORMAL ↔ EMERGENCY) 토글 버튼
- 마지막 수신 시간, 좌표 등 상세 정보 표시

### 센서 데이터 조회 (Sensor Data 탭)
- **필터링**: 센서 시리얼 넘버, 모드, 측정 시간 범위(timestamp), 서버 수신 시간 범위(created_at)
- **테이블 뷰**: 온도, 습도, 기압, 공기질 등 측정 데이터를 표로 표시
- **차트 뷰**: Recharts 라인 차트로 온도/습도/공기질 시각화
- **페이지네이션**: 이전/다음 페이지 네비게이션

### UI/UX
- **다크/라이트 모드**: CSS 변수 기반 테마 전환, localStorage 저장
- **반응형 디자인**: 데스크탑/모바일 지원
- **브라우저 로컬 시간**: 서버에서 UTC로 받은 시간을 브라우저 타임존으로 변환하여 표시

## 컴포넌트 구조
```
App
└── Layout (헤더 + 네비게이션)
    ├── SensorsPage
    │   └── SensorList
    │       └── SensorCard + ModeToggle
    └── SensorDataPage
        ├── DataFilters
        ├── DataTable / DataChart
        └── Pagination
```

## 상태 관리
- **서버 상태**: TanStack Query로 관리 (캐시, 자동 리페치, 뮤테이션)
- **UI 상태**: React useState (필터, 뷰 모드 등)
- **테마 상태**: React Context + localStorage

## 환경 변수
| 변수 | 기본값 | 설명 |
|------|--------|------|
| `VITE_API_URL` | `http://localhost:8000` | 백엔드 API 서버 주소 |

## 실행 방법

### 로컬 개발
```bash
npm install
npm run dev
```

### Docker
```bash
docker build -t iot-frontend .
docker run -p 80:80 iot-frontend
```
