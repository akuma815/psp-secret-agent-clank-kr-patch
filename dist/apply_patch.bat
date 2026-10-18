@echo off
setlocal EnableDelayedExpansion
title 비밀요원 클랭크 한글 패치 적용기

echo =======================================================================
echo   비밀요원 클랭크 (Secret Agent Clank) 한글 패치 v1.0
echo =======================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "XDELTA_EXE=%SCRIPT_DIR%xdelta3.exe"
set "PATCH=%SCRIPT_DIR%Secret_Agent_Clank_KR_v1.0.xdelta"
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
