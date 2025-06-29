import os
import csv
import argparse
from datetime import datetime


def _parse_timestamp(ts: str):
    """Convert a timestamp string to a datetime object."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(ts, fmt)
        except ValueError:
            continue
    try:
        # fallback: treat as epoch seconds
        return datetime.fromtimestamp(float(ts))
    except ValueError:
        return datetime.min


def _load_csv(path: str, prefix: str):
    data = {}
    if not os.path.exists(path):
        return data, []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        fields = []
        for row in reader:
            ts = row.get("timestamp")
            if ts is None:
                continue
            entry = data.setdefault(ts, {})
            for k, v in row.items():
                if k == "timestamp":
                    continue
                col = f"{prefix}_{k}"
                entry[col] = v
                if col not in fields:
                    fields.append(col)
    return data, fields


def merge_logs(completion_path="logs/completion_stats.csv",
               queue_path="logs/queue_stats.csv",
               rps_path="logs/rps_stats.csv",
               output_path="logs/merged_stats.csv"):
    sources = [
        (completion_path, "completion"),
        (queue_path, "queue"),
        (rps_path, "rps"),
    ]

    merged = {}
    headers = ["timestamp"]

    for path, prefix in sources:
        data, fields = _load_csv(path, prefix)
        headers.extend(f for f in fields if f not in headers)
        for ts, row in data.items():
            merged.setdefault(ts, {"timestamp": ts}).update(row)

    sorted_rows = sorted(merged.values(), key=lambda r: _parse_timestamp(r["timestamp"]))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in sorted_rows:
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge stats logs by timestamp")
    parser.add_argument("--completion", default="logs/completion_stats.csv", help="Path to completion stats CSV")
    parser.add_argument("--queue", default="logs/queue_stats.csv", help="Path to queue stats CSV")
    parser.add_argument("--rps", default="logs/rps_stats.csv", help="Path to rps stats CSV")
    parser.add_argument("-o", "--output", default="logs/merged_stats.csv", help="Output CSV path")
    args = parser.parse_args()

    merge_logs(args.completion, args.queue, args.rps, args.output)
