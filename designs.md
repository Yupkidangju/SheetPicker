# Data Scavenger 디자인 명세서 (Design Specifications)

## 1. 시스템 아키텍처 (ASCII)

```ascii
+-------------------------------------------------------+
|                   Main Window (UI)                    |
|  [ FavoritesPanel ] [ FileDropZone ]                  |
|  [ SearchGroup (TargetCol/Regex/Hist) ]               |
|  [ ResultFilter ] [ ResultTable (Highlighting) ]      |
|          [ ToastMessage Area ]                        |
+---------------------------+---------------------------+
                            |
           (Signals)        v        (Slots)
+-------------------------------------------------------+
|                 SearchWorker (Thread)                 |
|       - Iterates Files -> Chunks Data -> Search       |
+---------------------------+---------------------------+
                            |
        +-------------------+-------------------+
        |                                       |
        v                                       v
+-----------------------+           +-----------------------+
|  FileScanner (Core)   |           |  DataSearcher (Core)  |
| - Recursive Scan      |           | - DataFrame Search    |
| - Chunk Loader        |           | - Transpose Logic     |
| - Resource Mgmt       |           | - Case Sensitivity    |
+-----------------------+           | - Regex Support       |
                                    | - Column Targeting    |
                                    +-----------------------+
```

## 2. 컴포넌트 설계 상세 (v0.3 Update)

### 2.1. 파일 스캐너 (`src/core/scanner.py`)
* **역할:** 지원되는 파일 포맷(`.xlsx`, `.xls`, `.csv`)을 탐지하고 안전하게 로드합니다.
* **주요 로직:**
    * **메모리 안전성:** `.xlsx` 파일은 `openpyxl(read_only=True)`를 사용하여 전체를 RAM에 올리지 않고 데이터를 스트리밍합니다.
    * **리소스 관리:** 반복이 중단되더라도 파일 핸들이 닫히도록 `try...finally` 구문을 구현했습니다.

### 2.2. 검색 엔진 (`src/core/searcher.py`)
* **역할:** DataFrame 내에서 고속 텍스트 검색을 수행합니다.
* **주요 로직:**
    * **행 모드 (Row Mode):** 표준적인 `df.apply(...)` 방식을 사용합니다.
    * **열 모드 (Column Mode):** DataFrame을 전치(`df.T`)하여 매칭된 열이 결과 셋에서 행이 되도록 합니다.
    * **정규식 (Regex):** 사용자가 정규식 옵션을 켤 경우 `str.contains(regex=True)`를 사용하여 패턴 매칭을 수행합니다.
    * **최적화:** 정규식 매칭 전 데이터를 한 번에 문자열로 변환(`astype(str)`)합니다.

### 2.3. 스레딩 모델 (`src/core/workers.py`)
* **역할:** 무거운 I/O 및 CPU 작업 중 GUI가 멈추는(Freezing) 현상을 방지합니다.
* **메커니즘:** `QThread`를 상속받은 워커가 매칭 결과를 발견할 때마다 `result_found` 시그널을 방출하여 테이블을 실시간으로 업데이트합니다.

### 2.4. UI 인터랙션 확장 (v0.2)
* **검색 기록 (History):** `QLineEdit` 대신 `QComboBox`를 사용하여 최근 성공한 검색어 10개를 저장/로드합니다.
* **결과 상호작용:**
    * **더블 클릭:** `DetailDialog` 팝업을 띄워 해당 행의 전체 데이터를 Grid 형태로 표시합니다.
    * **우클릭 메뉴:** '파일 열기' 및 '폴더 열기' 기능을 제공하여 탐색기 연동성을 강화합니다.
* **내보내기 (Export):** 클립보드 복사 외에 결과를 `.xlsx` 또는 `.csv` 파일로 저장하는 기능을 제공합니다.

### 2.5. 고도화 기능 및 UX 개선 (v0.3)
* **키워드 하이라이팅 (Highlighting):** `QStyledItemDelegate`를 사용하여 검색된 키워드를 `<b><font color='red'>...</font></b>` 태그로 렌더링하여 시각적으로 강조합니다.
* **결과 내 재검색 (Result Filter):** `QSortFilterProxyModel`을 도입하여, 검색 결과 테이블 상단에 로컬 필터링 바를 제공합니다. DB 재검색 없이 결과 내에서 즉시 필터링합니다.
* **자주 쓰는 경로 (Favorites):** `src/utils/config.py` (JSON 기반)를 통해 자주 검색하는 폴더 경로를 저장하고, UI에서 원클릭으로 `FileDropZone`에 추가합니다.
* **컬럼 타겟팅 (Column Targeting):** `DataSearcher`에 `target_columns` 리스트를 전달하여, 특정 헤더 이름을 가진 컬럼만 검색 대상으로 한정합니다.
* **테마 및 디자인 (Theme/UX):**
    * **Dark Mode:** `QApplication.setPalette` 또는 QSS를 활용하여 다크 모드를 지원합니다.
    * **Toast Message:** `QMessageBox`의 차단을 피하기 위해, 하단에서 떠오르는 비동기 알림 위젯(`Toast`)을 구현합니다.
    * **Icons:** 텍스트 버튼을 직관적인 아이콘 버튼으로 대체하거나 병행 표기합니다.

## 3. 구현 제약 사항 및 참고
* **Windows 호환성:** 경로 역슬래시 문제를 피하기 위해 `pathlib`을 사용해야 합니다.
* **파일 잠금:** Windows에서는 "File in use" 에러 방지를 위해 엑셀 파일을 명시적으로 닫아야 합니다.
* **UI 반응성:** 모든 무거운 작업은 워커 스레드에서 수행되어야 하며, 메인 스레드는 오직 UI 업데이트만 담당합니다.
