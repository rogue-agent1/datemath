#!/usr/bin/env python3
"""datemath - Date arithmetic and business day calculator.

Single-file, zero-dependency CLI.
"""

import sys
import argparse
from datetime import datetime, date, timedelta
import calendar


def parse_date(s):
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]:
        try: return datetime.strptime(s, fmt).date()
        except ValueError: continue
    raise ValueError(f"Can't parse: {s}")


def parse_duration(s):
    """Parse duration like 5d, 3w, 2m, 1y."""
    import re
    m = re.match(r'^(-?\d+)([dwmy])$', s.lower())
    if not m: raise ValueError(f"Invalid duration: {s}")
    n, unit = int(m.group(1)), m.group(2)
    return n, unit


def add_duration(d, n, unit):
    if unit == "d": return d + timedelta(days=n)
    if unit == "w": return d + timedelta(weeks=n)
    if unit == "m":
        month = d.month + n
        year = d.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        day = min(d.day, calendar.monthrange(year, month)[1])
        return d.replace(year=year, month=month, day=day)
    if unit == "y": 
        try: return d.replace(year=d.year + n)
        except ValueError: return d.replace(year=d.year + n, day=28)  # Feb 29


def is_business_day(d):
    return d.weekday() < 5  # Mon-Fri


def cmd_add(args):
    d = parse_date(args.date) if args.date != "today" else date.today()
    n, unit = parse_duration(args.duration)
    result = add_duration(d, n, unit)
    delta = (result - date.today()).days
    print(f"  {d} + {args.duration} = {result} ({result.strftime('%A')})")
    if delta > 0:
        print(f"  {delta} days from today")
    elif delta < 0:
        print(f"  {abs(delta)} days ago")


def cmd_diff(args):
    d1 = parse_date(args.date1)
    d2 = parse_date(args.date2)
    delta = abs((d2 - d1).days)
    bdays = sum(1 for i in range(delta) if is_business_day(min(d1, d2) + timedelta(days=i)))
    print(f"  {d1} → {d2}")
    print(f"  Calendar days: {delta}")
    print(f"  Business days: {bdays}")
    print(f"  Weeks: {delta // 7} + {delta % 7}d")
    print(f"  Months: {abs((d2.year - d1.year) * 12 + d2.month - d1.month)}")


def cmd_bizdays(args):
    """Add business days."""
    d = parse_date(args.date) if args.date != "today" else date.today()
    n = args.days
    step = 1 if n > 0 else -1
    remaining = abs(n)
    current = d
    while remaining > 0:
        current += timedelta(days=step)
        if is_business_day(current):
            remaining -= 1
    print(f"  {d} + {n} business days = {current} ({current.strftime('%A')})")


def cmd_cal(args):
    """Show month calendar."""
    d = parse_date(args.date) if args.date and args.date != "today" else date.today()
    cal_text = calendar.month(d.year, d.month)
    print(cal_text)


def main():
    p = argparse.ArgumentParser(prog="datemath", description="Date arithmetic")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("add", aliases=["a"], help="Add duration to date")
    s.add_argument("date"); s.add_argument("duration", help="e.g. 5d, 3w, 2m, 1y")
    s = sub.add_parser("diff", aliases=["d"], help="Difference between dates")
    s.add_argument("date1"); s.add_argument("date2")
    s = sub.add_parser("bizdays", aliases=["biz"], help="Add business days")
    s.add_argument("date"); s.add_argument("days", type=int)
    s = sub.add_parser("cal", help="Show calendar")
    s.add_argument("date", nargs="?")
    args = p.parse_args()
    if not args.cmd: p.print_help(); return 1
    cmds = {"add": cmd_add, "a": cmd_add, "diff": cmd_diff, "d": cmd_diff,
            "bizdays": cmd_bizdays, "biz": cmd_bizdays, "cal": cmd_cal}
    return cmds[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
