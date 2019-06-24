import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

credit = pd.read_csv("build/research/Example_V1/credit_scores.txt", sep="|", index_col="sirad_id")
del credit["record_id"]

tax = pd.read_csv("build/research/Example_V1/tax.txt", sep="|", index_col="sirad_id")
del tax["record_id"]

df = credit.join(tax, how="inner")

print(df.head())

sns.set_style("whitegrid")
sns.regplot("agi", "credit_score", data=df, truncate=True)
plt.tight_layout()
plt.savefig("scatterplot.png")

