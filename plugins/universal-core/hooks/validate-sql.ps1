# PreToolUse hook: warns on DML/DDL SQL before execution against mssql-qa or mssql-int.
# Always allows - never blocks. Warn-only safety gate.

$input_json = $null
try {
    $raw = [Console]::In.ReadToEnd()
    $input_json = $raw | ConvertFrom-Json
} catch {
    # If stdin is not valid JSON, allow silently
    Write-Output '{"permissionDecision":"allow"}'
    exit 0
}

$query = ""
try {
    $query = $input_json.tool_input.query
    if (-not $query) {
        Write-Output '{"permissionDecision":"allow"}'
        exit 0
    }
} catch {
    Write-Output '{"permissionDecision":"allow"}'
    exit 0
}

# Strip single-line SQL comments (-- ...) and multi-line (/* ... */)
$stripped = $query -replace '--[^\r\n]*', ''
$stripped = $stripped -replace '/\*[\s\S]*?\*/', ''
$stripped = $stripped.Trim()

# Match DML/DDL operations
$dml_pattern = '(?i)^\s*(INSERT|UPDATE|DELETE|DROP|TRUNCATE|EXEC|EXECUTE|ALTER|CREATE\s+TABLE|MERGE)\b'

if ($stripped -match $dml_pattern) {
    $operation = $Matches[1].Trim().ToUpper()

    # Extract first table name after operation keyword (best-effort)
    $table = ""
    $table_match = $stripped -match '(?i)(?:INSERT\s+INTO|UPDATE|DELETE(?:\s+FROM)?|DROP\s+TABLE|TRUNCATE\s+TABLE|ALTER\s+TABLE|MERGE\s+INTO|MERGE)\s+(\[?[\w.]+\]?)'
    if ($table_match) {
        $table = " on table ``$($Matches[1])``"
    }

    $tool_name = $input_json.tool_name
    $db = if ($tool_name -match 'mssql-int') { 'mssql-int (INT database)' } else { 'mssql-qa (QA database)' }

    $warning = "WARNING: DML/DDL detected - $operation$table against $db. Confirm this write operation is intentional before proceeding."

    $output = [PSCustomObject]@{
        permissionDecision = "allow"
        additionalContext  = $warning
    }
    Write-Output ($output | ConvertTo-Json -Compress)
} else {
    Write-Output '{"permissionDecision":"allow"}'
}
