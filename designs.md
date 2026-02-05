# Data Scavenger 디자인 명세서 (Design Specifications)

## 1. 시스템 아키텍처 (ASCII)

```ascii
+-------------------------------------------------------+
|                   Main Window (UI)                    |
|  [ FileDropZone ] [ SearchGroup ] [ ResultTable ]     |
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
+-----------------------+           +-----------------------+
```

## 2. 컴포넌트 설계 상세

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
    * **최적화:** 정규식 매칭 전 데이터를 한 번에 문자열로 변환(`astype(str)`)합니다.

### 2.3. 스레딩 모델 (`src/core/workers.py`)
* **역할:** 무거운 I/O 및 CPU 작업 중 GUI가 멈추는(Freezing) 현상을 방지합니다.
* **메커니즘:** `QThread`를 상속받은 워커가 매칭 결과를 발견할 때마다 `result_found` 시그널을 방출하여 테이블을 실시간으로 업데이트합니다.

## 3. 구현 제약 사항 및 참고
* **Windows 호환성:** 경로 역슬래시 문제를 피하기 위해 `pathlib`을 사용해야 합니다.
* **파일 잠금:** Windows에서는 "File in use" 에러 방지를 위해 엑셀 파일을 명시적으로 닫아야 합니다.
* **UI 반응성:** 모든 무거운 작업은 워커 스레드에서 수행되어야 하며, 메인 스레드는 오직 UI 업데이트만 담당합니다.
