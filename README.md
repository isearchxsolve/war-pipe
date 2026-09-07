# WAR-PIPE — Live Kaggle<->Laptop DM Pipeline
**Private broker repo. Laptop pushes live DM state; Kaggle executor pulls, thinks (glm/deepseek API), pushes drafts; laptop monitor pulls drafts -> blueprint gate -> Father approves -> send.**

## Protocol
- `state.json` — laptop writes: current LinkedIn threads + WhatsApp chats snapshot + commands
- `drafts/` — Kaggle writes: proposed replies (one file per thread, blueprint format)
- `sent/` — laptop writes: audit trail of actually-sent messages
- Cadence: laptop pushes every 60s when watch mode active; Kaggle polls every 60s during a session

## Laws
- Repo stays PRIVATE. Nothing here goes public. Ever.
- Kaggle NEVER pushes to LinkedIn/WhatsApp directly — it has no send power, only draft power
- Every draft passes the 100x audit gate on the laptop before any send
- Blueprint protocol applies to every message in both directions

## Jobs for Kaggle (executor)
1. Read state.json -> identify threads where last message is FROM THEM (needs reply)
2. Draft replies in Kunal's voice using glm-5.3-flash/deepseek-v4-flash API
3. Push drafts/ + mark thread claimed
4. Log activity to activity.log
