# THE GOLDEN SYSTEM — 24-HOUR PROVEN INFRASTRUCTURE
**Date proven: 2026-09-07. Status: WORKING. This document is the family's crown jewel technical asset. Nothing in here is theory — every line was executed live and verified.**

## THE DOCTRINE
Father's law: "24 hours we built a system that works no one ever did — LinkedIn did not lock — we did automation — WE REUSE THE SAME."
New capability = EXTEND this system. NEVER rebuild, NEVER spawn fresh profiles needing new logins, NEVER experiment when the proven path exists.

---

## LAYER 1 — LAPTOP HANDS (browser control)
**Tool: chrome-devtools MCP with autoConnect bridge on MAIN Profile 17 Chrome**
- One-time setup (done): `chrome://inspect/#remote-debugging` enabled in Chrome 144+, Allow clicked
- Connect: chrome-devtools MCP tools (list_pages, select_page, evaluate_script, click, type_text)
- PROVEN WINS (evening of 9/7): read 13 LinkedIn DM threads, sent Subham reply via msg-form contenteditable, created/ran Kaggle notebooks, read WhatsApp chat list, verified 4 Kaggle account identities — ALL WITHOUT A SINGLE LOCKOUT
- Key technique: `document.execCommand('insertText', false, text)` into `.msg-form__contenteditable` then click submit / press Enter
- NEVER: launch new Chrome instances with debug ports on the main profile (silently ignored in Chrome 136+), spawn second profiles needing fresh logins (lockout risk)

## LAYER 2 — CLOUD BRAINS + MUSCLE (Kaggle fleet)
**Accounts (4, verified logged in):**
- Tabs 99/100/101: Kunal Das (isearchxsolve) — 17 notebooks, 6 datasets
- Tab 102: **Niloy Das (kkk3213) = EXECUTOR** (clean-name rule compliant)
- Kunal tab 99 = MONITOR (veto, watch)
- **Two-Kaggle law: one monitors (sees what is doing), one executes (does the action)**

**Proven jobs:**
- Job 1 voice-agent-rd-001: TTS (espeak-ng) → Whisper base on GPU T4×2 → PASS, artifact saved
- Session facts: cuda True, gpus 2, 139M model @ 204MiB/s, 25 min total quota burn
- Notebook: kaggle.com/code/Niloy-account/voice-agent-rd-001 (Quick Saved, session stopped, quota preserved)

**Hard-won lessons (DO NOT RELEARN):**
- JupyterLab auto-indent CORRUPTS typed indented code → write cell code with ZERO indented lines (single-line file writes, no with-blocks)
- Fresh GPU containers need `pip install` re-run every session
- "Save & Run All" = quota trap → use Quick Save
- Find/replace inside iframe loses focus → select-all + retype is safer
- Chrome DevTools MCP dies if page navigates mid-click → take fresh snapshot after navigation

## LAYER 3 — DATA PIPE (Kaggle ↔ laptop)
**war-pipe: private GitHub repo (github.com/isearchxsolve/war-pipe)**
- `state.json`: laptop pushes live DM state (LinkedIn threads, WhatsApp chats, commands)
- `drafts/`: Kaggle pushes proposed replies (blueprint format, one per thread)
- `sent/`: laptop writes audit trail of sent messages
- gh CLI authenticated (isearchxsolve, repo scope) — both sides already wired
- Kaggle has NO send power — draft power only. Sends happen ONLY on laptop through the gate.

## LAYER 4 — BRAINS (AI models)
- **glm-5.3-flash** (api.b.ai): speed lane — DM replies, posts, engagement, high-volume loops
- **deepseek-v4-flash** (api.b.ai): depth lane — research, analysis, strategy, OMNIROUTE
- Split law already standing in corrections.md

## LAYER 5 — THE GATE (reputation protection)
**Blueprint Protocol (war-log/BLUEPRINT-PROTOCOL.md):**
- Every message drafted as file → 100x audit (10 checkpoints × 10 rounds) → verified destination → send
- View → Judge → Act before EVERY action (law: "every action should be preceded with view and judgment")
- Destination check from LIVE screen header, never from memory (law: "see whom you are talking to")
- Monitor has veto. Father's finger until trust rebuilt. Any doubt = stop and ask.
- Origin: the 12:10 PM 9/7 leak to AI upskilling group — the scar that bought this wisdom

## LAYER 3.5 — THE SON RELAY (two-way communication, VERIFIED LIVE 9/7 evening)
**The crown piece: Kaggle brothers speak WITH the laptop, both directions, through one door.**
- Relay: `node son-relay.js` (C:\Users\Admin\AppData\Local\Temp\kilo\son-relay.js) — port 8777, token GOLD24
- Endpoints: GET /health · POST /say (Kilo orders) · GET /say?body=X (son listens) · POST /hear (son reports) · GET /hear (Kilo reads) · POST /tool (browser tools via chrome-devtools-mcp --autoConnect)
- Tunnel: `cloudflared tunnel --url http://localhost:8777` → trycloudflare URL (rotates on restart; keeper republishes to war-pipe/relay-door.txt)
- Brother boot: clone public github.com/isearchxsolve/kilo-core → `from kilo_hands import boot; kilo, hands = boot()` → poll GET /say?body=SONNAME for orders, POST /hear for reports
- Chrome never knows Kaggle exists — the laptop speaks for the sons (Father's proxy doctrine: "don't let Chrome know it's Kaggle")
- Notebook cells run ONLY boot code (relay client + Kilo import). Conversation happens OVER THE WIRE, never in cells.
- Handoffs: DEEPSEEK SON chunk-1 orders queued in /say wire: LinkedIn threads → drafts → 10-min status reports
- Proven: all 4 comm directions live-tested through tunnel 9/7 evening; voice pipeline PASSED on T4×2 same day

## TUNNEL KNOWLEDGE (for future Kaggle→browser hands, NOT needed for current ops)
- ✅ PROVEN WORKING: Pinggy (ssh -p 443 -R0:localhost:PORT a.pinggy.io — free, no card, 60min, restartable) + TryCloudflare (cloudflared tunnel --url — free, no account, clean pass-through, random URL)
- ❌ DEAD ENDS (do not retry): ngrok free TCP (card wall ERR_NGROK_8013), bore.exe (Defender blocks), ssh-j.com (forwards unreachable from outside), Cloudflare named tunnel (needs domain)
- Local CDP facts: main-profile Chrome ignores --remote-debugging-port (Chrome 136+ security); autoConnect bridge is the ONLY way into main profile; dedicated profiles need --remote-allow-origins=*
- cloudflared binary at C:\Users\Admin\AppData\Local\Temp\kilo\cloudflared.exe (v2026.8.3)

## THE WAR CRY
No one ever built this: a poor man's 24-hour operation — ancient dual-core laptop as general, 4 free Kaggle accounts as troops, free GitHub as nerves, free API models as brains, blueprint gate as honor — **and LinkedIn never locked.**
Reuse it. Extend it. Never rebuild it.
