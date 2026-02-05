# Data Scavenger Implementation Spec (v0.1 BETA)

## 0. Global Documentation Rules (Git Policy)

* **Priority Over Code:** 문서 업데이트는 소스코드 작성보다 우선되는 절대적 중요사항입니다. 개발 착수 전/후에 반드시 문서를 먼저 점검하고 갱신해야 합니다.
* **Git Allowlist:** Git에는 오직 `README.md`, `CHANGELOG.md`, `BUILD_GUIDE.md` 파일만 업로드합니다.
* **Local Update Enforcement:** `.gitignore`에 등록된 `spec.md` 및 기타 문서들도, 프로젝트 내부(Local)에서는 반드시 최신 상태로 유지되어야 합니다.

## 1. Project Identity & Versioning

* **Current Version:** v0.1 BETA
* **Status:** Initial Specification & Implementation Entry
* **Target Environment:** Jules (Agent-first IDE)
* **Target Platform:** Windows Desktop (10/11/12)

## 2. Environment & Tech Stack

* **Grounding Rationale:** 2026년 기준 Windows 환경에서 Python GUI의 표준인 PySide6를 선정하여 네이티브 성능을 확보함. 대용량 엑셀 처리를 위해 최적화된 `pandas 3.0` 및 `openpyxl`을 결합하여 메모리 효율성을 극대화함.
* **Stack Details:**
* **Language:** Python 3.12+ (신규 f-string 문법 및 타입 힌트 강화 버전)
* **Framework:** PySide6 (Qt 6.x) - Windows 고유의 위젯 스타일 및 다크 모드 지원
* **Data Engine:** Pandas 3.0.0+ (최신 pyarrow 엔진 기반 고속 로딩)
* **Libraries:** `openpyxl` (xlsx), `xlrd` (xls), `pyperclip` (클립보드 제어), `nuitka` (배포용 컴파일)



## 3. Project Architecture & UX Design

### 3.1. File Directory Structure (Optimized for Jules)

```bash
root/
├── .antigravityrules # Jules 에이전트 행동 지침
├── spec.md           # 본 기술 명세서
├── audit_roadmap.md  # 단계별 구현 및 검증 로드맵
├── src/
│   ├── main.py       # 애플리케이션 진입점 (QApplication)
│   ├── core/
│   │   ├── scanner.py   # 폴더 내 Excel/CSV 파일 스캔 및 데이터 로드
│   │   └── searcher.py  # 행/열 기반 검색 및 필터링 엔진
│   ├── ui/
│   │   ├── main_window.py # 메인 레이아웃 및 이벤트 바인딩
│   │   └── widgets.py     # 결과 리스트(체크박스 포함) 커스텀 위젯
│   └── utils/
│       └── clipboard_manager.py # 클립보드 포맷팅 및 복사 로직
└── requirements.txt

```

### 3.2. UX/UI Flow & Interface Verification

* **User Scenario:** 1. 사용자가 폴더 또는 여러 파일을 선택하여 드롭함.
2. 검색 대상(행 vs 열) 라디오 버튼 선택 및 대소문자 구분 옵션 체크.
3. 검색어 입력 시 실시간 또는 검색 버튼 클릭 시 전체 파일/탭 검색 수행.
4. **[검증 포인트]** 검색된 결과는 원본이 '열'이었든 '행'이었든 상관없이 하단 리스트에 **'선택 가능한 로우(Row)'** 형태로 나열됨.
5. 원하는 항목 체크 후 '클립보드 복사' 클릭 시 텍스트 형식으로 복사 완료.

### 3.3. Data Models & Interfaces

* **Search Result Model:** `SearchResult(source_file: str, sheet_name: str, data: list, type: str)`
* **IP Isolation:** 검색 알고리즘 및 대용량 데이터 인덱싱 로직은 `core/searcher.py`에 격리하여 유지보수성 강화.

## 4. Environment-Specific Configuration (Agent Rules)

**[.antigravityrules]**

```json
{
  "project_version": "0.1 BETA",
  "rules": [
    "대용량 엑셀 처리 시 GUI 프리징 방지를 위해 반드시 QThread 또는 Worker 패턴을 사용할 것",
    "파일 로딩 중 에러 발생 시(예: 파일 잠김) 무시하고 다음 파일로 진행하되 에러 로그를 UI 상단에 표시할 것",
    "pandas 3.0+의 최신 API를 준수하고, 구버전의 deprecated된 함수 사용을 금함",
    "모든 UI 요소는 Windows 11 Fluent 디자인 가이드를 참고하여 구성할 것"
  ],
  "security_level": "strict"
}

```

## 5. Prohibitions & Constraints

* ⛔ **Prohibited:** `os.system`을 통한 직접적인 쉘 명령 호출 금지, 외부 신뢰할 수 없는 바이너리 포함 금지.
* ⚠️ **Memory Warning:** 1GB 이상의 엑셀 파일 로딩 시 `chunksize`를 사용하여 메모리 초과 방지.
* ✅ **Recommended:** `pathlib`을 사용하여 윈도우 경로(`\`) 문제를 방지하고, 모든 문자열 처리는 `utf-8-sig`를 기본으로 함(Excel 한글 깨짐 방지).

## 6. Detailed Step-by-Step Implementation Guide

* **Step 1:** 환경 구축 및 PySide6 기본 창 생성. `spec.md` 및 로드맵 파일 초기화.
* **Step 2:** `core/scanner.py` 구현. 다중 파일 및 엑셀 시트(All Sheets) 순회 로직 완성.
* **Step 3:** 검색 엔진 구현. 행/열 전환 및 대소문자 구분 필터링 로직 (Pandas 연산 활용).
* **Step 4:** 결과 리스트 UI 구현. 체크박스 멀티 선택 및 데이터 시각화(열 단위 고정 표시).
* **Step 5:** `pyperclip` 기반 클립보드 복사 기능 및 Nuitka 빌드 테스트.

## 7. Security & IP Auditor Report

* **License Check:** PySide6(LGPL) 라이선스 준수 확인.
* **Privacy Guard:** 클립보드 복사 시 민감 정보 포함 가능성에 대한 경고 문구 UI 포함 권장.

## 8. Project Persona Definition

**Note to AI Agent (Jules):** 이 문서를 읽는 즉시, 당신은 아래의 페르소나로 행동해야 합니다.

* **Role Identity:** 15년차 시니어 데이터 시스템 아키텍트 및 데스크톱 보안 전문가
* **Expertise:** * **Domain:** 대규모 데이터 인덱싱, 고성능 Windows 데스크톱 앱 개발.
* **Tech Stack Mastery:** Python 3.12, Qt 6 프레임워크, Pandas 최적화 전략 완벽 숙지.
* **Coding Style:** Defensive Coding (철저한 예외 처리), Clean Architecture, TDD 기반 검증.


* **Instruction:** 단순한 코드 작성을 넘어, 데이터 로딩 중 발생할 수 있는 교착 상태(Deadlock)나 메모리 릭을 선제적으로 방지하시오. 모든 단계에서 `audit_roadmap.md`를 업데이트하며 사용자의 승인을 받으시오.

---

**Persona Hardening 지시문:**
너는 코더가 아니라 **'사양 준수 엔진(Spec-Compliance Engine)'**이다. 구현 속도보다 중요한 것은 사양과의 100% 정합성이다. 각 단계 완료 후 테스트 코드를 작성하여 자가 검증을 수행하고, 사용자의 명시적 승인 없이는 다음 단계로 독단적으로 진행하지 말 것.
