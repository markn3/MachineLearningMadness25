import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)


# Teams & Seasons
m_teams = pd.read_csv("./data/MTeams.csv")  # Contains TeamID and TeamName
w_teams = pd.read_csv("./data/WTeams.csv")
m_seasons = pd.read_csv("./data/MSeasons.csv")
w_seasons = pd.read_csv("./data/WSeasons.csv")

# Tournament Seeds
m_ncaa_seeds = pd.read_csv("./data/MNCAATourneySeeds.csv")
w_ncaa_seeds = pd.read_csv("./data/WNCAATourneySeeds.csv")

# Basic Game Results (Regular Season & Tournament)
m_regular_season_results = pd.read_csv("./data/MRegularSeasonCompactResults.csv")
w_reg_compact = pd.read_csv("./data/WRegularSeasonCompactResults.csv")
m_ncaa_compact = pd.read_csv("./data/MNCAATourneyCompactResults.csv")
w_ncaa_compact = pd.read_csv("./data/WNCAATourneyCompactResults.csv")

# Sample submission format (to guide matchup construction)
sample_submission = pd.read_csv("./data/SampleSubmissionStage1.csv")

# Data Preprocessing

# Extract numerical part of Seed (e.g., "W01" → 1, "X16" → 16)
m_ncaa_seeds["Seed"] = m_ncaa_seeds["Seed"].str.extract("(\d+)").astype(int)

# Load Tournament Results
m_tourney_results = pd.read_csv("./data/MNCAATourneyCompactResults.csv")

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

# Create Seed Difference Feature
m_tourney_results["Seed_Diff"] = m_tourney_results["WSeed"] - m_tourney_results["LSeed"]

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

# Create Seed Difference Feature
m_regular_season_results["Seed_Diff"] = m_regular_season_results["WSeed"] - m_regular_season_results["LSeed"]

# Display Processed Regular Season Data
print("Regular Season Data Sample:")
print(m_regular_season_results.shape)

# -----------------------------------------------

# Combine Both Datasets into One
all_games = pd.concat([m_regular_season_results, m_tourney_results], ignore_index=True)

# --------------------------------------------

# Offensive Rating

# Teams & Seasons
m_reg_detailed = pd.read_csv("./data/MRegularSeasonDetailedResults.csv")
m_t_detailed = pd.read_csv("./data/MNCAATourneyDetailedResults.csv")

# Offensive Rating
def calculate_ratings(df):
    df['WPoss'] = df['WFGA'] - df['WOR'] + df['WTO'] + 0.44 * df['WFTA']
    df['LPoss'] = df['LFGA'] - df['LOR'] + df['LTO'] + 0.44 * df['LFTA']

    df['W_OffRtg'] = (df['WScore'] / df['WPoss']) * 100
    df['L_OffRtg'] = (df['LScore'] / df['LPoss']) * 100

    print(df)

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

# Choose a specific team (e.g., TeamID 1101) and sort by DayNum (or date)
team_id = 1102
team_data = merged_final[(merged_final['WTeamID'] == team_id) | (merged_final['LTeamID'] == team_id)].sort_values(by=['Season', 'DayNum'])

# Display the results for that team
print(team_data)

print(merged_final)


cols_to_drop = [
    'WTeamName', 'LTeamName',
    'FirstD1Season_x', 'LastD1Season_x', 'FirstD1Season_y', 'LastD1Season_y',
    'WScore', 'LScore', 'W_OffRtg',  'L_OffRtg',  'W_DefRtg', 'L_DefRtg', 'NumOT' # if you don't need raw scores
]

merged_final.drop(columns=cols_to_drop, inplace=True)

print(merged_final)

# Optionally, save the final merged dataset to a CSV
# merged_final.to_csv("Merged_Final_Data.csv", index=False)