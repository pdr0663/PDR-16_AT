@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\.."
set "AVRSIM_EXE=%REPO_ROOT%\avrsim\avrsim.exe"

if exist "%AVRSIM_EXE%" (
  echo Found avrsim artifact: "%AVRSIM_EXE%"
  echo Use run_mega_vm_simavr.cmd to run the simulator.
  echo Use run_mega_vm_teraterm.cmd to open the Windows terminal.
  exit /b 0
)

echo Missing avrsim artifact: "%AVRSIM_EXE%"
echo Copy the Windows build into the repo's avrsim folder and name it avrsim.exe.
exit /b 1
