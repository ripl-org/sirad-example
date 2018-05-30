"""
Generate fake data to represent values stored in a database.
"""


from faker import Faker
import csv
import random
from datetime import date

N = 1000
SEED = 1010

fake = Faker()
fake.seed(SEED)

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


def get_agi(n):
    rn = random.random()
    if rn <= .25:
        return random.randrange(0, 20000)
    elif rn <= .90:
        return random.randrange(20000, 150000)
    else:
        return random.randrange(150000, 900000)
    return


def tax_info(number):
    for n in range(0, number):
        d = {}
        if n % 2 == 0:
            d['first'] = fake.first_name_female()
        else:
            d['first'] = fake.first_name_male()
        d['last'] = fake.last_name()
        d['ssn'] = fake.ssn()
        d['job'] = fake.job()
        bd = get_birth_date()
        d['birth_date'] = bd.strftime("%m-%d-%Y")
        d['file_date'] = fake.date_this_year()\
            .strftime("%m/%d/%Y")
        d['agi'] = get_agi(n)
        out.append(d)

    return out


def derive_cscore_file(path):
    """
    Create fake credit scores for subset of main person list.

    For some perc of people replace full first name with first initial
    """
    perc_included = .60
    perc_first_intial = .10
    out = []
    with open(path) as inf:
        reader = csv.DictReader(inf, delimiter="|")
        for row in reader:
            d = {}
            if random.random() <= perc_included:
                for fld in [
                    'first',
                    'last',
                    'birth_date'
                ]:
                    if (fld == 'first') and\
                        (random.random() <= perc_first_intial):
                        d[fld] = row[fld][0]
                    else:
                        d[fld] = row[fld]
                d['credit_score'] = random.randrange(300, 850)
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
    hr = tax_info(N)
    people = write_file(hr, tax_path)
    cscores = derive_cscore_file(people)
    write_file(cscores, cscore_path)


if __name__ == '__main__':
    tax_path = '/data/raw/tax.txt'
    cscore_path = '/data/raw/credit_scores.txt'
    main(tax_path, cscore_path)
