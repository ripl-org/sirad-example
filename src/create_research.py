"""
Create a research release.
"""
import sys

from sqlalchemy import create_engine

from src.db import data_eng, pii_eng, link_eng


def get_db_engine(version):
    return create_engine('sqlite:///build/research_v{}.db'.format(version))


def link_dbs(eng):
    """
    Connect data and pii using link.

    In actual workflow this would require some form of authentication.
    """
    conn = eng.raw_connection()
    c = conn.cursor()
    c.execute("attach database '{}' AS data".format(data_eng.engine.url.database))
    c.execute("attach database '{}' AS pii".format(pii_eng.engine.url.database))
    c.execute("attach database '{}' AS link".format(link_eng.engine.url.database))

    conn.commit()
    return conn


def build_research(version):
    research_eng = get_db_engine(version)
    conn = link_dbs(research_eng)
    data_tables = data_eng.table_names()
    pii_tables = pii_eng.table_names()
    has_pii = set(data_tables).intersection(set(pii_tables))
    for tbl in data_tables:
        if tbl not in has_pii:
            stmt = """
            create table {table} as
            select * from {table}
            """.format(table=tbl)
        else:
            stmt = """
            create table {table} as
            select r.RPE_ID, d.*
            from
              pii.rpe_id r
              join pii.{table} p on r.pii_id=p.pii_id and r.dsn="{table}"
              join link.{table} l on l.pii_id=p.pii_id
              join data.{table} d on d.record_id=l.record_id
            """.format(table=tbl)
        print(stmt, file=sys.stderr)

        conn.execute(stmt)


def main():
    build_research("v1")


if __name__ == '__main__':
    main()
