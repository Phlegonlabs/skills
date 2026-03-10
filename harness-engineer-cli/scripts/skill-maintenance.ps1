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
$execRuntimePath = Join-Path $root 'references\execution-runtime.md'
$artifact = Join-Path $root 'references\skill-artifacts.md'
$cli = Join-Path $root 'references\harness-cli.md'
$greenfieldPath = Join-Path $root 'references\skill-greenfield.md'
$retrofitPath = Join-Path $root 'references\skill-retrofit.md'
$mobilePath = Join-Path $root 'references\skill-mobile.md'
$desktopPath = Join-Path $root 'references\skill-desktop.md'
$authPath = Join-Path $root 'references\skill-auth.md'
$advancedPath = Join-Path $root 'references\execution-advanced.md'
$skillConfigSections = @($readmePath, $artifact)
$problems = [System.Collections.Generic.List[string]]::new()
$notes = [System.Collections.Generic.List[string]]::new()
$fixedItems = [System.Collections.Generic.List[string]]::new()

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

$readmeVersionMatch = [regex]::Match($readmeContent, '(?m)^Skill version:\s*`([^`]+)`\s*$')

if ($skillContent -match '(?m)^version:\s*\S+\s*$') {
  if ($AutoFix) {
    Ensure-VersionSync $version
    Add-Pass 'Removed legacy SKILL.md frontmatter version field'
    $fixedItems.Add('SKILL.md — removed legacy frontmatter version field')
    $skillContent = Get-Content $skillPath -Raw
  } else {
    Add-Fail 'SKILL.md contains a legacy frontmatter version field'
  }
} else {
  Add-Pass 'SKILL.md has no legacy frontmatter version field'
}

