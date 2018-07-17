# Worked example of Secure Infrastructure for Research with Administrative Data (SIRAD)

`sirad` is an integration framework for data from administrative systems. It
deidentifies administrative data by removing and replacing personally
identifiable information (PII) with a global anonymized identifier, allowing
researchers to securely join data on an individual from multiple tables without
knowing the individual's identity.

This is a simplified demonstration of how `sirad` works on simulated data; for
more details on how it is used in practice with real administrative data,
please see our manuscript preprint:

> J.S. Hastings, M. Howison, T. Lawless, J. Ucles, P. White. 2018.
> Integrating Administrative Data for Policy Insights.
> (under review)

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

Requires Python 3.6 or later.  There are several options for installing the
dependencies (list in `requirements.txt`).

You can use **pip** to install them globally with  
`pip install -r requirements.txt`.

If you do not have write access to install globally, you can install into your
home directory with  
`pip install --user -r requirements.txt`.

If you have Anaconda Python, you can use **conda** to install them in your
root environment with  
`conda install -c riipl-org --file requirements.txt`.

Or if you would prefer to create a named conda environment, use  
`conda install -c riipl-org -n sirad-example --file requirements.txt`  
and activate it with  
`source activate sirad-example`.

## Running the example

### Step 1: Simulate data

Command: `python simulate.py`

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

### Step 3: Stage the processed files in a database

Command: `sirad stage`

This step stages the PII, data, and link files in a relational database.

### Step 4: Create a versioned research database

Command: `sirad research --version 1`

This step uses the PII database to construct a global anonymized identifier
(the `sirad_id`), then uses the link files to attach it to each data table in
the database.  The result is a **research** database which contains no PII, but
in which individual-level data in different tables can be joined by the
anonymized identifier. Research databases are versioned to support reproducible
analysis.

## Resulting database

After the build finishes, an sqlite database called `research_v1.db` will be
created in the `build` directory.  This database has two tables created from
the simulated data:

### tax

sirad_id | record_id | job | file_date | adjusted_gross_income | import_dt
-|-|-|-|-|-

### credit_scores

sirad_id | record_id | credit_score | import_dt
-|-|-|-

Notes:
* `sirad_id` is an anonymized identifier created from the PII.
* `record_id` is a primary key for the research/data records, and `pii_id` is a
  shuffled primary key for the PII records.
* `import_dt` is a timestamp for when the raw data were processed.
* All PII fields (SSN, first/last, DOB) have been removed from the research database.

The results are organized in the following directory structure:
* `raw/`: the simulated raw data files
* `build/processed`: processed data files (organized by `data`, `pii`, and `link`)
* `build/db`: the staging databases for the processed files
* `build/research_v1.db`: the final research database

In a real-world application, only the `research_v1.db` database would be
accessible to researchers.  The `raw`, `processed`, and `db` directories should
be stored in a restricted location that is inaccessible to any individual
researcher, for example by using encryption with a multi-party key or
passphrase, auditing, real-time alerting, and/or other appropriate security
controls that ensure an individual researcher cannot access build files that
contain PII.

## Example analysis

`scatterplot.py` demonstrates an analysis that uses the `sirad_id` to
anonymously join records about individuals. It selects adjusted gross income
from the `tax` table joined to the corresponding credit score from the
`credit_scores` table, then generates this scatter plot:

![scatterplot](scatterplot.png)

**Note:** these variables are correlated by construction, and were drawn from a
joint distribution (with added noise) in the simulation.
