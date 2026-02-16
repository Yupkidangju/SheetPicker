# Data Scavenger 구현 명세 (Implementation Spec) v2.0.0

> **최종 갱신일:** 2026-02-17
> **문서 관리:** D3D Protocol 준수
> **프로젝트 상태:** v2.0.0 (대규모 리팩토링)

---

## 1. 프로젝트 개요
* **프로젝트명:** Data Scavenger
* **목적:** 대량의 Excel/CSV 파일에서 원하는 데이터를 빠르고 직관적으로 찾는 Windows 데스크톱 검색 도구.
* **대상 사용자:** 비개발자 사무직 (정규식·쿼리문 사용 금지)
* **현재 버전:** v2.0.0 (4계층 검색 엔진 + 인덱싱 기반)

## 2. 기술 스택 (2026-02 그라운딩)
* **Python:** 3.13+ (3.14 호환 준비)
* **GUI:** PySide6 >=6.10.0 (Qt 6)
* **데이터:** Pandas >=3.0.0 + PyArrow >=18.0.0
* **퍼지 매칭:** rapidfuzz >=3.6.0
* **BM25 랭킹:** rank_bm25 >=0.2.2
* **Excel I/O:** openpyxl >=3.1.5, xlrd >=2.0.1
* **캐시:** SQLite3 (내장)
* **빌드:** Nuitka >=4.0

## 3. 디렉토리 구조
```
SheetPicker/
├── src/
│   ├── main.py                 # 진입점
│   ├── core/
│   │   ├── scanner.py          # 파일 스캔/로드
│   │   ├── indexer.py          # 인덱스 구축 (Inverted/Chosung/BM25)
│   │   ├── searcher.py         # 다중 계층 검색 엔진
│   │   ├── jamo_utils.py       # 한글 자모 분해
│   │   ├── cache.py            # SQLite 캐시
│   │   └── workers.py          # QThread 워커 (인덱싱/검색)
│   ├── ui/
│   │   ├── main_window.py      # 메인 윈도우
│   │   ├── search_bar.py       # 구글 스타일 검색창
│   │   ├── file_tree.py        # 파일 트리 사이드바
│   │   ├── result_cards.py     # 카드 기반 결과 표시
│   │   ├── styles.py           # 다크/라이트 테마 QSS
│   │   └── toast.py            # 토스트 알림
│   └── utils/
│       ├── clipboard_manager.py
│       ├── config.py
│       ├── exporter.py         # xlsx/csv 내보내기
│       └── logger.py
├── tests/
├── build.py
├── requirements.txt
└── [문서 파일들]
```

## 4. 검색 아키텍처 (v2.0)
```
사용자 입력 → QueryParser → 4계층 동시 검색 → 결과 합산/랭킹 → UI 표시

계층 1: 정확 매칭 (Inverted Index) — 가중치 1.0
계층 2: 초성 검색 (Jamo Index)    — 가중치 0.85
계층 3: 퍼지 매칭 (rapidfuzz)     — 가중치 × 유사도
계층 4: BM25 랭킹                 — 관련도 가산점
```

## 5. D3D Protocol 적용
* §6: 문서 작성 한국어 (README 제외)
* §7: Git 허용 파일 3종 (README, CHANGELOG, BUILD_GUIDE) 외 .md 제외
* §8: 소스코드 주석 한국어, i18n 지원 (v2.1 예정)
* §9: 기능 추가/변경 시 연관 문서 즉시 동기화

## 6. .antigravityrules
```json
{
  "project_version": "2.0.0",
  "rule_concurrency": "PySide6에서는 반드시 QThread/Worker 패턴 사용",
  "rule_error_handling": "try/except 후 logger.error 기록, 사용자에게 토스트 표시",
  "rule_pandas": "Pandas 3.0 Copy-on-Write 시맨틱 준수, in-place 수정 금지",
  "rule_comment_language": "모든 소스코드 주석은 반드시 한국어로 작성 (D3D §8)",
  "rule_search": "사용자에게 정규식/쿼리문을 노출하지 않음. 내부 알고리즘으로만 처리",
  "rule_ui": "Windows 11 Fluent Design 기반, 복잡한 옵션 최소화"
}
```
