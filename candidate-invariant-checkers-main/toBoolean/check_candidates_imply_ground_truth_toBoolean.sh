#!/bin/bash
filename="$1"
# echo "checking valid candidates imply ground truth 1"
python check_candidate_implies_ground_truth_1_toBoolean.py "$filename" > candidate_checker_1.z3
z3 candidate_checker_1.z3
