# scripts/update_all.ps1
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Refreshing report..." -ForegroundColor Cyan

# Paths
$reportScript = Join-Path $repoRoot "03_Python\make_report.py"
$pdfDir       = Join-Path $repoRoot "06_Reports"
$excelDir     = Join-Path $repoRoot "04_Excel"

if (-not (Test-Path ".git")) { throw "Not a git repo: $repoRoot" }
if (-not (Test-Path $reportScript)) { throw "Report script not found: $reportScript" }

# Build artifacts (PDF + Excel snapshot from your Python script)
py -3.13 $reportScript

git --version | Out-Null

# Stage PDF(s) – use RELATIVE globs for git add
if (Test-Path $pdfDir)   { git add 06_Reports/*.pdf 2>$null }

# Stage Excel(s) only if any exist
$excelFiles = @()
if (Test-Path $excelDir) { $excelFiles = Get-ChildItem $excelDir -Filter *.xlsx -File -ErrorAction SilentlyContinue }
if ($excelFiles.Count -gt 0) { git add 04_Excel/*.xlsx 2>$null }

# Commit if anything is staged
git diff --cached --quiet
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
if ($LASTEXITCODE -ne 0) {
    git commit -m "chore(artifacts): refresh PDF + KPI Excel ($timestamp)"
    Write-Host "Committed changes." -ForegroundColor Yellow
} else {
    Write-Host "Nothing to commit (no artifact changes detected)." -ForegroundColor DarkGray
}

# Push
git push

Write-Host "Done. Latest PDF + Excel pushed." -ForegroundColor Green

