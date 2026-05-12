param(
    [string]$RepoRoot,
    [string]$PipeName = "PDR16_XT_UART0",
    [string]$BridgeExe,
    [string]$FirmwarePath,
    [string]$BridgeLogPath,
    [string]$BuildOrderPath,
    [string]$TranscriptPath,
    [int]$PromptTimeoutMs = 5000,
    [int]$QuietDrainMs = 300,
    [int]$InterLineDelayMs = 0,
    [switch]$ProbeWords
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-TranscriptLine {
    param(
        [System.Text.StringBuilder]$Buffer,

        [string]$Text
    )

    if ($null -eq $Text) {
        return
    }
    [void]$Buffer.Append($Text)
    if ($Text.Length -eq 0 -or -not $Text.EndsWith("`n")) {
        [void]$Buffer.Append("`r`n")
    }
}

function Format-ConsoleText {
    param(
        [string]$Text
    )

    if ($null -eq $Text) {
        return ""
    }

    return $Text.Replace("`r`n", "`n").Replace("`r", "`n").Replace([string][char]8, "")
}

function Emit-ConsoleText {
    param(
        [Parameter(Mandatory = $true)]
        [System.Text.StringBuilder]$LineBuffer,

        [string]$Text
    )

    if ([string]::IsNullOrEmpty($Text)) {
        return
    }

    foreach ($ch in $Text.ToCharArray()) {
        switch ($ch) {
            "`r" {
                if ($LineBuffer.Length -gt 0) {
                    Write-Host $LineBuffer.ToString()
                    $LineBuffer.Clear() | Out-Null
                } else {
                    Write-Host ""
                }
                continue
            }
            "`n" {
                if ($LineBuffer.Length -gt 0) {
                    Write-Host $LineBuffer.ToString()
                    $LineBuffer.Clear() | Out-Null
                } else {
                    Write-Host ""
                }
                continue
            }
            ([char]8) {
                if ($LineBuffer.Length -gt 0) {
                    [void]$LineBuffer.Remove($LineBuffer.Length - 1, 1)
                }
                continue
            }
            ([char]17) { continue }
            ([char]19) { continue }
            default {
                if ([int][char]$ch -ge 0x20) {
                    [void]$LineBuffer.Append($ch)
                }
            }
        }
    }
}

function Drain-PipeOutput {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Pipes.NamedPipeClientStream]$Pipe,

        [Parameter(Mandatory = $true)]
        [int]$PromptTimeoutMs,

        [Parameter(Mandatory = $true)]
        [int]$QuietDrainMs,

        [Parameter(Mandatory = $true)]
        [System.Text.StringBuilder]$ConsoleLineBuffer,

        [switch]$RequireXon
    )

    $output = New-Object System.Text.StringBuilder
    $deadline = [DateTime]::UtcNow.AddMilliseconds($PromptTimeoutMs)
    $quietDeadline = [DateTime]::UtcNow.AddMilliseconds($QuietDrainMs)
    $buffer = New-Object byte[] 4096
    $sawXon = $false

    while ([DateTime]::UtcNow -lt $deadline) {
        $readTask = $Pipe.ReadAsync($buffer, 0, $buffer.Length)
        $waitTask = [System.Threading.Tasks.Task]::Delay(10)
        $completed = [System.Threading.Tasks.Task]::WaitAny(@($readTask, $waitTask))

        if ($completed -eq 0) {
            $read = $readTask.Result
            if ($read -gt 0) {
                $chunk = [System.Text.Encoding]::UTF8.GetString($buffer, 0, $read)
                if ($chunk.IndexOf([char]17) -ge 0) {
                    $sawXon = $true
                }
                $chunk = $chunk.Replace([string][char]17, "").Replace([string][char]19, "")
                [void]$output.Append($chunk)
                Emit-ConsoleText -LineBuffer $ConsoleLineBuffer -Text $chunk
                $quietDeadline = [DateTime]::UtcNow.AddMilliseconds($QuietDrainMs)
                if ($RequireXon -and $sawXon) {
                    break
                }
                continue
            }
        }

        if (-not $RequireXon -and [DateTime]::UtcNow -ge $quietDeadline) {
            break
        }

        if ($RequireXon -and $sawXon -and [DateTime]::UtcNow -ge $quietDeadline) {
            break
        }
    }

    return [pscustomobject]@{
        Text = $output.ToString()
        SawXon = $sawXon
    }
}

function Send-Line {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Pipes.NamedPipeClientStream]$Pipe,

        [Parameter(Mandatory = $true)]
        [AllowEmptyString()]
        [string]$Line
    )

    if ($null -eq $Line) {
        $Line = ""
    }

    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Line + "`r")
    $Pipe.Write($bytes, 0, $bytes.Length)
    $Pipe.Flush()
}

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
}
if (-not $PSBoundParameters.ContainsKey('PipeName') -or [string]::IsNullOrWhiteSpace($PipeName)) {
    $PipeName = "PDR16_XT_UART0_{0}_{1}" -f $PID, ([DateTime]::UtcNow.Ticks)
}
if (-not $BridgeExe) {
    $BridgeExe = Join-Path $RepoRoot "tools\sim\bin\MegaVmTeraTerm\mega_vm_teraterm.exe"
}
if (-not $FirmwarePath) {
    $FirmwarePath = Join-Path $RepoRoot "firmware\mega\pdr_vm\.build-legacy\pdr_vm.ino.elf"
    if (-not (Test-Path -LiteralPath $FirmwarePath)) {
        $FirmwarePath = Join-Path $RepoRoot "firmware\mega\pdr_vm\.build-legacy\pdr_vm.ino.hex"
    }
}
if (-not $BridgeLogPath) {
    $BridgeLogPath = Join-Path $RepoRoot "tools\sim\logs\forth_library_bridge.log"
}
if (-not $BuildOrderPath) {
    $BuildOrderPath = Join-Path $RepoRoot "tools\forth\Forth Sources\build_order.txt"
}
if (-not $TranscriptPath) {
    $TranscriptPath = Join-Path $RepoRoot "tools\sim\logs\forth_library_compile.txt"
}

