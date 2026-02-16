# 빌드 가이드 (Build Guide)

> **최종 갱신일:** 2026-02-17

## 1. 환경 설정

### 필수 요구 사항
* Python 3.13 이상 (3.14 호환 가능)
* pip (최신 버전 권장)

### 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

## 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 주요 의존성 (2026-02 기준)
| 패키지 | 버전 | 용도 |
|--------|------|------|
| PySide6 | >=6.10.0 | Qt 6 기반 GUI 프레임워크 |
| pandas | >=3.0.0 | 데이터 처리 엔진 (Copy-on-Write 시맨틱) |
| openpyxl | >=3.1.5 | Excel 파일 읽기/쓰기 |
| xlrd | >=2.0.1 | 레거시 .xls 파일 지원 |
| pyperclip | >=1.9.0 | 시스템 클립보드 제어 |
| nuitka | >=4.0 | Python → EXE 컴파일러 |
| pyarrow | >=18.0.0 | Pandas 고속 백엔드 |

## 3. 실행 방법
프로젝트 루트 디렉토리에서 아래 명령어로 실행합니다.
```bash
python -m src.main
```

## 4. 배포용 빌드 (Nuitka 4.0+)

### 빌드 스크립트 사용
```bash
python build.py
```
* 이 프로세스는 하드웨어에 따라 5-10분이 소요될 수 있습니다.
* `pandas`와 `openpyxl`은 무거운 라이브러리이므로, 초기 빌드가 느릴 수 있습니다.
* Nuitka가 결과를 캐시하므로 이후 빌드는 더 빠릅니다.

### 수동 빌드 (직접 실행)
```bash
python -m nuitka --standalone --onefile --enable-plugin=pyside6 --windows-console-mode=disable src/main.py
```

### 빌드 결과물
* `src.dist/` 또는 `src.build/` 디렉토리에 실행 파일이 생성됩니다.
* `main.exe` (또는 빌드 설정에 따라 `Data Scavenger.exe`)를 찾으세요.
* 이 단일 파일로 대상 Windows 시스템에서 Python 설치 없이 실행 가능합니다.

### Dry Run (명령어만 확인)
```bash
python build.py --dry-run
```

## 5. 배포 (Distribution)

1. **복사:** `main.exe`를 대상 Windows 시스템의 원하는 폴더로 복사합니다.
2. **설정:** 앱은 첫 실행 시 동일 디렉토리에 `config.json` 파일을 생성합니다.
3. **로그:** 로그는 동일 디렉토리의 `app.log` 파일에 기록됩니다.

## 6. 문제 해결 (Troubleshooting)

* **"Failed to execute script":** `app.log`를 확인하거나 명령 프롬프트에서 직접 실행하여 stderr 출력을 확인하세요.
* **Missing DLLs:** 클린 Windows VM에서 실행 실패 시, Visual C++ Redistributable 설치를 확인하세요 (Nuitka가 보통 필요한 DLL을 번들링합니다).
* **GUI 프리징:** 1GB 이상의 엑셀 파일 처리 시 발생할 수 있습니다. 로그에서 메모리 관련 에러를 확인하세요.

*주의: 빌드 전 `requirements.txt`의 모든 패키지가 설치되어 있어야 합니다.*
