# Data Scavenger 디자인 명세서 (Design Specifications) v1.0.0

> **최종 갱신일:** 2026-02-17
> **문서 관리:** D3D Protocol §6 (DESIGNS_REFERENCE / DESIGNS_CONTENT_SPEC) 준수

---

## 1. 시스템 아키텍처 (ASCII)

```ascii
+---------------------------------------------------------------+
|                     Main Window (UI Layer)                     |
|  +-------------------+  +----------------------------+        |
|  |  FavoritesPanel   |  |  FileDropZone              |        |
|  |  (즐겨찾기 관리)  |  |  (Drag & Drop 파일 입력)   |        |
|  +-------------------+  +----------------------------+        |
|  +--------------------------------------------------------+   |
|  |  SearchGroup                                            |   |
|  |  [Row/Col Radio] [Case☑] [Regex☑] [TargetCol Input]   |   |
|  |  [SearchHistory ComboBox] [🔍 Search Button]           |   |
|  +--------------------------------------------------------+   |
|  +--------------------------------------------------------+   |
|  |  ResultFilter (결과 내 실시간 필터링)                   |   |
|  +--------------------------------------------------------+   |
|  +--------------------------------------------------------+   |
|  |  ResultTable (검색 결과 테이블)                         |   |
|  |  [☑] [File] [Sheet] [Preview] ← HTMLDelegate 렌더링   |   |
|  |  - 더블클릭 → DetailDialog                              |   |
|  |  - 우클릭 → 파일열기/폴더열기                           |   |
|  +--------------------------------------------------------+   |
|  [📋 COPY TO CLIPBOARD]  [📤 EXPORT RESULTS]  [🌙 THEME]     |
|  +--------------------------------------------------------+   |
|  |  ToastMessage (비동기 알림 / 하단 Fade-In/Out)         |   |
|  +--------------------------------------------------------+   |
+-------------------------------+-------------------------------+
                                |
               (Signals)        v        (Slots)
+---------------------------------------------------------------+
|                   SearchWorker (QThread)                       |
|         - 파일 순회 → Chunk 로딩 → 검색 → 결과 방출          |
|         - result_found / progress_updated / error_occurred     |
+-------------------------------+-------------------------------+
                                |
          +---------------------+---------------------+
          |                                           |
          v                                           v
+--------------------------+           +--------------------------+
|   FileScanner (Core)     |           |   DataSearcher (Core)    |
| - Recursive Scan         |           | - DataFrame Search       |
| - Chunk Loader           |           | - Transpose Logic (행/열)|
| - openpyxl read_only     |           | - Case Sensitivity       |
| - try/finally 리소스 관리|           | - Regex Support          |
| - .xlsx/.xls/.csv 지원   |           | - Column Targeting       |
+--------------------------+           | - astype(str) 최적화     |
                                       +--------------------------+
          +---------------------+---------------------+
          |                     |                     |
          v                     v                     v
+----------------+   +-----------------+   +------------------+
| ClipboardMgr   |   | ConfigManager   |   | ResultExporter   |
| TSV 포맷팅     |   | JSON 설정 저장  |   | xlsx/csv 내보내기|
| pyperclip 복사 |   | 테마/즐겨찾기   |   | Pandas DataFrame |
+----------------+   | /검색기록 관리  |   +------------------+
                      +-----------------+
                              |
                              v
                      +----------------+
                      | Logger         |
                      | RotatingFile   |
                      | 5MB × 3 백업  |
                      +----------------+
```

## 2. 컴포넌트 설계 상세 (v1.0.0)

### 2.1. 파일 스캐너 (`src/core/scanner.py`)
* **역할:** 지원되는 파일 포맷(`.xlsx`, `.xls`, `.csv`)을 탐지하고 안전하게 로드합니다.
* **주요 로직:**
    * **메모리 안전성:** `.xlsx` 파일은 `openpyxl(read_only=True)`를 사용하여 전체를 RAM에 올리지 않고 데이터를 스트리밍합니다.
    * **리소스 관리:** 반복이 중단되더라도 파일 핸들이 닫히도록 `try...finally` 구문을 구현했습니다.
    * **Chunk 로딩:** `chunksize` 파라미터로 한 번에 읽는 행 수를 제한하여 대용량 파일 처리가 가능합니다.
    * **CSV 인코딩:** `utf-8-sig` 기본 인코딩으로 한글 깨짐을 방지합니다.
* **구현 주의사항:**
    * Windows 환경에서 파일 잠김 현상 방지를 위해 `finally` 블록에서 `wb.close()` 필수 호출.
    * `os.walk` 사용 시 `pathlib.Path`로 감싸서 경로 호환성 확보.

