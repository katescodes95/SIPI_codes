"""
Project: Port Renaming from Touchstone Files for Use in ACVS
Author: Youngeun Na
Date: 2025-09-30
Version: 1.0
Description:
    - This is a script that renames ports in touchstone files to be compatible with ACVS.
    - Case numbers are assigned to each touchstone file based on their order in the folder.
    - The script outputs a CSV file mapping the touchstone file to its case number.
Dependencies:
    - Python 3.x
"""

import os
import csv

# Folder containing touchstone files
folder_path = r"path/to/touchstone/files" #Edit path

# Get list of touchstone files in the folder
touchstone_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".s40p")])

csv_rows = [] # For writing filename and case number to CSV

for case_number, filename in enumerate(touchstone_files, start = 1):
    case_id = f"C{case_number}"
    file_path = os.path.join(folder_path, filename)
    
    # Read the touchstone file
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    # Rename ports in the touchstone file
    renamed_lines = []
    for line in lines:
        if line.strip().startswith("! Port["):
            # Example: "! Port[1] = S11_T1"
            left, right = line.split("=", 1)  # Split only once
            right = right.strip()
            renamed_line = f"{left}= {case_id}_{right}\n"
            renamed_lines.append(renamed_line)
        else:
            renamed_lines.append(line)  # Keep all other lines untouched
    
    # Overwrite file with updated port mappings
    csv_path = os.path.join(folder_path, "case_mapping.csv")
    with open(file_path, "w") as file:
        file.writelines(renamed_lines)

    # Rename the file name by adding case ID prefix
    new_filename = f"{case_id}_{filename}"
    new_file_path = os.path.join(folder_path, new_filename)
    os.rename(file_path, new_file_path)
    
    # Append to CSV rows
    touchstone_name = os.path.splitext(filename)[0]
    csv_rows.append([case_id, touchstone_name])

    # Write CSV file
    csv_path = os.path.join(folder_path, "case_mapping.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Case", "Touchstone File"])
        writer.writerows(csv_rows)

print(f"Processed {len(touchstone_files)} files. Case mapping written to {csv_path}.")

