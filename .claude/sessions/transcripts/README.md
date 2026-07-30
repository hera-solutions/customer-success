# Raw session transcripts

**These are appendices, not records.** The record of a session is the written log in
`.claude/sessions/YYYY-MM-DD-*.md`. Read that first. It is written in plain language,
it captures the reasoning, and it is a few hundred lines rather than a few thousand.

These files exist only for the rare case where you need to see exactly what was run,
in what order, with what output. Treat them as a court transcript: complete, and
almost never the thing you actually want to read.

## Why the written log is the record and this is not

The convention in
[`knowledge/session-logging-prompt-for-code-repos.md`](../../../knowledge/session-logging-prompt-for-code-repos.md)
says plainly: *"Do not include raw chat transcripts. Write in plain language."* That
guidance is right, and these files are a deliberate exception requested for
completeness, not a change to it.

A raw transcript is a poor record because:

- Most of its volume is tool output: query results, file dumps, table listings. The
  reasoning is a small fraction of the bytes.
- It contains false starts, retracted claims and wrong figures presented as right at
  the time. Without the written log to tell you which conclusions survived, reading
  the transcript alone will actively mislead you.
- It is JSONL, so it is not readably diffable and greppable only by luck.

## What is in these files

Each line is one JSON object. Useful fields:

| Field | Meaning |
|---|---|
| `type` | `user`, `assistant`, `system`, `attachment`, and various UI records |
| `message.role` | `user` or `assistant` |
| `message.content` | Array of content blocks: text, `tool_use`, `tool_result` |
| `timestamp` | ISO 8601, UTC |

To read one as prose:

```bash
python3 - <<'EOF'
import json
for line in open('2026-07-28-cs-plugin-setup-and-health-model.jsonl'):
    d = json.loads(line)
    m = d.get('message') or {}
    if m.get('role') not in ('user', 'assistant'):
        continue
    c = m.get('content')
    if isinstance(c, str):
        print(f"\n### {m['role']}\n{c}")
    elif isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get('type') == 'text':
                print(f"\n### {m['role']}\n{b['text']}")
EOF
```

## Redactions

**These files are redacted. They are not byte-identical to the originals.**

Anything replaced is marked inline with an explicit `[REDACTED-...]` token, so you can
always tell where something was removed and what kind of thing it was.

| Session | Redaction | Why |
|---|---|---|
| `2026-07-28-cs-plugin-setup-and-health-model.jsonl` | `[REDACTED-MIRADORE-API-KEY]`, 14 occurrences | A live Miradore device-management API key for Tailwind Delivery LLC appeared in terminal output when `Tenant_202511241117.csv` was read from the home directory. It is a customer's third-party credential and git history is permanent |

**If you add a transcript here, scan it first.** Git history cannot be quietly
un-published. At minimum check for AWS key ids (`AKIA`/`ASIA` prefixes),
`SessionToken` values, PEM private-key headers, connection strings with embedded
passwords, and bearer, GitHub or Stripe tokens. Be aware that a scan script's own
patterns get echoed into the next transcript, so `-----BEGIN ... PRIVATE KEY-----`
appearing in a file is usually the pattern, not a key. Check with a real regex rather
than a substring test before concluding either way.

## Confidentiality

These transcripts contain **named customers with their revenue, driver counts, health
state and cancellation reasons**, plus production table names, index names and AWS
account structure. This repository is private and already holds customer data, so it
is an appropriate home. They should not be copied anywhere with a wider audience.

## Size

Roughly 5 MB per long session. Not gitignored, deliberately, because the point is that
they survive in history. If this directory grows unreasonably, prune old transcripts
rather than the written logs.
