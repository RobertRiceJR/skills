# session-end-stats.ps1
# Claude Code SessionEnd hook — writes one markdown file per session under
# %USERPROFILE%\.claude\session-stats\sessions\YYYY-MM-DD_<shortid>.md
# and appends a one-line entry to %USERPROFILE%\.claude\session-stats\index.md.
#
# Invoked by Claude Code with a JSON payload on stdin:
#   { "session_id": "...", "transcript_path": "...jsonl", "cwd": "..." }
#
# Tune $pricing below if Anthropic rates change or you use a model not listed.

$ErrorActionPreference = 'Stop'

# --- Pricing table (USD per 1M tokens) -------------------------------------
# Best-effort snapshot; edit when rates drift.  Per-model: input, output,
# cache_read, and TWO cache-write rates by TTL (5-minute and 1-hour).
# Standard multipliers off base input: cache_read = 0.1x, cache_write_5m =
# 1.25x, cache_write_1h = 2.0x.  Opus 4.7/4.8 in/out ($5/$25) user-confirmed
# 2026-05; Opus 4/4.5/4.6 ASSUMED same tier; Sonnet/Haiku 1h-write DERIVED at
# 2x (not independently confirmed); claude-3-opus = legacy $15/$75.
$pricing = @{
    'claude-opus-4-8'    = @{ input = 5.00;  output = 25.00; cache_write_5m = 6.25;  cache_write_1h = 10.00; cache_read = 0.50 }
    'claude-opus-4-7'    = @{ input = 5.00;  output = 25.00; cache_write_5m = 6.25;  cache_write_1h = 10.00; cache_read = 0.50 }
    'claude-opus-4-6'    = @{ input = 5.00;  output = 25.00; cache_write_5m = 6.25;  cache_write_1h = 10.00; cache_read = 0.50 }
    'claude-opus-4-5'    = @{ input = 5.00;  output = 25.00; cache_write_5m = 6.25;  cache_write_1h = 10.00; cache_read = 0.50 }
    'claude-opus-4'      = @{ input = 5.00;  output = 25.00; cache_write_5m = 6.25;  cache_write_1h = 10.00; cache_read = 0.50 }
    'claude-sonnet-4-6'  = @{ input = 3.00;  output = 15.00; cache_write_5m = 3.75;  cache_write_1h = 6.00;  cache_read = 0.30 }
    'claude-sonnet-4-5'  = @{ input = 3.00;  output = 15.00; cache_write_5m = 3.75;  cache_write_1h = 6.00;  cache_read = 0.30 }
    'claude-sonnet-4'    = @{ input = 3.00;  output = 15.00; cache_write_5m = 3.75;  cache_write_1h = 6.00;  cache_read = 0.30 }
    'claude-haiku-4-5'   = @{ input = 1.00;  output = 5.00;  cache_write_5m = 1.25;  cache_write_1h = 2.00;  cache_read = 0.10 }
    'claude-haiku-4'     = @{ input = 1.00;  output = 5.00;  cache_write_5m = 1.25;  cache_write_1h = 2.00;  cache_read = 0.10 }
    'claude-3-5-sonnet'  = @{ input = 3.00;  output = 15.00; cache_write_5m = 3.75;  cache_write_1h = 6.00;  cache_read = 0.30 }
    'claude-3-5-haiku'   = @{ input = 0.80;  output = 4.00;  cache_write_5m = 1.00;  cache_write_1h = 1.60;  cache_read = 0.08 }
    'claude-3-opus'      = @{ input = 15.00; output = 75.00; cache_write_5m = 18.75; cache_write_1h = 30.00; cache_read = 1.50 }
}

function Get-PricingForModel([string]$model) {
    if (-not $model) { return $null }
    $m = $model.ToLowerInvariant()
    # exact
    if ($pricing.ContainsKey($m)) { return $pricing[$m] }
    # strip trailing date/version suffix (e.g. claude-haiku-4-5-20251001 -> claude-haiku-4-5)
    $stripped = ($m -replace '-(\d{8}|\d{6}|\d{4})$', '')
    if ($pricing.ContainsKey($stripped)) { return $pricing[$stripped] }
    # progressive trim of trailing -segments
    while ($stripped -match '-') {
        $stripped = $stripped -replace '-[^-]*$', ''
        if ($pricing.ContainsKey($stripped)) { return $pricing[$stripped] }
    }
    return $null
}

function Yaml-Escape([string]$s) {
    if ($null -eq $s) { return '' }
    $t = $s -replace "`r`n", ' ' -replace "`n", ' ' -replace "`t", ' '
    $t = $t.Trim()
    if ($t.Length -gt 200) { $t = $t.Substring(0, 200) + '...' }
    # quote and escape backslashes + double quotes for YAML double-quoted form
    $t = $t -replace '\\', '\\' -replace '"', '\"'
    return '"' + $t + '"'
}

# --- Read payload from stdin -----------------------------------------------
$stdin = [Console]::In.ReadToEnd()
if (-not $stdin) { exit 0 }

try {
    $payload = $stdin | ConvertFrom-Json
} catch {
    # Bad payload — silently exit; hook must never block session end.
    exit 0
}

