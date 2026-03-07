#!/bin/bash
filename="$1"
echo "checking valid candidates imply ground truth 1"
python check_candidate_imply_ground_truth_1_copySignInt.py "$filename" > candidate_checker_1.z3
z3 candidate_checker_1.z3
echo "checking valid candidates imply ground truth 2"
python check_candidate_imply_ground_truth_2_copySignInt.py "$filename" > candidate_checker_2.z3
z3 candidate_checker_2.z3
echo "checking valid candidates imply ground truth 3"
python check_candidate_imply_ground_truth_3_copySignInt.py "$filename" > candidate_checker_3.z3
z3 candidate_checker_3.z3
echo "checking valid candidates imply ground truth 4"
python check_candidate_imply_ground_truth_4_copySignInt.py "$filename" > candidate_checker_4.z3
z3 candidate_checker_4.z3