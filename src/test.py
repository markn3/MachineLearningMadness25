import pandas as pd
pd.set_option('display.max_columns', None)
 

# Teams & Seasons
m_teams = pd.read_csv("./data/MTeams.csv")  # Contains TeamID and TeamName
# df = pd.read_csv("./data/MRegularSeasonDetailedResults.csv")
df = pd.read_csv("./data/MNCAATourneyDetailedResults.csv")


print(df)


# Offensive Rating

df['WPoss'] = df['WFGA'] - df['WOR'] + df['WTO'] + 0.44 * df['WFTA']
df['LPoss'] = df['LFGA'] - df['LOR'] + df['LTO'] + 0.44 * df['LFTA']

df['W_OffRtg'] = (df['WScore'] / df['WPoss']) * 100
df['L_OffRtg'] = (df['LScore'] / df['LPoss']) * 100

print(df)


# Defensive Rating
df['W_DefRtg'] = (df['LScore'] / df['LPoss']) * 100
df['L_DefRtg'] = (df['WScore'] / df['WPoss']) * 100


# Net Rating
df['W_NetRtg'] = df['W_OffRtg'] - df['W_DefRtg']
df['L_NetRtg'] = df['L_OffRtg'] - df['L_DefRtg']

# drop columns

df = df[['Season', 'DayNum', 'WTeamID', 'LTeamID', 'W_OffRtg', 'L_OffRtg', 'W_DefRtg', 'L_DefRtg']]

print(df)

all_games = pd.concat([m_regular_season_results, m_tourney_results], ignore_index=True)
