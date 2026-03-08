# Backend - IoT 환경 데이터 모니터링 시스템

## 기술 스택
- **Framework**: FastAPI
- **아키텍처**: [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) 기반

## 주요 기능
- 센서 데이터 수집 API (단일/배치 전송)
- 타임존 정규화 (UTC/KST 혼재 처리)
- 조회 API (시리얼 넘버, 모드, 기간별 필터링)
- 센서 상태 검증 (데이터 누락 판단)

## 센서 상태 검증 (APScheduler)
- 5초 간격으로 모든 센서의 `last_received_at`을 검사하여 데이터 누락(고장) 자동 감지
- NORMAL: 10분, EMERGENCY: 10초 주기 + 30초 허용치 초과 시 `MISSING` 처리
- API 호출 없이도 고장 센서를 놓치지 않기 위한 백그라운드 검사

## 실행 방법
> 추후 작성
