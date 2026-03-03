#!/bin/sh
set -eu

data_dir="/data/Twitter dataset"
out_dir="outputs"
log_dir="logs"

mkdir -p "$out_dir" "$log_dir"

# Only 2020 files
for file in "$data_dir"/geoTwitter20-*.zip; do
  base=$(basename "$file")
  log="$log_dir/${base}.log"

  echo "Starting $file -> $log"
  nohup python3 src/map.py --input_path "$file" --output_folder "$out_dir" > "$log" 2>&1 &
done

echo "All map.py jobs launched."
echo "Check progress: ls $log_dir | head"
echo "Check running: ps aux | grep 'python3 src/map.py' | grep -v grep"#!/bin/sh























