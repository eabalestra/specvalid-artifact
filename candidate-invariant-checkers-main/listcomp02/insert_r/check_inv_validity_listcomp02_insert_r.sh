#!/bin/bash

invs_file="$1"

echo "Translating candidate invariants to Alloy format..."
python translate_assertions.py < $invs_file

echo "Generating inv checker Alloy model..."
rm -f alloy-inv-checker-insert_r.als
cat alloy-checker-prelude-insert_r.als generated-preds.txt > alloy-inv-checker-insert_r.als

echo "Checking validity of candidate invariants using Alloy..."
java -jar ../../alloy/AlloyCommandline.jar alloy-inv-checker-insert_r.als 2>&1
total_count=$(grep "run" alloy-inv-checker-insert_r.als | wc -l | awk '{print $1}')
echo "total_candidates: $total_count"
