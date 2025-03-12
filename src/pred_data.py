import pandas as pd

df = pd.read_csv("./data/m_final_raw.csv")  # Load mens dataframe
print(df)

df = df[(2025 > df['Season']) & (df['Season']>=2021)] # get data from season 2021 onwards

print(df)

print(df['Team1'].nunique())
print(df['Team2'].nunique())



# For now use 2021
df = df[df['Season'] == 2021]
print(df)

