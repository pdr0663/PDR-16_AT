@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."
set "SKETCH_DIR=%REPO_ROOT%\firmware\mega\pdr_vm"
set "BUILD_DIR="
set "IMAGE_BUILDER=%SCRIPT_DIR%Other\build_forth_image.cmd"
set "ARDUINO_DATA_DIR=%LOCALAPPDATA%\Arduino15"
set "FQBN=arduino:avr:mega"
set "SKIP_IMAGE="
set "NO_PAUSE="
set "IDE_MODE=new"
set "IDE_DIR="
set "RESOLVER="
set "ARDUINO_TOOL="

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--skip-image" (
  set "SKIP_IMAGE=1"
  shift
  goto parse_args
)
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
if /I "%~1"=="--no-pause" (
  set "NO_PAUSE=1"
  shift
  goto parse_args
)
echo Unknown option: %~1
echo Supported options: --skip-image, --ide new^|old, --no-pause
exit /b 1

:args_done
if /I "%IDE_MODE%"=="new" (
  set "IDE_DIR=%SCRIPT_DIR%..\ide\new"
  set "RESOLVER=!IDE_DIR!\resolve_arduino_cli.cmd"
  set "BUILD_DIR=%SKETCH_DIR%\.build-cli"
  set "ARDUINO_DATA_DIR=%LOCALAPPDATA%\Arduino15"
  set "ARDUINO_TOOL=arduino-cli"
)
if /I "%IDE_MODE%"=="old" (
  set "IDE_DIR=%SCRIPT_DIR%..\ide\old"
  set "RESOLVER=!IDE_DIR!\resolve_arduino_root.cmd"
  set "BUILD_DIR=%SKETCH_DIR%\.build-legacy"
  set "ARDUINO_TOOL=arduino-builder"
)

if not defined RESOLVER (
  echo Unsupported IDE mode: %IDE_MODE%
  echo Supported values: new, old
  goto fail
)

for /f "usebackq delims=" %%I in (`call "%RESOLVER%"`) do (
  if not defined ARDUINO_VALUE set "ARDUINO_VALUE=%%I"
)

if not defined ARDUINO_VALUE goto fail

if /I "%IDE_MODE%"=="new" (
  set "ARDUINO_TOOL=%ARDUINO_VALUE%"
  if not exist "!ARDUINO_TOOL!" (
    echo Arduino CLI resolver returned a path that does not exist:
    echo   "!ARDUINO_TOOL!"
    goto fail
  )
)

if /I "%IDE_MODE%"=="old" (
  set "ARDUINO_ROOT=%ARDUINO_VALUE%"
  if not exist "!ARDUINO_ROOT!" (
    echo Arduino IDE root resolver returned a path that does not exist:
    echo   "!ARDUINO_ROOT!"
    goto fail
  )
  set "ARDUINO_TOOL=!ARDUINO_ROOT!\arduino-builder.exe"
  if not exist "!ARDUINO_TOOL!" (
    echo Missing legacy builder:
    echo   "!ARDUINO_TOOL!"
    goto fail
  )
)

if not defined ARDUINO_TOOL goto fail

if /I "%IDE_MODE%"=="new" (
  if not exist "%ARDUINO_DATA_DIR%" mkdir "%ARDUINO_DATA_DIR%"
)

if not exist "%SKETCH_DIR%" (
  echo Missing sketch directory:
  echo   "%SKETCH_DIR%"
  goto fail
)

if not defined SKIP_IMAGE (
  if not exist "%IMAGE_BUILDER%" (
    echo Missing Forth image builder:
    echo   "%IMAGE_BUILDER%"
    goto fail
  )
  call "%IMAGE_BUILDER%" --no-pause
  if errorlevel 1 goto fail
)

if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

echo Compiling Mega VM firmware with:
echo   "%ARDUINO_TOOL%"
echo IDE mode:
echo   %IDE_MODE%
if /I "%IDE_MODE%"=="new" (
  echo Arduino data dir:
  echo   "%ARDUINO_DATA_DIR%"
)
echo Using FQBN:
echo   %FQBN%
echo Build directory:
echo   "%BUILD_DIR%"

if /I "%IDE_MODE%"=="new" goto run_new
goto run_old

:run_new
"!ARDUINO_TOOL!" compile --fqbn %FQBN% --build-path "%BUILD_DIR%" "%SKETCH_DIR%"
if not defined NO_PAUSE pause
exit /b %ERRORLEVEL%

:run_old
"!ARDUINO_TOOL!" -compile -fqbn %FQBN% -build-path "%BUILD_DIR%" -build-cache "%BUILD_DIR%\cache" -hardware "!ARDUINO_ROOT!\hardware" -tools "!ARDUINO_ROOT!\hardware\tools\avr" -tools "!ARDUINO_ROOT!\tools-builder" "%SKETCH_DIR%"
if not defined NO_PAUSE pause
exit /b %ERRORLEVEL%

:fail
if not defined NO_PAUSE pause
exit /b 1
