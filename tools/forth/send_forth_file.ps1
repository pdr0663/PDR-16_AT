param(
    [Parameter(Mandatory = $true)]
    [string]$Port,

    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [int]$BaudRate = 115200,
    [int]$InterLineDelayMs = 25,
    [int]$PromptTimeoutMs = 1500,
    [int]$StartupDelayMs = 250
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.IO.Ports

function Read-UntilSettled {
    param(
        [Parameter(Mandatory = $true)]
        [System.IO.Ports.SerialPort]$SerialPort,

        [Parameter(Mandatory = $true)]
        [int]$TimeoutMs
    )

    $deadline = [DateTime]::UtcNow.AddMilliseconds($TimeoutMs)
    $buffer = New-Object System.Text.StringBuilder
    $sawData = $false
    $quietDeadline = $null

    while ([DateTime]::UtcNow -lt $deadline) {
        $chunk = $SerialPort.ReadExisting()
        if ($chunk.Length -gt 0) {
            [void]$buffer.Append($chunk)
            $sawData = $true
            $quietDeadline = [DateTime]::UtcNow.AddMilliseconds(120)
        } elseif ($sawData -and $quietDeadline -ne $null -and [DateTime]::UtcNow -ge $quietDeadline) {
            break
        } else {
            Start-Sleep -Milliseconds 10
        }
    }

    return $buffer.ToString()
}

function Normalize-ForDisplay {
    param([string]$Text)

    return $Text.Replace("`r", "\r").Replace("`n", "\n`n")
}

$resolvedSourcePath = (Resolve-Path -LiteralPath $SourcePath).Path
$lines = [System.IO.File]::ReadAllLines($resolvedSourcePath)

$serial = [System.IO.Ports.SerialPort]::new($Port, $BaudRate, [System.IO.Ports.Parity]::None, 8, [System.IO.Ports.StopBits]::One)
$serial.Handshake = [System.IO.Ports.Handshake]::None
$serial.ReadTimeout = 50
$serial.WriteTimeout = 5000
$serial.NewLine = "`r"
$serial.DtrEnable = $false
$serial.RtsEnable = $false

try {
    $serial.Open()
    Start-Sleep -Milliseconds $StartupDelayMs
    $serial.DiscardInBuffer()
    $serial.DiscardOutBuffer()

    Write-Host "Sending $resolvedSourcePath to $Port at $BaudRate baud"

    for ($index = 0; $index -lt $lines.Length; $index++) {
        $lineNumber = $index + 1
        $line = $lines[$index]

        $serial.Write($line)
        $serial.Write("`r")

        if ($InterLineDelayMs -gt 0) {
            Start-Sleep -Milliseconds $InterLineDelayMs
        }

        $response = Read-UntilSettled -SerialPort $serial -TimeoutMs $PromptTimeoutMs
        if ($response.Length -gt 0) {
            Write-Host ("[{0}] {1}" -f $lineNumber, (Normalize-ForDisplay -Text $response))
        }

        if ($response -match "VM fault" -or $response -match "fault\s+\d+") {
            throw "Target reported a VM fault after line $lineNumber."
        }
    }
}
finally {
    if ($serial.IsOpen) {
        $serial.Close()
    }
    $serial.Dispose()
}
