# 빌드 가이드 (Build Guide)

## 1. 환경 설정

### 필수 요구 사항
* Python 3.12 이상
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

## 3. 실행 방법
프로젝트 루트 디렉토리에서 아래 명령어로 실행합니다.
```bash
python -m src.main
```

## 4. 배포용 빌드 (Nuitka)
`nuitka`를 사용하여 단독 실행 파일(EXE)을 생성합니다.

```bash
python -m nuitka --standalone --onefile --enable-plugin=pyside6 --windows-console-mode=disable src/main.py
```
*주의: 빌드 전 `requirements.txt`의 모든 패키지가 설치되어 있어야 합니다.*
