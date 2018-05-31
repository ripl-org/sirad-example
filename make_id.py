import sys

import jellyfish

from db import pii_eng


def soundex(raw):
    """
    Soundex function for sqlite.
    """
    return jellyfish.soundex(raw)


def create_view(name, q):
    pii_eng.execute("DROP VIEW IF EXISTS " + name)
    q = "CREATE VIEW {} as\n".format(name) + q
    print(q, file=sys.stderr)
    pii_eng.execute(q)
    return True


def create():
    conn = pii_eng.raw_connection()
    conn.create_function("soundex", 1, soundex)

    q = """
    select *
    from (
        select 'tax' as dsn, pii_id, ssn, soundex(first_name) as first_sdx, first_name, last_name, dob
        from tax

        union

        select 'credit_scores' as dsn, pii_id, null as ssn, soundex(first_name) as first_sdx, first_name, last_name, dob
        from credit_scores
    )
    order by ssn, last_name, dob
    """
    create_view("rpe_id_pii", q)

    # Add SSNs to rows that don't have it matching on dob, last, first sdx
    q = """
    select MAX(s.SSN) AS SSN, p.DSN, p.PII_ID
    from rpe_id_pii p
    join rpe_id_pii s
        on p.last_name=s.last_name
        and p.first_sdx=s.first_sdx
        and p.dob=s.dob
    group by p.dsn, p.pii_id
    having count(distinct s.ssn) = 1
    """

    create_view("rpe_id_ssn_match", q)

    q = """
    select p.dsn, p.pii_id,
        case
            when s.ssn is null and (dob is null or last_name is null or first_sdx) then 0
            when s.ssn is not null then 'S_' || s.ssn
            else 'NDOB_' || dob || last_name || first_sdx
        end as key
    from rpe_id_pii p
    left join rpe_id_ssn_match s
        on p.dsn=s.dsn and p.pii_id=s.pii_id
    """

    create_view("rpe_id_keyed", q)

    q = """
    select
        (
        select count() + 1
        from (select distinct key from rpe_id_keyed as rk where rk.key < r.key)
        ) as rpe_id,
        p.dsn, p.pii_id, p.ssn, p.last_name, p.first_name, p.dob
    from rpe_id_keyed r
    join rpe_id_pii p on r.dsn=p.dsn and r.pii_id=p.pii_id
    order by key
    """

    pii_eng.execute("drop table if exists rpe_id")
    stmt = "create table rpe_id as\n" + q
    print(stmt, file=sys.stderr)

    pii_eng.execute(stmt)


def main():
    create()


if __name__ == '__main__':
    main()
