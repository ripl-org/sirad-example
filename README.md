# Worked example of Secure Infrastructure for Research with Administrative Data (SIRAD)

`sirad` is an integration framework for data from administrative systems. It
deidentifies administrative data by removing and replacing personally
identifiable information (PII) with a global anonymized identifier, allowing
researchers to securely join data on an individual from multiple tables without
knowing the individual's identity.

This is a simplified demonstration of how `sirad` works on simulated data; for
more details on how it is used in practice with real administrative data,
please see our article in *Communications of the ACM*:

> J.S. Hastings, M. Howison, T. Lawless, J. Ucles, P. White. (2019).
> Unlocking Data to Improve Public Policy. *Communications of the ACM* **62**(10): 48-53.
> doi:[10.1145/3335150](https://doi.org/10.1145/3335150)

More detail on the development and features of `sirad` and additional applications
are described in our article in *Software Impacts*:

> M. Howison, M. Goggins. (2022).
> SIRAD: Secure Infrastructure for Research with Administrative Data. *Software Impacts* **12**: 100245.
> doi:[10.1016/j.simpa.2022.100245](https://doi.org/10.1016/j.simpa.2022.100245)

## Worked example

In this worked example, we simulate two administrative data sets:

**1. IRS 1040 tax returns**, identified by social security number (SSN), first/last
   name, and date of birth (DOB)  
**2. Credit history**, identified by first/last name and date of birth (DOB)

`sirad` uses a deterministic matching algorithm to match records across the two
data sets corresponding to the same individual. It then assigns an anonymized
identifier (the `sirad_id`) to each matched individual, and creates a
deidentified table for each data set where the SSNs, names, and DOBs have been
replaced with the `sirad_id`. Finally, we demonstrate an analysis that uses the
`sirad_id` to join adjusted gross income from the tax returns table to credit
scores in the credit history table.

**Note**: the data are simulated by the `simulate.py` script using
[Faker](https://github.com/joke2k/faker), which creates realistic PII that does
not represent actual individuals. Any data in this example that look
personally identifiable are not!

## Installing dependencies

Requires Python 3.7 or later.  There are several options for installing the
dependencies (list in `requirements.txt`).

You can use **pip** to install them globally with  
`pip install -r requirements.txt`.

If you do not have write access to install globally, you can install into your
home directory with  
`pip install --user -r requirements.txt`.

## Running the example

### Step 1: Simulate data

Command: `python simulate.py`

This script uses the [Faker](https://github.com/joke2k/faker) package to
simulate raw data files, which are written to the `raw` directory. **Note**:
although the simulated files contain realistic PII, they do not represent
actual individuals.

### Step 2: Process the raw data into separate PII, data, and link files

Command: `sirad process`

`sirad` processes a set of **raw** data files specified by a set of **layout
files**. In this example, there are two simulated raw data files generated in
Step 1: tax records (`raw/tax.txt`) and credit history
(`raw/credit_scores.txt`). Their layouts are `layouts/tax.yaml` and
`layouts/credit_scores.yaml`. The layouts are YAML files that describe the
column layout and field types in the raw data files.

The processing step uses the `pii` properties in the layout to split the PII
fields from the data fields in each row of the raw files. It randomly shuffles
the order of the PII rows when writing to the PII file. The data file has the
same row order as the raw data file.  The link file provides a lookup table
that re-links the shuffled PII rows to the data rows.

The results are organized in the following directory structure:
* `build/data/Example_V1`: processed data files
* `build/pii/Example_V1`: processed PII files
* `build/link/Example_V1`: processed link files

### Step 3: Create a versioned research database

Command: `sirad research`

This step uses the PII files to construct a global anonymized identifier (the
`sirad_id`), then uses the link files to attach it to each data file.  The
result is a set of **research** files which contain no PII, but in which
individual-level data in different files can be joined by the anonymized
identifier. Research files are versioned to support reproducible analysis,
using the current version set in `sirad_config.py`. You will find two research
files in the `build/research/Example_V1` directory:

#### tax.txt

sirad_id | record_id | job | file_date | adjusted_gross_income | import_dt
-|-|-|-|-|-

#### credit_scores.txt

sirad_id | record_id | credit_score | import_dt
-|-|-|-

Notes:
* `sirad_id` is an anonymized identifier created from the PII.
* `record_id` is a primary key for the research/data records (which can be linked via the link files to the shuffled `pii_id` primary key in the PII files).
* `import_dt` is a timestamp for when the raw data were processed.
* All PII fields (SSN, first/last, DOB) have been removed from the research files.

In a real-world application, only the `build/research/Example_V1` directory
would be accessible to researchers.  The data, PII, and link directories from
the processing step above should be stored in a restricted location that is
inaccessible to any individual researcher, for example by using encryption with
a multi-party key or passphrase, auditing, real-time alerting, and/or other
appropriate security controls that ensure an individual researcher cannot
access build files that contain PII.

### Step 4: Example analysis

Command: `python scatterplot.py`

This step demonstrates an analysis that uses the `sirad_id` to
anonymously join records about individuals. It selects adjusted gross income
from the `tax` table joined to the corresponding credit score from the
`credit_scores` table, then generates this scatter plot (`scatterplot.png`):

![scatterplot](scatterplot.png)

**Note:** these variables are correlated by construction, and were drawn from a
joint distribution (with added noise) in the simulation.
