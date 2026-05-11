# avrsim Workspace

This directory is intentionally a local simulator workspace.  The `simavr`
source tree is present locally here so the simulator can be built either from
Linux/WSL or from Windows/MSYS2.

```sh
tools/sim/scripts/bootstrap_simavr.sh
```

The bootstrap script clones `https://github.com/buserror/simavr.git` into
`avrsim/simavr`, builds the core simulator library, and builds the
`examples/parts` library needed by the PDR-16/AT PTY harness.

After bootstrapping:

```sh
tools/sim/scripts/build_mega_vm_pty.sh
tools/sim/scripts/run_mega_vm_pty.sh
```

In another shell, connect to the UART PTY with:

```sh
tools/sim/scripts/run_mega_vm_picocom.sh
```

If `simavr` lives somewhere else, set `SIMAVR_ROOT` to the checkout root before
running the build script.

For Windows builds, see [README.windows.md](README.windows.md).
