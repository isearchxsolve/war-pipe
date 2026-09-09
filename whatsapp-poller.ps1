# WHATSAPP CONTINUOUS POLLER — via proven son-relay (reuse-proven-system-law)
# Polls Father's WhatsApp self-chat every 20s through relay /tool -> chrome-devtools MCP.
# Captures every new state of the chat into D:\anonym\war-log\whatsapp-poll.log
# CAPTURE ONLY — never sends. Sends happen only by Kilo with eyes open.

$relay = 'http://127.0.0.1:8777'
$token = 'GOLD24'
$log   = 'D:\anonym\war-log\whatsapp-poll.log'
$fn    = "() => { const p = document.querySelector('#main'); return p ? (p.innerText || '').slice(-1500) : 'NO_MAIN'; }"

function Post-Tool($name, $args) {
  $body = @{ name = $name; args = $args } | ConvertTo-Json -Depth 5 -Compress
  return Invoke-RestMethod -Method Post -Uri "$relay/tool?token=$token" -Body $body -ContentType 'application/json' -TimeoutSec 25
}

function Get-WaPageId {
  $r = Post-Tool 'list_pages' @{}
  $txt = ''
  if ($r -and $r.content) { $txt = ($r.content | ForEach-Object { $_.text }) -join "`n" }
  $lines = $txt -split "`n" | Where-Object { $_ -match '^\s*\d+:' }
  foreach ($ln in $lines) {
    if ($ln -match '(\d+):\s*(\((\d+)\)\s*)?(.*)\(https://web\.whatsapp\.com' -or $ln -match '(\d+):.*whatsapp') {
      $id = [int]$Matches[1]
      return @{ id = $id; desc = $ln.Trim() }
    }
  }
  return $null
}

$last = ''
$cycle = 0
Add-Content -Path $log -Value "=== POLLER START $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ==="

while ($true) {
  $cycle++
  try {
    $wa = Get-WaPageId
    if ($null -eq $wa) {
      Add-Content -Path $log -Value "[$(Get-Date -Format 'HH:mm:ss')] cycle $cycle : NO WHATSAPP PAGE FOUND"
    } else {
      $r  = Post-Tool 'evaluate_script' @{ pageId = $wa.id; function = $fn; waitForStableDom = $false }
      $txt = ''
      if ($r -and $r.content) { $txt = ($r.content | ForEach-Object { $_.text }) -join "`n" }
      if ($txt -ne $last) {
        Add-Content -Path $log -Value "[$(Get-Date -Format 'HH:mm:ss')] page $($wa.id) CHANGED:"
        Add-Content -Path $log -Value $txt
        Add-Content -Path $log -Value '----'
        $last = $txt
      }
    }
  } catch {
    Add-Content -Path $log -Value "[$(Get-Date -Format 'HH:mm:ss')] cycle $cycle ERROR: $($_.Exception.Message)"
  }
  Start-Sleep -Seconds 20
}
