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
from sqlalchemy.exc import OperationalError

from rpe.layout import layout_to_dict


def db_url(name):
    return create_engine('sqlite:///data/db/{}.db'.format(name))


data_eng = db_url('data')
pii_eng = db_url('pii')
link_eng = db_url('link')

metadata = MetaData(data_eng)
pii_metadata = MetaData(pii_eng)
link_metadata = MetaData(link_eng)


def load_link_table(name, path):
    """
    Load link tables
    """
    table = Table(
        name, link_metadata,
        Column('RECORD_ID', Integer, primary_key=True),
        Column('PII_ID', Integer)
    )
    try:
        table.drop(link_eng)
    except OperationalError:
        pass
    table.create(link_eng)

    if table is None:
        return True
    rows = []
    with open(path) as inf:
        for row in csv.DictReader(inf, delimiter="|"):
            rows.append(row)
    link_eng.execute(table.insert(), rows)
    return True


def make_table(name, layout):
    """
    Create sqlalchemy table metadata from
    a layout file.
    """

    ld = layout_to_dict(layout)

    data_table = Table(
        name, metadata,
        Column('RECORD_ID', Integer, primary_key=True)
    )

    for k, v in ld.items():
        if v['DATA'] != '1':
            continue
        cname = v['NAME']
        ctype = v['TYPE']
        if ctype == 'DATE':
            c = Column(cname, DateTime)
        elif ctype == 'NUMBER':
            c = Column(cname, Float)
        else:
            c = Column(cname, String(255))
        data_table.append_column(c)

    vsc = Column('VALID_SSN', Integer)
    data_table.append_column(vsc)

    data_table.append_column(
        Column('IMPORT_DT', DateTime, default=datetime.datetime.utcnow)
    )

    has_pii = False

    pii_table = Table(
        name, pii_metadata,
        Column('PII_ID', Integer, primary_key=True)
    )

    for k, v in ld.items():
        if v['PII'] == '0':
            continue
        has_pii = True
        cname = v['PII']
        ctype = v['TYPE']
        if ctype == 'DATE':
            c = Column(cname, DateTime)
        elif ctype == 'NUMBER':
            c = Column(cname, Float)
        else:
            c = Column(cname, String(255))
        pii_table.append_column(c)

    pii_table.append_column(
        Column('IMPORT_DT', DateTime, default=datetime.datetime.utcnow)
    )
    if has_pii is False:
        pii_table = None

    return data_table, pii_table


def load(processed_path, table, named_eng):
    """
    Load the raw file into the database
    using sqla's bulk insert.
    """
    if table is None:
        return True
    rows = []
    with open(processed_path) as inf:
        for row in csv.DictReader(inf, delimiter="|"):
            # Clumsily look for dates.
            for k, v in row.items():
                try:
                    dv = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
                    row[k] = dv
                except ValueError:
                    pass
            rows.append(row)
    named_eng.execute(table.insert(), rows)


def load_dataset(name, layout, data_file, link_file, pii_file):
    d_table, p_table = make_table(name, layout)

    active_tables = data_eng.table_names()
    if d_table.name in active_tables:
        d_table.drop(data_eng)
    d_table.create(data_eng)

    load(data_file, d_table, data_eng)

    # If PII exists, create those tables.
    if p_table is not None:
        pii_active_tables = pii_eng.table_names()
        if p_table.name in pii_active_tables:
            p_table.drop(pii_eng)
        p_table.create(pii_eng)

        load(pii_file, p_table, pii_eng)
        load_link_table(name, link_file)


def main():
    pass


if __name__ == '__main__':
    main()
