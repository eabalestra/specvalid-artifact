#!/bin/bash
filename_path="$1"
filename=$(basename -- "$filename_path")
unsat_filename="valid_$filename"
sat_filename="invalid_$filename"

while read candidate; do
    # Ignore lines starting with buckets, specs, ===========, ::: - present in buckets files
    if [[ "$candidate" == buckets* || "$candidate" == specs* || "$candidate" == "==========="* || "$candidate" == :::* ]]; then
        continue
    fi
    python check_inv_validity_foo.py "$candidate" > candidate.z3
    output=$(z3 candidate.z3)
    if [[ "$output" == "unsat" ]]; then
        echo "$candidate" >> "$unsat_filename"
        echo "unsat"
    elif [[ "$output" == "sat" ]]; then
        echo "$candidate" >> "$sat_filename"
        echo "sat"
    else
        echo "Warning: Unexpected output for line: $candidate" >&2
    fi
done < $filename_path
