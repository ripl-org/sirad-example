"""
Build steps.
"""
import os

from src import make_data as md
from src.db import load_dataset
from src import make_id as mid
from src.create_research import build_research

from rpe import config


def make_target_list(name):
    output_path = config.get_option('OUTPUT_PATH')
    out = []
    for e in ['data', 'link', 'pii']:
        t = os.path.join(output_path, e, name + ".txt")
        out.append(t)
    return out


def make_db(target, source, env):
    layout = env['LAYOUT']
    name = env['NAME']
    dataf, linkf, piif = (
        source[0].path,
        source[1].path,
        source[2].path
    )
    done = load_dataset(
        name,
        layout,
        dataf,
        linkf,
        piif
    )
    return None


def make_data(target, source, env):
    md.main(target[0].path, target[1].path)


def build_research_version(target, source, env):
    v = env['VERSION']
    mid.create()
    build_research(v)


def get_research_db_path(version):
    from src import create_research
    return create_research.get_db_engine(version).url.database
