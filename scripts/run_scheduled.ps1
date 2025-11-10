# scripts/run_scheduled.ps1
$ErrorActionPreference = "Stop"

# Resolve repo root from this script’s location
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

# Ensure logs dir exists
$logDir = Join-Path $repoRoot "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp  = Get-Date -Format "yyyy-MM-dd_HH-mm"
$log    = Join-Path $logDir "run_$stamp.log"

# Run the existing orchestrator and tee output to a log
try {
  "=== Run start: $(Get-Date -Format u) ===" | Tee-Object -FilePath $log
  .\scripts\update_all.ps1 2>&1 | Tee-Object -FilePath $log -Append
  "=== Run end: $(Get-Date -Format u) ===" | Tee-Object -FilePath $log -Append
} catch {
  "!!! ERROR: $($_.Exception.Message)" | Tee-Object -FilePath $log -Append
  exit 1
}
