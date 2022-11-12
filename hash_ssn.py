"""
Worked example of validating SSNs and replacing with a salted SHA-1 hash value.
"""

import argparse
import hashlib
import pandas as pd
import sys

def validate_ssn(digits):
    """
    Remove dashes from the SSN and check if it is invalid using SSA rules.
    See: https://www.ssa.gov/employer/stateweb.htm
    """
    digits = str(digits).replace("-", "")
    # Wrong length
    if len(digits) != 9:
        return 1
    # Any component is all 0
    elif digits[:3] == "000" or digits[3:5] == "00" or digits[5:9] == "0000":
        return 1
    # Area 666
    elif digits[:3] == "666":
        return 1
    # Areas 900-999
    elif digits.startswith("9"):
        return 1
    # Used in an ad by the Social Security Administration
    elif digits == "219099999":
        return 1
    # Woolworth Wallet Fiasco
    elif digits == "078051120":
        return 1
    return 0

def salted_hash(value, salt):
    """
    Add the salt value to the original value and return a hexidecimal
    representation of the value's SHA-1 hash.
    """
    if salt is None:
        value = str(value).encode("utf-8")
    else:
        value = (str(value) + salt).encode("utf-8")
    return hashlib.sha1(value).hexdigest()

if __name__ == "__main__":
    """
    Process SSNs in an input CSV file by validating them, adding a column with
    an indicator for invalid SSNs, and replacing the original SSN column with
    salted hashes.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", required=True, help="input CSV file")
    parser.add_argument("-d", "--delimiter", default=",", help="delimiter for input file")
    parser.add_argument("-c", "--ssn-column", required=True, help="column name of SSN column in input")
    parser.add_argument("-s", "--salt", required=True, help="salt value")
    parser.add_argument("-o", "--output", required=True, help="output CSV file")
    args = parser.parse_args()

    data = pd.read_csv(args.input, delimiter=args.delimiter)
    if args.ssn_column not in data.columns:
        print(f"ERROR: could not find SSN column '{args.ssn_column}'", file=sys.stderr)
    else:
        data[args.ssn_column + "_invalid"] = data[args.ssn_column].apply(validate_ssn)
        data[args.ssn_column] = data[args.ssn_column].apply(salted_hash, args=(args.salt,))
        data.to_csv(args.output, index=False)
        print(f"wrote output to '{args.output}'", file=sys.stderr)
