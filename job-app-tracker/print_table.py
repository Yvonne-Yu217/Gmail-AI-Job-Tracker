# print_table.py
import argparse
import json
import os
from datetime import datetime
import pandas as pd

DATA_PATH = os.path.join("data", "job_applications.json")


def parse_args():
    p = argparse.ArgumentParser(
        description="Print or export a table of your job applications from data/job_applications.json"
    )
    p.add_argument("--status", nargs="*", default=None,
                   help="Filter by status, e.g. --status Applied Interviewed Offer Declined")
    p.add_argument("--since", type=str, default=None,
                   help="Only include records on/after this date (YYYY-MM-DD)")
    p.add_argument("--until", type=str, default=None,
                   help="Only include records on/before this date (YYYY-MM-DD)")
    p.add_argument("--limit", type=int, default=None,
                   help="Limit the number of rows after sorting by date (desc)")
    p.add_argument("--output", type=str, default=None,
                   help="Optional path to save. Extension decides the format: .md, .csv, or .xlsx")
    return p.parse_args()


def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}. Run main.py first to generate it.")
    with open(path, "r") as f:
        data = json.load(f)
    # Normalize to DataFrame
    df = pd.DataFrame(data)
    # Ensure expected columns exist
    for col in ["Company", "Job Title", "Location", "status", "Date"]:
        if col not in df.columns:
            df[col] = ""
    # Parse date for sorting/filtering
    def parse_date(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None
    df["_Date"] = df["Date"].apply(parse_date)
    return df


def apply_filters(df: pd.DataFrame, status_list, since, until) -> pd.DataFrame:
    out = df.copy()
    if status_list:
        status_set = {s.strip().capitalize() for s in status_list}
        out = out[out["status"].str.capitalize().isin(status_set)]
    if since:
        since_d = datetime.strptime(since, "%Y-%m-%d").date()
        out = out[(out["_Date"].notna()) & (out["_Date"] >= since_d)]
    if until:
        until_d = datetime.strptime(until, "%Y-%m-%d").date()
        out = out[(out["_Date"].notna()) & (out["_Date"] <= until_d)]
    return out


def sort_and_limit(df: pd.DataFrame, limit: int | None) -> pd.DataFrame:
    out = df.sort_values(by=["_Date"], ascending=False, na_position="last")
    if limit is not None:
        out = out.head(limit)
    return out


def select_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Company", "Job Title", "Location", "status", "Date"]
    return df[cols]


def save_output(df: pd.DataFrame, out_path: str):
    ext = os.path.splitext(out_path)[1].lower()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    if ext == ".md":
        with open(out_path, "w") as f:
            f.write(df.to_markdown(index=False))
        print(f"Saved markdown table to {out_path}")
    elif ext == ".csv":
        df.to_csv(out_path, index=False)
        print(f"Saved CSV to {out_path}")
    elif ext in (".xlsx", ".xls"):
        df.to_excel(out_path, index=False)
        print(f"Saved Excel to {out_path}")
    else:
        raise ValueError("Unsupported extension. Use .md, .csv, or .xlsx")


def main():
    args = parse_args()
    df = load_data(DATA_PATH)
    df = apply_filters(df, args.status, args.since, args.until)
    df = sort_and_limit(df, args.limit)
    df = select_columns(df)

    # Print to console nicely
    try:
        print(df.to_markdown(index=False))
    except Exception:
        # Fallback to simple print if tabulate is unavailable in this pandas version
        print(df.to_string(index=False))

    # Optional save
    if args.output:
        save_output(df, args.output)


if __name__ == "__main__":
    main()
