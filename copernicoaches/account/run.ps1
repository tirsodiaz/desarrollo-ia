param(
    [string]$DataDir = ".\account\data",
    [switch]$VerboseMode,
    [string]$PythonExe = "",
    [switch]$Daemon,
    [int]$Interval = 10
)

$root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path -Path $root)) {
    Write-Error "No se pudo resolver la raíz del repositorio."
    exit 1
}

Set-Location $root
$env:PYTHONPATH = ".\account"

if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $cmd = @("py", "-3", "-m", "check_account_balance", "--data-dir", $DataDir)
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $cmd = @("python", "-m", "check_account_balance", "--data-dir", $DataDir)
    }
    else {
        Write-Error "No se encontró un ejecutable de Python (py o python)."
        exit 1
    }
}
else {
    $cmd = @($PythonExe, "-m", "check_account_balance", "--data-dir", $DataDir)
}

if ($VerboseMode) {
    $cmd += "--verbose"
}

if ($Daemon) {
    $cmd += "--daemon"
    $cmd += "--interval"
    $cmd += "$Interval"
}

$exe = $cmd[0]
$args = @()
if ($cmd.Count -gt 1) {
    $args = $cmd[1..($cmd.Count - 1)]
}

& $exe @args
exit $LASTEXITCODE
