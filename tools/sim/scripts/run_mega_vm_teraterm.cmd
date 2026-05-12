@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."
set "BUILD_MODE=new"
set "DEFAULT_ELF="
set "DEFAULT_HEX="
set "TERATERM_EXE=%TERATERM_EXE%"
set "TERATERM_TITLE=PDR-16/XT avrsim"
set "BRIDGE_EXE=%REPO_ROOT%\tools\sim\bin\MegaVmTeraTerm\mega_vm_teraterm.exe"
set "BRIDGE_LOG_DIR=%REPO_ROOT%\tools\sim\logs"
set "PIPE_NAME=%AVRSIM_PIPE%"
set "RUN_ARGS="
set "PARSE_RUN_ARGS="

:parse_args
if "%~1"=="" goto args_done
if defined PARSE_RUN_ARGS (
  set "RUN_ARGS=!RUN_ARGS! %~1"
  shift
  goto parse_args
)
if /I "%~1"=="--ide" (
  if "%~2"=="" (
    echo Missing value for --ide.
    echo Supported values: new, old
    exit /b 1
  )
  set "BUILD_MODE=%~2"
  shift
  shift
  goto parse_args
)
if "%~1"=="--" (
  set "PARSE_RUN_ARGS=1"
  shift
  goto parse_args
)
echo Unknown option: %~1
echo Use -- before harness arguments. Supported options: --ide new^|old
exit /b 1

:args_done

if not defined PIPE_NAME set "PIPE_NAME=PDR16_XT_UART0"

if /I "%BUILD_MODE%"=="new" (
  set "DEFAULT_ELF=%REPO_ROOT%\firmware\mega\pdr_vm\.build-cli\pdr_vm.ino.elf"
  set "DEFAULT_HEX=%REPO_ROOT%\firmware\mega\pdr_vm\.build-cli\pdr_vm.ino.hex"
)
if /I "%BUILD_MODE%"=="old" (
  set "DEFAULT_ELF=%REPO_ROOT%\firmware\mega\pdr_vm\.build-legacy\pdr_vm.ino.elf"
  set "DEFAULT_HEX=%REPO_ROOT%\firmware\mega\pdr_vm\.build-legacy\pdr_vm.ino.hex"
)

if not defined DEFAULT_ELF (
  echo Unsupported IDE mode: %BUILD_MODE%
  echo Supported values: new, old
  exit /b 1
)

if defined TERATERM_EXE if not exist "%TERATERM_EXE%" set "TERATERM_EXE="

if not defined TERATERM_EXE (
  for %%P in (
    "C:\Program Files (x86)\teraterm\ttermpro.exe"
    "%ProgramFiles%\teraterm\ttermpro.exe"
    "%ProgramFiles(x86)%\teraterm\ttermpro.exe"
    "%ProgramFiles%\teraterm5\ttermpro.exe"
    "%ProgramFiles(x86)%\teraterm5\ttermpro.exe"
  ) do (
    if not defined TERATERM_EXE if exist "%%~fP" set "TERATERM_EXE=%%~fP"
  )
)

if not defined TERATERM_EXE (
  for /f "delims=" %%I in ('where ttermpro.exe 2^>nul') do (
    if not defined TERATERM_EXE set "TERATERM_EXE=%%I"
  )
)

if not defined TERATERM_EXE (
  echo Could not find Tera Term.
  echo Install it or set TERATERM_EXE to ttermpro.exe.
  exit /b 1
)

if not exist "%DEFAULT_ELF%" set "FIRMWARE=%DEFAULT_HEX%"
if exist "%DEFAULT_ELF%" set "FIRMWARE=%DEFAULT_ELF%"
if not exist "%FIRMWARE%" (
  echo Missing firmware image:
  echo   "%DEFAULT_ELF%"
  echo   "%DEFAULT_HEX%"
  exit /b 1
)

if not exist "%BRIDGE_EXE%" (
  call "%SCRIPT_DIR%Other\build_mega_vm_pipe_bridge.cmd"
  if errorlevel 1 exit /b %ERRORLEVEL%
)

if not exist "%BRIDGE_LOG_DIR%" mkdir "%BRIDGE_LOG_DIR%" >nul 2>nul
if defined RUN_ARGS (
  start "" /b "%BRIDGE_EXE%" --pipe-name %PIPE_NAME% --firmware "%FIRMWARE%" --mcu atmega2560 --freq 16000000 --log-path "%BRIDGE_LOG_DIR%\mega_vm_pipe_bridge.log" %RUN_ARGS%
) else (
  start "" /b "%BRIDGE_EXE%" --pipe-name %PIPE_NAME% --firmware "%FIRMWARE%" --mcu atmega2560 --freq 16000000 --log-path "%BRIDGE_LOG_DIR%\mega_vm_pipe_bridge.log"
)

timeout /t 1 /nobreak >nul
start "" "%TERATERM_EXE%" "\\.\pipe\%PIPE_NAME%" /PIPE /W="%TERATERM_TITLE%" /AUTOWINCLOSE=off
exit /b 0
