#!/usr/bin/env python3
import pandas as pd
import math
import os
import re

CSV_FILE = "topstep.csv"
OUT_DIR = "parts"
PARTS = 7
COMPLETED_FILE = "finished.txt"

def sanitize_filename(name: str) -> str:
    """Remove invalid filename characters for Windows/Linux/Mac."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def normalize_title(title: str) -> str:
    """Normalize titles to match the format in completed_trades.txt"""
    # title = title.replace(":", "__")
    # title = re.sub(r"[ /]", "_", title)

    title = sanitize_filename(title).replace(" ","_") + " done"
    # print(title)
    return title


def load_completed_trades(file_path=COMPLETED_FILE) -> set:
    """Load completed trades into a set"""
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def main():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"{CSV_FILE} not found")

    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_csv(CSV_FILE, sep=";", header=None, names=["Title", "URL"])
    print("the length of the df is ",len(df))

    # ✅ Load completed trades and filter them out
    completed = load_completed_trades()
    # print(completed)
    
    df = df[~df["Title"].apply(lambda t: normalize_title(t) in completed)]
    print("the length of the df is ",len(df))

    rows = len(df)
    if rows == 0:
        print("No new trades to process.")
        return

    chunk_size = math.ceil(rows / PARTS)

    for i in range(PARTS):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, rows)
        part_df = df.iloc[start:end]

        if not part_df.empty:
            out_file = os.path.join(OUT_DIR, f"part_{i+1:03}.csv")
            part_df.to_csv(out_file, index=False)
            print(f"Saved {out_file} with {len(part_df)} rows")


if __name__ == "__main__":
    main()