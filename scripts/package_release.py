"""Build release zip package for Secret Agent Clank in accordance with git release standards."""
import os
import shutil
import zipfile
from pathlib import Path

ROOT = Path("G:/Downloads/Korean Traslate Project/Games/Clank  Ratchet - Maruhi Mission Ignition")
DIST = ROOT / "dist"
PKG_DIR = DIST / "Secret_Agent_Clank_KR_v1.0_20261017"

# Clean/Create package directory
if PKG_DIR.exists():
    shutil.rmtree(PKG_DIR)
PKG_DIR.mkdir(parents=True, exist_ok=True)
(PKG_DIR / "patches").mkdir(parents=True, exist_ok=True)

# 1. Copy xdelta patch and xdelta3 tool
shutil.copy(DIST / "Secret_Agent_Clank_KR_v1.0.xdelta", PKG_DIR / "patches/Secret_Agent_Clank_KR_v1.0.xdelta")
shutil.copy(ROOT.parent.parent / "Tools/xdelta3-3.2.0-windows-x86_64/xdelta3.exe", PKG_DIR / "xdelta3.exe")

# 2. Create 적용방법.txt
readme_text = """================================================================================
PSP 비밀요원 클랭크 (Secret Agent Clank) 한글 패치 v1.0
================================================================================

본 패치는 PlayStation Portable(PSP)용 액션 게임 《비밀요원 클랭크 (Secret Agent Clank)》
한국어판(UCKS45096 v1.00)의 번역 품질 전면 개선 및 대사 전수 교정 패치입니다.
일본판 원본(UCJS10086) 및 북미 영문 스크립트와 1:1 대조 감사를 거쳐 총 135건의
미번역 영문, 오역, 오타, 캐릭터 보이스(클랭크 경어체/라쳇 말투)를 정비하였습니다.

--------------------------------------------------------------------------------
1. 파일 목록
--------------------------------------------------------------------------------
- 적용방법.txt                              : 본 안내 문서
- apply.cmd                                 : Windows용 원클릭 자동 패치 실행기 (SHA-256 해시 자동 대조)
- apply.py                                  : Python 3 환경용 크로스 플랫폼 패치 스크립트
- xdelta3.exe                               : xdelta3 패치 실행 프로그램
- patches/Secret_Agent_Clank_KR_v1.0.xdelta : 한글 패치 델타 파일

--------------------------------------------------------------------------------
2. 패치 대상 및 결과 파일 정보
--------------------------------------------------------------------------------
[지원 원본 ISO]
- 정식 명칭    : 비밀요원 클랭크 (Secret Agent Clank) 한국 정발판
- 파일명       : 제한 없음 (SHA-256 해시로 원본 자동 판별)
- 권장 파일명  : Secret Agent Clank [K].iso
- Disc ID      : UCKS45096 (v1.00)
- 파일 크기    : 1,222,705,152 바이트
- SHA-256 해시 : f0d5a191bdbf2fc05b403b065cbbb867a8974dd89686b3deb8a0d69601391007

[패치 파일]
- 파일명       : patches/Secret_Agent_Clank_KR_v1.0.xdelta
- 파일 크기    : 16,269 바이트
- SHA-256 해시 : df662e535c6213ffb5fd983ebbafef0498e7305b9f445384674c29d235f6345c

[패치 완료 결과 ISO]
- 파일명       : Secret Agent Clank [K] (Updated).iso
- 파일 크기    : 1,222,705,152 바이트
- SHA-256 해시 : ccad6a0f2c7baaf90548736c64b498f585570733ca7708fa815e4b3cca2cbb7e

* 주의: 미국판, 유럽판, 순정 일본판 또는 변조된 ISO에는 적용되지 않습니다.
  반드시 상기 SHA-256 해시와 일치하는 한국 정발판 원본 ISO를 준비해 주십시오.

--------------------------------------------------------------------------------
3. 패치 적용 방법
--------------------------------------------------------------------------------
[방법 1: Windows 드래그 앤 드롭 (가장 간편, 추천)]
1) 다운로드한 압축 파일의 압축을 모두 풉니다.
2) 소장하고 계신 원본 ISO 파일(파일명 무관)을 마우스로 끌어서 `apply.cmd` 위에 놓습니다.
3) 프로그램이 자동으로 SHA-256 무결성을 계산·검증한 후, 원본 파일이 있는 폴더에
   `Secret Agent Clank [K] (Updated).iso` 한글 패치 롬을 생성합니다.

[방법 2: apply.cmd 직접 실행 (자동 탐색)]
1) 다운로드한 압축을 풀고, 같은 폴더에 소장 중인 원본 ISO 파일을 넣습니다 (파일명 무관).
2) `apply.cmd`를 더블클릭하여 실행합니다.
3) 폴더 내 ISO 파일들의 SHA-256 해시를 자동으로 계산하여 원본 롬을 찾아 패치합니다.

[방법 3: Python 3 환경 (Linux, macOS, Windows)]
터미널에서 아래 명령어를 실행합니다 (파일명 무관, 해시 자동 검증).
  python apply.py [원본_ISO_경로]

--------------------------------------------------------------------------------
4. 주요 수정 내역 요약 (총 135건)
--------------------------------------------------------------------------------
1) 미번역 영문 및 시스템 텍스트 번역 (20건)
   - 옵션 메뉴 내 미번역 영문: "Brightness" -> "밝기", "Wide Screen" -> "와이드 스크린"
   - 조작 안내 버튼 영문: "Pause" -> "일시정지", "Camera Reset" -> "시점 초기화"
   - 로딩 팁 및 인터페이스 텍스트 완전 한국어화
2) 포맷 스트링 및 엔진 제어 코드 복구
   - 버튼 아이콘 누락 매크로 `<BTN_CROSS>`, `<BTN_CIRCLE>` 등 정상 심볼 복구
3) 스토리 대사 전수 교정 및 캐릭터 말투 통일
   - 클랭크의 신사적이고 정중한 경어체 어조 복원
   - 라쳇의 능청스럽고 자신감 넘치는 말투 복원
   - 번역기 직역투 및 어색한 외래어 표기 전면 정비

--------------------------------------------------------------------------------
5. 권리 표기 및 크레딧
--------------------------------------------------------------------------------
- 원작 개발: High Impact Games / Sony Computer Entertainment
- 한글 패치 제작: AKUMA815 (https://github.com/akuma815)
- 본 패치는 비상업적 팬 패치이며, 원본 게임 소프트웨어는 별도로 소장하셔야 합니다.
"""

