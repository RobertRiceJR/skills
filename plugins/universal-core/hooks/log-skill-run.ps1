# PostToolUse hook - auto-log Zephyr TC creation to domain/skill-runs.md
$raw = [System.Console]::In.ReadToEnd()
$data = $raw | ConvertFrom-Json

# Extract TC key and name from the Zephyr response.
# Try top-level .key first (standard Zephyr REST shape), then .testCaseKey,
# then a content-array wrapper (some MCP servers serialize responses this way).
$tcKey = $data.tool_response.key
if (-not $tcKey) { $tcKey = $data.tool_response.testCaseKey }
if (-not $tcKey -and $data.tool_response.content) {
    try {
        $inner = ($data.tool_response.content | Select-Object -First 1).text | ConvertFrom-Json
        $tcKey = $inner.key
        if (-not $tcKey) { $tcKey = $inner.testCaseKey }
    } catch {}
}
# Last resort: scan the raw payload for a CI test-case key (CI-T####), so the log
# still records regardless of how the real MCP response nests the field.
if (-not $tcKey -and $raw -match 'CI-T\d+') { $tcKey = $Matches[0] }

$tcName = $data.tool_input.name

# Failure-only diagnostic: if a response came back but no key could be extracted,
# capture the raw payload once so the real shape can be inspected. Fires only on
# the anomaly - not on every call - so it is not the per-call dump that was removed.
if (-not $tcKey -and $data.tool_response) {
    $dbg = Join-Path $env:TEMP "zephyr-hook-unparsed.json"
    $raw | Out-File -FilePath $dbg -Encoding UTF8 -Force
}

if ($tcKey) {
    # Compute memory root (same algorithm as memory-inject.ps1). Portable: derived
    # purely from the current project. If unresolved, exit quietly — no old-project fallback.
    $projectDir = $env:CLAUDE_PROJECT_DIR
    if (-not $projectDir) { exit 0 }
    $key = $projectDir.Substring(0,1).ToLower() + $projectDir.Substring(1)
    $key = $key -replace ":\\", "--" -replace "\\", "-" -replace "_", "-"
    $memRoot = "$env:USERPROFILE\.claude\projects\$key\memory"
    if (-not (Test-Path $memRoot)) { exit 0 }

    $date    = Get-Date -Format "yyyy-MM-dd"
    $logFile = "$memRoot\domain\skill-runs.md"
    $row     = "| $date | auto-logged | $tcKey | $tcName | (update ticket + skill manually) |"

    Add-Content -Path $logFile -Value $row -Encoding UTF8
}

exit 0
