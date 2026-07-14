# Shift Linkage Roles

Reference for how linked shifts and their role labels work in the new scheduler. This is the source of truth for the label list, the directional/mutual distinction, and the default giving/receiving word pairs. Update it when conventions change.

## What a linked shift is

Two shifts can be linked when one driver relates to another driver's shift for the day: finishing their stops, riding along to learn, splitting a route, and so on. On each shift card, a "Linked as" area shows the other driver, the referenced shift, and this driver's role in the link.

A shift can be linked to more than one other shift (e.g., linked as Sweeper to one driver and Helper to another). Each link is its own record.

## Model

Link labels work like Roster Status pills: a customizable list with shipped defaults. DSPs use different words for the same operational act, so customers pick from the defaults or add their own. Do not lock customers into a fixed taxonomy.

Each link record stores structure, not a display string:

- `linkLabel` — the customer-chosen label (from defaults or custom)
- `direction` — `directional` or `mutual` (a property of the label, see below)
- `role` — `initiating` or `receiving` (only meaningful when the label is directional)
- reference to the other shift + driver
- (optional, deferred) `reportingGroup` — see Reporting

The displayed role word is derived from `linkLabel` + `role`, never stored as free text.

## Direction: the one structural distinction

Vocabulary is open, but every label is one of two shapes. This is not customer-editable wording, it drives how the two cards render.

- **Directional** — one driver acts on the other. The two cards show different words: an initiating (giving) form and a receiving form. Example: Rescuer / Rescued.
- **Mutual** — peers, no giver or receiver. Both cards show the same word. Example: both cards read "Paired With."

When a customer creates a custom label, they choose directional or mutual. If directional, they set (or accept the default for) the giving word and the receiving word.

## Default labels

Shipped defaults. Customers can rename, add, or hide them.

### Directional

| Label | Initiating (giving) | Receiving |
|---|---|---|
| Sweeper | Sweeper | Swept |
| Rescuing | Rescuer | Rescued |
| Helping | Helper | Helped |
| Supporting | Supporter | Supported |
| Assisting | Assister | Assisted |
| Relieving | Reliever | Relieved |
| Covering | Coverer | Covered |
| Taking Over | Took Over | Handed Off |
| Training | Trainer | Trainee |
| Shadowing | Shadower | Shadowed |
| Ride Along | Rider | Host |
| Escorting | Escort | Escorted |
| Auditing | Auditor | Audited |

### Mutual (same word on both cards)

| Label |
|---|
| Paired With |
| Splitting Route |
| Load Balancing |

## Custom labels

A customer adding their own label provides:

1. The label name (e.g., "Backing Up").
2. Direction: directional or mutual.
3. If directional: the giving word and the receiving word. Default the receiving word to `<label> (received)` if they do not set one.

## Notes

- **Sweep and Rescue are intentionally distinct**, not aliases. This is a product decision. Keep the distinction documented for support so the two are not conflated.
- All labels are synonyms customers choose between. The default set is broad on purpose so a DSP finds their own language rather than being forced into ours.

## Open items

- **Display sentence frame (UI, for Andy and Jake):** how the receiving side reads on the card. One option is a preposition flip, "Linked as Rescuer to Mark Twain" on the giving card and "Rescued by John Smith" on the receiving card, so direction is carried by to/by. Not yet decided.
- **Reporting (deferred):** if per-label counts later need to roll up (e.g., all assist-type synonyms into one number), add an optional `reportingGroup` on each label now so the option exists later. Not built yet.
