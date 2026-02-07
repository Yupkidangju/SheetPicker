# 배포 가이드 (Deployment Guide)

## 1. 사전 요구 사항 (Prerequisites)
* **Python 3.12 이상** 설치 필요.
* 의존성 설치:
  ```bash
  pip install -r requirements.txt
  ```
* `nuitka` 설치 확인 (requirements에 포함됨).

## 2. 실행 파일 빌드 (Building the Executable)
Nuitka를 사용하여 Python 소스를 단독 실행 가능한 Windows 실행 파일(`.exe`)로 컴파일합니다.

### 빌드 명령어 (Build Command)
프로젝트 루트에서 빌드 스크립트를 실행합니다:
```bash
python build.py
```
* 하드웨어 사양에 따라 5~10분 정도 소요될 수 있습니다.
* **참고:** `pandas`와 `openpyxl`은 용량이 큰 라이브러리이므로 초기 빌드가 느릴 수 있습니다. Nuitka는 이후 빌드를 위해 결과를 캐싱합니다.

### 빌드 결과물 (Build Artifacts)
* 결과물은 `src.dist/` 또는 `src.build/` 디렉토리에 생성됩니다 (Nuitka 버전에 따라 다름).
* `main.exe` (또는 `Data Scavenger.exe`) 파일을 확인하세요.
* 이 단일 파일에는 앱 실행에 필요한 모든 것이 포함되어 있습니다. 대상 머신에 Python을 설치할 필요가 없습니다.

## 3. 배포 (Distribution)
1. **복사:** `main.exe`를 대상 Windows 머신의 원하는 폴더로 이동합니다.
2. **설정 (Config):** 애플리케이션 설정(`config.json`)은 실행 파일 위치가 아닌, **OS 표준 사용자 데이터 디렉토리**에 저장됩니다.
   * 예 (Windows): `%LOCALAPPDATA%\JulesCorp\Data Scavenger\config.json`
   * 초기 실행 시 기본 설정으로 자동 생성됩니다.
3. **로그 (Logs):** 로그는 실행 파일과 동일한 디렉토리의 `app.log` 파일에 기록됩니다.

## 4. 문제 해결 (Troubleshooting)
* **"Failed to execute script" 오류:** `app.log`를 확인하거나 명령 프롬프트(CMD)에서 실행하여 에러 출력을 확인하세요.
* **DLL 누락:** 클린 윈도우 VM에서 실행 실패 시, Visual C++ Redistributable 설치 여부를 확인하세요 (보통 Nuitka가 필요한 DLL을 번들링합니다).
