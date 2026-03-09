<# 
Usage:
  pwsh scripts/skill-maintenance.ps1
  pwsh scripts/skill-maintenance.ps1 -AutoFix
  pwsh scripts/skill-maintenance.ps1 -AutoFix -Version 2026.03.12
#>
[CmdletBinding()]
param(
  [switch]$AutoFix,
  [string]$Version
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$versionPath = Join-Path $root 'VERSION'
$skillPath = Join-Path $root 'SKILL.md'
$readmePath = Join-Path $root 'README.md'
$execPath = Join-Path $root 'references\skill-execution.md'
$artifact = Join-Path $root 'references\skill-artifacts.md'
$cli = Join-Path $root 'references\harness-cli.md'
$advancedPath = Join-Path $root 'references\execution-advanced.md'
$skillConfigSections = @($readmePath, $artifact)
$problems = [System.Collections.Generic.List[string]]::new()
$notes = [System.Collections.Generic.List[string]]::new()

function Add-Fail {
  param([string]$Message)
  $problems.Add($Message)
}

function Add-Pass {
  param([string]$Message)
  $notes.Add("[PASS] $Message")
}

function Ensure-VersionSync {
  param([string]$TargetVersion)
  $bump = Join-Path $PSScriptRoot 'bump-version.ps1'
  & (Resolve-Path $bump) -Version $TargetVersion | Out-Null
}

function Count-Pattern {
  param([string[]]$Files, [string]$Pattern)
  $hits = 0
  foreach ($file in $Files) {
    $hits += (Select-String -Path $file -Pattern $Pattern -SimpleMatch | Measure-Object).Count
  }
  return $hits
}

if (-not (Test-Path $versionPath)) { throw "Missing VERSION file: $versionPath" }
if (-not (Test-Path $skillPath)) { throw "Missing SKILL.md: $skillPath" }
if (-not (Test-Path $readmePath)) { throw "Missing README.md: $readmePath" }

$version = (Get-Content $versionPath -Raw).Trim()
if (-not ([regex]::IsMatch($version, '^\d{4}\.\d{2}\.\d{2}$'))) {
  Add-Fail "VERSION format invalid: '$version' (expected YYYY.MM.DD)"
}

if ($Version) {
  if (-not ([regex]::IsMatch($Version, '^\d{4}\.\d{2}\.\d{2}$'))) {
    throw "Version parameter has invalid format: $Version"
  }
  if ($Version -ne $version) {
    Ensure-VersionSync $Version
    $version = (Get-Content $versionPath -Raw).Trim()
  }
}

$skillContent = Get-Content $skillPath -Raw
$readmeContent = Get-Content $readmePath -Raw

$skillVersionMatch = [regex]::Match($skillContent, '(?m)^version:\s*(\S+)\s*$')
$readmeVersionMatch = [regex]::Match($readmeContent, '(?m)^Skill version:\s*`([^`]+)`\s*$')

if (-not $skillVersionMatch.Success) {
  Add-Fail 'SKILL.md version field missing'
} else {
  $skillVersion = $skillVersionMatch.Groups[1].Value
  if ($skillVersion -ne $version) {
    if ($AutoFix) {
      Ensure-VersionSync $version
      Add-Pass "Synced SKILL.md and README.md version from VERSION"
    } else {
      Add-Fail "SKILL.md version mismatch: SKILL.md=$skillVersion, VERSION=$version"
    }
  } else {
    Add-Pass "SKILL.md version matches VERSION"
  }
}

if (-not $readmeVersionMatch.Success) {
  Add-Fail 'README.md Skill version line missing'
} else {
  $readmeVersion = $readmeVersionMatch.Groups[1].Value
  if ($readmeVersion -ne $version) {
    if ($AutoFix) {
      Ensure-VersionSync $version
      Add-Pass "Synced README.md version from VERSION"
    } else {
      Add-Fail "README.md version mismatch: README.md=$readmeVersion, VERSION=$version"
    }
  } else {
    Add-Pass "README.md version matches VERSION"
  }
}

if ($skillContent -match 'Current skill version:\s*') {
  if ($AutoFix) {
    $updated = [regex]::Replace($skillContent, '(?m)^Current skill version:\s*.*\r?\n', '')
    if ($updated -ne $skillContent) {
      Set-Content -Path $skillPath -Value $updated -Encoding utf8
      Add-Pass "Removed duplicate inline version line from SKILL.md"
      $skillContent = $updated
    }
  } else {
    Add-Fail 'SKILL.md contains duplicate inline version declaration'
  }
}

$allMd = Get-ChildItem -Path $root -Recurse -Filter *.md -File | Select-Object -ExpandProperty FullName
$aliasCount = Count-Pattern -Files $allMd -Pattern 'sync-template'
$aliasCount += Count-Pattern -Files $allMd -Pattern 'cmdSyncTemplate'
$aliasCount += Count-Pattern -Files $allMd -Pattern 'sync_template'
if ($aliasCount -eq 0) {
  Add-Pass "No sync-template alias remnants"
} else {
  Add-Fail "Found $aliasCount sync-template alias references"
}

$readmeCfg = $readmeContent -match 'references/project-configs.md'
$artifactCfg = (Get-Content $artifact -Raw) -match 'references/project-configs.md'
if ($readmeCfg) { Add-Pass 'README references project-configs.md as config source' } else { Add-Fail 'README missing project-configs reference' }
if ($artifactCfg) { Add-Pass 'skill-artifacts references project-configs.md as config source' } else { Add-Fail 'skill-artifacts missing project-configs reference' }

if (Test-Path $advancedPath) {
  Add-Pass 'execution-advanced reference file exists'
} else {
  Add-Fail 'execution-advanced.md missing'
}

$advMentions = 0
foreach ($path in @($readmePath, $skillPath, $execPath)) {
  $hasRef = (Select-String -Path $path -Pattern 'execution-advanced.md' -SimpleMatch | Measure-Object).Count
  if ($hasRef -gt 0) {
    Add-Pass "execution-advanced.md referenced in $([IO.Path]::GetFileName($path))"
  } else {
    Add-Fail "execution-advanced.md not referenced in $([IO.Path]::GetFileName($path))"
    $advMentions++
  }
}

$execContent = Get-Content $execPath -Raw
if (($execContent -match '## Idle Protocol — All Initial Milestones Complete') -or ($execContent -match '### Idle Protocol — All Initial Milestones Complete')) {
  Add-Pass 'skill-execution has authoritative Idle Protocol heading'
} else {
  Add-Fail 'skill-execution missing authoritative Idle Protocol heading'
}

$releaseStub = ($execContent -match '(?s)### Release Automation.*See `references/execution-advanced.md`')
$docsStub = ($execContent -match '(?s)## Phase 6: Documentation Site.*See `references/execution-advanced.md`')
$memoryStub = ($execContent -match '(?s)## Agent Memory System.*See `references/execution-advanced.md`')

if ($releaseStub) { Add-Pass 'Release Automation section points to execution-advanced.md' } else { Add-Fail 'Release Automation section is not a stub reference to execution-advanced.md' }
if ($docsStub) { Add-Pass 'Documentation Site section points to execution-advanced.md' } else { Add-Fail 'Documentation Site section is not a stub reference to execution-advanced.md' }
if ($memoryStub) { Add-Pass 'Agent Memory System section points to execution-advanced.md' } else { Add-Fail 'Agent Memory System section is not a stub reference to execution-advanced.md' }

$readmeOpsLabel = ($readmeContent -match 'Ops / rarely needed manually')
if ($readmeOpsLabel) {
  Add-Pass 'README has ops command grouping'
} else {
  Add-Fail 'README missing ops command grouping'
}

$cliAlias = Count-Pattern -Files @($cli) -Pattern 'sync-template'
$cliAlias += Count-Pattern -Files @($cli) -Pattern 'cmdSyncTemplate'
if ($cliAlias -eq 0) {
  Add-Pass 'harness-cli docs have no sync-template command references'
} else {
  Add-Fail "harness-cli docs still include sync-template/cmdSyncTemplate ($cliAlias)"
}

if ($problems.Count -eq 0) {
  Write-Host "PASS: Skill maintenance checks passed."
  $notes | ForEach-Object { Write-Host $_ }
  if ($AutoFix) {
    Write-Host "AutoFix checks done."
  }
  exit 0
}

Write-Host "FAIL: $($problems.Count) maintenance checks failed."
Write-Host "---"
$problems | ForEach-Object { Write-Host "[FAIL] $_" }
Write-Host "---"
$notes | ForEach-Object { Write-Host $_ }

if ($AutoFix) {
  Write-Host "AutoFix attempted. Re-run with no pending failures expected."
}
exit 1
