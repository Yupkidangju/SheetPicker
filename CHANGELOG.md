# 변경 이력 (CHANGELOG)

## [v0.1 BETA] - 2024-05-21
### 추가됨 (Added)
- **프로젝트 초기화:** `AGENTS.md` (구 `.julesrules`) 및 기본 문서 구조 생성.
- **문서:** `README.md` (다국어), `audit_roadmap.md` 생성.
- **문서:** `BUILD_GUIDE.md`, `IMPLEMENTATION_SUMMARY.md`, `DESIGN_DECISIONS.md`, `LESSONS_LEARNED.md` 생성.
- **규칙:** `.antigravityrules` 생성.
- **기능:** `Scanner` (File I/O) 및 `Searcher` (Pandas Logic) 코어 엔진 구현.
- **UI:** PySide6 기반 메인 윈도우, Drag & Drop, 결과 테이블 구현.
- **기능:** 검색 결과 클립보드 복사 (Privacy Warning 포함).

## [v1.0.0] - 2024-05-21 (Official Release)
### 주요 변경 사항 (Major Changes)
- **Data Scavenger 공식 릴리즈:** v0.x 베타 기간 동안 개발된 모든 기능 통합 및 안정화.
- **안정성 강화:** 로깅 시스템 도입, 단위 테스트 커버리지 확보, CI/CD 구축.
- **성능 최적화:** Nuitka 빌드 최적화 및 불필요한 패키지 정리.

### 기능 요약 (Features)
- **핵심 검색:** Excel/CSV 대용량 파일 고속 검색 (Pandas 3.0 기반).
- **고급 검색:** 정규식(Regex), 컬럼 타겟팅, 대소문자 구분.
- **편의성:** 검색 기록, 즐겨찾기 폴더, 다크 모드, 토스트 알림.
- **결과 활용:** 클립보드 복사, 엑셀/CSV 내보내기, 상세 보기, 파일 바로 열기.
- **시각화:** 검색어 하이라이팅 및 결과 내 실시간 필터링.

### 기술적 개선 (Technical)
- Python 3.12 + PySide6 기반 모던 아키텍처.
- Worker Thread 기반의 Non-freezing GUI.
- `ConfigManager`를 통한 사용자 설정 지속성 보장.

## [v1.0.1] - 2024-05-21 (Hotfix & i18n)
### 수정됨 (Fixed)
- **크리티컬 버그 수정:** 검색 결과 표시 중 `AttributeError: QCommonStyle` 발생 문제 해결 (PySide6 호환성).
- **기능 복구:** 위 오류로 인해 클립보드 복사 및 내보내기가 작동하지 않던 문제 해결.

### 추가됨 (Added)
- **다국어 지원 (i18n):** 한국어, English, 日本語, 繁體中文, 简体中文 지원. (View -> Language 메뉴)
- **편의성:** 결과 테이블 '모두 선택' (Select All) 버튼 추가.
