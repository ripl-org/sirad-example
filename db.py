"""
Create a sample database from our rpe processed files.
"""
import csv
import datetime

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import Integer, Float, String, DateTime

from rpe.layout import layout_to_dict

eng = create_engine('sqlite:///data/data.db')

metadata = MetaData(eng)

def make_table(name, layout, ttype='data'):

    ld = layout_to_dict(layout)
    table = Table(
        name, metadata,
        Column('RECORD_ID', Integer, primary_key=True)
    )

    for k, v in ld.items():
        if v['DATA'] != '1':
            continue
        cname = v['NAME']
        ctype = v['TYPE']
        if ctype == 'DATE':
            c = Column(cname, String)
        elif ctype == 'NUMBER':
            c = Column(cname, Float)
        else:
            c = Column(cname, String(255))
        table.append_column(c)

    vsc = Column('VALID_SSN', Integer)
    table.append_column(vsc)

    table.append_column(
        Column('IMPORT_DT', DateTime, default=datetime.datetime.utcnow)
    )

    return table

def load(processed_path, table):
    rows = []
    with open(processed_path) as inf:
        for row in csv.DictReader(inf, delimiter="|"):
            rows.append(row)
    eng.execute(table.insert(), rows)


tax_t = make_table('tax', 'layouts/tax_layout.tsv')
credit_t = make_table('credit_scores', 'layouts/credit_score_layout.tsv')

tax_t.drop(eng)
credit_t.drop(eng)

metadata.create_all()

for _t in metadata.tables:
    print("Table:", _t)


load('data/processed/data/tax.txt', tax_t)
load('data/processed/data/credit_scores.txt', credit_t)
