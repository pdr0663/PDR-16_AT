@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."
set "IDE_MODE=new"
set "SKIP_IMAGE="
set "BUILD_ARGS="
set "FIRMWARE_PATH="

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--ide" (
  if "%~2"=="" (
    echo Missing value for --ide.
    echo Supported values: new, old
    exit /b 1
  )
  set "IDE_MODE=%~2"
  shift
  shift
  goto parse_args
)
if /I "%~1"=="--skip-image" (
  set "SKIP_IMAGE=1"
  shift
  goto parse_args
)
echo Unknown option: %~1
echo Supported options: --ide new^|old, --skip-image
exit /b 1

:args_done
if /I "%IDE_MODE%"=="new" goto build_new
if /I "%IDE_MODE%"=="old" goto build_old
echo Unsupported IDE mode: %IDE_MODE%
echo Supported values: new, old
exit /b 1

:build_new
set "BUILD_ARGS=--ide new --no-pause"
if defined SKIP_IMAGE set "BUILD_ARGS=%BUILD_ARGS% --skip-image"
set "BUILD_DIR=%REPO_ROOT%\firmware\mega\pdr_vm\.build-cli-run_%RANDOM%%RANDOM%"
set "BUILD_ARGS=%BUILD_ARGS% --build-dir %BUILD_DIR%"
call "%SCRIPT_DIR%build_mega_vm_firmware.cmd" %BUILD_ARGS%
if errorlevel 1 exit /b %ERRORLEVEL%
set "FIRMWARE_PATH=%BUILD_DIR%\pdr_vm.ino.elf"
if not exist "%FIRMWARE_PATH%" set "FIRMWARE_PATH=%BUILD_DIR%\pdr_vm.ino.hex"
goto compile

:build_old
set "BUILD_ARGS=--ide old --no-pause"
if defined SKIP_IMAGE set "BUILD_ARGS=%BUILD_ARGS% --skip-image"
call "%SCRIPT_DIR%build_mega_vm_firmware.cmd" %BUILD_ARGS%
if errorlevel 1 exit /b %ERRORLEVEL%
set "FIRMWARE_PATH=%REPO_ROOT%\firmware\mega\pdr_vm\.build-legacy\pdr_vm.ino.elf"
if not exist "%FIRMWARE_PATH%" set "FIRMWARE_PATH=%REPO_ROOT%\firmware\mega\pdr_vm\.build-legacy\pdr_vm.ino.hex"

:compile
set "TRANSCRIPT=%REPO_ROOT%\tools\sim\logs\forth_library_compile_%IDE_MODE%.txt"
set "BRIDGE_LOG=%REPO_ROOT%\tools\sim\logs\forth_library_bridge_%IDE_MODE%.log"
if not exist "%REPO_ROOT%\tools\sim\logs" mkdir "%REPO_ROOT%\tools\sim\logs" >nul 2>nul

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%Other\compile_forth_libraries.ps1" -RepoRoot "%REPO_ROOT%" -FirmwarePath "%FIRMWARE_PATH%" -BuildOrderPath "%REPO_ROOT%\tools\forth\Forth Sources\build_order.txt" -TranscriptPath "%TRANSCRIPT%" -BridgeLogPath "%BRIDGE_LOG%" -ProbeWords
set "RC=%ERRORLEVEL%"
pause
exit /b %RC%
