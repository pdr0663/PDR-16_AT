@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."
set "SKETCH_DIR=%REPO_ROOT%\firmware\mega\pdr_vm"
set "BUILD_DIR=%SKETCH_DIR%\.build-cli"
set "RESOLVER=%SCRIPT_DIR%resolve_arduino_cli.cmd"
set "FQBN=arduino:avr:mega"
set "SKIP_IMAGE="

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--skip-image" (
  set "SKIP_IMAGE=1"
  shift
  goto parse_args
)
echo Unknown option: %~1
echo Supported options: --skip-image
exit /b 1

:args_done
if not exist "%RESOLVER%" (
  echo Missing Arduino CLI resolver:
  echo   "%RESOLVER%"
  exit /b 1
)

for /f "usebackq delims=" %%I in (`call "%RESOLVER%"`) do (
  if not defined ARDUINO_CLI set "ARDUINO_CLI=%%I"
)

if not defined ARDUINO_CLI exit /b 1

if not defined SKIP_IMAGE (
  call "%SCRIPT_DIR%build_forth_image.cmd"
  if errorlevel 1 exit /b %ERRORLEVEL%
)

if not exist "%SKETCH_DIR%" (
  echo Missing sketch directory:
  echo   "%SKETCH_DIR%"
  exit /b 1
)

if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

echo Compiling Mega VM firmware with:
echo   "%ARDUINO_CLI%"
echo Using FQBN:
echo   %FQBN%
echo Build directory:
echo   "%BUILD_DIR%"

"%ARDUINO_CLI%" compile --fqbn %FQBN% --build-path "%BUILD_DIR%" "%SKETCH_DIR%"
pause
exit /b %ERRORLEVEL%
