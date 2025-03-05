import pandas as pd
pd.set_option('display.max_columns', None)

from sklearn.preprocessing import StandardScaler

men_df = pd.read_csv("./data/men_dataset.csv")
women_df = pd.read_csv("./data/women_dataset.csv")


men_df['Gender'] = 'M'
women_df['Gender'] = 'W'

combined_df = pd.concat([men_df, women_df], ignore_index=True)

print(combined_df)