(PKG_DIR / "적용방법.txt").write_text(readme_text, encoding="utf-8")

# 3. Create apply.cmd (CP949, CRLF, hash verification via native certutil)
apply_cmd_text = r"""@echo off
setlocal EnableDelayedExpansion
title 비밀요원 클랭크 한글 패치 적용기

echo =======================================================================
echo   비밀요원 클랭크 (Secret Agent Clank) 한글 패치 v1.0
echo =======================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "XDELTA_EXE=%SCRIPT_DIR%xdelta3.exe"
set "PATCH=%SCRIPT_DIR%patches\Secret_Agent_Clank_KR_v1.0.xdelta"
set "EXPECTED_HASH=f0d5a191bdbf2fc05b403b065cbbb867a8974dd89686b3deb8a0d69601391007"
set "OUTPUT_NAME=Secret Agent Clank [K] (Updated).iso"

if not exist "%XDELTA_EXE%" (
    echo [오류] 패치 프로그램 [xdelta3.exe] 을 찾을 수 없습니다: "%XDELTA_EXE%"
    echo.
    pause
    exit /b 1
)

if not exist "%PATCH%" (
    echo [오류] 패치 파일 [.xdelta] 을 찾을 수 없습니다: "%PATCH%"
    echo.
    pause
    exit /b 1
)

set "TARGET_ISO="

rem 1. 사용자가 드래그 앤 드롭으로 파일을 전달한 경우
if "%~1" neq "" (
    set "CANDIDATE=%~1"
    echo [*] 전달된 파일의 해시 [SHA-256] 를 계산하여 원본 여부를 검증합니다...
    echo     파일: "!CANDIDATE!"
    echo.
    if not exist "!CANDIDATE!" (
        echo [오류] 지정한 파일이 존재하지 않습니다: "!CANDIDATE!"
        echo.
        pause
        exit /b 1
    )
    call :check_hash "!CANDIDATE!" IS_MATCH CALC_HASH
    if "!IS_MATCH!"=="1" (
        set "TARGET_ISO=!CANDIDATE!"
        goto :apply_patch
    ) else (
        echo [오류] 파일의 SHA-256 해시값이 원본과 일치하지 않습니다.
        echo   - 계산된 해시: !CALC_HASH!
        echo   - 필요한 해시: %EXPECTED_HASH%
        echo.
        echo 한국 정식 발매판 원본 ISO가 맞는지 다시 확인해 주십시오.
        echo.
        pause
        exit /b 1
    )
)

rem 2. 드래그 앤 드롭 없이 직접 실행한 경우: 현재 폴더의 모든 *.iso 파일 해시 검사
echo [*] 폴더 내 ISO 파일들의 해시 [SHA-256] 를 계산하여 원본을 탐색합니다...
for %%F in ("%SCRIPT_DIR%*.iso") do (
    set "FNAME=%%~nxF"
    if /i not "!FNAME!"=="%OUTPUT_NAME%" (
        echo   - 검사 중: "%%~nxF"
        call :check_hash "%%~ffF" IS_MATCH CALC_HASH
        if "!IS_MATCH!"=="1" (
            echo     -^> [일치] 원본 ISO 확인 완료!
            set "TARGET_ISO=%%~ffF"
            goto :apply_patch
        ) else (
            echo     -^> [불일치] 해시: !CALC_HASH!
        )
    )
)

rem 3. 폴더 내에서 일치하는 ISO를 찾지 못한 경우 직접 입력 요청
echo.
echo [안내] 폴더 내에서 해시가 일치하는 원본 ISO를 찾지 못했습니다.
echo.
echo [지원 원본 정보]
echo   - 대상 타이틀  : 비밀요원 클랭크 (Secret Agent Clank)
echo   - Disc ID      : UCKS45096 (v1.00)
echo   - 기준 SHA-256 : %EXPECTED_HASH%
echo.
echo 원본 ISO 파일을 이 창으로 드래그 앤 드롭한 뒤 Enter를 누르거나,
echo 파일의 전체 경로를 입력해 주십시오.
echo.
set "USER_INPUT="
set /p "USER_INPUT=ISO 파일 경로: "

if not defined USER_INPUT (
    echo [오류] 경로가 입력되지 않았습니다.
    pause
    exit /b 1
)

rem 따옴표 제거
set "USER_INPUT=%USER_INPUT:"=%"

if not exist "!USER_INPUT!" (
    echo [오류] 지정한 파일이 존재하지 않습니다: "!USER_INPUT!"
    pause
    exit /b 1
)

echo.
echo [*] 입력된 파일의 해시 [SHA-256] 를 계산하고 있습니다...
call :check_hash "!USER_INPUT!" IS_MATCH CALC_HASH
if "!IS_MATCH!"=="1" (
    set "TARGET_ISO=!USER_INPUT!"
    goto :apply_patch
) else (
    echo [오류] 파일의 SHA-256 해시값이 원본과 일치하지 않습니다.
    echo   - 계산된 해시: !CALC_HASH!
    echo   - 필요한 해시: %EXPECTED_HASH%
    echo.
    echo 한국 정식 발매판 원본 ISO가 맞는지 다시 확인해 주십시오.
    echo.
    pause
    exit /b 1
)

:apply_patch
echo.
echo =======================================================================
echo   패치 적용 대상 확인 완료
echo =======================================================================
echo   - 원본 파일 : "!TARGET_ISO!"
echo   - 패치 파일 : "%PATCH%"

for %%I in ("!TARGET_ISO!") do set "TARGET_DIR=%%~dpI"
set "OUT_FILE=!TARGET_DIR!!OUTPUT_NAME!"
echo   - 생성 파일 : "!OUT_FILE!"
echo.
echo [*] 한글 패치를 적용하고 있습니다. 잠시만 기다려주세요...

set "XDELTA="
"%XDELTA_EXE%" -d -f -s "!TARGET_ISO!" "!PATCH!" "!OUT_FILE!"
set "PATCH_ERR=!ERRORLEVEL!"

if !PATCH_ERR! equ 0 (
    echo.
    echo =======================================================================
    echo   [성공] 한글 패치 적용이 정상적으로 완료되었습니다!
    echo =======================================================================
    echo 생성된 파일: "!OUT_FILE!"
    echo.
    echo PPSSPP 에뮬레이터 또는 PSP 실기에서 플레이하실 수 있습니다.
) else (
    echo.
    echo =======================================================================
    echo   [실패] 패치 적용 중 오류가 발생했습니다. [오류 코드: !PATCH_ERR!]
    echo =======================================================================
    echo 원본 ISO 손상 여부 또는 드라이브 저장 공간 부족 여부를 확인해주세요.
)

echo.
pause
exit /b 0

:check_hash
set "CH_FILE=%~1"
set "CH_MATCH_VAR=%~2"
set "CH_HASH_VAR=%~3"
set "CALC="
for /f "skip=1 tokens=* delims=" %%H in ('certutil -hashfile "!CH_FILE!" SHA256 2^>nul') do (
    if not defined CALC (
        set "CALC=%%H"
    )
)
set "CALC=!CALC: =!"
set "%CH_HASH_VAR%=!CALC!"
if /i "!CALC!"=="%EXPECTED_HASH%" (
    set "%CH_MATCH_VAR%=1"
) else (
    set "%CH_MATCH_VAR%=0"
)
exit /b 0
"""
apply_cmd_bytes = apply_cmd_text.replace("\r\n", "\n").replace("\n", "\r\n").encode("cp949")
(PKG_DIR / "apply.cmd").write_bytes(apply_cmd_bytes)

