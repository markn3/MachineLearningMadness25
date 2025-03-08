import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)

# Teams & Seasons
m_teams = pd.read_csv("./data/WTeams.csv")  # Contains TeamID and TeamName
w_teams = pd.read_csv("./data/WTeams.csv")
m_seasons = pd.read_csv("./data/MSeasons.csv")
w_seasons = pd.read_csv("./data/WSeasons.csv")

# Tournament Seeds
m_ncaa_seeds = pd.read_csv("./data/WNCAATourneySeeds.csv")
w_ncaa_seeds = pd.read_csv("./data/WNCAATourneySeeds.csv")

# Basic Game Results (Regular Season & Tournament)
m_regular_season_results = pd.read_csv("./data/WRegularSeasonCompactResults.csv")
w_reg_compact = pd.read_csv("./data/WRegularSeasonCompactResults.csv")

# Sample submission format (to guide matchup construction)
sample_submission = pd.read_csv("./data/SampleSubmissionStage1.csv")

# Data Preprocessing

# Extract numerical part of Seed (e.g., "W01" → 1, "X16" → 16)
m_ncaa_seeds["Seed"] = m_ncaa_seeds["Seed"].str.extract("(\d+)").astype(int)

# Load Tournament Results
m_tourney_results = pd.read_csv("./data/WNCAATourneyCompactResults.csv")

# Merge Tournament Data with Seeds for Winners
m_tourney_results = m_tourney_results.merge(m_ncaa_seeds, left_on=["Season", "WTeamID"], right_on=["Season", "TeamID"], how="left")
m_tourney_results.rename(columns={"Seed": "WSeed"}, inplace=True)
m_tourney_results.drop(columns=["TeamID"], inplace=True)

# Merge Tournament Data with Seeds for Losers
m_tourney_results = m_tourney_results.merge(m_ncaa_seeds, left_on=["Season", "LTeamID"], right_on=["Season", "TeamID"], how="left")
m_tourney_results.rename(columns={"Seed": "LSeed"}, inplace=True)
m_tourney_results.drop(columns=["TeamID"], inplace=True)

# Merge Tournament Data with Team Names
m_tourney_results = m_tourney_results.merge(m_teams, left_on="WTeamID", right_on="TeamID", how="left").rename(columns={"TeamName": "WTeamName"}).drop(columns=["TeamID"])
m_tourney_results = m_tourney_results.merge(m_teams, left_on="LTeamID", right_on="TeamID", how="left").rename(columns={"TeamName": "LTeamName"}).drop(columns=["TeamID"])


# Display Processed Tournament Data
print("Tournament Data Sample:")
print(m_tourney_results.shape)

# -----------------------------------------------

# Merge Regular Season Data with Seeds (Winners)
m_regular_season_results = m_regular_season_results.merge(m_ncaa_seeds, left_on=["Season", "WTeamID"], right_on=["Season", "TeamID"], how="left")
m_regular_season_results.rename(columns={"Seed": "WSeed"}, inplace=True)
m_regular_season_results.drop(columns=["TeamID"], inplace=True)

# Merge Regular Season Data with Seeds (Losers)
m_regular_season_results = m_regular_season_results.merge(m_ncaa_seeds, left_on=["Season", "LTeamID"], right_on=["Season", "TeamID"], how="left")
m_regular_season_results.rename(columns={"Seed": "LSeed"}, inplace=True)
m_regular_season_results.drop(columns=["TeamID"], inplace=True)

# Merge Regular Season Data with Team Names
m_regular_season_results = m_regular_season_results.merge(m_teams, left_on="WTeamID", right_on="TeamID", how="left").rename(columns={"TeamName": "WTeamName"}).drop(columns=["TeamID"])
m_regular_season_results = m_regular_season_results.merge(m_teams, left_on="LTeamID", right_on="TeamID", how="left").rename(columns={"TeamName": "LTeamName"}).drop(columns=["TeamID"])

# Handle Missing Seeds
m_regular_season_results.fillna({"WSeed": 0, "LSeed": 0}, inplace=True)

# Display Processed Regular Season Data
print("Regular Season Data Sample:")
print(m_regular_season_results.shape)

# -----------------------------------------------

# Combine Both Datasets into One
all_games = pd.concat([m_regular_season_results, m_tourney_results], ignore_index=True)

# --------------------------------------------

# Offensive Rating

# Teams & Seasons
m_reg_detailed = pd.read_csv("./data/WRegularSeasonDetailedResults.csv")
m_t_detailed = pd.read_csv("./data/WNCAATourneyDetailedResults.csv")

