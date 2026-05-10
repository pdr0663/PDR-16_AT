@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."
set "SIMAVR_BIN=simavr"
set "WSL_SCRIPT=/mnt/c/Users/Paul/PDR-16_AT/tools/sim/scripts/run_mega_vm_simavr.sh"

if not exist "%REPO_ROOT%\firmware\mega\pdr_vm\.build-cli\pdr_vm.ino.elf" (
  echo ELF not found: %REPO_ROOT%\firmware\mega\pdr_vm\.build-cli\pdr_vm.ino.elf
  exit /b 1
)

wsl bash -lc "SIMAVR_BIN='%SIMAVR_BIN%' '%WSL_SCRIPT%'"
