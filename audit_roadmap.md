# 감사 및 구현 로드맵 (Audit Roadmap)

## 프로젝트 정보
* **프로젝트명:** Data Scavenger
* **현재 버전:** v0.1 BETA
* **목표 환경:** Windows Desktop (PySide6)

## 구현 마일스톤

### Phase 1: 초기화 및 기본 UI 구성 (Step 1)
- [x] **[Doc]** 프로젝트 문서 초기화 (README, CHANGELOG, etc.)
- [x] **[Env]** 가상환경 설정 및 `requirements.txt` 작성
- [x] **[UI]** PySide6 기반 메인 윈도우(Main Window) 스켈레톤 구현
- [x] **[UI]** 기본 레이아웃 및 위젯(FileDropZone, SearchGroup) 배치 확인

### Phase 2: 스캐너 엔진 구현 (Step 2)
- [x] **[Core]** `src/core/scanner.py` 구현 (파일 순회)
- [x] **[Core]** Excel/CSV 파일 로딩 로직 (Pandas/Openpyxl)
- [x] **[Test]** 대용량 파일 로딩 시 메모리 사용량 체크
- [x] **[Test]** 예외 처리 (파일 잠김, 권한 없음) 검증

### Phase 3: 검색 엔진 구현 (Step 3)
- [x] **[Core]** `src/core/searcher.py` 구현
- [x] **[Logic]** 행(Row) vs 열(Column) 검색 알고리즘 구현
- [x] **[Logic]** 대소문자 구분 및 부분 일치 로직
- [x] **[Thread]** QThread/Worker 패턴 적용 (Phase 4에서 통합 완료)

### Phase 4: 결과 UI 및 상호작용 (Step 4)
- [x] **[UI]** `src/ui/widgets.py` - Drag & Drop 이벤트 처리
- [x] **[Thread]** `src/core/workers.py` - SearchWorker 구현
- [x] **[UI]** Main Window - Worker 연결 및 결과 테이블 업데이트
- [x] **[UI]** 진행 상태 표시 (Status Bar / Progress)

### Phase 5: 클립보드 및 배포 (Step 5)
- [ ] **[Feat]** `src/utils/clipboard_manager.py` 구현
- [ ] **[Feat]** 선택 항목 클립보드 복사 기능
- [ ] **[Build]** Nuitka 빌드 테스트 및 실행 파일 생성

## 보안 및 규정 준수 감사
- [ ] **[License]** PySide6 (LGPL) 라이선스 고지 확인
- [ ] **[Privacy]** 클립보드 복사 시 민감 정보 경고 문구 확인
- [ ] **[Code]** 방어적 코딩 (Defensive Coding) 적용 여부 검토
