"""
BROTHER BRAINS — wire real AI drafting into the fleet loop.
Each duty function calls the API, drafts in Kunal's voice, speaks to /hear.
Keys come from war-pipe (private) - NEVER hardcoded in public repos.
"""

import json, os, urllib.request

# Father's provider (from memory: https://api.b.ai/v1/chat/completions)
API_BASE = "https://api.b.ai/v1/chat/completions"
KEY_FILE = "/kaggle/working/war-pipe/api_keys.json"  # pushed privately


def load_keys():
    if not os.path.exists(KEY_FILE):
        return None
    with open(KEY_FILE) as f:
        return json.load(f)


def draft(model, system, prompt, keys):
    k = keys.get(model)
    if not k:
        return None
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300
    }).encode()
    req = urllib.request.Request(
        API_BASE, data=body, method="POST",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {k}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.loads(r.read().decode())
            return out["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[draft failed: {e}]"


KUNAL_VOICE = (
    "You write as Kunal Das: direct sentences, builder's pride, "
    "no AI-speak, no apologies, no over-explaining. "
    "Sign-off '- Kunal' when suitable. NEVER mention: banks, loans, "
    "courts, police, EMIs, prices, agent codenames, phone numbers."
)


def dm_draft(thread_context, keys):
    return draft("deepseek-v4-flash", KUNAL_VOICE,
                 f"Reply to this LinkedIn DM thread. Context: {thread_context}. "
                 f"Write one warm, professional reply that moves the conversation forward.",
                 keys)


def wa_draft(who, keys):
    return draft("glm-5.3-flash", KUNAL_VOICE,
                 f"Warm WhatsApp check-in to {who} (family/elder). Tell them things "
                 f"are fixed and under control. Short, warm, respectful.",
                 keys)


def comment_draft(topic, keys):
    return draft("glm-5.3-flash", KUNAL_VOICE,
                 f"Write one value-adding LinkedIn comment on: {topic}. "
                 f"2-3 sentences, builder's insight, no hashtags.",
                 keys)


def post_draft(theme, keys):
    return draft("deepseek-v4-flash", KUNAL_VOICE,
                 f"Write tomorrow's LinkedIn post on: {theme}. "
                 f"Hook line, 5-8 short lines, one takeaway, no hashtags.",
                 keys)
