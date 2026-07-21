# PreToolUse hook - inject domain-memory context the FIRST time a session touches
# a tool category (Zephyr / MSSQL / Playwright / Atlassian), then stay silent on
# every subsequent matched call. Context-only: it no longer force-approves the tool.

# Compute the per-project memory root from CLAUDE_PROJECT_DIR. Fully portable:
# the memory files are resolved from whatever project the current session is in.
# If CLAUDE_PROJECT_DIR is unset or the project has no memory dir yet, exit quietly —
# there is simply nothing to inject (no hardcoded old-project fallback).
$projectDir = $env:CLAUDE_PROJECT_DIR
if (-not $projectDir) { exit 0 }
$key = $projectDir.Substring(0,1).ToLower() + $projectDir.Substring(1)
$key = $key -replace ":\\", "--" -replace "\\", "-" -replace "_", "-"
$memRoot = "$env:USERPROFILE\.claude\projects\$key\memory"
if (-not (Test-Path $memRoot)) { exit 0 }

# Read hook payload from stdin JSON
$raw = [System.Console]::In.ReadToEnd()
$data = $raw | ConvertFrom-Json
$tool = $data.tool_name
$session = $data.session_id

# Map tool category -> memory files + a short tag for the once-per-session guard
$files = @()
$category = ""
if ($tool -match "mcp__zephyr-scale__") {
    $category = "zephyr"; $files = @("tools\zephyr-api.md", "domain\zephyr.md")
} elseif ($tool -match "mcp__mssql") {
    $category = "mssql"; $files = @("tools\mssql.md", "domain\data-relationships.md")
} elseif ($tool -match "mcp__playwright__") {
    $category = "playwright"; $files = @("tools\playwright.md")
} elseif ($tool -match "mcp__claude_ai_Atlassian") {
    $category = "atlassian"; $files = @("domain\failures.md")
}

if ($files.Count -eq 0) { exit 0 }

# Once-per-session-per-category guard. Inject on the first matched call, then skip.
# If session_id is absent, degrade gracefully to the original always-inject behavior.
if ($session) {
    $flag = Join-Path $env:TEMP ("claude-meminject-{0}-{1}.flag" -f $session, $category)
    if (Test-Path $flag) { exit 0 }
    New-Item -ItemType File -Path $flag -Force | Out-Null
}

$parts = $files | ForEach-Object {
    Get-Content "$memRoot\$_" -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
}
$context = $parts -join "`n`n---`n`n"

@{
    hookSpecificOutput = @{
        hookEventName     = "PreToolUse"
        additionalContext = $context
    }
} | ConvertTo-Json -Depth 3

exit 0
