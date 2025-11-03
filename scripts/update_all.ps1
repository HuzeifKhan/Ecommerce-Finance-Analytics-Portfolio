# scripts/update_all.ps1
# One-click refresh: rebuild PDF report and push changes to GitHub

$ErrorActionPreference = "Stop"

# Correct: repo root is ONE level above /scripts
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Refreshing report..."

# Resolve paths safely
$reportScript = Join-Path $repoRoot "03_Python\make_report.py"
$pdfGlob      = Join-Path $repoRoot "06_Reports\*.pdf"

# Sanity checks
if (-not (Test-Path ".git")) {
    throw "This folder is not a git repository: $repoRoot"
}
if (-not (Test-Path $reportScript)) {
    throw "Report script not found: $reportScript"
}

# Run the Python report generator (use 'python' if your py launcher isn't set)
py -3.13 $reportScript

# Ensure Git is installed
git --version | Out-Null

# Stage the updated PDF(s)
git add $pdfGlob

# Create a timestamped commit message
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
$commitMessage = "chore(report): refresh PDF ($timestamp)"

# Try to commit; if nothing staged, commit returns non-zero
& git commit -m $commitMessage 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nothing to commit (no PDF changes detected)."
} else {
    Write-Host "Committed: $commitMessage"
}

# Push (safe even if there was nothing new)
git push

Write-Host "Done. Latest report pushed."
