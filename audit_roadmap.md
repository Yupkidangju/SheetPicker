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
- [ ] **[Core]** `src/core/scanner.py` 구현 (파일 순회)
- [ ] **[Core]** Excel/CSV 파일 로딩 로직 (Pandas/Openpyxl)
- [ ] **[Test]** 대용량 파일 로딩 시 메모리 사용량 체크
- [ ] **[Test]** 예외 처리 (파일 잠김, 권한 없음) 검증

### Phase 3: 검색 엔진 구현 (Step 3)
- [ ] **[Core]** `src/core/searcher.py` 구현
- [ ] **[Logic]** 행(Row) vs 열(Column) 검색 알고리즘 구현
- [ ] **[Logic]** 대소문자 구분 및 부분 일치 로직
- [ ] **[Thread]** QThread/Worker 패턴 적용 (UI 프리징 방지)

### Phase 4: 결과 UI 및 상호작용 (Step 4)
- [ ] **[UI]** `src/ui/widgets.py` - ResultTable 구현
- [ ] **[UI]** 검색 결과 데이터 바인딩 및 체크박스 기능
- [ ] **[UI]** 진행 상태 표시 (Status Bar / Progress)

### Phase 5: 클립보드 및 배포 (Step 5)
- [ ] **[Feat]** `src/utils/clipboard_manager.py` 구현
- [ ] **[Feat]** 선택 항목 클립보드 복사 기능
- [ ] **[Build]** Nuitka 빌드 테스트 및 실행 파일 생성

## 보안 및 규정 준수 감사
- [ ] **[License]** PySide6 (LGPL) 라이선스 고지 확인
- [ ] **[Privacy]** 클립보드 복사 시 민감 정보 경고 문구 확인
- [ ] **[Code]** 방어적 코딩 (Defensive Coding) 적용 여부 검토