# Offensive Rating
def calculate_ratings(df):
    df['WPoss'] = df['WFGA'] - df['WOR'] + df['WTO'] + 0.44 * df['WFTA']
    df['LPoss'] = df['LFGA'] - df['LOR'] + df['LTO'] + 0.44 * df['LFTA']

    df['W_OffRtg'] = (df['WScore'] / df['WPoss']) * 100
    df['L_OffRtg'] = (df['LScore'] / df['LPoss']) * 100

    # Defensive Rating
    df['W_DefRtg'] = (df['LScore'] / df['LPoss']) * 100
    df['L_DefRtg'] = (df['WScore'] / df['WPoss']) * 100

    # drop unnecessary columns
    df = df[['Season', 'DayNum', 'WTeamID', 'LTeamID', 'W_OffRtg', 'L_OffRtg', 'W_DefRtg', 'L_DefRtg']]

    return df

m_reg_detailed = calculate_ratings(m_reg_detailed)
m_t_detailed = calculate_ratings(m_t_detailed)

m_detailed = pd.concat([m_reg_detailed, m_t_detailed], ignore_index=True)

merged_final = pd.merge(
    all_games, 
    m_detailed, 
    on=['Season', 'DayNum', 'WTeamID', 'LTeamID'], 
    how='inner'
)

# --- Assume merged_final is already built and includes:
# 'Season', 'DayNum', 'WTeamID', 'LTeamID', 'W_OffRtg', 'W_DefRtg',
# 'L_OffRtg', 'L_DefRtg', etc.

# Step 1: Create long format for winning teams (include OffRtg, DefRtg, NetRtg)
w_data = merged_final[['Season', 'DayNum', 'WTeamID', 'W_OffRtg', 'W_DefRtg']].copy()
w_data.rename(columns={
    'WTeamID': 'TeamID',
    'W_OffRtg': 'OffRtg',
    'W_DefRtg': 'DefRtg'
}, inplace=True)
w_data['Role'] = 'W'

# Step 2: Create long format for losing teams (include OffRtg, DefRtg, NetRtg)
l_data = merged_final[['Season', 'DayNum', 'LTeamID', 'L_OffRtg', 'L_DefRtg']].copy()
l_data.rename(columns={
    'LTeamID': 'TeamID',
    'L_OffRtg': 'OffRtg',
    'L_DefRtg': 'DefRtg',
}, inplace=True)
l_data['Role'] = 'L'

# Step 3: Combine both DataFrames into one long-format DataFrame
all_team_games_long = pd.concat([w_data, l_data], ignore_index=True)

# Step 4: Sort by Season, TeamID, and DayNum so games are in chronological order
all_team_games_long.sort_values(by=['Season', 'TeamID', 'DayNum'], inplace=True)

# Step 5: Compute the rolling/dynamic ratings per team (average of previous games)
def compute_rolling_ratings(group):
    roll_off = []
    roll_def = []
    roll_wins = []
    roll_losses = []
    cumulative_off = 0.0
    cumulative_def = 0.0
    cumulative_wins = 0
    cumulative_losses = 0
    count = 0
    # Iterate over the rows in this group (already sorted by DayNum)
    for off, defe, role in zip(group['OffRtg'], group['DefRtg'], group['Role']):
        if count == 0:
            roll_off.append(np.nan)
            roll_def.append(np.nan)
            roll_wins.append(np.nan)
            roll_losses.append(np.nan)
        else:
            roll_off.append(cumulative_off / count)
            roll_def.append(cumulative_def / count)
            roll_wins.append(cumulative_wins)
            roll_losses.append(cumulative_losses)
        cumulative_off += off
        cumulative_def += defe
        if role == "W":
            cumulative_wins += 1
        elif role == "L": 
            cumulative_losses += 1
        count += 1
    group = group.copy()
    group['roll_off'] = roll_off
    group['roll_def'] = roll_def
    group['roll_wins'] = roll_wins
    group['roll_losses'] = roll_losses
    return group

# Apply the function group-by-group (for each team in each season)
all_team_games_long = all_team_games_long.groupby(['Season', 'TeamID']).apply(compute_rolling_ratings)
all_team_games_long.reset_index(drop=True, inplace=True)

# For winning teams: extract and rename the dynamic ratings
w_dynamic = all_team_games_long[all_team_games_long['Role'] == 'W'][['Season', 'TeamID', 'DayNum', 'roll_off', 'roll_def', 'roll_wins', 'roll_losses']].copy()
w_dynamic.rename(columns={
    'TeamID': 'WTeamID',
    'roll_off': 'W_roll_Off',
    'roll_def': 'W_roll_Def',
    'roll_wins': 'W_roll_Wins',
    'roll_losses': 'W_roll_Losses'
}, inplace=True)

# Merge the winning team's dynamic ratings back into merged_final
merged_final = pd.merge(merged_final, w_dynamic, on=['Season', 'WTeamID', 'DayNum'], how='left')

# For losing teams: extract and rename the dynamic ratings
l_dynamic = all_team_games_long[all_team_games_long['Role'] == 'L'][['Season', 'TeamID', 'DayNum', 'roll_off', 'roll_def', 'roll_wins', 'roll_losses']].copy()
l_dynamic.rename(columns={
    'TeamID': 'LTeamID',
    'roll_off': 'L_roll_Off',
    'roll_def': 'L_roll_Def',
    'roll_wins': 'L_roll_Wins',
    'roll_losses': 'L_roll_Losses'
}, inplace=True)

