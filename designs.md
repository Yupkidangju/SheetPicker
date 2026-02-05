# 📑 Data Scavenger: Integrated Master Blueprint (v0.1 BETA)

## 1. Project Identity & Governance

* **Project Name:** Data Scavenger
* **Current Version:** v0.1 BETA
* **Target Environment:** Jules (Agent-first IDE), Windows Desktop (10/11/12)
* **Priority Rule:** 문서 업데이트는 소스코드 작성보다 우선하며, 모든 변경 사항은 본 문서에 즉시 반영되어야 합니다.

---

## 2. Tech Stack & Directory Structure

* **Language & Framework:** Python 3.12+, PySide6 (Qt 6.x), Pandas 3.0.0+ (pyarrow).
* **Core Libraries:** `openpyxl`, `xlrd`, `pyperclip`, `nuitka`.
* **Directory Logic:**
* `src/core/`: 검색/스캔 엔진 격리.
* `src/ui/`: `main_window.py` 및 커스텀 `widgets.py` 배치.
* `src/utils/`: 클립보드 포맷팅 전담.



---

## 3. UI/UX Design & Widget Specification

### 3.1. Main Layout Wireframe

```text
+-----------------------------------------------------------------------+
|  Data Scavenger v0.1 BETA  [ - ] [ □ ] [ X ]                          |
+-----------------------------------------------------------------------+
| [!] System Status: Ready to Scan (or Error Log: File 'A.xlsx' Locked) |
+-----------------------------------------------------------------------+
|                                                                       |
|  [ Drop Files/Folders Here ]                                          |
|  +-----------------------------------------------------------------+  |
|  | C:\Users\Admin\Documents\Project_Alpha\Data_2026.xlsx       [X] |  |
|  | D:\Legacy_Records\Archived_CSV_01.csv                       [X] |  |
|  +-----------------------------------------------------------------+  |
|                                                                       |
|  Search Strategy:                                                     |
|  ( ) Search by Row   (*) Search by Column      [v] Case Sensitive     |
|                                                                       |
|  +--------------------------------------------+    +---------------+  |
|  | Enter search keyword...                    |    |   [ SEARCH ]  |  |
|  +--------------------------------------------+    +---------------+  |
|                                                                       |
+-----------------------------------------------------------------------+
|  Results Index:                                                       |
|  +-----+------------+-------------+--------------------------------+  |
|  | [X] | Source     | Sheet       | Preview (Row Data)             |  |
|  +-----+------------+-------------+--------------------------------+  |
|  | [v] | Data_2026  | Sales_Q1    | 2026-02-01 | Samsung | 100...  |  |
|  +-----+------------+-------------+--------------------------------+  |
|                                                                       |
+-----------------------------------------------------------------------+
|  [ Selected: 2 items ]                        [ COPY TO CLIPBOARD ]   |
+-----------------------------------------------------------------------+

```

### 3.2. Detailed Widget Implementation Map

| Class Name | Component | Type | Description |
| --- | --- | --- | --- |
| `MainWindow` | `lbl_status` | `QLabel` | 상단 상태 알림 (에러 시 배경색 변경). |
| `FileDropZone` | `list_files` | `QListWidget` | 파일 경로 리스트 및 개별 삭제([X]) 버튼. |
| `SearchGroup` | `btn_search` | `QPushButton` | 검색 실행. 클릭 시 스레드 가동. |
| `ResultTable` | `table_results` | `QTableWidget` | 체크박스 + 출처 + 시트 + 데이터 미리보기 열 구성. |
| `CopyAction` | `btn_copy` | `QPushButton` | 선택된 행의 텍스트 클립보드 복사. |

---

## 4. Functional Logic & Operational Rules

### 4.1. Core Threading Strategy

* **Anti-Freezing:** 대용량 데이터 로딩 시 GUI 멈춤을 방지하기 위해 `QThread`와 Worker 패턴을 필수 적용합니다.
* **Signal Path:** `Worker.result_found` -> `MainWindow.update_table` 방식으로 실시간 결과 행을 추가합니다.

### 4.2. Constraints & Safety

* **Memory Guard:** 1GB 초과 파일은 `chunksize` 옵션을 사용하여 메모리 폭주를 방지합니다.
* **Fault Tolerance:** 파일 잠김 등 에러 발생 시 해당 파일은 건너뛰고 상단 알림 바에 기록합니다.
* **Security:** 클립보드 복사 전 민감 정보 포함 가능성에 대한 경고 안내를 UI에 포함합니다.

---

## 5. Interaction Flow & Roadmap

### 5.1. User Journey

1. **Load:** 파일/폴더 드롭.
2. **Set:** 검색 옵션(행/열, 대소문자) 선택.
3. **Search:** 키워드 입력 후 검색(비동기 처리).
4. **Action:** 결과 체크 후 클립보드 복사.

### 5.2. Implementation Steps

* **Step 1:** PySide6 기반 Fluent Design 메인 창 및 드롭 존 UI 구현.
* **Step 2:** `core/scanner.py`를 이용한 파일 트리 순회 기능 완성.
* **Step 3:** Pandas 기반 행/열 검색 엔진 및 스레드 워커 연결.
* **Step 4:** 멀티 체크박스가 포함된 결과 테이블 및 클립보드 기능 통합.

---

## 6. Project Persona (Jules' Identity)

당신은 **15년차 데이터 시스템 아키텍트**로서, 구현 속도보다 **사양과의 100% 정합성**과 **방어적 코딩(Defensive Coding)**을 최우선으로 합니다. 모든 단계 완료 후 자가 검증을 수행하십시오.


**Next Step:** 이제 이 **완전 통합 문서**를 기반으로 개발을 시작할 모든 준비가 끝났습니다. 첫 번째 단계인 **`src/ui/widgets.py`에서 `FileDropZone`과 기본 레이아웃 코드 작성**부터 진행해 드릴까요?