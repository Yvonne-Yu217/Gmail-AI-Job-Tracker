import json
import os
from datetime import datetime


STATUS_PRIORITY = {
    # lower number = lower progress; higher number = higher progress
    "Applied": 1,
    "Assessment": 2,
    "Interviewed": 3,
    "Offer": 4,
    "Declined": 5,
}


def count_unknown_fields(app):
    """Count the number of 'Unknown' fields in an application record."""
    unknown_count = sum(1 for value in app.values() if value == "Unknown")
    return unknown_count


def parse_date(s: str):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


def pick_best_record(app_list):
    """Given a list of (idx, app) for same Company+Job Title, keep the best one.
    Priority: higher STATUS_PRIORITY, then fewer Unknown fields, then newer Date.
    Returns the idx to keep and a set of idxs to drop.
    """
    # Build comparable tuples
    scored = []
    for idx, app in app_list:
        status = app.get("status", "Applied")
        prio = STATUS_PRIORITY.get(status, 0)
        unknowns = count_unknown_fields(app)
        d = parse_date(app.get("Date", ""))
        scored.append((idx, app, prio, unknowns, d))

    # Sort by: priority desc, unknowns asc, date desc
    scored.sort(key=lambda x: (x[2], -x[3], x[4] or datetime.min.date()))  # temporary sort; will reorder next
    # We actually want: priority DESC, unknowns ASC, date DESC
    scored = sorted(scored, key=lambda x: (
        x[2],                    # priority
        -x[3],                   # negative unknowns for fewer first
        (x[4] or datetime.min.date())
    ), reverse=True)

    keep_idx = scored[0][0]
    drop_idxs = {idx for idx, *_ in scored[1:]}
    return keep_idx, drop_idxs


def clean_duplicates(filename="data/job_applications.json"):
    # Load the existing job applications
    if not os.path.exists(filename):
        print("No job_applications.json found.")
        return

    with open(filename, 'r') as f:
        applications = json.load(f)

    print(f"Found {len(applications)} records before cleaning.")

    # Group applications by (Company, Job Title)
    buckets = {}
    for i, app in enumerate(applications):
        key = (app.get('Company', ''), app.get('Job Title', ''))
        buckets.setdefault(key, []).append((i, app))

    to_remove = set()

    for key, app_list in buckets.items():
        if len(app_list) <= 1:
            continue
        keep, drops = pick_best_record(app_list)
        to_remove.update(drops)

    # Remove in reverse order to avoid index shift
    removed = 0
    for idx in sorted(to_remove, reverse=True):
        del applications[idx]
        removed += 1

    # Save the cleaned data
    with open(filename, 'w') as f:
        json.dump(applications, f, indent=4)

    print(f"Cleaned {removed} duplicate entries. Now {len(applications)} records remain.")


if __name__ == '__main__':
    clean_duplicates()