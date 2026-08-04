# CS plugin configuration, mirrored

**This is a copy for version control and backup. It is NOT the live configuration.**

The plugins read from:

```
~/.claude/plugins/config/claude-for-customer-success/
```

That directory is not a git repository, so until this mirror existed a week of configuration work lived in exactly one place with no history and no backup.

## Restore

Paths here match the live tree exactly, so restoring is a straight copy:

```
rsync -a --include='*/' --include='*.md' --exclude='*' \
  cs-plugin-config/ ~/.claude/plugins/config/claude-for-customer-success/
```

## Re-sync after editing the live config

```
rsync -a --include='*/' --include='*.md' --exclude='*' \
  ~/.claude/plugins/config/claude-for-customer-success/ cs-plugin-config/
```

**This is a manual mirror, so it drifts the moment the live config is edited.** Re-run the sync above before committing, or the repo silently holds a stale copy. A symlink would remove the drift and is worth considering.

## What is here

| File | What it is |
|---|---|
| `csm/CLAUDE.md` | The main CSM config. Health model, heartbeat trigger, outreach lifecycle, escalation matrix, data-quality traps |
| `csm/engage-message-templates.md` | **DRAFT.** Six ENGAGE outreach drafts covering 33 accounts |
| `adoption-conversation.md` | **DRAFT.** The RISK call script |
| `outcome-catalog.md` | `provisional-1.0`, 16 outcomes across 6 operator jobs. **Unratified, barred from customer-facing use** |
| `amp-cohort.md` | The 46 AMP accounts parked on Trial, plus 21 genuine trials |
| `company-profile.md` | Shared profile, read by all four CS plugins |
| `rollout-readiness.md` | What is still missing before the first customer call |
| `zoho-task-cleanup-2026-08-03.md` | Audit of the 217 stale tasks that were closed |

## Two things to know

**Nothing marked DRAFT is approved, and no customer contact is authorised.** The generator that consumes this config is dry-run by default.

**`csm/CLAUDE.md` is a real `CLAUDE.md`.** Working on files inside `cs-plugin-config/csm/` will load it as directory instructions. That is harmless but surprising if you have forgotten it is here. The filename is kept so a restore is a straight copy.
