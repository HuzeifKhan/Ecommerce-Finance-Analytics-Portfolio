# scripts/update_all.ps1
# One-click refresh: rebuilds PDF report and pushes changes to GitHub

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

Write-Host "🔁 Refreshing report..." -ForegroundColor Cyan
py -3.13 03_Python\make_report.py

# Ensure git is available
git --version | Out-Null

git add 06_Reports/*.pdf
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
git commit -m "chore(report): refresh PDF ($timestamp)" 2>$null || Write-Host "ℹ️ Nothing to commit."
git push

Write-Host "✅ Done. Latest report pushed." -ForegroundColor Green
