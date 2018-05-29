

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
    make_db
)

tax_raw = os.path.join("data", "raw", "tax.txt")
tax_targets = make_target_list("tax")

credit_score_raw = os.path.join("data", "raw", "credit_scores.txt")
credit_targets = make_target_list("credit_scores")

process = Builder(action="rpe --layout=$LAYOUT --file=$SOURCE")
env = Environment(BUILDERS={'Process': process}, ENV=os.environ)


# Build the sample data
fake = Command(
    [tax_raw, credit_score_raw],
    '',
    make_data
)

# Run rpe
tax_proc = env.Process(
    source=tax_raw,
    target=tax_targets,
    LAYOUT="layouts/tax_layout.tsv"
)

credit_proc = env.Process(
    source=credit_score_raw,
    target=credit_targets,
    LAYOUT="layouts/credit_score_layout.tsv"
)

Depends(tax_proc, fake)
Depends(credit_proc, fake)

# Load
tax_load = env.Command(
    None,
    tax_targets,
    make_db,
    LAYOUT="layouts/tax_layout.tsv",
    NAME='tax'
)

credit_load = env.Command(
    None,
    credit_targets,
    make_db,
    LAYOUT="layouts/credit_score_layout.tsv",
    NAME='credit_scores'
)

Depends(tax_load, tax_proc)
Depends(credit_load, credit_proc)
