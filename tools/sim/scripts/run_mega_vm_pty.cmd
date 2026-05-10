@echo off
setlocal

set "WSL_SCRIPT=/mnt/c/Users/Paul/PDR-16_AT/tools/sim/scripts/run_mega_vm_pty.sh"
wsl bash -lc "'%WSL_SCRIPT%'"
