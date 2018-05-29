"""
Build steps.
"""
import os

import make_data as md
from db import load_dataset

from rpe_config import OUTPUT_PATH


def make_target_list(name):
    out = []
    for e in ['data', 'link', 'pii']:
        t = os.path.join(OUTPUT_PATH, e, name + ".txt")
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
    print(piif,)
    done = load_dataset(name,
        layout,
        dataf,
        linkf,
        piif
    )
    return done


def make_data(target, source, env):
    md.main(target[0].path, target[1].path)
