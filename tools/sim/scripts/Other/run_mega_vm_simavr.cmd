@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."
set "AVRSIM_EXE=%REPO_ROOT%\avrsim\avrsim.exe"
set "DEFAULT_ELF=%REPO_ROOT%\firmware\mega\pdr_vm\.build-cli\pdr_vm.ino.elf"
set "DEFAULT_HEX=%REPO_ROOT%\firmware\mega\pdr_vm\.build-cli\pdr_vm.ino.hex"

if not exist "%AVRSIM_EXE%" (
  echo Missing avrsim binary: "%AVRSIM_EXE%"
  echo Copy the Windows build into the repo's avrsim folder and name it avrsim.exe.
  exit /b 1
)

set "FIRMWARE=%DEFAULT_ELF%"
if not exist "%FIRMWARE%" set "FIRMWARE=%DEFAULT_HEX%"
if not exist "%FIRMWARE%" (
  echo Missing firmware image:
  echo   "%DEFAULT_ELF%"
  echo   "%DEFAULT_HEX%"
  exit /b 1
)

echo Running:
echo   "%AVRSIM_EXE%" -m atmega2560 -f 16000000 "%FIRMWARE%" %*
"%AVRSIM_EXE%" -m atmega2560 -f 16000000 "%FIRMWARE%" %*
