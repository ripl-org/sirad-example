import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sqlite3

sql = """
      SELECT t.sirad_id,
             adjusted_gross_income,
             credit_score
        FROM tax t
  INNER JOIN credit_scores cs
          ON t.sirad_id=cs.sirad_id
      """

with sqlite3.connect("build/research_v1.db") as cxn:
    df = pd.read_sql(sql, cxn, index_col="sirad_id")

print(df.head())

sns.set_style("whitegrid")
sns.regplot("adjusted_gross_income", "credit_score", data=df, truncate=True)
plt.tight_layout()
plt.savefig("scatterplot.png")

