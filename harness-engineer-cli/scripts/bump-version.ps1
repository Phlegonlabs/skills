<# 
Usage:
  pwsh scripts/bump-version.ps1
  pwsh scripts/bump-version.ps1 -Version 2026.03.11
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $false)]
  [ValidatePattern('^\d{4}\.\d{2}\.\d{2}$')]
  [string] $Version
)

$ErrorActionPreference = 'Stop'
$versionPattern = '^\d{4}\.\d{2}\.\d{2}$'

$root = Split-Path -Parent $PSScriptRoot
$versionPath = Join-Path $root 'VERSION'
$skillPath = Join-Path $root 'SKILL.md'
$readmePath = Join-Path $root 'README.md'

if (-not (Test-Path $versionPath)) {
  throw "Missing VERSION file: $versionPath"
}

$currentVersion = (Get-Content $versionPath -Raw).Trim()
if (-not [regex]::IsMatch($currentVersion, $versionPattern)) {
  throw "Current VERSION format invalid: $currentVersion"
}

$currentDate = [datetime]::ParseExact($currentVersion, 'yyyy.MM.dd', [System.Globalization.CultureInfo]::InvariantCulture)
$nextVersion = if ($Version) { 
  $Version 
} else {
  $today = [datetime]::Today
  $nextDate = if ($today -le $currentDate) { $currentDate.AddDays(1) } else { $today }
  $nextDate.ToString('yyyy.MM.dd')
}

if ($currentVersion -eq $nextVersion) {
  Write-Host "No-op: VERSION is already $currentVersion"
  return
}

Set-Content -Path $versionPath -Value $nextVersion -Encoding utf8

$skillContent = Get-Content $skillPath -Raw
$updatedSkill = [regex]::Replace($skillContent, '(?m)^version:\s*.*$', "version: $nextVersion")
if ($updatedSkill -eq $skillContent) {
  throw "Failed to update SKILL.md version line"
}
Set-Content -Path $skillPath -Value $updatedSkill -Encoding utf8

$readmeContent = Get-Content $readmePath -Raw
$backtick = '`'
$replacement = "Skill version: $backtick$nextVersion$backtick"
$updatedReadme = [regex]::Replace(
  $readmeContent,
  '(?m)^Skill version:\s*`[^`]*`$',
  $replacement
)
if ($updatedReadme -eq $readmeContent) {
  throw "Failed to update README version line"
}
Set-Content -Path $readmePath -Value $updatedReadme -Encoding utf8

Write-Host "Version bump: $currentVersion -> $nextVersion"
Write-Host "Updated:"
Write-Host " - $versionPath"
Write-Host " - $skillPath"
Write-Host " - $readmePath"
