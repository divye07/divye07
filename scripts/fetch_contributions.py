#!/usr/bin/env python3
"""
Fetch real daily contribution counts from GitHub's public, unauthenticated
contributions endpoint and write data/contributions.json with the raw days
plus derived stats (current streak, longest streak, best day, monthly totals).

No token, no auth, no GraphQL -- just the public HTML GitHub already serves.
Run daily by .github/workflows/update-profile-art.yml.

Usage:
    python scripts/fetch_contributions.py [username]
"""
import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

USERNAME = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_PROFILE_USER", "divye07")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        # fallback: try the newer data-level attribute cells
        cells = soup.select("[data-date]")
    if not cells:
        print("no calendar cells found -- github markup may have changed", file=sys.stderr)
        sys.exit(1)

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""

        # Try data-level as fallback for count approximation
        level = int(td.get("data-level", 0))
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.match(r"(\d+)", text)
            count = int(m.group(1)) if m else (level * 3 if level > 0 else 0)
        days.append({"date": date, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def compute_current_streak(days):
    today = datetime.date.today().isoformat()
    streak = 0
    for d in reversed(days):
        if d["date"] > today:
            continue
        if d["count"] > 0:
            streak += 1
        else:
            break
    return streak


def compute_longest_streak(days):
    longest = 0
    current = 0
    for d in days:
        if d["count"] > 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def compute_monthly_totals(days):
    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["count"]
    return monthly


def main():
    print(f"fetching contributions for @{USERNAME}...")
    days = fetch_days()
    total = sum(d["count"] for d in days)
    best = max((d["count"] for d in days), default=0)
    best_day = next((d["date"] for d in days if d["count"] == best), None)

    data = {
        "username": USERNAME,
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        "total": total,
        "best_day": best_day,
        "best_count": best,
        "current_streak": compute_current_streak(days),
        "longest_streak": compute_longest_streak(days),
        "monthly": compute_monthly_totals(days),
        "days": days,
    }

    os.makedirs(os.path.dirname(os.path.abspath(OUT_PATH)), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"saved {len(days)} days -> {OUT_PATH}")
    print(f"  total={total}  best={best} on {best_day}")
    print(f"  current streak={data['current_streak']}  longest={data['longest_streak']}")


if __name__ == "__main__":
    main()
