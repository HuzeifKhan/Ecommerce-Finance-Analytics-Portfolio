# scripts/update_all.ps1
# Pull latest, rebuild PDF + Excel snapshot, stage, commit, push

$ErrorActionPreference = "Stop"

function Say($msg, $color='Gray') { Write-Host $msg -ForegroundColor $color }

# Resolve repo root (one level above /scripts)
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

# Paths
$reportScript = Join-Path $repoRoot "03_Python\make_report.py"
$pdfDir       = Join-Path $repoRoot "06_Reports"
$excelDir     = Join-Path $repoRoot "04_Excel"

# --- Interpreter selection (no activation; avoids ExecutionPolicy issues)
$VenvPy  = Join-Path $repoRoot ".venv\Scripts\python.exe"  # your local 3.13.7 venv
$Py      = $null
$PyArgs  = @()

if (Test-Path $VenvPy) {
    $Py = $VenvPy
    Say "Using venv Python: $Py" "DarkGray"
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $Py = "py"
    $PyArgs = @("-3.11")   # aligned with your GitHub Actions runner
    Say "Using Python via launcher: py $($PyArgs -join ' ')" "DarkGray"
}
else {
    $Py = "python"
    Say "Using system Python on PATH" "DarkGray"
}

# Basic checks
if (-not (Test-Path ".git")) { throw "Not a git repository: $repoRoot" }
if (-not (Test-Path $reportScript)) { throw "Report script not found: $reportScript" }

# Ensure git is available
& git --version | Out-Null

# Ensure binary merge rules (avoid text merges on PDFs/XLSX/PNGs)
if (-not (Test-Path ".gitattributes")) { '' | Out-File ".gitattributes" -Encoding utf8 }
$attrs = Get-Content ".gitattributes" -ErrorAction SilentlyContinue
$needed = @("*.pdf binary","*.xlsx binary","*.png binary","*.jpg binary","*.jpeg binary")
foreach ($line in $needed) {
    if ($attrs -notcontains $line) { Add-Content ".gitattributes" $line }
}
git add .gitattributes 2>$null
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { git commit -m "chore: ensure binary merge rules in .gitattributes" }

# Pull latest (rebase)
Say "Pulling latest changes (rebase)..." "Cyan"
git fetch origin
try { git pull --rebase origin main } catch {}

# If there are merge conflicts on binary files, keep ours
$conflicted = (& git diff --name-only --diff-filter=U) 2>$null
if ($conflicted) {
    $binExt = @(".pdf",".xlsx",".png",".jpg",".jpeg")
    foreach ($f in $conflicted) {
        if ($binExt -contains ([IO.Path]::GetExtension($f).ToLower())) {
            Say "Auto-resolving binary conflict (keeping ours): $f" "Yellow"
            git checkout --ours -- "$f"
            git add -- "$f"
        } else {
            throw "Manual conflict encountered: $f"
        }
    }
    git rebase --continue
    Say "Rebase completed after conflict resolution." "Green"
}

# Log interpreter info (helpful for debugging)
& $Py @PyArgs "-c" "import sys, platform; print('Python used:', sys.version.replace('\n',' ')); print('Platform:', platform.platform())"

# Build artifacts
Say "Building report and Excel snapshot..." "Cyan"
& $Py @PyArgs "$reportScript"
if ($LASTEXITCODE -ne 0) {
    throw "Report build failed with exit code $LASTEXITCODE"
}

# Stage artifacts using explicit relative paths (avoid wildcard issues)
# PDFs
if (Test-Path $pdfDir) {
    $pdfs = Get-ChildItem $pdfDir -Filter *.pdf -File -ErrorAction SilentlyContinue
    foreach ($f in $pdfs) {
        $rel = Resolve-Path -Relative $f.FullName
        & git add -- "$rel" 2>$null
    }
}

# Excel
if (Test-Path $excelDir) {
    $excels = Get-ChildItem $excelDir -Filter *.xlsx -File -ErrorAction SilentlyContinue
    foreach ($f in $excels) {
        $rel = Resolve-Path -Relative $f.FullName
        & git add -- "$rel" 2>$null
    }
}

# Cohort CSV
$cohortCsv = Join-Path $repoRoot "01_Data\processed\retention_cohorts.csv"
if (Test-Path $cohortCsv) {
    $rel = Resolve-Path -Relative $cohortCsv
    & git add -- "$rel" 2>$null
}

# Analysis figures (PNGs)
$figDir = Join-Path $repoRoot "03_Analysis\figures"
if (Test-Path $figDir) {
    $pngs = Get-ChildItem $figDir -Filter *.png -File -ErrorAction SilentlyContinue
    foreach ($f in $pngs) {
        $rel = Resolve-Path -Relative $f.FullName
        & git add -- "$rel" 2>$null
    }
}

# Commit if anything staged
git diff --cached --quiet
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
if ($LASTEXITCODE -ne 0) {
    $msg = "chore(artifacts): refresh PDF + KPI Excel ($timestamp)"
    & git commit -m $msg
    Say "Committed: $msg" "Yellow"
} else {
    Say "Nothing to commit (no artifact changes detected)." "DarkGray"
}

# Push
& git push
Say "Done. Latest PDF and Excel pushed." "Green"
