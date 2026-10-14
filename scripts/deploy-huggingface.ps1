param(
    [string]$SourceRepository = "C:\Users\ckakalou\PycharmProjects\SDoH_Screener",
    [string]$DeploymentRepository = "C:\Users\ckakalou\PycharmProjects\SDoH_Screener_HF_Deploy"
)

$ErrorActionPreference = "Stop"

$sourceBranch = "redesign/react-fastapi"
$githubUrl = "https://github.com/ckakalou/SDoH_Screener.git"
$huggingFaceUrl = "https://huggingface.co/spaces/ckakalou/Healie_SDoHScreener"

$excludedPngFiles = @(
    "frontend/public/healie-favicon.png",
    "frontend/public/healie_final_official_logo_full.png",
    "frontend/public/healie_final_official_logo_trans_crop.png",
    "frontend/src/assets/hero.png",
    "sdoh_favicon.png"
)

function Invoke-Git {
    param(
        [string]$Repository,
        [string[]]$GitArguments
    )

    & git -C $Repository @GitArguments

    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git -C `"$Repository`" $($GitArguments -join ' ')"
    }
}

if (-not (Test-Path "$SourceRepository\.git")) {
    throw "Source repository was not found at $SourceRepository"
}

if (-not (Test-Path "$DeploymentRepository\.git")) {
    throw "Hugging Face deployment repository was not found at $DeploymentRepository"
}

$sourceStatus = & git -C $SourceRepository status --porcelain

if ($sourceStatus) {
    throw "The source repository has uncommitted changes. Commit them before deploying."
}

$currentBranch = (& git -C $SourceRepository branch --show-current).Trim()

if ($currentBranch -ne $sourceBranch) {
    throw "The source repository must be on $sourceBranch. Current branch: $currentBranch"
}

Invoke-Git $SourceRepository @(
    "fetch",
    "origin",
    $sourceBranch
)

$sourceHead = (& git -C $SourceRepository rev-parse "HEAD").Trim()
$githubHead = (& git -C $SourceRepository rev-parse "origin/$sourceBranch").Trim()

if ($sourceHead -ne $githubHead) {
    throw "The source branch is not synchronized with GitHub. Push or pull before deploying."
}

$deploymentStatus = & git -C $DeploymentRepository status --porcelain

if ($deploymentStatus) {
    throw "The Hugging Face deployment repository has uncommitted changes."
}

$hfRemote = & git -C $DeploymentRepository remote get-url hf 2>$null

if ($LASTEXITCODE -ne 0) {
    Invoke-Git $DeploymentRepository @(
        "remote",
        "add",
        "hf",
        $huggingFaceUrl
    )
}
elseif ($hfRemote.Trim() -ne $huggingFaceUrl) {
    throw "The deployment repository's hf remote points to an unexpected URL."
}

$sourceRemote = & git -C $DeploymentRepository remote get-url source 2>$null

if ($LASTEXITCODE -ne 0) {
    Invoke-Git $DeploymentRepository @(
        "remote",
        "add",
        "source",
        $githubUrl
    )
}
elseif ($sourceRemote.Trim() -ne $githubUrl) {
    throw "The deployment repository's source remote points to an unexpected URL."
}

Write-Host "Fetching the latest GitHub version..."
Invoke-Git $DeploymentRepository @(
    "fetch",
    "source",
    $sourceBranch
)

Write-Host "Synchronizing the deployment snapshot..."
Invoke-Git $DeploymentRepository @(
    "rm",
    "-r",
    "--ignore-unmatch",
    "."
)

Invoke-Git $DeploymentRepository @(
    "checkout",
    "source/$sourceBranch",
    "--",
    "."
)

foreach ($relativePath in $excludedPngFiles) {
    $fullPath = Join-Path $DeploymentRepository $relativePath

    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
    }
}

Invoke-Git $DeploymentRepository @("add", "-A")

$remainingPngFiles = Get-ChildItem `
    -Path $DeploymentRepository `
    -Recurse `
    -File `
    -Filter "*.png" |
    Where-Object {
        $_.FullName -notmatch "\\.git\\|\\node_modules\\|\\dist\\"
    }

if ($remainingPngFiles) {
    $paths = $remainingPngFiles.FullName -join [Environment]::NewLine
    throw "PNG files remain in the deployment snapshot:`n$paths"
}

& git -C $DeploymentRepository diff --cached --check

if ($LASTEXITCODE -ne 0) {
    throw "git diff --cached --check failed."
}

& git -C $DeploymentRepository diff --cached --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "Hugging Face is already up to date."
    exit 0
}

$shortSourceCommit = (& git -C $SourceRepository rev-parse --short HEAD).Trim()

Invoke-Git $DeploymentRepository @(
    "commit",
    "-m",
    "Deploy GitHub revision $shortSourceCommit"
)

Write-Host "Pushing the deployment to Hugging Face..."
Invoke-Git $DeploymentRepository @(
    "push",
    "hf",
    "main:main"
)

Write-Host "Deployment pushed successfully."
Write-Host "https://huggingface.co/spaces/ckakalou/Healie_SDoHScreener"