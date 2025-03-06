import pandas as pd
from sklearn.preprocessing import StandardScaler
pd.set_option('display.max_columns', None)

men_df = pd.read_csv("./data/men_dataset.csv")
women_df = pd.read_csv("./data/women_dataset.csv")

df = pd.concat([men_df, women_df], ignore_index=True)

# Seperate Target from features
target = df['Target']

# We will drop columns that are identifiers if not needed as features
# For example, Team1 and Team2 are matchup identifiers that might be used only for submission
# However, if you already computed differential features (like net_diff), you can drop raw team IDs.
features = df.drop(columns=['Target'])
# features = df.drop(columns=['Target', 'Team1', 'Team2']) 


# One hot encode categorical features
# We'll one-hot encode 'Gender' and 'HomeCourt'
features = pd.get_dummies(features, columns=['HomeCourt'], drop_first=True)

# Normalize DayNum within each season so that its scaled from 0 to 1:
features['Normalized_DayNum'] = features.groupby('Season')['DayNum'].transform(lambda x: x / x.max())
features = df.drop(columns=['DayNum'])

print(features)



