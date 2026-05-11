@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."
set "AVRSIM_EXE=%REPO_ROOT%\avrsim\avrsim.exe"
set "TERATERM_EXE=%TERATERM_EXE%"
set "TERATERM_TITLE=PDR-16/AT avrsim"
set "TERATERM_BAUD=115200"

if not exist "%AVRSIM_EXE%" (
  echo Missing avrsim artifact: "%AVRSIM_EXE%"
  exit /b 1
)

if not defined TERATERM_EXE (
  for %%P in ("%ProgramFiles%\teraterm5\ttermpro.exe" "%ProgramFiles(x86)%\teraterm5\ttermpro.exe") do (
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

if defined AVRSIM_PIPE (
  start "" "%TERATERM_EXE%" /PIPE=%AVRSIM_PIPE% /BAUD=%TERATERM_BAUD% /W="%TERATERM_TITLE%" /AUTOWINCLOSE=off
  exit /b 0
)

if defined AVRSIM_COM (
  set "SERIAL_PORT=%AVRSIM_COM%"
  if /I "!SERIAL_PORT:~0,3!"=="COM" set "SERIAL_PORT=!SERIAL_PORT:~3!"
  start "" "%TERATERM_EXE%" /C=!SERIAL_PORT! /BAUD=%TERATERM_BAUD% /W="%TERATERM_TITLE%" /AUTOWINCLOSE=off /WAITCOM
  exit /b 0
)

echo Set AVRSIM_PIPE for a named pipe or AVRSIM_COM for a COM port.
echo Example: set AVRSIM_COM=4
exit /b 1
