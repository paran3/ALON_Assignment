# Project: IoT 환경 데이터 모니터링 시스템

## 과제 명세
- `assignment.md` 참고

## 디렉토리 구조
- `backend/` - FastAPI 백엔드
- `frontend/` - React 프론트엔드
- `sensor/` - 가상 센서 (보류)

## 기술 스택 및 아키텍처
- **Backend**: FastAPI, 아키텍처는 [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) 참고
- **Frontend**: React, 데스크탑/모바일 반응형 UI/UX, best practice 준수
- **가상 센서**: 보류 (추후 백엔드 API로 데이터 전송용)

## 코딩 규칙
- 상수값은 최대한 Enum으로 정의하여 사용

## 작업 규칙
- 설계/디자인 패턴 선택 이유가 있으면 루트 `README.md`에 기록
- 각 디렉토리(`backend/`, `frontend/`, `sensor/`)마다 개별 `README.md` 유지
- `assignment.md`에 없는 추가 기능을 구현한 경우, 해당 디렉토리의 `README.md`에 기능과 이유를 기록
