import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_build(dry_run=False):
    """
    [v1.0.0] Nuitka를 사용하여 프로젝트를 빌드합니다.
    Nuitka 4.0+ 기준으로 최적화 옵션을 구성합니다.
    """
    project_root = Path(__file__).parent.resolve()
    main_script = project_root / "src" / "main.py"

    if not main_script.exists():
        print(f"[오류] 메인 스크립트를 찾을 수 없습니다: {main_script}")
        sys.exit(1)

    # Nuitka 빌드 명령어 구성
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--enable-plugin=pyside6",
        "--include-package=pandas",       # Pandas 명시적 포함
        "--include-package=openpyxl",
        "--windows-console-mode=disable", # GUI 앱이므로 콘솔 숨김

        # 메타데이터 및 회사 정보
        "--company-name=Antigravity",
        "--product-name=Data Scavenger",
        "--file-version=2.0.0",
        "--product-version=2.0.0",
        "--file-description=고성능 Excel/CSV 검색 도구",
        "--copyright=Copyright (c) 2026 Antigravity",

        # 최적화 옵션 (LTO) - 빌드 시간 증가하므로 릴리즈 시 사용 권장
        # "--lto=yes",

        str(main_script)
    ]

    print(f"[빌드] 실행 명령: {' '.join(cmd)}")

    if not dry_run:
        try:
            subprocess.run(cmd, check=True)
            print("[빌드] 빌드가 성공적으로 완료되었습니다.")
        except subprocess.CalledProcessError as e:
            print(f"[오류] 빌드 실패. 종료 코드: {e.returncode}")
            sys.exit(e.returncode)
    else:
        print("[빌드] Dry-run 모드입니다. 실제 빌드는 수행되지 않았습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Scavenger Nuitka 빌드 스크립트")
    parser.add_argument("--dry-run", action="store_true", help="명령어만 출력하고 실행하지 않음")
    args = parser.parse_args()

    run_build(dry_run=args.dry_run)
