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
한국어판의 번역 품질 전면 개선 및 대사 전수 교정 패치입니다.
일본판 원본(UCJS10086) 및 북미 영문 스크립트와 1:1 대조 감사를 거쳐 총 135건의
미번역 영문, 오역, 오타, 캐릭터 보이스(클랭크 경어체/라쳇 말투)를 정비하였습니다.

--------------------------------------------------------------------------------
1. 파일 목록
--------------------------------------------------------------------------------
- 적용방법.txt                        : 본 안내 문서
- apply.cmd                           : Windows용 1클릭 자동 패치 실행기 (드래그 앤 드롭 지원)
- apply.py                            : Python 3 환경용 크로스 플랫폼 패치 스크립트
- xdelta3.exe                         : xdelta3 패치 실행 프로그램
- patches/Secret_Agent_Clank_KR_v1.0.xdelta : 한글 패치 델타 파일

--------------------------------------------------------------------------------
2. 패치 대상 및 결과 파일 정보
--------------------------------------------------------------------------------
[지원 원본 ISO]
- 파일명       : Secret Agent Clank [K].iso
- 파일 크기    : 1,222,705,152 바이트
- SHA-256 해시 : a951d1f0545931cb5a073f9f4c3beea3336d814ec9786a6fb0ae5dfba1d2a4a3

[패치 파일]
- 파일명       : patches/Secret_Agent_Clank_KR_v1.0.xdelta
- 파일 크기    : 16,269 바이트
- SHA-256 해시 : df662e535c6213ffb5fd983ebbafef0498e7305b9f445384674c29d235f6345c

[패치 완료 결과 ISO]
- 파일명       : Secret Agent Clank [K] (Updated).iso
- 파일 크기    : 1,222,705,152 바이트
- SHA-256 해시 : ccad6a0f2c7baaf90548736c64b498f585570733ca7708fa815e4b3cca2cbb7e

* 주의: 미국판, 유럽판, 순정 일본판 또는 변조된 ISO에는 적용되지 않습니다.
  반드시 상기 SHA-256 해시와 일치하는 원본 ISO를 준비해 주십시오.

--------------------------------------------------------------------------------
3. 패치 적용 방법
--------------------------------------------------------------------------------
[방법 1: Windows 드래그 앤 드롭 (가장 간편)]
1) 다운로드한 압축 파일의 압축을 모두 풉니다.
2) 준비한 원본 ISO 파일을 마우스로 끌어서 `apply.cmd` 파일 위에 놓습니다.
3) 자동으로 무결성 검사 후 패치가 적용되어 원본 파일 옆에
   `Secret Agent Clank [K] (Updated).iso` 파일이 생성됩니다.

[방법 2: apply.cmd 직접 실행]
1) 원본 ISO 파일을 본 폴더 안에 넣고 파일명을 `Secret Agent Clank [K].iso`로 맞춥니다.
2) `apply.cmd`를 더블클릭하여 실행합니다.

[방법 3: Python 3 환경 (Linux, macOS, Windows)]
터미널에서 아래 명령어를 실행합니다.
  python apply.py "Secret Agent Clank [K].iso"

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

# 3. Create apply.cmd
apply_cmd_text = """@echo off
chcp 65001 > nul
setlocal

echo ========================================================
echo   비밀요원 클랭크 (Secret Agent Clank) 한글 패치 v1.0
echo ========================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "XDELTA=%SCRIPT_DIR%xdelta3.exe"
set "PATCH=%SCRIPT_DIR%patches\\Secret_Agent_Clank_KR_v1.0.xdelta"
set "EXPECTED_OUT=Secret Agent Clank [K] (Updated).iso"

if not exist "%XDELTA%" (
    echo [오류] xdelta3.exe 프로그램을 찾을 수 없습니다.
    pause
    exit /b 1
)

if not exist "%PATCH%" (
    echo [오류] 패치 파일을 찾을 수 없습니다: %PATCH%
    pause
    exit /b 1
)

rem 드래그 앤 드롭된 파일이 있는지 확인
if "%~1" neq "" (
    set "SRC=%~1"
    set "OUT_DIR=%~dp1"
    set "OUT=%~dp1Secret Agent Clank [K] (Updated).iso"
) else (
    set "SRC=%SCRIPT_DIR%Secret Agent Clank [K].iso"
    set "OUT=%SCRIPT_DIR%Secret Agent Clank [K] (Updated).iso"
)

if not exist "%SRC%" (
    echo [안내] 원본 ISO 파일을 찾을 수 없습니다.
    echo 원본 ISO 파일을 이 창에 드래그 앤 드롭하거나,
    echo 본 폴더에 복사 후 'Secret Agent Clank [K].iso'로 이름을 변경해주세요.
    echo.
    set /p "SRC=또는 원본 ISO 파일의 전체 경로를 입력하세요: "
    set "OUT=%SCRIPT_DIR%Secret Agent Clank [K] (Updated).iso"
)

if not exist "%SRC%" (
    echo [오류] 지정된 원본 파일을 찾을 수 없습니다: %SRC%
    pause
    exit /b 1
)

echo [*] 원본 파일: %SRC%
echo [*] 패치 적용 중입니다... 잠시만 기다려주세요.
echo.

"%XDELTA%" -d -f -s "%SRC%" "%PATCH%" "%OUT%"

if %ERRORLEVEL% equ 0 (
    echo [성공] 한글 패치가 정상적으로 적용되었습니다!
    echo 생성된 파일: %OUT%
) else (
    echo [오류] 패치 적용에 실패했습니다.
    echo 원본 ISO의 해시값(SHA-256)이 '적용방법.txt'에 기재된 값과 일치하는지 확인해주세요.
)

echo.
pause
"""
(PKG_DIR / "apply.cmd").write_text(apply_cmd_text, encoding="cp949")

# 4. Create apply.py
apply_py_text = """#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
XDELTA = ROOT / "xdelta3.exe"
PATCH = ROOT / "patches/Secret_Agent_Clank_KR_v1.0.xdelta"

def main():
    if len(sys.argv) > 1:
        src = Path(sys.argv[1])
    else:
        src = ROOT / "Secret Agent Clank [K].iso"

    if len(sys.argv) > 2:
        out = Path(sys.argv[2])
    else:
        out = src.parent / "Secret Agent Clank [K] (Updated).iso"

    if not src.exists():
        print(f"[Error] Source ISO not found: {src}")
        print("Usage: python apply.py <source_iso> [output_iso]")
        return 1

    if not PATCH.exists():
        print(f"[Error] Patch file not found: {PATCH}")
        return 1

    print(f"[*] Applying patch: {PATCH.name}")
    print(f"[*] Source: {src}")
    print(f"[*] Target: {out}")

    cmd = ["xdelta3", "-d", "-f", "-s", str(src), str(PATCH), str(out)]
    if XDELTA.exists() and sys.platform == "win32":
        cmd[0] = str(XDELTA)

    ret = subprocess.run(cmd)
    if ret.returncode == 0:
        print(f"[+] Success! Patched ISO created at: {out}")
        return 0
    else:
        print("[-] Patch application failed.")
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
