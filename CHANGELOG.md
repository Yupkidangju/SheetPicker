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

## [v0.2 BETA] (Upcoming)
### 추가됨 (Added)
- **기능:** 정규표현식(Regex) 검색 지원.
- **UI:** 검색 기록 (History) 저장 및 불러오기 (`QComboBox`).
- **UI:** 결과 테이블 더블 클릭 시 전체 데이터 상세 보기 (`DetailDialog`).
- **UI:** 결과 테이블 우클릭 메뉴 (파일 열기, 폴더 위치 열기).
- **기능:** 검색 결과 Excel(.xlsx) 및 CSV(.csv) 내보내기.
