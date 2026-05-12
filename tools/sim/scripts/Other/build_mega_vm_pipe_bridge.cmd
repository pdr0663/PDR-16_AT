@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%..\..\..\.."
set "PORTABLE_ROOT=C:\avrsim-portable"
set "GCC_EXE=%PORTABLE_ROOT%\msys64\mingw64\bin\gcc.exe"
set "SIMAVR_INCLUDE=%PORTABLE_ROOT%\out\include"
set "SIMAVR_LIB=%PORTABLE_ROOT%\out\lib"
set "SOURCE=%REPO_ROOT%\tools\sim\src\mega_vm_teraterm.c"
set "OUT_DIR=%REPO_ROOT%\tools\sim\bin\MegaVmTeraTerm"
set "OUT_EXE=%OUT_DIR%\mega_vm_teraterm.exe"

if not exist "%SOURCE%" (
  echo Missing bridge source: "%SOURCE%"
  exit /b 1
)

if not exist "%GCC_EXE%" (
  echo Missing portable MinGW compiler: "%GCC_EXE%"
  exit /b 1
)

if not exist "%SIMAVR_INCLUDE%\simavr\sim_avr.h" (
  echo Missing simavr headers: "%SIMAVR_INCLUDE%\simavr\sim_avr.h"
  exit /b 1
)

if not exist "%SIMAVR_LIB%\libsimavr.a" (
  echo Missing simavr library: "%SIMAVR_LIB%\libsimavr.a"
  exit /b 1
)

if not exist "%OUT_DIR%" mkdir "%OUT_DIR%" >nul 2>nul

set "PATH=%PORTABLE_ROOT%\msys64\mingw64\bin;%PATH%"

"%GCC_EXE%" -std=gnu11 -O2 -Wall -Wextra -Wno-unused-parameter -Wno-unused-function -DWIN32_LEAN_AND_MEAN ^
  -I"%REPO_ROOT%\tools\sim\src" -I"%SIMAVR_INCLUDE%" ^
  "%SOURCE%" -L"%SIMAVR_LIB%" -lsimavr -ldwarf -lelf -ladvapi32 -lws2_32 -o "%OUT_EXE%"
