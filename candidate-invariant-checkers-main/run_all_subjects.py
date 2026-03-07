import os
import subprocess

curr_dir = os.getcwd()

subjects_file = "subjects_list.txt"

with open(subjects_file) as f:
    for line in f.readlines():
        subject = line.strip()
        print(f"Running {subject}")
        command = [
            "bash",
            "run_subject.sh",
            subject,
            f"{curr_dir}/{subject}/candidate_invs.txt"
        ]
        # with open(log_file, "a") as log:
        #subprocess.run(command, stdout=log, stderr=log, check=True)
        subprocess.run(command, check=True)
