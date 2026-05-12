@echo off
setlocal EnableExtensions
set "NO_PAUSE="

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\..\.."
set "PYTHON=python"
set "BUILDER=%REPO_ROOT%\tools\image_builder\export_forth_rom_header.py"

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--no-pause" (
  set "NO_PAUSE=1"
  shift
  goto parse_args
)
echo Unknown option: %~1
echo Supported options: --no-pause
exit /b 1

:args_done

if not exist "%BUILDER%" (
  echo Missing Forth image builder: "%BUILDER%"
  exit /b 1
)

echo Building the seeded Forth image from Python sources...
%PYTHON% "%BUILDER%"
if defined NO_PAUSE exit /b %ERRORLEVEL%
pause
exit /b %ERRORLEVEL%
