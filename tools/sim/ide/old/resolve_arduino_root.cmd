@echo off
setlocal EnableExtensions EnableDelayedExpansion

if defined ARDUINO_LEGACY_ROOT (
  if exist "!ARDUINO_LEGACY_ROOT!\arduino-builder.exe" (
    echo !ARDUINO_LEGACY_ROOT!
    exit /b 0
  )
  >&2 echo ARDUINO_LEGACY_ROOT is set but does not contain arduino-builder.exe:
  >&2 echo   "!ARDUINO_LEGACY_ROOT!"
  exit /b 1
)

call set "CANDIDATE=%%ProgramFiles(x86)%%\Arduino"
if exist "!CANDIDATE!\arduino-builder.exe" (
  echo !CANDIDATE!
  exit /b 0
)

for /f "delims=" %%I in ('where arduino-builder.exe 2^>nul') do (
  for %%J in ("%%~dpI.") do (
    echo %%~fJ
    exit /b 0
  )
)

>&2 echo Could not find the legacy Arduino IDE root.
>&2 echo Install Arduino IDE 1.8.x or set ARDUINO_LEGACY_ROOT.
exit /b 1
pause