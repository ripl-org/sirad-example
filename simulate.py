"""
Simulate data for IRS 1040 tax returns and credit history.
"""

from faker import Faker
import csv
import math
import numpy as np
from pathlib import Path
import random
import os
from datetime import date

from sirad import config

N = 1000
SEED = 1010

fake = Faker()
fake.seed(SEED)
random.seed(SEED)
np.random.seed(SEED)

out = []

def get_birth_date():
    """
    Faker on Windows is not generating dates prior to 1970.
    Work around this for now.
    See: https://stackoverflow.com/a/35709408/758157
    Start year: 1950
    End year: 1999
    """
    return date(
        random.randint(1949, 1999),
        random.randint(1, 12),
        random.randint(1, 28)
    )

def simulate_addresses():
    streets = [(fake.city(), fake.city(), fake.zipcode()) for _ in range(N)]
    with open(config.get_option("CENSUS_STREET_FILE"), "w") as f:
        print("street,zip,blkgrp", file=f)
        for street in streets:
            if random.random() > 0.3:
                print(street[0].upper(), street[2], random.randint(1, 10), sep=",", file=f)
    with open(config.get_option("CENSUS_STREET_NUM_FILE"), "w") as f:
        print("street_num,street,zip,blkgrp", file=f)
        for street in streets:
            if random.random() > 0.3:
                for _ in range(random.randint(1, 20)):
                    print(fake.building_number(), street[0].upper(), street[2], random.randint(1, 10), sep=",", file=f)
    return streets

def simulate_tax(number, streets):
    perc_bad_ssn = 0.05
    for n in range(0, number):
        d = {}
        if n % 2 == 0:
            d['first'] = fake.first_name_female()
        else:
            d['first'] = fake.first_name_male()
        d['last'] = fake.last_name()
        d['ssn'] = fake.ssn()
        if (random.random() <= perc_bad_ssn):
            d['ssn'] = '000-' + d['ssn'][4:]
        d['job'] = fake.job()
        bd = get_birth_date()
        d['birth_date'] = bd.strftime("%m-%d-%Y")
        d['file_date'] = fake.date_this_year().strftime("%m/%d/%Y")
        d['agi'] = int(20000 * np.random.lognormal())
        street = streets[random.randint(0, N-1)]
        d['street_num'] = fake.building_number()
        d['street_name'] = street[0]
        d['city'] = street[1]
        d['zipfull'] = street[2] + "-{:04d}".format(random.randint(0, 9999))
        street = streets[random.randint(0, N-1)]
        d['w2_empl_address'] = fake.building_number() + ' ' + street[0]
        d['w2_empl_city'] = street[1]
        d['w2_empl_zip'] = street[2]
        out.append(d)

    return out

def simulate_credit_scores(path, streets):
    """
    Create fake credit scores for subset of main person list.

    For some perc of people replace full first name with first initial
    """
    perc_included = .60
    perc_first_intial = .10
    perc_drop_last = .005
    perc_drop_birth = .01
    out = []
    with open(path) as f:
        reader = csv.DictReader(f, delimiter="|")
        for row in reader:
            d = {}
            if random.random() <= perc_included:
                for fld in ['first', 'last', 'birth_date']:
                    if (fld == 'first') and (random.random() <= perc_first_intial):
                        d[fld] = row[fld][0]
                    elif (fld == 'last') and (random.random() <= perc_drop_last):
                        d[fld] = ""
                    elif (fld == 'birth_date') and (random.random() <= perc_drop_birth):
                        d[fld] = ""
                    else:
                        d[fld] = row[fld]
                street = streets[random.randint(0, N-1)]
                d['street_address'] = fake.building_number() + ' ' + street[0]
                d['city'] = street[1]
                d['zipcode'] = street[2]
                # Simulate credit score as joint distribution with AGI with a normal error term
                cscore = 300 + 225 * (math.log(float(row['agi']) / 20000.0) + 0.5 * np.random.normal())
                # Clamp score
                cscore = np.clip(cscore, 300, 850)
                d['credit_score'] = int(cscore)
                d['credit_date'] = fake.date_this_year().strftime("%m/%d/%Y")
                out.append(d)
    return out

def write_file(records, path, separator="|"):
    fieldnames = records[0].keys()
    with open(path, "w") as outf:
        writer = csv.DictWriter(
            outf,
            lineterminator='\n',
            delimiter=separator,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(records)
    return path


def main(tax_path, cscore_path):
    streets = simulate_addresses()
    tax = simulate_tax(N, streets)
    people = write_file(tax, tax_path)
    cscores = simulate_credit_scores(people, streets)
    write_file(cscores, cscore_path)


if __name__ == '__main__':
    outdir = config.get_option("RAW_DIR")
    Path(outdir).mkdir(parents=True, exist_ok=True)
    tax_path = os.path.join(outdir, 'tax.txt')
    cscore_path = os.path.join(outdir, 'credit_scores.txt')
    main(tax_path, cscore_path)
