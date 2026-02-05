# 구현 요약 (Implementation Summary)

## 개요
본 문서는 **Data Scavenger** 프로젝트의 구현 현황을 요약합니다.

## 현재 상태 (v0.1 BETA)
* **초기화 단계:** 프로젝트 구조 및 기본 문서 생성 완료 (Phase 1 완료).
* **스캐너 엔진:** 파일 시스템 순회 및 Chunk 기반 대용량 파일 로더 구현 완료 (Phase 2 완료).
* **진행 중:** 검색 엔진 구현 (Phase 3) - Pandas 기반 행/열 검색 로직 개발.

## 주요 컴포넌트
* **Main Window:** PySide6 기반의 GUI 진입점.
* **Scanner:** `src/core/scanner.py` - `FileScanner` 클래스.
  - CSV (utf-8-sig), XLSX (read_only), XLS 지원.
  - Generator 기반 Chunk 처리로 메모리 최적화.
* **Searcher:** `src/core/searcher.py` (구현 중).
  - DataFrame 기반 고속 검색.
  - 행/열 모드 지원 (Transpose 활용).
