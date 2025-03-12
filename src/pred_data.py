import pandas as pd
import itertools


m_df = pd.read_csv("./data/m_final_raw.csv")  # Load mens dataframe
w_df = pd.read_csv("./data/w_final_raw.csv")


s_df = pd.read_csv("./data/SampleSubmissionStage1.csv")  # Load mens dataframe
print(s_df.head())

s_df[['Season', 'Team1', 'Team2']] = s_df['ID'].str.split('_', expand=True)

# Convert to integers for easier comparison
s_df[['Season', 'Team1', 'Team2']] = s_df[['Season', 'Team1', 'Team2']].astype(int)

s_df = s_df[s_df['Season'] == 2021]
print(s_df)

# Get all unique teams for the season
teams = pd.concat([s_df['Team1'], s_df['Team2']]).nunique()
print(teams)

# New plan: Use the SampleSubmissionStage1 to get the team matches
# Note: get IDs for men and women
