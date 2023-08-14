import json
import csv

# Config
reference_file = 'validation_format_reference.json'

from validation_functions import (validate_float, validate_quantile, validate_year, validate_week,
                                  validate_location, validate_horizon, validate_quantile_label)

with open(reference_file, "r") as file:
    format_mapping = json.load(file)

# Main funct
def validate_csv_files(file_format, csv_file):

    assert file_format in format_mapping, f"Unknown file format: {file_format} not found in mapping."

    file_fields = format_mapping[file_format]['fields']
    validation_funcs = format_mapping[file_format]['functions']

    with open(csv_file, "r") as in_file:

        reader = csv.reader(in_file)

        for rec in reader:

            if reader.line_num == 1:
                assert rec == file_fields
                continue

            is_valid = True
            for ck in zip(validation_funcs, rec, file_fields):
                is_valid = is_valid and eval(ck[0])(ck[1])

                if not is_valid:
                    raise Exception(f"Invalid record in line {reader.line_num} of file {csv_file}\n"
                        f"Value {ck[1]} not acceptable for field {ck[2]}.")

    return 'OK'
