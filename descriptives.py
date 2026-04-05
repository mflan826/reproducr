import pandas as pd
from database import engine

df = pd.read_sql_table(
    "article_detailed",
    con=engine,
    schema="daan_822"
)

df = df.astype({
    "reference_count": "Int64",
    "table_count": "Int64",
    "figure_count": "Int64",
})

print("Reference Count")
print(df['reference_count'].describe())
print("Fig Count")
print(df['figure_count'].describe())
print("Table Count")
print(df['table_count'].describe())

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

counts, edges, bars = plt.hist(
    df['figure_count'].dropna(),
    bins=30,
    edgecolor='black'
)

# Normalize counts to [0, 1] for colormap
norm = mcolors.Normalize(vmin=counts.min(), vmax=counts.max())
cmap = cm.viridis  # or 'plasma', 'Blues', 'YlOrRd', etc.

for bar, count in zip(bars, counts):
    bar.set_facecolor(cmap(norm(count)))

plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=plt.gca(),label='Frequency')
plt.xlabel('Figure Count')
plt.title('Distribution of Figure Count')
plt.tight_layout()
plt.savefig('fig_count_hist.png')
plt.show()


