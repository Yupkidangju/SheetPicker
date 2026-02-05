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
- [x] **[Thread]** QThread/Worker 패턴 적용

### Phase 4: 결과 UI 및 상호작용 (Step 4)
- [x] **[UI]** `src/ui/widgets.py` - Drag & Drop 이벤트 처리
- [x] **[Thread]** `src/core/workers.py` - SearchWorker 구현
- [x] **[UI]** Main Window - Worker 연결 및 결과 테이블 업데이트
- [x] **[UI]** 진행 상태 표시 (Status Bar / Progress)

### Phase 5: 클립보드 및 배포 (Step 5)
- [x] **[Feat]** `src/utils/clipboard_manager.py` 구현
- [x] **[Feat]** 선택 항목 클립보드 복사 기능
- [x] **[Build]** Nuitka 빌드 테스트 및 실행 파일 생성

## 보안 및 규정 준수 감사
- [x] **[License]** PySide6 (LGPL) 라이선스 고지 확인
- [x] **[Privacy]** 클립보드 복사 시 민감 정보 경고 문구 확인
- [x] **[Code]** 방어적 코딩 (Defensive Coding) 적용 여부 검토

### Phase 6: 기능 확장 및 편의성 개선 (v0.2) (Step 6)
- [x] **[Core]** 정규표현식(Regex) 검색 지원 추가
- [x] **[UI]** 검색어 입력창을 `QComboBox`로 교체하여 히스토리 기능 구현
- [x] **[UI]** 결과 테이블 우클릭 메뉴 구현 (파일 열기, 폴더 열기)
- [x] **[UI]** 결과 항목 더블 클릭 시 상세 보기(Detail View) 팝업 구현
- [x] **[Feat]** 검색 결과 파일 내보내기 (Export to Excel/CSV) 구현
- [x] **[Doc]** `designs.md` 및 `README.md` 기능 설명 업데이트

### Phase 7: 고도화 및 UX 오버홀 (v0.3) (Step 7)
- [x] **[Core]** 컬럼 타겟팅(Column Targeting) 로직 구현 (`searcher.py`)
- [x] **[UI]** 키워드 하이라이팅 (HTML Delegate) 구현
- [x] **[UI]** 결과 내 실시간 필터링 (ProxyModel) 구현
- [x] **[Feat]** 설정 관리자 (`ConfigManager`) 및 즐겨찾기(Favorites) 기능
- [x] **[UX]** 다크 모드/테마 (QSS) 및 아이콘 UI 적용
- [x] **[UX]** Non-blocking Toast Message 알림 구현
- [x] **[Doc]** 디자인 문서 및 사용자 가이드 최신화

### Phase 8: 안정화 및 배포 후보 (v1.0 RC) (Step 8)
- [x] **[Log]** 구조화된 로깅 시스템 도입 (`logging` 모듈 전환)
- [x] **[Test]** 주요 로직에 대한 단위 테스트 (Unit Tests) 커버리지 80% 달성
- [ ] **[Test]** 통합 테스트 (Integration Tests) 및 시나리오 검증
- [x] **[CI/CD]** GitHub Actions를 통한 자동 빌드 및 테스트 워크플로우 구성
- [ ] **[Build]** Nuitka 최적화 옵션을 적용한 최종 실행 파일 빌드
- [ ] **[Doc]** 최종 사용자 매뉴얼 및 배포 가이드 작성
