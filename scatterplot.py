import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

credit = pd.read_csv("build/research/Example_V1/credit_scores.txt",
                     sep="|",
                     usecols=["sirad_id", "credit_score"],
                     index_col="sirad_id")

tax = pd.read_csv("build/research/Example_V1/tax.txt",
                  sep="|",
                  usecols=["sirad_id", "agi"],
                  index_col="sirad_id")

df = credit.join(tax, how="inner")

print(df.head())

sns.set_style("whitegrid")
sns.regplot("agi", "credit_score", data=df, truncate=True)
plt.tight_layout()
plt.savefig("scatterplot.png")

