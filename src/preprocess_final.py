import pandas as pd
pd.set_option('display.max_columns', None)

from sklearn.preprocessing import StandardScaler

men_df = pd.read_csv("./data/men_dataset.csv")
women_df = pd.read_csv("./data/women_dataset.csv")


# men_df['Gender'] = 'M'
# women_df['Gender'] = 'W'

df = pd.concat([men_df, women_df], ignore_index=True)

# Seperate Target from features
target = df['target']

# We will drop columns that are identifiers if not needed as features
# For example, Team1 and Team2 are matchup identifiers that might be used only for submission
# However, if you already computed differential features (like net_diff), you can drop raw team IDs.
features = df.drop(columns=['Target', 'Team1', 'Team2'])



print(df)

# One hot encode categorical features

ohe_df = pd.get_dummies(df, columns=['HomeCourt'])
print(ohe_df)