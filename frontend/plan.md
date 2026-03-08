# Frontend 개발 계획

## Context
백엔드 API를 호출하여 센서/센서 데이터를 시각화하는 대시보드. React 기반, 미니멀 디자인, 화이트/다크 모드 지원.

## 개발 가이드라인
- `/web-design-guidelines` — UI 구현 시 Web Interface Guidelines 준수
- `/vercel-react-best-practices` — React 컴포넌트 작성 시 Vercel 성능 최적화 패턴 준수

## 기술 스택
- **React** (Vite)
- **TypeScript**
- **TanStack Query** — 서버 상태 관리 (API 캐싱, 리페칭)
- **React Router** — 탭 라우팅
- **CSS Modules** 또는 **Tailwind CSS** — 미니멀 스타일링
- **date-fns** — UTC → 브라우저 로컬 시간 변환
- **Recharts** — 센서 데이터 차트 시각화

## 디렉토리 구조
```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx                    # 라우터 + 레이아웃
│   ├── api/
│   │   └── client.ts              # fetch wrapper, base URL
│   ├── hooks/
│   │   ├── useSensors.ts          # GET /sensors
│   │   ├── useSensorData.ts       # GET /sensor-data (필터+페이지네이션)
│   │   └── useSensorModeMutation.ts # PATCH /sensors/{sn}/mode
│   ├── components/
│   │   ├── Layout.tsx             # 헤더, 탭 네비게이션, 다크모드 토글
│   │   ├── ThemeProvider.tsx      # 다크/화이트 모드 Context
│   │   ├── sensors/
│   │   │   ├── SensorList.tsx     # 센서 목록 테이블
│   │   │   ├── SensorCard.tsx     # 개별 센서 상태 카드
│   │   │   └── ModeToggle.tsx     # NORMAL ↔ EMERGENCY 전환 버튼
│   │   └── sensor-data/
│   │       ├── DataTable.tsx      # 데이터 리스트 테이블
│   │       ├── DataChart.tsx      # 센서 데이터 차트 (온도/습도/기압 추이)
│   │       ├── DataFilters.tsx    # 필터 UI (serial_number, mode, 기간)
│   │       └── Pagination.tsx     # 페이지네이션 컴포넌트
│   ├── pages/
│   │   ├── SensorsPage.tsx        # 센서 탭
│   │   └── SensorDataPage.tsx     # 센서 데이터 탭
│   ├── types/
│   │   └── api.ts                 # API 응답 타입 정의
│   └── styles/
│       └── global.css             # CSS 변수 (테마), 리셋
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── Dockerfile
└── README.md
```

## 페이지 구성

### 공통 레이아웃
- 상단 헤더: 프로젝트 제목 + 다크/화이트 모드 토글
- 탭 네비게이션: **센서** | **센서 데이터**

### 탭 1: 센서 (SensorsPage)
- `GET /api/v1/sensors` 호출
- 센서 목록을 카드 또는 테이블로 표시
  - serial_number, mode, status(HEALTHY/MISSING), last_received_at
  - status에 따라 색상 구분 (HEALTHY: 초록, MISSING: 빨강)
- 모드 변경 버튼 (NORMAL ↔ EMERGENCY)
  - `PATCH /api/v1/sensors/{serial_number}/mode` 호출
- 주기적 자동 리페치 (5초) — 센서 상태 실시간 반영

### 탭 2: 센서 데이터 (SensorDataPage)
- `GET /api/v1/sensor-data` 호출
- 필터 영역:
  - serial_number (드롭다운, 센서 목록에서 가져옴)
  - mode (NORMAL / EMERGENCY / 전체)
  - 기간 필터 2종:
    - timestamp (센서 생성 시간) 기준 from/to
    - created_at (서버 수신 시간) 기준 from/to
- 데이터 테이블:
  - serial_number, timestamp(로컬 변환), server_received_at(로컬 변환), mode, temperature, humidity, pressure, air_quality
- 데이터 차트:
  - 테이블/차트 뷰 전환 토글
  - Recharts 라인 차트 — 온도/습도/기압/공기질 추이 (timestamp 기준 X축)
- 페이지네이션

## 핵심 로직

### 1. 시간 표시 — UTC → 브라우저 로컬 변환
- 서버 응답의 UTC 시간(`2024-05-23T08:30:00Z`)을 브라우저 타임존에 맞춰 표시
- `date-fns`의 `format` + 브라우저 `Intl.DateTimeFormat` 활용

### 2. 다크/화이트 모드
- CSS 변수 기반 테마 전환
- `ThemeProvider` Context로 전역 상태 관리
- localStorage에 사용자 선택 저장

### 3. API 통신
- TanStack Query로 서버 상태 관리
- 센서 목록: 5초 간격 자동 리페치 (refetchInterval)
- 센서 데이터: 필터/페이지 변경 시 쿼리 키 갱신으로 자동 리페치
- 모드 변경: useMutation + 성공 시 센서 목록 invalidate

### 4. 반응형 UI
- 데스크탑: 테이블 레이아웃
- 모바일: 카드 레이아웃 또는 축소 테이블

## 사용 API 정리

| API | 용도 | 페이지 |
|---|---|---|
| `GET /api/v1/sensors` | 센서 목록 + 상태 | 센서 탭 |
| `PATCH /api/v1/sensors/{sn}/mode` | 모드 변경 | 센서 탭 |
| `GET /api/v1/sensor-data` | 데이터 조회 (필터+페이지네이션) | 센서 데이터 탭 |

## 검증 방법
1. 센서 목록 정상 표시, status별 색상 구분 확인
2. 모드 변경 → API 호출 → 목록 즉시 갱신 확인
3. 센서 데이터 필터링 (serial_number, mode, timestamp 기간, created_at 기간) 동작 확인
4. 페이지네이션 동작 확인
5. UTC 시간 → 브라우저 로컬 시간 변환 확인
6. 테이블/차트 뷰 전환 확인
7. 다크/화이트 모드 전환 확인
8. 모바일/데스크탑 반응형 확인

## 제출물 참고
- `frontend/README.md`에 상태 관리 및 컴포넌트 설계안 포함 (assignment.md 요구사항)
