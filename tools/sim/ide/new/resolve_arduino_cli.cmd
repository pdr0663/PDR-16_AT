@echo off
setlocal EnableExtensions

if defined ARDUINO_CLI_EXE (
  if exist "%ARDUINO_CLI_EXE%" (
    echo %ARDUINO_CLI_EXE%
    exit /b 0
  )
  >&2 echo ARDUINO_CLI_EXE is set but does not exist:
  >&2 echo   "%ARDUINO_CLI_EXE%"
  exit /b 1
)

set "CANDIDATE=%ProgramFiles%\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe"
if exist "%CANDIDATE%" (
  echo %CANDIDATE%
  exit /b 0
)

for /f "delims=" %%I in ('where arduino-cli.exe 2^>nul') do (
  echo %%I
  exit /b 0
)

>&2 echo Could not find arduino-cli.exe.
>&2 echo Install Arduino CLI, install Arduino IDE, or set ARDUINO_CLI_EXE.
exit /b 1
