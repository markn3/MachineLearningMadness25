import pandas as pd
import itertools
pd.set_option('display.max_columns', None)

import pandas as pd
import itertools

# --------------------------
# Step 1: Load data & generate matchups
# --------------------------
# Load raw game details
df_m = pd.read_csv("./data/m_final_raw.csv")
df_m = df_m[(df_m['Season'] < 2025) & (df_m['Season'] >= 2021)]

# Create ordered matchup keys so that order is consistent.
df_m['Team_lower'] = df_m.apply(lambda row: min(row['Team1'], row['Team2']), axis=1)
df_m['Team_higher'] = df_m.apply(lambda row: max(row['Team1'], row['Team2']), axis=1)

# For each matchup, select the game with the maximum DayNum (latest game)
latest_indices = df_m.groupby(['Season', 'Team_lower', 'Team_higher'])['DayNum'].idxmax()
df_m_latest = df_m.loc[latest_indices]

# Generate all possible matchups for the season based on the teams available in the raw data.
teams = pd.concat([df_m['Team1'], df_m['Team2']]).unique()
teams = sorted(teams)
season = 2021

matchup_dicts = [
    {"Season": season,
     "Team_lower": min(t1, t2),
     "Team_higher": max(t1, t2),
     "matchup": f"{season}_{min(t1, t2)}_{max(t1, t2)}"}
    for t1, t2 in itertools.combinations(teams, 2)
]
m_matchups_df = pd.DataFrame(matchup_dicts)

# Merge generated matchups with the latest game details (if available)
m_matchups_full = pd.merge(m_matchups_df, df_m_latest, on=["Season", "Team_lower", "Team_higher"], how="left")

# --------------------------
# Step 2: Build a lookup table for each team’s latest metrics
# --------------------------
# When a team appears as Team1
df_team1 = df_m[['Season', 'DayNum', 'Team1', 'T1_Seed', 'T1_roll_Off', 'T1_roll_Def', 'T1_win_ratio']].rename(
    columns={'Team1': 'Team', 
             'T1_Seed': 'Seed', 
             'T1_roll_Off': 'roll_Off', 
             'T1_roll_Def': 'roll_Def', 
             'T1_win_ratio': 'win_ratio'}
)

# When a team appears as Team2
df_team2 = df_m[['Season', 'DayNum', 'Team2', 'T2_Seed', 'T2_roll_Off', 'T2_roll_Def', 'T2_win_ratio']].rename(
    columns={'Team2': 'Team', 
             'T2_Seed': 'Seed', 
             'T2_roll_Off': 'roll_Off', 
             'T2_roll_Def': 'roll_Def', 
             'T2_win_ratio': 'win_ratio'}
)

# Combine and then get each team’s latest metrics based on the maximum DayNum.
df_team_all = pd.concat([df_team1, df_team2])
latest_team_metrics = (
    df_team_all.sort_values('DayNum')
    .groupby(['Season', 'Team'], as_index=False)
    .last()
)
# latest_team_metrics now has one row per team per season with their latest metrics

# --------------------------
# Step 3: Merge individual team metrics for missing matchups and calculate matchup features
# --------------------------
# For teams with no direct matchup game, we merge in their latest individual metrics.
# Merge for Team_lower metrics:
m_matchups_full = pd.merge(
    m_matchups_full, 
    latest_team_metrics, 
    left_on=['Season', 'Team_lower'], 
    right_on=['Season', 'Team'], 
    how='left',
    suffixes=('', '_lower')
)
# Rename the merged columns for clarity.
m_matchups_full.rename(columns={
    'Seed': 'Seed_lower',
    'roll_Off': 'roll_Off_lower',
    'roll_Def': 'roll_Def_lower',
    'win_ratio': 'win_ratio_lower'
}, inplace=True)
m_matchups_full.drop(columns=['Team'], inplace=True)

# Merge for Team_higher metrics:
m_matchups_full = pd.merge(
    m_matchups_full,
    latest_team_metrics,
    left_on=['Season', 'Team_higher'],
    right_on=['Season', 'Team'],
    how='left',
    suffixes=('', '_higher')
)
m_matchups_full.rename(columns={
    'Seed': 'Seed_higher',
    'roll_Off': 'roll_Off_higher',
    'roll_Def': 'roll_Def_higher',
    'win_ratio': 'win_ratio_higher'
}, inplace=True)
m_matchups_full.drop(columns=['Team'], inplace=True)

# Now, for matchups where there was no direct game, you can compute the desired metrics
# using the individual team metrics.
# For example, let’s define net_diff as the difference in win_ratio:
m_matchups_full['net_diff'] = m_matchups_full['win_ratio_lower'].fillna(0) - m_matchups_full['win_ratio_higher'].fillna(0)

# And as an example, define HomeCourt_1 and HomeCourt_2 based on team seeds
# (you can modify this logic to suit your actual definition)
m_matchups_full['HomeCourt_1'] = (m_matchups_full['Seed_lower'] < m_matchups_full['Seed_higher']).astype(int)
m_matchups_full['HomeCourt_2'] = (m_matchups_full['Seed_lower'] > m_matchups_full['Seed_higher']).astype(int)

print(m_matchups_full)
