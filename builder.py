"""
Build steps.
"""
import os

import make_data as md

from rpe_config import OUTPUT_PATH


def make_target_list(name):
    out = []
    for e in ['data', 'link', 'pii']:
        t = os.path.join(OUTPUT_PATH, e, name + ".txt")
        out.append(t)
    return out

def make_data(target, source, env):
    md.main(target[0].path, target[1].path)