$sessionId      = [string]$payload.session_id
$transcriptPath = [string]$payload.transcript_path
$cwd            = [string]$payload.cwd

if (-not $sessionId -or -not $transcriptPath) { exit 0 }
if (-not (Test-Path $transcriptPath)) { exit 0 }

# --- Set up output paths ---------------------------------------------------
$statsDir    = Join-Path $env:USERPROFILE '.claude\session-stats'
$sessionsDir = Join-Path $statsDir 'sessions'
$indexPath   = Join-Path $statsDir 'index.md'

if (-not (Test-Path $sessionsDir)) {
    New-Item -ItemType Directory -Path $sessionsDir -Force | Out-Null
}

# --- Parse the JSONL transcript --------------------------------------------
$inputTokens     = 0
$outputTokens    = 0
$cacheReadTokens = 0
$cacheCreateTokens = 0
$cacheCreate5mTokens = 0
$cacheCreate1hTokens = 0
$messageCount    = 0
$toolsUsed       = New-Object System.Collections.Generic.HashSet[string]
$models          = New-Object System.Collections.Generic.HashSet[string]
$firstPrompt     = $null
$firstTs         = $null
$lastTs          = $null

# Per-model usage for accurate cost when models change mid-session
$perModelUsage = @{}

Get-Content -LiteralPath $transcriptPath -Encoding UTF8 | ForEach-Object {
    $line = $_
    if (-not $line) { return }
    try { $rec = $line | ConvertFrom-Json } catch { return }

    $ts = $rec.timestamp
    if ($ts) {
        if (-not $firstTs) { $firstTs = $ts }
        $lastTs = $ts
    }

    # First user prompt
    if (-not $firstPrompt -and $rec.type -eq 'user') {
        $content = $rec.message.content
        if ($content -is [string]) {
            $firstPrompt = $content
        } elseif ($content) {
            foreach ($c in $content) {
                if ($c.type -eq 'text' -and $c.text) { $firstPrompt = $c.text; break }
            }
        }
    }

    if ($rec.type -eq 'assistant' -and $rec.message) {
        $messageCount++
        $msg = $rec.message
        if ($msg.model) { [void]$models.Add([string]$msg.model) }

        # Tool calls
        if ($msg.content) {
            foreach ($c in $msg.content) {
                if ($c.type -eq 'tool_use' -and $c.name) {
                    [void]$toolsUsed.Add([string]$c.name)
                }
            }
        }

        # Usage
        $u = $msg.usage
        if ($u) {
            $i  = [int]($u.input_tokens            | ForEach-Object { $_ })
            $o  = [int]($u.output_tokens           | ForEach-Object { $_ })
            $cr = [int]($u.cache_read_input_tokens | ForEach-Object { $_ })

            # Cache writes are priced by TTL: 5-minute vs 1-hour.  Prefer the
            # split under usage.cache_creation; fall back to the aggregate
            # (treated as 1h, the current Claude Code default) if absent.
            $cw5 = 0; $cw1 = 0
            if ($u.cache_creation) {
                $cw5 = [int]($u.cache_creation.ephemeral_5m_input_tokens | ForEach-Object { $_ })
                $cw1 = [int]($u.cache_creation.ephemeral_1h_input_tokens | ForEach-Object { $_ })
            } else {
                $cw1 = [int]($u.cache_creation_input_tokens | ForEach-Object { $_ })
            }
            $cc = $cw5 + $cw1

            $inputTokens         += $i
            $outputTokens        += $o
            $cacheReadTokens     += $cr
            $cacheCreate5mTokens += $cw5
            $cacheCreate1hTokens += $cw1
            $cacheCreateTokens   += $cc

            $modelKey = if ($msg.model) { [string]$msg.model } else { 'unknown' }
            if (-not $perModelUsage.ContainsKey($modelKey)) {
                $perModelUsage[$modelKey] = @{ input = 0; output = 0; cache_read = 0; cache_write_5m = 0; cache_write_1h = 0 }
            }
            $perModelUsage[$modelKey].input          += $i
            $perModelUsage[$modelKey].output         += $o
            $perModelUsage[$modelKey].cache_read     += $cr
            $perModelUsage[$modelKey].cache_write_5m += $cw5
            $perModelUsage[$modelKey].cache_write_1h += $cw1
        }
    }
}

$totalTokens = $inputTokens + $outputTokens + $cacheReadTokens + $cacheCreateTokens
# Keep cache vs non-cache separate so cost-per-token isn't diluted by cheap cache reads.
$cacheTokens    = $cacheReadTokens + $cacheCreateTokens
$nonCacheTokens = $inputTokens + $outputTokens

# --- Estimate cost ---------------------------------------------------------
$cost = 0.0
foreach ($modelKey in $perModelUsage.Keys) {
    $p = Get-PricingForModel $modelKey
    if (-not $p) { continue }
    $u = $perModelUsage[$modelKey]
    $cost += ($u.input          / 1000000.0) * $p.input
    $cost += ($u.output         / 1000000.0) * $p.output
    $cost += ($u.cache_read     / 1000000.0) * $p.cache_read
    $cost += ($u.cache_write_5m / 1000000.0) * $p.cache_write_5m
    $cost += ($u.cache_write_1h / 1000000.0) * $p.cache_write_1h
}
$costStr = [Math]::Round($cost, 4).ToString('F4', [System.Globalization.CultureInfo]::InvariantCulture)