$buildOrderPath = (Resolve-Path -LiteralPath $BuildOrderPath).Path
$sourceRoot = Split-Path -Parent $buildOrderPath
$firmwarePath = (Resolve-Path -LiteralPath $FirmwarePath).Path
$bridgeExePath = (Resolve-Path -LiteralPath $BridgeExe).Path
$bridgeLogDir = Split-Path -Parent $BridgeLogPath
$transcriptDir = Split-Path -Parent $TranscriptPath
if (-not (Test-Path -LiteralPath $bridgeLogDir)) {
    New-Item -ItemType Directory -Path $bridgeLogDir | Out-Null
}
if (-not (Test-Path -LiteralPath $transcriptDir)) {
    New-Item -ItemType Directory -Path $transcriptDir | Out-Null
}

$bridgeArgs = @(
    "--pipe-name", $PipeName,
    "--firmware", $firmwarePath,
    "--mcu", "atmega2560",
    "--freq", "16000000",
    "--log-path", $BridgeLogPath
)

$bridge = $null
$pipe = $null
$transcript = New-Object System.Text.StringBuilder
$consoleLineBuffer = New-Object System.Text.StringBuilder

try {
    Write-Host "Starting bridge:"
    Write-Host "  $bridgeExePath"
    $bridge = Start-Process -FilePath $bridgeExePath -ArgumentList $bridgeArgs -WorkingDirectory $RepoRoot -PassThru -WindowStyle Hidden

    $pipe = [System.IO.Pipes.NamedPipeClientStream]::new(".", $PipeName, [System.IO.Pipes.PipeDirection]::InOut, [System.IO.Pipes.PipeOptions]::None)
    $pipe.Connect(10000)

    Write-TranscriptLine -Buffer $transcript -Text ("[bridge] connected to \\.\pipe\{0}" -f $PipeName)
    Write-Host ("[bridge] connected to \\.\pipe\{0}" -f $PipeName)

    $startup = Drain-PipeOutput -Pipe $pipe -PromptTimeoutMs $PromptTimeoutMs -QuietDrainMs $QuietDrainMs -ConsoleLineBuffer $consoleLineBuffer
    if ($startup.Text.Length -gt 0) {
        Write-TranscriptLine -Buffer $transcript -Text $startup.Text
    }

    $sourceFiles = Get-Content -LiteralPath $buildOrderPath | ForEach-Object { $_.Trim() } | Where-Object { $_ -and -not $_.StartsWith("#") }
    foreach ($sourceName in $sourceFiles) {
        $sourcePath = Join-Path $sourceRoot $sourceName
        $resolvedSourcePath = (Resolve-Path -LiteralPath $sourcePath).Path

        Write-Host ""
        Write-Host ("Compiling {0}" -f $resolvedSourcePath)
        Write-TranscriptLine -Buffer $transcript -Text ""
        Write-TranscriptLine -Buffer $transcript -Text ("=== {0} ===" -f $resolvedSourcePath)

        $lines = [System.IO.File]::ReadAllLines($resolvedSourcePath)
        for ($index = 0; $index -lt $lines.Length; $index++) {
            $line = $lines[$index]
            Write-Host ("  line {0}/{1}" -f ($index + 1), $lines.Length)
            Send-Line -Pipe $pipe -Line $line
            if ($InterLineDelayMs -gt 0) {
                Start-Sleep -Milliseconds $InterLineDelayMs
            }

            $response = Drain-PipeOutput -Pipe $pipe -PromptTimeoutMs $PromptTimeoutMs -QuietDrainMs $QuietDrainMs -ConsoleLineBuffer $consoleLineBuffer -RequireXon
            if ($response.Text.Length -gt 0) {
                Write-TranscriptLine -Buffer $transcript -Text $response.Text
            }

            if (-not $response.SawXon) {
                throw "Timed out waiting for XON after sending line $($index + 1) of $resolvedSourcePath."
            }

            if ($response.Text -match "VM fault" -or $response.Text -match "fault\s+\d+") {
                throw "Target reported a VM fault while compiling $resolvedSourcePath."
            }
        }
    }

    if ($ProbeWords) {
        Write-Host ""
        Write-Host "Probing WORDS"
        Write-TranscriptLine -Buffer $transcript -Text ""
        Write-TranscriptLine -Buffer $transcript -Text "=== WORDS ==="
        Send-Line -Pipe $pipe -Line "WORDS"
        $probe = Drain-PipeOutput -Pipe $pipe -PromptTimeoutMs $PromptTimeoutMs -QuietDrainMs $QuietDrainMs -ConsoleLineBuffer $consoleLineBuffer -RequireXon
        if ($probe.Text.Length -gt 0) {
            Write-TranscriptLine -Buffer $transcript -Text $probe.Text
        }
    }
}
finally {
    if ($pipe -ne $null) {
        $pipe.Dispose()
    }
    if ($bridge -ne $null -and -not $bridge.HasExited) {
        try {
            Stop-Process -Id $bridge.Id -Force
        }
        catch {
            # Best-effort cleanup only.
        }
    }
}

[System.IO.File]::WriteAllText($TranscriptPath, $transcript.ToString(), [System.Text.Encoding]::UTF8)
Write-Host ""
Write-Host ("Wrote transcript to {0}" -f $TranscriptPath)
