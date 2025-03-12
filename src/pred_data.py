import pandas as pd
import itertools





s_df = pd.read_csv("./data/SampleSubmissionStage1.csv")  # Load mens dataframe
print(s_df.head())

s_df[['Season', 'Team1', 'Team2']] = s_df['ID'].str.split('_', expand=True)

# Convert to integers for easier comparison
s_df[['Season', 'Team1', 'Team2']] = s_df[['Season', 'Team1', 'Team2']].astype(int)

s_df.drop(columns=["Pred"], inplace=True)

s_df = s_df[s_df['Season'] == 2021]
print(s_df)

# Get all unique teams for the season
num = pd.concat([s_df['Team1'], s_df['Team2']]).nunique()
print(num)


# New plan: Use the SampleSubmissionStage1 to get the team matches
# Note: get IDs for men and women


m_df = pd.read_csv("./data/m_final_raw.csv")  # Load mens dataframe
w_df = pd.read_csv("./data/w_final_raw.csv") 


m_df = m_df[m_df['Season']==2021]
w_df = w_df[w_df['Season']==2021]
all_games = pd.concat([m_df, w_df], ignore_index=True)

print(all_games)

