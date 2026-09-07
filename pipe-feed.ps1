# ==== LIVE PIPE FEED — LinkedIn + WhatsApp state -> GitHub broker ====
# Runs one cycle: pull current DM state from browser, write state.json, push.
# Usage: powershell -ExecutionPolicy Bypass -File pipe-feed.ps1  (loop mode: add -Loop)

param([switch]$Loop)

$repo = "D:\anonym\war-pipe"

function Write-State {
    # State comes from Kilo's browser watch (chrome-devtools MCP reads LinkedIn tab 98 + WhatsApp tab 95)
    # This script wraps whatever Kilo captures. Kilo calls this after each sweep.
    param($json)
    $json | Set-Content "$repo\state.json" -Encoding UTF8
    Set-Location $repo
    git add state.json
    git commit -m "pipe: state update $(Get-Date -Format 'HH:mm:ss')" --quiet
    git push --quiet 2>$null
    if ($LASTEXITCODE -eq 0) { Write-Host "[$(Get-Date -Format HH:mm:ss)] pushed" } else { Write-Host "[$(Get-Date -Format HH:mm:ss)] push failed (will retry next cycle)" }
}

if ($Loop) {
    while ($true) {
        # Kilo injects state each cycle via the watcher
        Start-Sleep -Seconds 60
    }
}