# Also generate dist/apply_patch.bat (in dist folder)
dist_bat_text = apply_cmd_text.replace(
    r'set "PATCH=%SCRIPT_DIR%patches\Secret_Agent_Clank_KR_v1.0.xdelta"',
    r'set "PATCH=%SCRIPT_DIR%Secret_Agent_Clank_KR_v1.0.xdelta"'
)
dist_bat_bytes = dist_bat_text.replace("\r\n", "\n").replace("\n", "\r\n").encode("cp949")
(DIST / "apply_patch.bat").write_bytes(dist_bat_bytes)

# 4. Create apply.py (cross-platform, SHA-256 verification)
apply_py_text = """#!/usr/bin/env python3
\"\"\"Cross-platform patch applicator for Secret Agent Clank (Korea).
Validates source ISO integrity using SHA-256 before applying xdelta3 patch.
\"\"\"
import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
XDELTA = ROOT / "xdelta3.exe"
PATCH = ROOT / "patches/Secret_Agent_Clank_KR_v1.0.xdelta"
EXPECTED_HASH = "f0d5a191bdbf2fc05b403b065cbbb867a8974dd89686b3deb8a0d69601391007"
OUTPUT_NAME = "Secret Agent Clank [K] (Updated).iso"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().lower()


def main():
    print("=" * 70)
    print("  비밀요원 클랭크 (Secret Agent Clank) 한글 패치 v1.0")
    print("=" * 70)
    print()

    target_iso = None
    if len(sys.argv) > 1:
        cand = Path(sys.argv[1]).resolve()
        if not cand.exists():
            print(f"[오류] 지정한 파일을 찾을 수 없습니다: {cand}")
            return 1
        print("[*] 지정된 파일의 해시(SHA-256)를 계산하여 원본 무결성을 검증합니다...")
        print(f"    파일: {cand.name}")
        calc = sha256_file(cand)
        if calc == EXPECTED_HASH.lower():
            target_iso = cand
        else:
            print("[오류] 원본 ISO 해시값이 일치하지 않습니다.")
            print(f"  - 계산된 해시: {calc}")
            print(f"  - 필요한 해시: {EXPECTED_HASH}")
            return 1
    else:
        print("[*] 현재 폴더에서 원본 ISO 파일을 탐색하고 해시를 검증합니다...")
        for iso in ROOT.glob("*.iso"):
            if iso.name == OUTPUT_NAME or "(Updated)" in iso.name:
                continue
            print(f"  - 검사 중: {iso.name}")
            if sha256_file(iso) == EXPECTED_HASH.lower():
                print("    -> [일치] 원본 ISO 확인 완료!")
                target_iso = iso
                break

    if not target_iso:
        print("[안내] 현재 폴더에서 일치하는 원본 ISO를 찾지 못했습니다.")
        print(f"기준 SHA-256: {EXPECTED_HASH}")
        path_input = input("원본 ISO 파일 경로를 입력하세요: ").strip().strip('"')
        if not path_input:
            return 1
        cand = Path(path_input).resolve()
        if not cand.exists():
            print(f"[오류] 지정한 파일이 존재하지 않습니다: {cand}")
            return 1
        print("[*] 입력된 파일의 해시(SHA-256)를 계산합니다...")
        calc = sha256_file(cand)
        if calc == EXPECTED_HASH.lower():
            target_iso = cand
        else:
            print(f"[오류] 해시값이 일치하지 않습니다 ({calc}).")
            return 1

    out_file = target_iso.parent / OUTPUT_NAME
    if len(sys.argv) > 2:
        out_file = Path(sys.argv[2]).resolve()

    if not PATCH.exists():
        print(f"[오류] 패치 파일을 찾을 수 없습니다: {PATCH}")
        return 1

    print()
    print("=" * 70)
    print("  패치 적용 대상 확인 완료")
    print("=" * 70)
    print(f"  - 원본 파일 : {target_iso}")
    print(f"  - 패치 파일 : {PATCH}")
    print(f"  - 생성 파일 : {out_file}")
    print()
    print("[*] 한글 패치를 적용하고 있습니다. 잠시만 기다려주세요...")

    cmd = ["xdelta3", "-d", "-f", "-s", str(target_iso), str(PATCH), str(out_file)]
    if XDELTA.exists() and sys.platform == "win32":
        cmd[0] = str(XDELTA)

    env = os.environ.copy()
    env.pop("XDELTA", None)
    ret = subprocess.run(cmd, env=env)
    if ret.returncode == 0:
        print()
        print("=" * 70)
        print("  [성공] 한글 패치 적용이 정상적으로 완료되었습니다!")
        print("=" * 70)
        print(f"생성된 파일: {out_file}")
        return 0
    else:
        print(f"[오류] 패치 적용 실패 (코드: {ret.returncode})")
        return ret.returncode


if __name__ == "__main__":
    sys.exit(main())
"""
(PKG_DIR / "apply.py").write_text(apply_py_text, encoding="utf-8")
shutil.copy(PKG_DIR / "적용방법.txt", PKG_DIR / "README.txt")

# 5. Build ZIP
zip_name = DIST / "Secret_Agent_Clank_KR_v1.0_20261017.zip"
with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(PKG_DIR):
        for f in files:
            p = Path(root) / f
            arcname = str(p.relative_to(PKG_DIR)).replace("\\", "/")
            zinfo = zipfile.ZipInfo(arcname)
            zinfo.flag_bits |= 0x800  # UTF-8 flag
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zinfo, p.read_bytes())

print(f"[+] Created {zip_name} (Size: {zip_name.stat().st_size:,} bytes)")
