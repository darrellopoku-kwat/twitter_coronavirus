#!/usr/bin/env python3

# command line args
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input_path', required=True)
parser.add_argument('--key', required=True)
parser.add_argument('--percent', action='store_true')
args = parser.parse_args()

# imports
import json
import matplotlib
matplotlib.use("Agg")  # needed on shared servers with no display
import matplotlib.pyplot as plt


# open the input path
with open(args.input_path) as f:
    counts = json.load(f)

# pick the dictionary we want to visualize
data = counts[args.key]  # e.g., counts["_all"]

# normalize (convert to percentages of the selected key's total)
ylabel = "Count"
if args.percent:
    total = sum(data.values())
    if total > 0:
        for k in data:
            data[k] = data[k] / total * 100.0
    ylabel = "Percent (%)"

# sort high -> low to get top 10
items = sorted(data.items(), key=lambda item: (item[1], item[0]), reverse=True)[:10]

# final results should be sorted low -> high
items = sorted(items, key=lambda item: (item[1], item[0]))

# bar graph
labels = [k for k, v in items]
values = [v for k, v in items]

plt.figure(figsize=(10, 5))
plt.bar(labels, values)
plt.xlabel("Key")
plt.ylabel(ylabel)
plt.title(f"Top 10 (low→high): {args.key}")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

output_file = f"{args.input_path}.{args.key}.top10.png"
plt.savefig(output_file, dpi=200)
plt.close()

print(f"Saved graph to {output_file}")
