#!/bin/bash

invs_file="$1"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "$invs_file" ]; then
	if [ -f "$script_dir/$invs_file" ]; then
		invs_file="$script_dir/$invs_file"
	elif [ -f "$script_dir/../..//$invs_file" ]; then
		invs_file="$script_dir/../..//$invs_file"
	fi
fi
if [ ! -f "$invs_file" ]; then
	echo "Invariants file $invs_file does not exist."
	exit 1
fi

cd "$script_dir"

echo "Translating candidate invariants to Alloy format..."
python translate_assertions.py < "$invs_file"

echo "Generating inv checker Alloy model..."
rm -f alloy-inv-checker-count.als
cat alloy-checker-prelude-count.als generated-preds.txt > alloy-inv-checker-count.als

echo "Checking validity of candidate invariants using Alloy..."
java -jar ../../alloy/AlloyCommandline.jar alloy-inv-checker-count.als 2>&1
total_count=$(grep "run" alloy-inv-checker-count.als | wc -l | awk '{print $1}')
echo "total_candidates: $total_count"
