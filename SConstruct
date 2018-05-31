

import os

from SCons.Script import (
    Builder,
    Command,
    Environment,
    Depends
)

from builder import (
    make_data,
    make_target_list,
    make_db,
    get_research_db_path,
    build_research_version
)


RESEARCH_VERSION = "1"

tax_raw_file = os.path.join("data", "raw", "tax.txt")

credit_scores_raw_file = os.path.join("data", "raw", "credit_scores.txt")

process = Builder(action="rpe --layout=$LAYOUT --file=$SOURCE")
env = Environment(BUILDERS={'Process': process}, ENV=os.environ)


datasets = [
    ('tax', 'layouts/tax_layout.tsv', tax_raw_file),
    ('credit_scores', 'layouts/credit_score_layout.tsv', credit_scores_raw_file)
]

# Build the sample data
fake = Command(
    [tax_raw_file, credit_scores_raw_file],
    '',
    make_data
)


def process_datasets():
    done = []
    for name, layout, raw_file in datasets:

        processed_files = make_target_list(name)

        # Run rpe
        proc = env.Process(
            source=raw_file,
            target=processed_files,
            LAYOUT=layout
        )
        done.append(Depends(proc, fake))

        # Load
        load = env.Command(
            None,
            processed_files,
            make_db,
            LAYOUT=layout,
            NAME=name
        )
        done.append(Depends(load, proc))
    return done


datasets = process_datasets()

research_db_path = get_research_db_path(RESEARCH_VERSION)

version = env.Command(
        [research_db_path],
        None,
        build_research_version,
        VERSION=RESEARCH_VERSION
)

Depends(version, datasets)