if (-not $readmeVersionMatch.Success) {
  Add-Fail 'README.md Skill version line missing'
} else {
  $readmeVersion = $readmeVersionMatch.Groups[1].Value
  if ($readmeVersion -ne $version) {
    if ($AutoFix) {
      Ensure-VersionSync $version
      Add-Pass "Synced README.md version from VERSION"
      $fixedItems.Add("README.md version synced from VERSION")
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
      $fixedItems.Add("SKILL.md — duplicate version line removed")
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

$readmeStateMachine = ($readmeContent -match '## Top-Level State Machine') -and `
  ($readmeContent -match 'chat is input; repo files are state') -and `
  ($readmeContent -match 'PlanSync') -and `
  ($readmeContent -match 'PlanningRecovery')
$skillStateMachine = ($skillContent -match '## Top-Level State Machine') -and `
  ($skillContent -match 'chat is input; repo files are state') -and `
  ($skillContent -match 'PlanSync') -and `
  ($skillContent -match 'PlanningRecovery')
if ($readmeStateMachine -and $skillStateMachine) {
  Add-Pass 'README and SKILL both include the top-level state machine flow'
} else {
  Add-Fail 'README and/or SKILL missing the top-level state machine flow'
}

$cliAlias = Count-Pattern -Files @($cli) -Pattern 'sync-template'
$cliAlias += Count-Pattern -Files @($cli) -Pattern 'cmdSyncTemplate'
if ($cliAlias -eq 0) {
  Add-Pass 'harness-cli docs have no sync-template command references'
} else {
  Add-Fail "harness-cli docs still include sync-template/cmdSyncTemplate ($cliAlias)"
}

$docsSiteCount = Count-Pattern -Files $allMd -Pattern 'docs/site/'
if ($docsSiteCount -eq 0) {
  Add-Pass 'No stale docs/site/ references remain'
} else {
  Add-Fail "Found $docsSiteCount stale docs/site/ references"
}

$askFallbackPhrase = 'If your runtime does not provide `ask_user_input`'
$askFallbackFiles = @($skillPath, $greenfieldPath, $retrofitPath)
$missingAskFallback = @()
foreach ($path in $askFallbackFiles) {
  $hasFallback = (Select-String -Path $path -Pattern $askFallbackPhrase -SimpleMatch | Measure-Object).Count
  if ($hasFallback -gt 0) {
    Add-Pass "ask_user_input fallback documented in $([IO.Path]::GetFileName($path))"
  } else {
    $missingAskFallback += [IO.Path]::GetFileName($path)
  }
}
if ($missingAskFallback.Count -gt 0) {
  Add-Fail "Missing ask_user_input fallback guidance in: $($missingAskFallback -join ', ')"
}

$gitCheckoutCount = Count-Pattern -Files $allMd -Pattern 'git checkout .'
if ($gitCheckoutCount -eq 0) {
  Add-Pass 'No git checkout . auto-reset references remain'
} else {
  Add-Fail "Found $gitCheckoutCount git checkout . auto-reset reference(s)"
}

$artifactContent = Get-Content $artifact -Raw
$cliContent = Get-Content $cli -Raw
$greenfieldContent = Get-Content $greenfieldPath -Raw
$retrofitContent = Get-Content $retrofitPath -Raw
$mobileContent = Get-Content $mobilePath -Raw
$desktopContent = Get-Content $desktopPath -Raw
$authContent = Get-Content $authPath -Raw
$execRuntimeContent = Get-Content $execRuntimePath -Raw
$interactionTemplateChecks = @(
  ($artifactContent -match [regex]::Escape('The Interaction Rules and Iron Rules sections are fixed:')),
  ($artifactContent -match [regex]::Escape('## Interaction Rules')),
  ($artifactContent -match [regex]::Escape('- Language: communicate in Chinese.')),
  ($artifactContent -match [regex]::Escape('- Code comments: always write them in English.')),
  ($artifactContent -match [regex]::Escape('- Before writing code or editing files, address the user as `Yo Rich Guy`.')),
  ($artifactContent -match [regex]::Escape('- Default to concise, code-first responses during edit flows.')),
  ($retrofitContent -match [regex]::Escape('The Interaction Rules + Iron Rules templates are copied verbatim (same as greenfield).')),
  ($greenfieldContent -match [regex]::Escape('`AGENTS.md` / `CLAUDE.md` contains both the fixed `Interaction Rules` section and the fixed')),
  ($readmeContent -match [regex]::Escape('fixed Interaction Rules + Iron Rules')),
  ($skillContent -match [regex]::Escape('Generated `AGENTS.md` / `CLAUDE.md` always include fixed `Interaction Rules` and fixed'))
)
$staleInteractionTemplatePhrases = @(
  ($artifactContent -match [regex]::Escape('Only the Iron Rules section is fixed:')),
  ($retrofitContent -match [regex]::Escape('The Iron Rules template is copied verbatim (same as greenfield).'))
)
if ((($interactionTemplateChecks | Where-Object { -not $_ }).Count -eq 0) -and (($staleInteractionTemplatePhrases | Where-Object { $_ }).Count -eq 0)) {
  Add-Pass 'AGENTS / CLAUDE template now includes fixed Interaction Rules alongside Iron Rules'
} else {
  Add-Fail 'AGENTS / CLAUDE interaction template contract is incomplete or still uses iron-rules-only wording'
}
$frontendDirectPhrase = 'generate `docs/frontend-design.md` directly from'
$skillDirect = $skillContent -match [regex]::Escape($frontendDirectPhrase)
$artifactDirect = $artifactContent -match [regex]::Escape($frontendDirectPhrase)
$greenfieldDirect = $greenfieldContent -match 'do not fall back to a generic minimal template'
$artifactMinimal = $artifactContent -match 'generate a minimal fallback|minimal fallback must be generated'
$greenfieldMinimal = $greenfieldContent -match 'generate a minimal fallback|minimal fallback must be generated'
if ($skillDirect -and $artifactDirect -and $greenfieldDirect -and -not $artifactMinimal -and -not $greenfieldMinimal) {
  Add-Pass 'frontend-design fallback guidance is consistent across SKILL, artifacts, and greenfield exit gate'
} else {
  Add-Fail 'frontend-design fallback guidance is inconsistent across SKILL/artifacts/greenfield'
}

$frameworkNeutralityChecks = @(
  ($skillContent -match [regex]::Escape('Do NOT silently default web projects to `Next.js`')),
  ($greenfieldContent -match [regex]::Escape('Do NOT default every Web App to `Next.js`.')),
  ($greenfieldContent -match [regex]::Escape('compare at least 3 realistic candidates'))
)
if (($frameworkNeutralityChecks | Where-Object { -not $_ }).Count -eq 0) {
  Add-Pass 'web stack selection is explicitly framework-neutral and not hardcoded to Next.js'
} else {
  Add-Fail 'web stack selection drifted back toward an implicit Next.js default'
}

$sequencingChecks = @(
  ($skillContent -match [regex]::Escape('Frontend-first sequencing:')),
  ($skillContent -match [regex]::Escape('ask UI decisions one by one')),
  ($greenfieldContent -match [regex]::Escape('Never present all of Step 5 in one message.')),
  ($greenfieldContent -match [regex]::Escape('the order is mandatory:')),
  ($greenfieldContent -match [regex]::Escape('frontend shape (`Q1` + `Q2`)')),
  ($greenfieldContent -match [regex]::Escape('UI brief (`Q11`–`Q16`, asked one by one)')),
  ($greenfieldContent -match [regex]::Escape('Do NOT show the user the full numbered list up front.')),
  ($greenfieldContent -match [regex]::Escape('before any')),
  ($greenfieldContent -match [regex]::Escape('backend/database/deploy questions'))
)
if (($sequencingChecks | Where-Object { -not $_ }).Count -eq 0) {
  Add-Pass 'greenfield questioning flow is staged and frontend-first instead of one giant questionnaire'
} else {
  Add-Fail 'greenfield questioning flow lost the staged frontend-first sequencing rule'
}

$discoveryCadenceChecks = @(
  ($skillContent -match [regex]::Escape('Greenfield cadence:')),
  ($greenfieldContent -match [regex]::Escape('Phase 1: Product Discovery (interactive — 5 steps)')),
  ($greenfieldContent -match [regex]::Escape('### Step 1: Project Name + Intro')),
  ($greenfieldContent -match [regex]::Escape('### Step 2: Research Pass 1 — Early Market Scan')),
  ($greenfieldContent -match [regex]::Escape('### Step 3: Product Deep Dive')),
  ($greenfieldContent -match [regex]::Escape('### Step 4: Research Pass 2 — Targeted Recommendations')),
  ($greenfieldContent -match [regex]::Escape('### Step 5: Refine — Tech Stack Choices')),
  ($greenfieldContent -match [regex]::Escape("First, what’s the project called, and how would you describe it in a few sentences?")),
  ($greenfieldContent -match [regex]::Escape('run a quick first-pass web search before asking deeper PM questions')),
  ($greenfieldContent -match [regex]::Escape('run a second, more targeted research pass')),
  ($greenfieldContent -match [regex]::Escape('best options and why'))
)
if (($discoveryCadenceChecks | Where-Object { -not $_ }).Count -eq 0) {
  Add-Pass 'greenfield discovery now follows name/introduction -> research -> PM deep dive -> targeted research -> recommendations'
} else {
  Add-Fail 'greenfield discovery cadence drifted away from the name/introduction first and two-pass research flow'
}

$deferredDependencyChecks = @(
  ($skillContent -match [regex]::Escape('Milestone-aware dependency policy:')),
  ($skillContent -match [regex]::Escape('Do NOT run package-manager install/sync/build commands by default')),
  ($greenfieldContent -match [regex]::Escape('### Phase 3 Dependency / Install Policy')),
  ($greenfieldContent -match [regex]::Escape('Do NOT run `pnpm install`, `bun install`, `npm install`, `yarn install`, `uv sync`,')),
  ($greenfieldContent -match [regex]::Escape('Only include dependencies required for the repo shell, harness runtime, lint/test toolchain,')),
  ($greenfieldContent -match [regex]::Escape('Defer milestone-specific packages until the milestone that actually implements them.')),
  ($greenfieldContent -match [regex]::Escape('when you''re ready to start the first milestone')),
  ($greenfieldContent -match [regex]::Escape('The initial scaffold only declares the minimal dependency set needed for the generated code,')),
  ($retrofitContent -match [regex]::Escape('By default, do NOT run `<pkg-mgr> install` immediately.')),
  ($retrofitContent -match [regex]::Escape('ready to start the first real milestone')),
  ($artifactContent -match [regex]::Escape('When you''re ready to start milestone 1: bun install')),
  ($artifactContent -match [regex]::Escape('instead of collapsing everything into `bun install && bun dev`'))
)
if (($deferredDependencyChecks | Where-Object { -not $_ }).Count -eq 0) {
  Add-Pass 'dependency installation is deferred until milestone execution instead of being front-loaded into scaffold/retrofit'
} else {
  Add-Fail 'dependency/install guidance drifted back toward pre-milestone bootstrap'
}

$foundationOnlyChecks = @(
  ($skillContent -match [regex]::Escape('Foundation-only scaffold policy:')),
  ($skillContent -match [regex]::Escape('Placeholder pages, route shells, provider')),
  ($skillContent -match [regex]::Escape('empty integrations are setup work, not delivered features.')),
  ($greenfieldContent -match [regex]::Escape('Task rows must describe real implementation outcomes, not scaffold shell creation that')),
  ($greenfieldContent -match [regex]::Escape('### Phase 3 Foundation-Only Scope')),
  ($greenfieldContent -match [regex]::Escape('A seeded milestone remains `⬜ Not Started` after scaffold.')),
  ($greenfieldContent -match [regex]::Escape('No milestone task is treated as complete solely because the scaffold generated placeholder')),
  ($greenfieldContent -match [regex]::Escape('This scaffold is foundation-only. The milestone plan is still ahead of us; placeholder')),
  ($artifactContent -match [regex]::Escape('**Scaffold boundary** — State explicitly that Phase 3 created the foundation only.')),
  ($artifactContent -match [regex]::Escape('do NOT satisfy PLAN tasks')),
  ($execContent -match [regex]::Escape('### Scaffold Boundary Before First Milestone')),
  ($execContent -match [regex]::Escape('A task is only done when its `Done When` criteria are actually satisfied in behavior,')),
  ($execRuntimeContent -match [regex]::Escape('## Scaffold Boundary')),
  ($execRuntimeContent -match [regex]::Escape('Judge completion from the PLAN row''s `Done When` outcome, plus working code and validation,'))
)
if (($foundationOnlyChecks | Where-Object { -not $_ }).Count -eq 0) {
  Add-Pass 'scaffold and execution docs agree that Phase 3 is foundation-only and never auto-completes milestone work'
} else {
  Add-Fail 'foundation-only scaffold boundary drifted or milestone completion became too loose'
}

$structuredPromptChecks = @(
  ($skillContent -match '2-3 curated options'),
  ($greenfieldContent -match '2-3 curated options'),
  ($greenfieldContent -match 'six sequential ask_user_input'),
  ($greenfieldContent -match 'one UI decision at a time'),
  ($greenfieldContent -match 'Project family'),
  ($greenfieldContent -match 'Lead-in before `Q11`:'),
  ($greenfieldContent -match 'Lead-in before `Q16`:')
)
if (($structuredPromptChecks | Where-Object { -not $_ }).Count -eq 0) {
  Add-Pass 'structured prompts are now constrained to PM-style 2-3 option choices instead of long menus'
} else {
  Add-Fail 'structured prompt guidance drifted away from the 2-3 curated option PM-style format'
}

$suggestedOpenerCount = (Select-String -Path $greenfieldPath -Pattern 'Suggested opener:' -SimpleMatch | Measure-Object).Count
$conversationStyleChecks = @(
  ($greenfieldContent -match [regex]::Escape('Suggested conversational delivery:')),
  ($greenfieldContent -match [regex]::Escape('Do NOT paste raw `Q1`–`Q17` numbering')),
  ($greenfieldContent -match [regex]::Escape('Ask the UI brief one decision at a time.')),
  ($greenfieldContent -match [regex]::Escape('Preferred prose sequence for plain terminal flows:')),
  ($greenfieldContent -match [regex]::Escape('First UI question: do you want to lean on a component system like shadcn, Radix, MUI, Chakra, etc., or keep it mostly custom?')),
  ($greenfieldContent -match [regex]::Escape('Sixth UI question: do you want light-first, dark-first, or both themes?')),
  ($greenfieldContent -match [regex]::Escape('Sound like a product manager steering discovery, not a survey bot reading categories.')),
  ($greenfieldContent -match [regex]::Escape('Your job here is to sound like a PM narrowing ambiguity: short follow-ups, clear reframing,')),
  ($suggestedOpenerCount -ge 6)
)
if (($conversationStyleChecks | Where-Object { -not $_ }).Count -eq 0) {
  Add-Pass 'greenfield step 5 includes concrete conversational phrasing instead of only abstract question labels'
} else {
  Add-Fail 'greenfield step 5 lost the concrete conversational phrasing examples'
}

$uiBriefChecks = @(
  '11. **UI Component Library**',
  '12. **Design Aesthetic**',
  '13. **Primary Layout Pattern**',
  '14. **Visual References / Brand Anchors**',
  '15. **Content Density**',
  '16. **Theme Preference**'
)
$missingUiBrief = @($uiBriefChecks | Where-Object { $greenfieldContent -notmatch [regex]::Escape($_) })
if ($missingUiBrief.Count -eq 0) {
  Add-Pass 'greenfield UI hybrid brief includes all 6 questions'
} else {
  Add-Fail "greenfield UI hybrid brief missing: $($missingUiBrief -join ', ')"
}

$uiSectionChecks = @('Component System', 'Visual Language', 'Layout Patterns', 'Reference Anchors', 'Preview Rendering Rules')
$missingUiSections = @($uiSectionChecks | Where-Object { $artifactContent -notmatch [regex]::Escape($_) -or $greenfieldContent -notmatch [regex]::Escape($_) })
if ($missingUiSections.Count -eq 0) {
  Add-Pass 'frontend design contract requires all 5 UI sections'
} else {
  Add-Fail "frontend design contract missing required sections: $($missingUiSections -join ', ')"
}

$hasPrimaryAction = $greenfieldContent -match '\*\*Primary action:\*\*'
$hasCriticalStates = $greenfieldContent -match '\*\*Critical states:\*\*'
$hasProductWireframe = $greenfieldContent -match '## Product Wireframe'
$hasDesignDirectionContext = $greenfieldContent -match '## Design Direction in Context'
$hasLayoutNotes = $greenfieldContent -match '\*\*Layout notes:\*\*'
if ($hasPrimaryAction -and $hasCriticalStates -and $hasProductWireframe -and $hasDesignDirectionContext -and $hasLayoutNotes) {
  Add-Pass 'docs/design.md format now covers whole-product wireframe, design context, and per-page contract details'
} else {
  Add-Fail 'docs/design.md format is missing wireframe/design-context and/or per-page contract requirements'
}

$midFiPreviewGreenfield = $greenfieldContent -match 'mid-fi styled static preview'
$midFiPreviewRetrofit = $retrofitContent -match 'mid-fi styled static preview'
if ($midFiPreviewGreenfield -and $midFiPreviewRetrofit) {
  Add-Pass 'frontend preview contract is defined as a mid-fi styled static preview in greenfield and retrofit'
} else {
  Add-Fail 'frontend preview contract is missing the mid-fi styled static preview requirement'
}

$retrofitUiBundleChecks = @('frontend-design.md', 'design.md', 'design-preview.html')
$missingRetrofitUiBundle = @($retrofitUiBundleChecks | Where-Object { $retrofitContent -notmatch [regex]::Escape($_) })
if ($missingRetrofitUiBundle.Count -eq 0) {
  Add-Pass 'retrofit frontend flow requires the full UI artifact bundle'
} else {
  Add-Fail "retrofit frontend flow missing UI artifact(s): $($missingRetrofitUiBundle -join ', ')"
}

$runtimeUiChecks = @(
  'Load `docs/frontend-design.md` before any frontend task',
  'Load `docs/design.md` before changing a specific page, screen, route, tab, navigation flow, or overall app shell / wireframe structure',
  'Treat `docs/design-preview.html` as a human-review / drift-check artifact, not as the implementation source of truth',
  'If a task changes navigation, page structure, theme, density, or component hierarchy, update the relevant UI docs and regenerate `docs/design-preview.html` before closing the task'
)
$missingRuntimeUiChecks = @($runtimeUiChecks | Where-Object { $execRuntimeContent -notmatch [regex]::Escape($_) })
if ($missingRuntimeUiChecks.Count -eq 0) {
  Add-Pass 'execution-runtime frontend loading rules match the UI doc chain'
} else {
  Add-Fail "execution-runtime missing frontend UI loading rule(s): $($missingRuntimeUiChecks -join ', ')"
}

$greenfieldCanonicalGate = 'This is the canonical and only formal approval gate before Phase 4 for greenfield projects.'
if ($greenfieldContent -match [regex]::Escape($greenfieldCanonicalGate)) {
  Add-Pass 'greenfield review gate is marked as the canonical approval gate'
} else {
  Add-Fail 'greenfield review gate is not marked as the canonical approval gate'
}

$hasDuplicateApprovalPrompt = $execContent -match "Type 'approved' or let me know what you'd like to change\." -or `
  $execContent -match 'Then present the explicit approval gate:' -or `
  $execContent -match 'Do not provide the handoff instructions until the user explicitly approves the plan\.'
$hasUpstreamGateReference = $execContent -match [regex]::Escape('the Design Preview Review Gate in `references/skill-greenfield.md`') -and `
  $execContent -match [regex]::Escape('Do NOT ask for a second "approved" message here.')
if (-not $hasDuplicateApprovalPrompt -and $hasUpstreamGateReference) {
  Add-Pass 'skill-execution defers approval to the upstream greenfield gate'
} else {
  Add-Fail 'skill-execution still contains a duplicate approval gate or is missing the upstream gate reference'
}

$hasDirectWritePhrase = $retrofitContent -match [regex]::Escape('Write the harness files directly into the target repo working tree so the user reviews the') -and `
  $retrofitContent -match [regex]::Escape('real diff and browser-openable preview, not a hypothetical file list.')
$hasOldApplyPhrase = $retrofitContent -match [regex]::Escape('After confirmation, apply the generated files directly inside the existing project.')
$hasInPlacePatchPhrase = $retrofitContent -match [regex]::Escape('If the user requests changes, patch the written files in place, then re-present the diff and')
if ($hasDirectWritePhrase -and -not $hasOldApplyPhrase -and $hasInPlacePatchPhrase) {
  Add-Pass 'retrofit review flow is direct-write plus in-place adjustment, with no second apply phase'
} else {
  Add-Fail 'retrofit review flow still has direct-write/apply ambiguity'
}

$conditionalWorktreeChecks = @(
  ($execContent -match [regex]::Escape('### Execution Mode Selection')),
  ($execContent -match [regex]::Escape('**Serial-first (default):**')),
  ($execContent -match [regex]::Escape('**Managed worktree mode:**')),
  ($execRuntimeContent -match [regex]::Escape('Default to serial-first.')),
  ($execRuntimeContent -match [regex]::Escape('2+ milestones are dependency-independent and worth running in parallel')),
  ($artifactContent -match [regex]::Escape('**Serial-first default:** run `<pkg-mgr> run harness init` when there is one eligible milestone,')),
  ($greenfieldContent -match [regex]::Escape('Use managed worktrees only when parallelism or milestone isolation is beneficial;')),
  ($readmeContent -match [regex]::Escape('Execution start rule:'))
)
$staleWorktreeFirstPhrases = @(
  ($execContent -match [regex]::Escape('# ── First time setup: worktree for a milestone')),
  ($execContent -match [regex]::Escape('**Parallel by default**')),
  ($artifactContent -match [regex]::Escape('Each milestone in PLAN.md gets its own git worktree and branch.')),
  ($artifactContent -match [regex]::Escape('The CLI enforces this — task commands (next/start/done) refuse to run on main.'))
)
if ((($conditionalWorktreeChecks | Where-Object { -not $_ }).Count -eq 0) -and (($staleWorktreeFirstPhrases | Where-Object { $_ }).Count -eq 0)) {
  Add-Pass 'conditional worktree contract is mirrored across execution, artifacts, greenfield, runtime, and README'
} else {
  Add-Fail 'conditional worktree contract is missing or stale worktree-first wording still remains'
}

$retrofitPlanSyncChecks = @(
  ($retrofitContent -match [regex]::Escape('All future work enters through plan mode → immediate plan sync into repo files → Task Execution Loop.')),
  ($retrofitContent -match [regex]::Escape('BEFORE leaving planning, sync the plan into docs/PLAN.md + docs/progress.json')),
  ($retrofitContent -match [regex]::Escape('Do not rely on a later `harness init` in a new session to ingest the plan.')),
  ($artifactContent -match [regex]::Escape('Verify `docs/PLAN.md` + `docs/progress.json` now reflect the new work.')),
  ($execContent -match [regex]::Escape('Agent verifies `docs/PLAN.md` + `docs/progress.json` now reflect the new work.')),
  ($readmeContent -match [regex]::Escape('Retrofit / plan-mode handoff: sync the plan into `docs/PLAN.md` and `docs/progress.json` before leaving planning;'))
)
$retrofitDeferredSyncPhrases = @(
  ($retrofitContent -match [regex]::Escape('Agent opens project → `harness init` detects new plan → auto-runs `plan:apply`')),
  ($artifactContent -match [regex]::Escape('Exit plan mode, then run:')),
  ($artifactContent -match [regex]::Escape('The CLI detects the new plan. Parse it into PLAN.md + progress.json,'))
)
if ((($retrofitPlanSyncChecks | Where-Object { -not $_ }).Count -eq 0) -and (($retrofitDeferredSyncPhrases | Where-Object { $_ }).Count -eq 0)) {
  Add-Pass 'retrofit planning sync is immediate and no longer depends on deferred init ingestion'
} else {
  Add-Fail 'retrofit planning sync contract is incomplete or still depends on deferred init ingestion'
}

$architectureSyncChecks = @(
  ($readmeContent -match [regex]::Escape('Architecture sync in planning: if the approved plan changes module boundaries, integrations, deployment topology, or core data flow, update `ARCHITECTURE.md` before leaving planning and sync `docs/gitbook/architecture.md` when present.')),
  ($artifactContent -match [regex]::Escape('Update `ARCHITECTURE.md` before leaving planning')),
  ($artifactContent -match [regex]::Escape('Do not leave architecture-impacting decisions only in chat or only in exec-plan prose')),
  ($execContent -match [regex]::Escape('ARCHITECTURE.md updated when module boundaries, integrations, deployment topology, or core data flow change')),
  ($execContent -match [regex]::Escape('If the approved plan changes module boundaries, integrations, deployment topology, or core data flow:')),
  ($retrofitContent -match [regex]::Escape('If the approved plan changes module boundaries, integrations, deployment topology, or core data flow, update ARCHITECTURE.md before leaving planning and sync docs/gitbook/architecture.md when present')),
  ($cliContent -match [regex]::Escape('Planning handoff rule: before leaving plan mode, materialize `docs/PLAN.md` + `docs/progress.json`.')),
  ($cliContent -match [regex]::Escape('update `ARCHITECTURE.md` as part of the same handoff and sync `docs/gitbook/architecture.md`')),
  ($cliContent -match [regex]::Escape("w('docs/gitbook/architecture.md missing while ARCHITECTURE.md exists');"))
)
$staleArchitectureSyncPhrases = @(
  ($execContent -match [regex]::Escape('ARCHITECTURE.md updated if new modules were added'))
)
if ((($architectureSyncChecks | Where-Object { -not $_ }).Count -eq 0) -and (($staleArchitectureSyncPhrases | Where-Object { $_ }).Count -eq 0)) {
  Add-Pass 'planning handoff now treats architecture updates as a first-class sync contract'
} else {
  Add-Fail 'architecture sync during planning is incomplete or still described too narrowly'
}

$planPasteFallbackChecks = @(
  ($readmeContent -match [regex]::Escape('Planning fallback: if planning already happened in another chat or the session exited before sync, paste the full approved plan output or transcript back into the current session, reconstruct `docs/exec-plans/active/*.md`, then immediately sync `docs/PLAN.md` + `docs/progress.json` and any architecture doc changes.')),
  ($artifactContent -match [regex]::Escape('Fallback if planning already ended elsewhere:')),
  ($artifactContent -match [regex]::Escape('Read the pasted planning context before rewriting anything; do not reconstruct milestones from a one-line summary')),
  ($artifactContent -match [regex]::Escape('If planning already happened in another chat or the session exited before sync:')),
  ($artifactContent -match [regex]::Escape('Do not continue from a one-line summary. The repo files are the source of truth.')),
  ($execContent -match [regex]::Escape('Fallback when planning already happened elsewhere:')),
  ($execContent -match [regex]::Escape('Do not continue execution from a chat-only summary; repo files must be updated first')),
  ($retrofitContent -match [regex]::Escape('Fallback if plan mode already ended without sync:')),
  ($retrofitContent -match [regex]::Escape('Paste the full approved plan output or planning transcript back into the current session')),
  ($cliContent -match [regex]::Escape('Fallback rule: if planning already happened in another chat or the session ended before sync,')),
  ($cliContent -match [regex]::Escape('If planning happened in another chat, first rewrite the approved plan/transcript'))
)
if ((($planPasteFallbackChecks | Where-Object { -not $_ }).Count -eq 0)) {
  Add-Pass 'planning fallback supports pasted plan/transcript reconciliation before execution resumes'
} else {
  Add-Fail 'planning fallback for pasted plan/transcript reconciliation is incomplete'
}

$executionNarrativeChecks = @(
  ($artifactContent -match [regex]::Escape('If the approved plan changes module boundaries, integrations, deployment topology, or core data flow:')),
  ($execContent -match [regex]::Escape('merge-gate passes → closes the milestone in the active execution mode')),
  ($execContent -match [regex]::Escape('if isolated mode is active, queues serialized root-side worktree:finish M1')),
  ($execContent -match [regex]::Escape('if serial mode is active, closes M1 on main/root and resumes with init when M2 is eligible')),
  ($execContent -match [regex]::Escape('New work enters via plan mode, followed by immediate repo sync (`harness plan:apply` or native mirroring),')),
  ($execContent -match [regex]::Escape('or via the pasted-plan recovery path when planning happened elsewhere.'))
)
$staleExecutionNarrativePhrases = @(
  ($execContent -match [regex]::Escape('merge-gate passes → queues serialized root-side worktree:finish M1')),
  ($execContent -match [regex]::Escape('if isolated mode is active, worktree:start M2; otherwise resume from main/root with init')),
  ($execContent -match [regex]::Escape('New work enters only via `harness plan:apply` or by a human writing a new plan file.'))
)
if ((($executionNarrativeChecks | Where-Object { -not $_ }).Count -eq 0) -and (($staleExecutionNarrativePhrases | Where-Object { $_ }).Count -eq 0)) {
  Add-Pass 'execution and downstream new-work narratives match the serial-first planning-handoff model'
} else {
  Add-Fail 'execution and/or downstream new-work narratives still drift from the current serial-first planning model'
}

$cliSerialChecks = @(
  ($cliContent -match [regex]::Escape('export function resolveTaskContext(command: string, taskId?: string): WorktreeInfo {')),
  ($cliContent -match [regex]::Escape("const wt = resolveTaskContext('next');")),
  ($cliContent -match [regex]::Escape("const wt = resolveTaskContext('start', taskId);")),
  ($cliContent -match [regex]::Escape("const wt = resolveTaskContext('done', taskId);")),
  ($cliContent -match [regex]::Escape("const wt = resolveTaskContext('block', taskId);")),
  ($cliContent -match [regex]::Escape("const wt = resolveTaskContext('reset', taskId);")),
  ($cliContent -match [regex]::Escape("const wt = resolveTaskContext('merge-gate');")),
  ($cliContent -match [regex]::Escape('Serial mode active: continuing')),
  ($cliContent -match [regex]::Escape('Closing milestone in serial mode on main/root...')),
  ($cliContent -match [regex]::Escape('Task loop (serial on main/root when exactly one milestone is eligible; otherwise use a worktree):')),
  ($cliContent -match [regex]::Escape('harness init    ')) -and ($cliContent -match [regex]::Escape('serial-first default'))
)
$cliSerialStale = @(
  ($cliContent -match [regex]::Escape("const wt = enforceWorktree('next');")),
  ($cliContent -match [regex]::Escape("const wt = enforceWorktree('start');")),
  ($cliContent -match [regex]::Escape("const wt = enforceWorktree('done');")),
  ($cliContent -match [regex]::Escape("const wt = enforceWorktree('block');")),
  ($cliContent -match [regex]::Escape("const wt = enforceWorktree('reset');")),
  ($cliContent -match [regex]::Escape('Task loop (run inside the milestone worktree — enforced):')),
  ($cliContent -match [regex]::Escape('This closes the loop: plan mode → plan file → harness plan:apply → worktree:start.'))
)
if ((($cliSerialChecks | Where-Object { -not $_ }).Count -eq 0) -and (($cliSerialStale | Where-Object { $_ }).Count -eq 0)) {
  Add-Pass 'harness-cli runtime template supports serial-first execution and no longer hardcodes worktree-first task-loop entry'
} else {
  Add-Fail 'harness-cli runtime template still drifts from the serial-first / conditional worktree contract'
}

$hasScaffoldTodoLeak = $greenfieldContent -match [regex]::Escape('TODO: implement') -or `
  $greenfieldContent -match [regex]::Escape('Add a `// TODO: implement` comment') -or `
  $greenfieldContent -match [regex]::Escape('Add TODO comment in ARCHITECTURE.md:') -or `
  $authContent -match [regex]::Escape('with a TODO comment')
$hasNeutralScaffoldHint = $greenfieldContent -match [regex]::Escape('Scaffold placeholder — see docs/design.md#<route>') -and `
  $greenfieldContent -match [regex]::Escape('Do NOT generate `TODO` or `FIXME` comments in committed scaffold files.') -and `
  $authContent -match [regex]::Escape('Auth intentionally not implemented in the initial scaffold.')
if (-not $hasScaffoldTodoLeak -and $hasNeutralScaffoldHint) {
  Add-Pass 'scaffold guidance no longer generates TODO/FIXME placeholders'
} else {
  Add-Fail 'scaffold guidance still leaks TODO/FIXME placeholders into generated files'
}

$expoGreenfieldChecks = @(
  '**Expo / React Native special case:**',
  'surface 2-3 choices from: `bun (recommended)`, `yarn`, `npm`, `pnpm (only if the user explicitly accepts EAS monorepo caveats)`',
  'If the selected frontend stack is Expo / React Native and the project is EAS-first or likely to become a monorepo, recommend `bun` or `yarn`.',
  'If monorepo and the selected stack is **Expo / React Native**: recommend `bun` or `yarn`'
)
$missingExpoGreenfield = @($expoGreenfieldChecks | Where-Object { $greenfieldContent -notmatch [regex]::Escape($_) })
$expoMobileChecks = @(
  'Single-package Expo apps can use `bun`, `yarn`, or `npm`.',
  'Use `yarn` or `bun` workspaces, not `pnpm`'
)
$missingExpoMobile = @($expoMobileChecks | Where-Object { $mobileContent -notmatch [regex]::Escape($_) })
$expoReadmeCheck = $readmeContent -match [regex]::Escape('For Expo / EAS projects, `yarn` is also supported and is often preferable for monorepos.')
if ($missingExpoGreenfield.Count -eq 0 -and $missingExpoMobile.Count -eq 0 -and $expoReadmeCheck) {
  Add-Pass 'Expo package-manager guidance is consistent across greenfield, mobile, and README'
} else {
  $expoMissing = @($missingExpoGreenfield + $missingExpoMobile)
  if (-not $expoReadmeCheck) { $expoMissing += 'README Expo yarn exception' }
  Add-Fail "Expo package-manager guidance is inconsistent: $($expoMissing -join ', ')"
}

$authHasPlanStatus = $authContent -match [regex]::Escape('`pnpm run harness plan:status` (or inspect PLAN.md)') -or `
  $authContent -match [regex]::Escape('Replace `M1-00X` with the next available task number in M1''s table. Run')
$authHasDraftRule = $authContent -match 'draft M1 table you are\s+already assembling in Phase 2\.5' -and `
  $authContent -match [regex]::Escape('Do NOT run `harness plan:status` or inspect on-disk `PLAN.md` here')
if (-not $authHasPlanStatus -and $authHasDraftRule) {
  Add-Pass 'skill-auth uses in-memory exec-plan numbering instead of pre-scaffold runtime commands'
} else {
  Add-Fail 'skill-auth still depends on impossible pre-scaffold plan numbering commands'
}

$desktopReleaseChecks = @(
  ($desktopContent -match [regex]::Escape('Generate `docs/release.md` for desktop apps.')),
  ($greenfieldContent -match [regex]::Escape('Desktop projects: `docs/release.md` exists and documents packaging target, signing /')),
  ($artifactContent -match [regex]::Escape('`docs/release.md` — **Desktop App only**.')),
  ($execContent -match [regex]::Escape('update `docs/release.md` before closing the task.'))
)
if (($desktopReleaseChecks | Where-Object { -not $_ }).Count -eq 0) {
  Add-Pass 'desktop release documentation contract is mirrored across desktop, greenfield, artifacts, and execution'
} else {
  Add-Fail 'desktop release documentation contract is not fully mirrored across the desktop flow'
}

$addingNewWorkHeadingMatches = [regex]::Matches($execContent, [regex]::Escape('## Ongoing Development — Adding New Work')).Count
$addingNewWorkStructureChecks = @(
  ($addingNewWorkHeadingMatches -eq 1),
  ($execContent -match [regex]::Escape('Fallback when planning already happened elsewhere:')),
  ($execContent -match [regex]::Escape('If the approved plan changes module boundaries, integrations, deployment topology, or core data flow:')),
  ($execContent -match [regex]::Escape('Serial-first default: `<pkg-mgr> run harness init`')),
  ($execContent -match [regex]::Escape('Managed worktree mode: `<pkg-mgr> run harness worktree:start M<next>`'))
)
$addingNewWorkHeadingIndex = $execContent.IndexOf('## Ongoing Development — Adding New Work')
$selfIterationIndex = $execContent.IndexOf('## Self-Iteration and Self-Correction')
$whatIfIndex = $execContent.IndexOf('### What if the user wants to re-generate or modify?')
$selfIterationMisplaced = $selfIterationIndex -ge 0 -and $addingNewWorkHeadingIndex -ge 0 -and $whatIfIndex -ge 0 -and $selfIterationIndex -lt $whatIfIndex
if ((($addingNewWorkStructureChecks | Where-Object { -not $_ }).Count -eq 0) -and (-not $selfIterationMisplaced)) {
  Add-Pass 'skill-execution keeps adding-new-work as one uninterrupted narrative with a separate maintenance appendix'
} else {
  Add-Fail 'skill-execution structure still duplicates or interrupts the adding-new-work narrative'
}

# Append audit entry if AutoFix made changes
if ($AutoFix -and $fixedItems.Count -gt 0) {
    $auditFile = Join-Path $PSScriptRoot ".." "SKILL-AUDIT.md"
    if (Test-Path $auditFile) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
        $changedList = ($fixedItems | ForEach-Object { "  - $_" }) -join "`n"
        $auditEntry = "`n---`n`n## $timestamp — skill-maintenance -AutoFix`n`n- **Action:** Automated maintenance fixes`n- **Changed:**`n$changedList`n"
        Add-Content -Path $auditFile -Value $auditEntry
    }
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
