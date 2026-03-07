#!/bin/bash

echo "Generating valid specs imply ground truth..."
java -jar ../../alloy/AlloyCommandline.jar alloy-inv-checker-enqueue.als 2> alloy-output.txt
python generate_valid_specs_imply_ground_truth_from_alloy_output.py < alloy-output.txt

echo "Preparing ground truth check Alloy model..."
cat alloy-inv-checker-enqueue.als groundtruth-checks.als > check-gt.als

echo "Checking ground truth implications using Alloy..."
java -jar ../../alloy/AlloyCommandline.jar check-gt.als
