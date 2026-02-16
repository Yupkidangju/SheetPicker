# 설계 결정 사항 (Design Decisions)

> **최종 갱신일:** 2026-02-17
> **문서 관리:** D3D Protocol §6, §9 (on_architecture_change) 준수

---

## 1. 기술 스택 선정 이유

### Python 3.13+ (3.14 호환 준비)
* **이유:** Windows 데스크톱 환경에서의 네이티브 호환성과 개발 생산성 고려.
* **이점:** 최신 Python 문법 활용 (타입 힌트 강화, f-string 개선). 3.14 정식 릴리즈(2026-02) 시 즉시 전환 가능.
* **결정 근거:** 2026년 2월 기준 Python 3.14.3 안정 버전 존재. 단, PySide6 6.10 호환성이 3.14를 지원하므로 점진적 전환 가능.

### PySide6 6.10+ (Qt 6.x)
* **이유:** Qt 6의 강력한 크로스 플랫폼 UI 프레임워크. LGPL 라이선스로 상업적 사용 가능.
* **이점:** Windows 11 Fluent 스타일 모방 용이, 다크 모드 네이티브 지원, Python 3.14 호환.
* **대안 검토:** PyQt6 대비 라이선스 유연성에서 우위.

### Pandas 3.0.0+ & PyArrow
* **이유:** 대용량 엑셀/CSV 데이터의 고속 처리를 위해 선정.
* **이점:** Copy-on-Write(COW) 시맨틱 기본 활성화로 메모리 효율 극대화. PyArrow 엔진 기본 탑재로 구버전 대비 로딩 속도 2-3배 향상.
* **주의점:** COW가 기본이므로 기존 in-place DataFrame 수정 코드 패턴 검토 필요.
* **결정 근거:** 2026-01-21 정식 릴리즈. 전용 문자열 타입(`pd.StringDtype`)이 기본값.

### Nuitka 4.0+
* **이유:** Python → Windows EXE 컴파일. PyInstaller 대비 실행 성능 우수.
* **이점:** PySide6 전용 플러그인 지원으로 Qt 관련 라이브러리 자동 포함.
* **결정 근거:** 2026년 2월 기준 안정 버전 4.0.

## 2. 아키텍처 설계

### 디렉토리 구조 (3-레이어)
* **src/core:** 비즈니스 로직(스캔, 검색, 워커)을 UI와 분리하여 테스트 용이성 확보.
* **src/ui:** 화면 표현 계층. `widgets.py` 분리를 통해 재사용성 증대. `styles.py`와 `toast.py`로 관심사 분리.
* **src/utils:** 클립보드, 설정, 내보내기, 로깅 등 유틸리티 기능 격리.

### 동시성 처리 (Concurrency)
* **QThread/Worker:** 대용량 파일 처리 시 GUI 프리징을 방지하기 위해 필수 적용.
* **Signal/Slot 패턴:** 스레드 간 안전한 데이터 전송. `result_found`, `progress_updated`, `error_occurred` 시그널로 실시간 UI 업데이트.
* **결정 근거:** Python GIL의 제약 하에서도 I/O-bound 작업에는 QThread가 효과적.

### 검색 알고리즘 (Transpose 기법)
* **결정:** 열 검색 시 `df.T`를 사용하여 열을 행으로 변환 후 동일 알고리즘 적용.
* **이유:** 행과 열 검색에 동일한 로직을 재사용할 수 있어 코드 중복 제거.
* **트레이드오프:** 전치 비용이 존재하나, 검색 편의성과 코드 일관성이 더 중요하다고 판단.

### 메모리 관리 전략
* **결정:** `openpyxl(read_only=True)` + Chunk 기반 로딩.
* **이유:** 1GB+ 파일 처리 시 메모리 초과 방지. `pandas.read_excel`은 전체 로딩이 기본이므로 부적합.
* **보완:** CSV는 `pd.read_csv(chunksize=N)`으로 청크 처리.

### 설정 저장 방식
* **결정:** JSON 파일 (`config.json`) 기반 ConfigManager.
* **이유:** 외부 DB 의존성 없이 단순 파일 기반으로 설정 지속성 확보.
* **대안 검토:** SQLite는 오버엔지니어링으로 판단. QSettings는 Windows Registry 의존으로 이식성 저하.

## 3. UI/UX 설계 결정

### 다크 모드
* **방식:** `QPalette` 색상 재정의 + QSS (Qt Style Sheet) 위젯별 커스터마이징.
* **이유:** Windows 11 시스템 다크 모드와 독립적으로 앱 내 테마 전환 지원.

### 토스트 알림
* **방식:** `QPropertyAnimation` 기반 Fade In/Out 비동기 알림.
* **이유:** `QMessageBox`의 모달 차단을 회피하여 사용자 경험 개선.

### 검색 기록
* **방식:** `QComboBox`로 최근 검색어 10개 유지.
* **이유:** `QLineEdit` 단독 사용 대비 빈번한 재검색 효율 향상.
