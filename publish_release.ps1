# StarsailX - publish installer to GitHub Releases
# Usage: .\publish_release.ps1
# Prereq: .\build.ps1 done, gh auth login

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Version = "2.2.2"
$Tag = "v$Version"
$SetupName = "StarsailX_Setup_$Version.exe"
$SetupPath = Join-Path $Root "release\$SetupName"
$Repo = "IMAF7/StarsailX"

function Find-Gh {
    $gh = Get-Command gh -ErrorAction SilentlyContinue
    if ($gh) { return $gh.Source }
    $portable = Join-Path $env:TEMP "gh-cli\bin\gh.exe"
    if (Test-Path $portable) { return $portable }
    throw "gh CLI not found. Install GitHub CLI or run: winget install GitHub.cli"
}

if (-not (Test-Path $SetupPath)) {
    throw "Installer missing: $SetupPath`nRun .\build.ps1 first."
}

$Gh = Find-Gh
Write-Host "GitHub CLI: $Gh"

& $Gh auth status 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "gh not logged in. Run: gh auth login"
}

Push-Location $Root
try {
    if (-not (Test-Path ".git")) {
        & "C:\Program Files\Git\bin\git.exe" init
        & "C:\Program Files\Git\bin\git.exe" branch -M main
    }

    $remoteUrl = "https://github.com/$Repo.git"
    $remotes = & "C:\Program Files\Git\bin\git.exe" remote 2>$null
    if ($remotes -notcontains "origin") {
        & "C:\Program Files\Git\bin\git.exe" remote add origin $remoteUrl
    }

    $repoExists = & $Gh repo view $Repo --json name -q .name 2>$null
    if (-not $repoExists) {
        Write-Host "Creating repo $Repo ..."
        & $Gh repo create $Repo --public --source=. --remote=origin --description "Starsail multi-account client" --push
    }

    Write-Host "Publishing $Tag ..."
    $null = & $Gh release view $Tag --repo $Repo 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Release $Tag exists; uploading installer ..."
        & $Gh release upload $Tag $SetupPath --repo $Repo --clobber
    }
    else {
        $notes = @"
## StarsailX $Version

- Fix emoji inserting at end of message after typing text
- Restore account context menu: add/edit group
- Faster group management panel; smoother download page
- Quote preview and image copy improvements

Download page: https://imaf7.github.io/StarsailX/download/
"@
        & $Gh release create $Tag $SetupPath --repo $Repo --title "StarsailX $Version" --notes $notes
    }

    Write-Host ""
    Write-Host "Publish done."
    Write-Host "  Installer: https://github.com/$Repo/releases/latest/download/$SetupName"
    Write-Host "  Pages: download\index.html"
}
finally {
    Pop-Location
}
