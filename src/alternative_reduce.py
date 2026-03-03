#!/usr/bin/env python3
"""
alternative_reduce.py

Usage example:
  python3 src/alternative_reduce.py --hashtags "#coronavirus" "#코로나바이러스"

What it does:
- Scans outputs/geoTwitter20-YYYY-MM-DD.zip.lang JSON files produced by map.py
- For each requested hashtag, computes the number of tweets containing that hashtag per day
  (summing across languages for that hashtag on that day)
- Plots one line per hashtag:
    x-axis: day of year (1..366 for 2020)
    y-axis: tweet count for that hashtag on that day
- Saves a PNG.
"""

import argparse
import glob
import json
import os
import re
from datetime import date
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")  # server-safe (no display needed)
import matplotlib.pyplot as plt


DATE_RE = re.compile(r"geoTwitter20-(\d{2})-(\d{2})\.zip\.lang$")


def parse_mm_dd_from_filename(path: str) -> Tuple[int, int]:
    """Extract (month, day) from a mapper output filename."""
    base = os.path.basename(path)
    m = DATE_RE.search(base)
    if not m:
        raise ValueError(f"Unexpected filename format (expected geoTwitter20-MM-DD.zip.lang): {base}")
    month = int(m.group(1))
    day = int(m.group(2))
    return month, day


def day_of_year_2020(month: int, day: int) -> int:
    """Return day-of-year (1..366) for 2020."""
    return (date(2020, month, day) - date(2020, 1, 1)).days + 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hashtags",
        nargs="+",
        required=True,
        help='List of hashtags to plot, e.g. --hashtags "#coronavirus" "#코로나바이러스"',
    )
    parser.add_argument(
        "--outputs_folder",
        default="outputs",
        help="Folder containing mapper outputs (default: outputs)",
    )
    parser.add_argument(
        "--output_png",
        default="outputs/hashtag_timeseries.png",
        help="Where to save the PNG (default: outputs/hashtag_timeseries.png)",
    )
    args = parser.parse_args()

    hashtags: List[str] = args.hashtags
    outputs_folder: str = args.outputs_folder

    # 1) Scan mapper outputs (.lang files)
    lang_paths = glob.glob(os.path.join(outputs_folder, "geoTwitter20-*.zip.lang"))
    if not lang_paths:
        raise FileNotFoundError(
            f"No .lang files found in {outputs_folder}. Expected files like geoTwitter20-01-01.zip.lang"
        )

    # Build a list of (doy, path) sorted by day-of-year
    doy_and_path: List[Tuple[int, str]] = []
    for p in lang_paths:
        mm, dd = parse_mm_dd_from_filename(p)
        doy = day_of_year_2020(mm, dd)
        doy_and_path.append((doy, p))
    doy_and_path.sort(key=lambda t: t[0])

    # We'll construct a complete day range from min..max (typically 1..366)
    min_doy = doy_and_path[0][0]
    max_doy = doy_and_path[-1][0]
    x_days = list(range(min_doy, max_doy + 1))

    # Dataset: hashtag -> {doy -> count}
    counts_by_hashtag: Dict[str, Dict[int, int]] = {h: {} for h in hashtags}

    # 2) Construct dataset by reading each day's JSON once
    for doy, path in doy_and_path:
        with open(path, "r") as f:
            day_json = json.load(f)  # structure: { "_all": {lang: count, ...}, "#tag": {lang: count, ...}, ... }

        for h in hashtags:
            # If hashtag not present that day, treat as 0
            if h in day_json and isinstance(day_json[h], dict):
                # sum across languages to get total tweets for that hashtag that day
                total_for_day = 0
                for _, v in day_json[h].items():
                    try:
                        total_for_day += int(v)
                    except Exception:
                        # ignore non-numeric values if any
                        pass
                counts_by_hashtag[h][doy] = total_for_day
            else:
                counts_by_hashtag[h][doy] = 0

    # Convert to aligned series lists
    y_series: Dict[str, List[int]] = {}
    for h in hashtags:
        y_series[h] = [counts_by_hashtag[h].get(d, 0) for d in x_days]

    # 3) Plot
    os.makedirs(os.path.dirname(args.output_png) or ".", exist_ok=True)

    plt.figure(figsize=(12, 6))
    for h in hashtags:
        plt.plot(x_days, y_series[h], label=h)

    plt.xlabel("Day of Year (2020)")
    plt.ylabel("Number of Tweets Using Hashtag")
    plt.title("Hashtag Usage Over 2020")
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output_png, dpi=200)
    plt.close()

    print(f"Saved plot to {args.output_png}")


if __name__ == "__main__":
    main()