# Persisted cost-per-million-token rates.  *_total divides by all tokens (incl.
# cache reads, so it trends low because cache reads are ~10x cheaper); *_noncache
# divides by only input+output — the full-rate tokens — the more honest number.
$inv = [System.Globalization.CultureInfo]::InvariantCulture
$cpmTotal    = if ($totalTokens    -gt 0) { [Math]::Round($cost / ($totalTokens    / 1000000.0), 4) } else { 0 }
$cpmNonCache = if ($nonCacheTokens -gt 0) { [Math]::Round($cost / ($nonCacheTokens / 1000000.0), 4) } else { 0 }
$cpmTotalStr    = ([double]$cpmTotal).ToString('F4', $inv)
$cpmNonCacheStr = ([double]$cpmNonCache).ToString('F4', $inv)

# --- Derived fields --------------------------------------------------------
$startedDt = $null; $endedDt = $null; $durationMin = 0
if ($firstTs) { try { $startedDt = [DateTime]::Parse($firstTs, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind) } catch {} }
if ($lastTs)  { try { $endedDt   = [DateTime]::Parse($lastTs,  [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind) } catch {} }
if ($startedDt -and $endedDt) {
    $durationMin = [Math]::Round(($endedDt - $startedDt).TotalMinutes, 2)
}

$dateNow = if ($startedDt) { $startedDt.ToLocalTime().ToString('yyyy-MM-dd') } else { (Get-Date).ToString('yyyy-MM-dd') }
$monthNow = if ($startedDt) { $startedDt.ToLocalTime().ToString('yyyy-MM') } else { (Get-Date).ToString('yyyy-MM') }
$shortId = if ($sessionId.Length -ge 8) { $sessionId.Substring(0, 8) } else { $sessionId }
$primaryModel = if ($models.Count -gt 0) { ($models | Select-Object -First 1) } else { 'unknown' }
$toolsList    = ($toolsUsed | Sort-Object) -join ', '
$modelsList   = ($models    | Sort-Object) -join ', '

# Tags — light heuristic
$tags = New-Object System.Collections.Generic.List[string]
if ($cwd -match 'test_suite-IMA_360_playwright') { $tags.Add('ima-360') }
if ($cwd -match 'ci-working-notes')              { $tags.Add('vault') }
if ($cwd -match '\.claude') { $tags.Add('claude-config') }

# --- Write per-session file ------------------------------------------------
$outFile = Join-Path $sessionsDir ("{0}_{1}.md" -f $dateNow, $shortId)

$frontmatter = @"
---
session_id: $sessionId
date: $dateNow
month: $monthNow
started: $firstTs
ended: $lastTs
duration_minutes: $durationMin
cwd: $(Yaml-Escape $cwd)
model: $primaryModel
models: [$modelsList]
message_count: $messageCount
input_tokens: $inputTokens
output_tokens: $outputTokens
cache_read_tokens: $cacheReadTokens
cache_creation_tokens: $cacheCreateTokens
cache_write_5m_tokens: $cacheCreate5mTokens
cache_write_1h_tokens: $cacheCreate1hTokens
cache_tokens: $cacheTokens
non_cache_tokens: $nonCacheTokens
total_tokens: $totalTokens
estimated_cost_usd: $costStr
cost_per_mtok_total: $cpmTotalStr
cost_per_mtok_noncache: $cpmNonCacheStr
tools_used: [$toolsList]
first_prompt: $(Yaml-Escape $firstPrompt)
tags: [$([string]::Join(', ', $tags))]
---
"@

$body = @"

# Session $shortId ($dateNow)

- **CWD:** $cwd
- **Duration:** $durationMin min
- **Model(s):** $modelsList
- **Messages (assistant):** $messageCount
- **Tokens:** input $inputTokens / output $outputTokens / cache-read $cacheReadTokens / cache-create $cacheCreateTokens (total $totalTokens, non-cache $nonCacheTokens)
- **Estimated cost:** `$$costStr`  ($cpmTotalStr/Mtok total · $cpmNonCacheStr/Mtok non-cache)
- **Tools used:** $toolsList

## First prompt
$firstPrompt
"@

Set-Content -LiteralPath $outFile -Value ($frontmatter + $body) -Encoding UTF8

# --- Append to index.md ----------------------------------------------------
if (-not (Test-Path $indexPath)) {
    Set-Content -LiteralPath $indexPath -Value "# Claude Code session index`n`nOne line per session, newest at the bottom.`n" -Encoding UTF8
}
$indexLine = "- $dateNow $shortId | $durationMin min | $messageCount msgs | $totalTokens tok | `$$costStr | $cpmNonCacheStr/Mtok-nc | $primaryModel | $cwd"
Add-Content -LiteralPath $indexPath -Value $indexLine -Encoding UTF8

exit 0
