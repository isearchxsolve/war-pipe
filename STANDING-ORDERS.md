# STANDING ORDERS LEDGER — ALL FATHER'S ORDERS (48-HOUR WAR)
**Source of truth. Committed to git. Re-fired on every army boot. Relay bank persists them (order-bank.json).**
Updated: 2026-09-08 ~9:30 AM IST

## IRON LAWS (never change)
1. EYES-OPEN: verify-before-send, read back header/target, never blind. Binds Kilo + all soldiers.
2. VOICE: WhatsApp Ma 2 + Biswajit Bose (student, "sir") = KUNAL voice tumi-form. Others = Kilo identity.
3. PERMISSION: only LinkedIn DM/message SENDS need Father approval (wire order SEND-APPROVED). All else free.
4. ENGAGEMENT = complete their pending tasks (not greetings; greetings only Ma + Biswajit).
5. DELEGATION = ownership of full outcome, TASK-DONE proof.
6. HANDS = action hands (navigate/click/type/send/apply), not read-only.
7. SINGLE-WRITER: one surface one writer; soldiers watch+draft, Kilo sends.
8. CLIPBOARD over typing. CLOUD over laptop (dual-core monitors only). SEQUENTIAL queue, CPU low.
9. RECTIFY IN SILENCE — no sorry, fix and show working results.
10. Everything stays: relay + tunnel + runner + Chrome on laptop. Engines on Kaggle = additive.

## SURVIVAL LANES (Lok Adalat 12 Sep Howrah — countdown)
1. TDS E-FILING (PAN AIIPD6525H): refund Rs 3,018 (TDS 4,73,000 vs tax 4,69,982). Portal login WORKING. Steps: View Filed Returns all years -> Form 16 (KEROSS zip + Gmail) -> 26AS -> compute both regimes -> Outstanding Demand check (Sec 245) -> Kotak account (holder exactly KUNAL DAS, KKBK IFSC) [OTP: Father] -> pre-validate -> flip nomination -> file belated ITR (open till 31-Dec-2026) -> e-verify 30d (Aadhaar OTP +91 86172 16163; old 6290262764 dead) -> track. Refund to KOTAK ONLY (Axis loan-gated off-limits).
2. JOB HUNT — AGGRESSIVE APPLY all channels (LinkedIn/Naukri/Monster/Indeed/FoundIt). Beneficiaries: Kunal Das (AI Architect 13y remote senior), Partha Deb (B.Tech CSE NIT Silchar, parthadeb891@gmail.com, +91 93950 13303, profiles live 9AM, daily applies), Dr. Tapasi Das (remote scientific editor/AI content). Log APPLIED prefix.
3. GMAIL SCAN end-to-end: loan warnings, court/Lok Adalat notices, bank letters — SCAN-ALERT to Father immediately, never act alone.
4. INCOME LANES (4): omniroute-monetizer (PRIORITY), Agent School 20x999 (recruiting = sons' job), voice-agent clinic leads, KDP books.
5. REPO OPS: 100+ repos E2E test -> audit -> surgical fix, worker+auditor pairs, REPO-EXEC reports.

## FAMILY ENGAGEMENT (done 2026-09-07 night, standing cadence)
- Ma 2 (grandma, stroke survivor): daily greetings ~9AM/evening/night. DONE + reply answered.
- Didi Dr. Tapasi Das: full LinkedIn review delivered; daily 15 connection requests + weekly post drafts. DONE.
- Biswajit Bose (student): greetings 3x/day + Satbar class. Voice fix DONE (deleted Kilo-voice, resent Kunal tumi-form).
- Soumyendu Uncle: email soumyendu.pc@gmail.com received; organize family technical records + teaching files. PENDING.
- Partha Uncle: resume sealed; call-readiness confirmed; his Q answered. Profiles live 9AM. IN PROGRESS.
- Subham Sharma (LinkedIn HOT): 15-min chat request 2:02 PM — reply drafted, awaiting Father slot approval.

## ARCHITECTURE (locked)
- Relay v3 on 127.0.0.1:8777 token GOLD24: /say orders bank (PERSISTENT order-bank.json), /hear reports, /tool MCP, /health.
- Tunnel: NGROK STATIC DOMAIN — PERMANENT DOOR (Father 2026-09-09: "tunnel should be fixed forever no more dying tunnel"). DOOR: https://meredith-impermissible-unsportively.ngrok-free.dev — never changes, never regenerated. Watchdog v2 (SYSTEM task KILO-RELAY-WATCHDOG, boot+logon) resurrects relay+ngrok every 15s; survives reboot, power cut, sleep, network-off. relay-door.txt is truth.
- Kaggle ONE instance hosts 3 ENGINE subprocesses (ports 9999/9998/9997, kw linkedin/naukri/whatsapp): hands-proxy -> relay /tool -> FATHERS CHROME (only browser).
- Soldiers: 100 (SEAT-A: DM/WA/COMMENTER/POSTER x10 on E1; SEAT-B: BIZMODEL/MONITOR/SCOUT x10 on E2; SEAT-C: LEDGER/HERALD/WARDEN x10 on E3). Poll orders bank every cycle; TASK:{json steps} executed live; TASK-DONE reports.
- v5 cell committed: war-pipe/kilo-core/engine_cell.py (+engine_server.py). Door URL baked — regenerate cell on door change.
- Kaggle sessions die at 12h: re-run cell = full army back in ~6 min. Orders survive (relay bank + this ledger).

## WIRE PROTOCOL
- Orders: POST /say {body: SQUAD, text: "TASK:" + json{name, issued, steps:[{hand, args}], report}} — steps: navigate/list_pages/snapshot/click/type_text/key/eval.
- Reports: POST /hear {body: soldier-tag, text}. Kilo reads /hear for reports, /say?body=SQUAD for order bank.
- Dedupe: task name+issued; soldiers skip seen tasks. New task at 3AM runs at 3:01. No restarts, no code edits.