"""The daily CS run. Order matters, and two of these are critical alerts.

ESTABLISHED 08-05-2026. John classified both roster drop-off and driver cliff as
CRITICAL DAILY signals: "that could mean real change that they are potentially going
to churn."

WHY THESE TWO ARE DAILY AND THE HEARTBEATS ARE NOT

The heartbeats are days-since measures against a 30-day line, so running them daily
changes nothing much: an account crossing 30 days today was at 29 yesterday. These
two measure RATE, and rate is only visible if you look often.

The GNC Transportation case makes the argument. Its billed driver count:

    07-26   92 drivers
    07-27   19          <- lost 73 in ONE DAY
    07-29    7
    08-03    1

The last closed invoice, dated 07-02, still reads 80.5 average drivers and $745.84.
**Billing would not reveal this collapse until the September invoice**, roughly 37
days after it happened. The daily count showed it on 07-27.

ORDER, and why it is this order

    1  staff_history.py     Daily activeStaff per tenant from InvoiceLineItem.
                            MUST BE FIRST: usage_signals reads it for the 4th
                            heartbeat, and driver_cliff computes entirely from it.
    2  driver_cliff.py      CRITICAL. Pure computation on step 1, no queries.
    3  usage_signals.py     The four heartbeats and the tier per tenant.
    4  roster_dropoff.py    CRITICAL. Needs step 1 for the adoption vs shrinking split.
    5  generate_tasks.py     Dry run. Reads steps 1 and 3.

Usage:
    python3 run_daily.py                  # whole chain, as of today
    python3 run_daily.py --as-of 2026-08-04
    python3 run_daily.py --critical-only  # just the two alert steps, needs step 1 cached
"""
import argparse, datetime as dt, os, subprocess, sys

# Parent stdout is block-buffered when piped, so our warnings appeared AFTER the
# child scripts' output and the back-dating banner was effectively invisible.
def say(*a):
    print(*a, flush=True)

HERE = os.path.dirname(os.path.abspath(__file__))

# (script, args, is_critical, one-line purpose)
CHAIN = [
    ("staff_history.py",  [], False, "daily driver counts, feeds everything below"),
    ("driver_cliff.py",   [], True,  "CRITICAL: roster falling off a cliff"),
    ("usage_signals.py",  [], False, "the four heartbeats and tiers"),
    ("roster_dropoff.py", [], True,  "CRITICAL: abandoning the daily roster"),
    ("generate_tasks.py", [], False, "task plan, dry run only"),
]


def warn_if_backdated(as_of):
    """
    Refuse to run quietly against a past date.

    TRAP, hit 08-05-2026 and it produced a wildly wrong answer. Running the chain
    with --as-of 2026-08-04 on 08-05 made ENGAGE jump from 34 tasks to 102 and
    'document' dark from 34 accounts to 114. Nothing was broken: to_date() correctly
    clamps any date AFTER as_of to None, because several source fields are
    user-entered and hold typos like 8610-07-17. So every customer who did something
    TODAY was scored as having done nothing, ever.

    Back-dating is legitimate for reproducing an old run, but it must be deliberate,
    because the failure is silent and it inflates darkness across the whole book.
    """
    today = dt.date.today()
    if as_of < today:
        say("*" * 78)
        say(f"  WARNING: --as-of {as_of} is BEFORE today ({today}).")
        say("  Every signal dated after {} is clamped away, so accounts active".format(as_of))
        say("  since then will read as DARK. Task counts will be inflated.")
        say("  This is only correct if you are deliberately reproducing an old run.")
        say("*" * 78)
        return True
    return False


def run(script, args, as_of):
    cmd = [sys.executable, os.path.join(HERE, script), "--as-of", as_of] + args
    say("\n" + "=" * 78)
    say(f"  {script}")
    say("=" * 78)
    r = subprocess.run(cmd, cwd=HERE)
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--as-of", default=dt.date.today().isoformat())
    ap.add_argument("--critical-only", action="store_true")
    a = ap.parse_args()

    as_of_date = dt.date.fromisoformat(a.as_of)
    warn_if_backdated(as_of_date)

    steps = [c for c in CHAIN if c[2]] if a.critical_only else CHAIN
    if a.critical_only:
        say("CRITICAL ONLY. Assumes staff_history.py has already run today.")

    failed = []
    for script, args, crit, why in steps:
        code = run(script, args, a.as_of)
        if code != 0:
            failed.append(script)
            # A critical step failing must not be buried under later output.
            if crit:
                print(f"\n  *** {script} FAILED (exit {code}). This is a critical "
                      f"alert step. Do not treat today's run as clean. ***")

    print("\n" + "=" * 78)
    if failed:
        print("  FAILED STEPS: " + ", ".join(failed))
        sys.exit(1)
    print("  all steps completed. No tasks were written to Zoho: the generator is")
    print("  dry-run only and has no writer yet.")


if __name__ == "__main__":
    main()