# Merge the losing team's dynamic ratings back into merged_final
merged_final = pd.merge(merged_final, l_dynamic, on=['Season', 'LTeamID', 'DayNum'], how='left')

# Inspect the final merged dataset sample with dynamic ratings for both winners and losers
print("Merged Final Dataset Sample with Dynamic Ratings:")
print(merged_final.head())

print(merged_final.shape)
nan_count = merged_final[['W_roll_Off','W_roll_Def','L_roll_Off','L_roll_Def']].isna().sum()
print(nan_count)

merged_final = merged_final.dropna(subset=['W_roll_Off','W_roll_Def','L_roll_Off','L_roll_Def', 'L_roll_Wins', 'L_roll_Losses','W_roll_Wins', 'W_roll_Losses'])
nan_count = merged_final[['W_roll_Off','W_roll_Def','L_roll_Off','L_roll_Def', 'L_roll_Wins', 'L_roll_Losses','W_roll_Wins', 'W_roll_Losses']].isna().sum()
print(nan_count)

cols_to_drop = [
    'WTeamName', 'LTeamName',
    'WScore', 'LScore', 'W_OffRtg',  'L_OffRtg',  'W_DefRtg', 'L_DefRtg', 'NumOT' # if you don't need raw scores
]

merged_final.drop(columns=cols_to_drop, inplace=True)

# Assume merged_final contains the original game data
def reformat_matchup(row):
    w_id = row['WTeamID']
    l_id = row['LTeamID']
    
    # Determine lower and higher team ID
    team1 = min(w_id, l_id)
    team2 = max(w_id, l_id)
    
    # Target: 1 if the lower ID team won, 0 otherwise
    target = 1 if w_id == team1 else 0
    
    # Swap team-related columns to match Team1 and Team2
    if w_id == team1:
        return pd.Series([row['Season'], row['DayNum'], team1, team2, target, row['WSeed'], row['LSeed'], 
                          row['W_roll_Off'], row['W_roll_Def'], row['W_roll_Wins'], row['W_roll_Losses'],
                          row['L_roll_Off'], row['L_roll_Def'], row['L_roll_Wins'], row['L_roll_Losses'], row['WLoc']
                         ])
    else:
        return pd.Series([row['Season'], row['DayNum'], team1, team2, target, row['LSeed'], row['WSeed'], 
                          row['L_roll_Off'], row['L_roll_Def'], row['L_roll_Wins'], row['L_roll_Losses'],
                          row['W_roll_Off'], row['W_roll_Def'], row['W_roll_Wins'], row['W_roll_Losses'], row['WLoc']
                         ])

# Apply the function to each row
matchup_data = merged_final.apply(reformat_matchup, axis=1)

# Rename the columns
matchup_data.columns = ['Season','DayNum','Team1', 'Team2', 'Target', 
                        'T1_Seed', 'T2_Seed', 
                        'T1_roll_Off', 'T1_roll_Def', 'T1_roll_Wins', 'T1_roll_Losses',
                        'T2_roll_Off', 'T2_roll_Def', 'T2_roll_Wins', 'T2_roll_Losses', 'WLoc']

def assign_homecourt(row):
    # row['WLoc'] is the location of the winning team.
    # row['Target'] is 1 if Team1 (the lower-ID team) won, 0 otherwise.
    if row['WLoc'] == 'N':
        return 0  # neutral site, no home advantage
    elif row['WLoc'] == 'H':
        # Winning team was at home.
        if row['Target'] == 1:
            # Team1 won and is the winning team → Team1 was at home.
            return 1
        else:
            # Team2 won and is the winning team → Team2 was at home.
            return 2
    elif row['WLoc'] == 'A':
        # Winning team was away.
        if row['Target'] == 1:
            # Team1 won but was away → therefore, Team2 was at home.
            return 2
        else:
            # Team2 won but was away → therefore, Team1 was at home.
            return 1
    else:
        # In case of any unexpected value, treat it as neutral.
        return 0

# Apply the function to each row of your matchup DataFrame
matchup_data['HomeCourt'] = matchup_data.apply(assign_homecourt, axis=1)

matchup_data['net_diff'] = (matchup_data['T1_roll_Off'] - matchup_data['T1_roll_Def']) - (matchup_data['T2_roll_Off'] - matchup_data['T2_roll_Def'])

matchup_data.drop(columns=["WLoc"], inplace=True)

matchup_data['Gender'] = 0

# Reorder columns so that 'Target' is the last column
cols = list(matchup_data.columns)
cols.remove('Target')
cols.append('Target')
matchup_data = matchup_data[cols]
print("Columns after reordering:", list(matchup_data.columns))

print(matchup_data)

matchup_data.to_csv("./data/women_dataset.csv", index=False)
