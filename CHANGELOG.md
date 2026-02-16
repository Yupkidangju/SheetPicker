# 변경 이력 (CHANGELOG)

이 프로젝트의 모든 주목할 만한 변경사항은 이 파일에 기록됩니다.
[Keep a Changelog](https://keepachangelog.com/ko/1.0.0/) 형식을 따르며,
[Semantic Versioning](https://semver.org/lang/ko/) 기준으로 버전을 관리합니다.

---

## [v2.0.0] - 2026-02-17 (대규모 리팩토링)

### 추가됨 (Added)
- **다중 계층 검색 엔진:** 4가지 검색 알고리즘 동시 실행 (정확/퍼지/초성/BM25)
- **한글 초성 검색:** `ㅎㄱㄷ` 입력 → `홍길동` 자동 매칭 (`jamo_utils.py`)
- **퍼지 매칭:** rapidfuzz 기반 오타 허용 검색 (유사도 슬라이더로 임계값 조절)
- **BM25 랭킹:** 관련도 기반 결과 정렬 (`rank_bm25`)
- **인덱싱 엔진:** Inverted Index + 초성 Index 사전 구축 → 이후 검색 <100ms
- **SQLite 캐시:** 파일 데이터 캐싱으로 앱 재시작 시 재로드 없이 인덱스 복원
- **숫자 범위 검색:** `10000~50000` 형식 지원
- **제외 검색:** `-키워드`로 불필요한 결과 필터링
- **AND 검색:** 공백으로 구분한 멀티 키워드 동시 매칭
- **파일 세트 즐겨찾기:** 파일 목록을 이름 붙여 저장/복원
- **카드 기반 결과 UI:** 파일/시트별 그룹핑, 매칭 유형 색상 태그
- **유사도 슬라이더:** 실시간 필터링 (40%~100%)
- **검색 결과 내보내기:** 체크된 항목만 or 전체를 xlsx/csv로 저장 (출처 메타 포함)

### 변경됨 (Changed)
- **UI 전면 개편:** Drop Zone → 파일 트리 사이드바 + 구글 스타일 단일 검색창
- **검색 엔진 재설계:** 단순 DataFrame 순회 → Inverted Index O(1) 조회
- **테마 시스템:** QPalette 기반 → 포괄적 QSS 기반 (다크/라이트)
- **프로젝트 버전:** v1.0.0 → v2.0.0

### 제거됨 (Removed)
- 행/열 전환 라디오 버튼 (내부적으로 자동 처리)
- 정규식 체크박스 (사용자에게 불필요한 복잡성)
- 컬럼 타겟팅 입력 (불필요 — AND 검색으로 대체)
- `widgets.py` (search_bar, file_tree, result_cards로 분리)

### 기술적 변경 (Technical)
- 신규 의존성: `rapidfuzz>=3.6.0`, `rank_bm25>=0.2.2`
- 신규 파일: `jamo_utils.py`, `indexer.py`, `cache.py`, `search_bar.py`, `file_tree.py`, `result_cards.py`
- 재작성: `searcher.py`, `workers.py`, `main_window.py`, `styles.py`, `exporter.py`

---

## [v1.0.0] - 2026-02-17 (공식 릴리즈 / 문서 동기화)

### 변경됨 (Changed)
- D3D Protocol 기준 전 문서 동기화
- 기술 스택 현행화 (PySide6 6.10+, Pandas 3.0+, Nuitka 4.0+)
- `.gitignore` D3D Protocol §7 규칙 적용

---

## [v0.1 BETA] - 2024-05-21

### 추가됨 (Added)
- 프로젝트 초기화 및 전체 기능 구현
- Scanner, Searcher, Worker 코어 엔진
- PySide6 기반 GUI (드래그&드롭, 결과 테이블, 클립보드 복사)
