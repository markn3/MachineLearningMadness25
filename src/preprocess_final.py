import pandas as pd
from sklearn.preprocessing import StandardScaler
pd.set_option('display.max_columns', None)

men_df = pd.read_csv("./data/men_dataset.csv")
women_df = pd.read_csv("./data/women_dataset.csv")

df = pd.concat([men_df, women_df], ignore_index=True)

# One hot encode categorical features
# We'll one-hot encode 'Gender' and 'HomeCourt'
df = pd.get_dummies(df, columns=['HomeCourt'], drop_first=True)

# Normalize DayNum within each season so that its scaled from 0 to 1:
df['Normalized_DayNum'] = df.groupby('Season')['DayNum'].transform(lambda x: x / x.max())
df = df.drop(columns=['DayNum'])

#standardize other numeric columns with StandardScaler:
numeric_cols = [
    'Normalized_DayNum', 'T1_Seed', 'T2_Seed',
    'T1_roll_Off', 'T1_roll_Def', 'T1_roll_Wins', 'T1_roll_Losses',
    'T2_roll_Off', 'T2_roll_Def', 'T2_roll_Wins', 'T2_roll_Losses', 'net_diff'
]

scaler = StandardScaler()
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

print(df)

df.to_csv("./data/final_df.csv", index=False)



