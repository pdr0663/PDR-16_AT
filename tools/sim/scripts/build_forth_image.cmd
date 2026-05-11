@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."
set "PYTHON=python"
set "BUILDER=%REPO_ROOT%\tools\image_builder\export_forth_rom_header.py"

if not exist "%BUILDER%" (
  echo Missing Forth image builder: "%BUILDER%"
  exit /b 1
)

echo Building the seeded Forth image from Python sources...
%PYTHON% "%BUILDER%"
pause
exit /b %ERRORLEVEL%