### 2.2. 검색 엔진 (`src/core/searcher.py`)
* **역할:** DataFrame 내에서 고속 텍스트 검색을 수행합니다.
* **주요 로직:**
    * **행 모드 (Row Mode):** 표준적인 `df.apply(...)` 방식을 사용합니다.
    * **열 모드 (Column Mode):** DataFrame을 전치(`df.T`)하여 매칭된 열이 결과 셋에서 행이 되도록 합니다.
    * **정규식 (Regex):** 사용자가 정규식 옵션을 켤 경우 `str.contains(regex=True)`를 사용하여 패턴 매칭을 수행합니다.
    * **컬럼 타겟팅:** `target_columns` 리스트를 전달하여 특정 헤더 이름을 가진 컬럼만 검색 대상으로 한정합니다.
    * **최적화:** 정규식 매칭 전 데이터를 한 번에 문자열로 변환(`astype(str)`)합니다.
* **구현 주의사항:**
    * Pandas 3.0 Copy-on-Write 시맨틱에 유의하여 in-place 수정 지양.
    * 정규식 오류 시 빈 결과 반환으로 크래시 방지 (Defensive Coding).

### 2.3. 스레딩 모델 (`src/core/workers.py`)
* **역할:** 무거운 I/O 및 CPU 작업 중 GUI가 멈추는(Freezing) 현상을 방지합니다.
* **메커니즘:** `QThread`를 상속받은 `SearchWorker`가 매칭 결과를 발견할 때마다 `result_found` 시그널을 방출하여 테이블을 실시간으로 업데이트합니다.
* **시그널 정의:**
    * `result_found(dict)` — 검색 결과 1건 발견 시
    * `progress_updated(str)` — 진행 상태 메시지
    * `error_occurred(str)` — 에러 발생 시 (파일 단위, 전체 중단하지 않음)
    * `finished_task()` — 작업 완료 시

### 2.4. UI 인터랙션 (v0.2 → v1.0)
* **검색 기록 (History):** `QLineEdit` 대신 `QComboBox`를 사용하여 최근 성공한 검색어 10개를 저장/로드합니다.
* **결과 상호작용:**
    * **더블 클릭:** `DetailDialog` 팝업을 띄워 해당 행의 전체 데이터를 Grid 형태로 표시합니다.
    * **우클릭 메뉴:** '파일 열기' 및 '폴더 열기' 기능을 제공하여 탐색기 연동성을 강화합니다.
* **내보내기 (Export):** 클립보드 복사 외에 결과를 `.xlsx` 또는 `.csv` 파일로 저장하는 기능을 제공합니다.

### 2.5. 고도화 기능 및 UX 개선 (v0.3 → v1.0)
* **키워드 하이라이팅 (Highlighting):** `QStyledItemDelegate` 기반 `HTMLDelegate`를 사용하여 검색 키워드를 시각적으로 강조합니다.
* **결과 내 재검색 (Result Filter):** `setRowHidden`을 활용한 간이 필터링으로, 검색 결과 테이블 상단에 로컬 필터링 바를 제공합니다.
* **자주 쓰는 경로 (Favorites):** `ConfigManager` (JSON 기반)를 통해 자주 검색하는 폴더 경로를 저장하고, UI에서 원클릭으로 `FileDropZone`에 추가합니다.
* **컬럼 타겟팅 (Column Targeting):** `DataSearcher`에 `target_columns` 리스트를 전달하여, 특정 헤더의 컬럼만 검색 대상으로 한정합니다.
* **테마 및 디자인 (Theme/UX):**
    * **Dark Mode:** `QPalette` 및 QSS를 활용하여 다크 모드를 지원합니다. (`AppStyle` 클래스)
    * **Light Mode:** Windows 11 Fluent 디자인 가이드를 모방한 라이트 모드입니다.
    * **Toast Message:** 하단에서 떠오르는 비동기 알림 위젯(`ToastMessage`). QPropertyAnimation Fade In/Out.

### 2.6. 안정화 인프라 (v1.0)
* **로깅 시스템:** `logging` 모듈 기반, `RotatingFileHandler`(5MB × 3 백업). 콘솔과 파일 동시 출력.
* **단위 테스트:** `tests/` 디렉토리에 4종 테스트 (scanner, searcher, workers, clipboard). 헤드리스 환경 대응(`unittest.mock`).
* **CI/CD:** GitHub Actions 워크플로우 (`ubuntu-latest`, Python 3.12). `QT_QPA_PLATFORM=offscreen` 설정.
* **빌드 스크립트:** `build.py` — Nuitka 4.0 기반, `--standalone --onefile` 옵션.

## 3. 구현 제약 사항 및 참고
* **Windows 호환성:** 경로 역슬래시 문제를 피하기 위해 `pathlib`을 사용해야 합니다.
* **파일 잠금:** Windows에서는 "File in use" 에러 방지를 위해 엑셀 파일을 명시적으로 닫아야 합니다.
* **UI 반응성:** 모든 무거운 작업은 워커 스레드에서 수행되어야 하며, 메인 스레드는 오직 UI 업데이트만 담당합니다.
* **Pandas 3.0 Copy-on-Write:** 기본 활성화되므로 `df.iloc[...]` 등의 in-place 수정 패턴에 주의해야 합니다.
