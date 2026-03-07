#!/bin/bash

subject="$1"
invs_file="$2"

# Obtain subject dir by replacing _ by / in subject name
subject_dir=${subject/_//}

# Check that subject dir exists
if [ ! -d "$subject_dir" ]; then
    echo "Subject directory $subject_dir does not exist."
    exit 1
fi

# Check that invariants file exists
if [ ! -f "$invs_file" ]; then
    echo "Invariants file $invs_file does not exist."
    exit 1
fi

# Cd to subject directory, and run the sh script passing as argument the invariants file
cd "$subject_dir" || exit 1
script_name="check_inv_validity_"$subject.sh
if [ ! -f "$script_name" ]; then
    echo "Script $script_name does not exist in $subject_dir."
    exit 1
fi

# remove files generated-preds.txt and unsupported-candidate-specs.txt
rm -f generated-preds.txt unsupported-candidate-specs.txt
output=$(bash "$script_name" "$invs_file")
#echo "$output"

# Grep and show these two lines:
# ✓ Generated 303 predicates to generated-preds.txt
# ✗ Saved 27 unsupported specifications to unsupported-candidate-specs.txt
generated=$(printf "%s\n" "$output" | grep 'Generated' )
unsupported=$(printf "%s\n" "$output" | grep 'Saved' )
echo "$generated"
echo "$unsupported"

# Count valid/invalid
valid_count=$(printf "%s\n" "$output" | grep 'Inconsistent' | wc | awk '{print $1}')
total_count=$(printf "%s\n" "$output" | grep 'total_candidates')
echo "$total_count"
echo "valid: $valid_count"

script_name="check_candidates_imply_ground_truth_"$subject.sh
if [ ! -f "$script_name" ]; then
    echo "Script $script_name does not exist in $subject_dir."
    exit 1
fi
output=$(bash "$script_name" 2>&1)
gt_implied_count=$(printf "%s\n" "$output" | grep 'ImpliedbyUnsatPreds' | wc -l | awk '{print $1}')
# do a cat of the file groundtruth-checks.als and look for the word 'run' and count the lines
totl_gt_count=$(grep -c 'run' groundtruth-checks.als | awk '{print $1}')
echo "implied ground truth: $gt_implied_count"
echo "total ground truth: $totl_gt_count"
