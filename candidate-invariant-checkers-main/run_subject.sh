#!/bin/bash

subject="$1"
invs_file="$2"

# Check that subject dir exists
if [ ! -d "$subject" ]; then
    echo "Subject directory $subject does not exist."
    exit 1
fi

# Check that invariants file exists
if [ ! -f "$invs_file" ]; then
    echo "Invariants file $invs_file does not exist."
    exit 1
fi

# Cd to subject directory, and run the sh script passing as argument the invariants file
cd "$subject" || exit 1
script_name="check_inv_validity_"$subject.sh
if [ ! -f "$script_name" ]; then
    echo "Script $script_name does not exist in $subject."
    exit 1
fi

# Remove valid/invalid if exits
rm -f valid_$(basename -- "$invs_file") invalid_$(basename -- "$invs_file")
output=$(bash "$script_name" "$invs_file")

unsat_count=$(printf "%s\n" "$output" | grep -Eo '\bunsat\b' | wc -w | awk '{print $1}')
sat_count=$(printf "%s\n" "$output" | grep -Eo '\bsat\b' | wc -w | awk '{print $1}')

echo "valid: $unsat_count"
echo "invalid: $sat_count"

valid_invs_file="valid_$(basename -- "$invs_file")"
output=$(bash check_candidates_imply_ground_truth_$subject.sh $valid_invs_file)

unsat_count=$(printf "%s\n" "$output" | grep -Eo '\bunsat\b' | wc -w | awk '{print $1}')
sat_count=$(printf "%s\n" "$output" | grep -Eo '\bsat\b' | wc -w | awk '{print $1}')

echo "implied ground truth: $unsat_count"
echo "not implied ground truth: $sat_count"
