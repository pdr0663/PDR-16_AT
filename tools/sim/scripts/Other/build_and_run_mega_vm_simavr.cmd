@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "BUILD_ARGS="
set "RUN_ARGS="
set "PARSE_RUN_ARGS="

:parse_args
if "%~1"=="" goto args_done
if defined PARSE_RUN_ARGS (
  set "RUN_ARGS=!RUN_ARGS! %~1"
  shift
  goto parse_args
)
if "%~1"=="--" (
  set "PARSE_RUN_ARGS=1"
  shift
  goto parse_args
)
if /I "%~1"=="--skip-image" (
  set "BUILD_ARGS=!BUILD_ARGS! --skip-image"
  shift
  goto parse_args
)
echo Unknown option: %~1
echo Supported build options: --skip-image
echo Use -- before avrsim arguments.
exit /b 1

:args_done
call "%SCRIPT_DIR%build_mega_vm_firmware.cmd" !BUILD_ARGS!
if errorlevel 1 exit /b %ERRORLEVEL%

if defined RUN_ARGS (
  call "%SCRIPT_DIR%run_mega_vm_teraterm.cmd" -- !RUN_ARGS!
) else (
  call "%SCRIPT_DIR%run_mega_vm_teraterm.cmd"
)
pause
exit /b %ERRORLEVEL%
