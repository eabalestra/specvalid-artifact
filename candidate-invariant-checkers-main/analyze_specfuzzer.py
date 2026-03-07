import os
import subprocess
import csv
import sys

curr_dir = os.getcwd()

specfuzzer_results_dir = os.path.join(curr_dir, "../specfuzzer-subject-results")
invs_type = sys.argv[1] # e.g., "all_invs", "buckets"
single_subject = sys.argv[2] if len(sys.argv) > 2 else None

if invs_type not in ["all_invs", "buckets"]:
    print("Invalid invs_type. Use 'all_invs' or 'buckets'.")
    sys.exit(1)

def get_invs_file(output_folder, invs_t):
    for file in os.listdir(output_folder):
        if invs_t == "all_invs" and file.endswith("assertions") and not file.endswith("buckets.assertions"):
            return os.path.join(output_folder, file)
        if invs_t == "buckets" and file.endswith("buckets.assertions"):
            return os.path.join(output_folder, file)
    return None


def analyze_subject_with_alloy(subject_folder, method_name, invs_file, csv_output_data):
    # Placeholder for Alloy analysis implementation
    command = [
        "bash",
        "run_subject_alloy_checkers.sh",
        subject_folder,
        invs_file
    ]
    # Run command, get the output console and look for the following four variables:
    # total_candidates: 303
    # valid: 170
    # implied ground truth: 3
    # not implied ground truth: 0
    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout
    lines = output.splitlines()
    valid = int([line for line in lines if line.startswith("valid:")][0].split(":")[1].strip())
    total_candidates = int([line for line in lines if line.startswith("total_candidates:")][0].split(":")[1].strip())
    implied = int([line for line in lines if line.startswith("implied ground truth:")][0].split(":")[1].strip())
    total_gt = int([line for line in lines if line.startswith("total ground truth:")][0].split(":")[1].strip())

    # Calculate metrics
    invalid = total_candidates - valid
    total = total_candidates
    not_implied = total_gt - implied

    # Calculate precision (valid / total), handle division by zero
    precision = valid / total if total > 0 else 0.0
    precision *= 100

    # Calculate recall (implied / total_gt), handle division by zero
    recall = implied / total_gt if total_gt > 0 else 0.0
    recall *= 100

    f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print(f"valid: {valid}")
    print(f"invalid: {invalid}")
    print(f"implied ground truth: {implied}")
    print(f"not implied ground truth: {not_implied}")
    print(f"total: {total}")
    print(f"precision: {precision:.2f}")
    print(f"recall: {recall:.2f}")
    print(f"F1 score: {f1_score:.2f}")
    print()

    # Add row to CSV data
    csv_output_data.append({
        "subject": folder,
        "method": method_name,
        "total": total,
        "valid": valid,
        "invalid": invalid,
        "precision": f"{precision:.2f}",
        "total_gt": total_gt,
        "gt_implied": implied,
        "gt_not_implied": not_implied,
        "recall": f"{recall:.2f}",
        "f1_score": f"{f1_score:.2f}"
    })


# Prepare CSV data
csv_data = []
csv_headers = ["subject", "method", "total", "valid", "invalid", "precision",
               "total_gt", "gt_implied", "gt_not_implied", "recall", "f1_score"]

# Loop over all folders in specfuzzer_results_dir
for folder in os.listdir(specfuzzer_results_dir):
    folder_path = os.path.join(specfuzzer_results_dir, folder)
    if os.path.isdir(folder_path):
        output_folder = os.path.join(folder_path, "output")
        if not os.path.exists(output_folder):
            continue
        invs_file = get_invs_file(output_folder, invs_type)
        if invs_file is None:
            continue

        if single_subject and folder != single_subject:
            continue

        print(f"subject: {folder}")
        method_name = folder.split("_")[1]
        print(f"method: {method_name}")
        alloy_subject = False
        if not os.path.exists(method_name):
            snd_folder_option = folder.replace("_", "/", 1)
            alloy_subject = True
            if not os.path.exists(snd_folder_option):
                print('Missing ground truth checkers. Skipping...\n')
                continue

        print(f"Using invariants file: {invs_file}")
        if alloy_subject:
            analyze_subject_with_alloy(folder, method_name, invs_file, csv_data)
            continue

        # Check candidates with respect to the ground truth
        command = [
            "bash",
            "run_subject.sh",
            method_name,
            invs_file
        ]
        # Run command, get the output console and look for the following four variables:
        # valid: 13
        # invalid: 0
        # implied ground truth: 3
        # not implied ground truth: 0
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        lines = output.splitlines()
        valid = int([line for line in lines if line.startswith("valid:")][0].split(":")[1].strip())
        invalid = int([line for line in lines if line.startswith("invalid:")][0].split(":")[1].strip())
        implied = int([line for line in lines if line.startswith("implied ground truth:")][0].split(":")[1].strip())
        not_implied = int(
            [line for line in lines if line.startswith("not implied ground truth:")][0].split(":")[1].strip())

        # Calculate metrics
        total = valid + invalid
        total_gt = implied + not_implied

        # Calculate precision (valid / total), handle division by zero
        precision = valid / total if total > 0 else 0.0
        precision *= 100

        # Calculate recall (implied / total_gt), handle division by zero
        recall = implied / total_gt if total_gt > 0 else 0.0
        recall *= 100

        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        print(f"valid: {valid}")
        print(f"invalid: {invalid}")
        print(f"implied ground truth: {implied}")
        print(f"not implied ground truth: {not_implied}")
        print(f"total: {total}")
        print(f"precision: {precision:.2f}")
        print(f"recall: {recall:.2f}")
        print(f"F1 score: {f1_score:.2f}")
        print()

        # Add row to CSV data
        csv_data.append({
            "subject": folder,
            "method": method_name,
            "total": total,
            "valid": valid,
            "invalid": invalid,
            "precision": f"{precision:.2f}",
            "total_gt": total_gt,
            "gt_implied": implied,
            "gt_not_implied": not_implied,
            "recall": f"{recall:.2f}",
            "f1_score": f"{f1_score:.2f}"
        })

# If single subject, just print the CSV content without writing to file
if single_subject:
    print("CSV Output:")
    writer = csv.DictWriter(sys.stdout, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(csv_data)
    sys.exit(0)

# Write CSV file
output_csv = f"specfuzzer-results-{invs_type}.csv"
with open(output_csv, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
    writer.writeheader()
    writer.writerows(csv_data)

print(f"Results written to {output_csv}")