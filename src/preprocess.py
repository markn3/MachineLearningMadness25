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


    # Net Rating
    df['W_NetRtg'] = df['W_OffRtg'] - df['W_DefRtg']
    df['L_NetRtg'] = df['L_OffRtg'] - df['L_DefRtg']

    # drop unnecessary columns
    df = df[['Season', 'DayNum', 'WTeamID', 'LTeamID', 'W_OffRtg', 'L_OffRtg', 'W_DefRtg', 'L_DefRtg', 'W_NetRtg', 'L_NetRtg']]

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
# 'Season', 'DayNum', 'WTeamID', 'LTeamID', 'W_NetRtg', 'L_NetRtg', etc.

# Step 1: Create long format for winning teams
w_data = merged_final[['Season', 'DayNum', 'WTeamID', 'W_NetRtg']].copy()
w_data.rename(columns={'WTeamID': 'TeamID', 'W_NetRtg': 'NetRtg'}, inplace=True)
w_data['Role'] = 'W'

# Step 2: Create long format for losing teams
l_data = merged_final[['Season', 'DayNum', 'LTeamID', 'L_NetRtg']].copy()
l_data.rename(columns={'LTeamID': 'TeamID', 'L_NetRtg': 'NetRtg'}, inplace=True)
l_data['Role'] = 'L'

# Step 3: Combine both DataFrames into one
all_team_games_long = pd.concat([w_data, l_data], ignore_index=True)

# Step 4: Sort by Season, TeamID, and DayNum so games are in chronological order
all_team_games_long.sort_values(by=['Season', 'TeamID', 'DayNum'], inplace=True)

# Step 5: Compute the rolling/dynamic rating per team (average NetRtg from all previous games)
def compute_rolling_rating(group):
    dynamic_ratings = []
    cumulative_sum = 0.0
    count = 0
    for net in group['NetRtg']:
        if count == 0:
            dynamic_ratings.append(np.nan)  # No previous game exists
        else:
            dynamic_ratings.append(cumulative_sum / count)
        cumulative_sum += net
        count += 1
    group = group.copy()
    group['DynamicRating'] = dynamic_ratings
    return group

# Apply the function for each team in each season
all_team_games_long = all_team_games_long.groupby(['Season', 'TeamID']).apply(compute_rolling_rating)
all_team_games_long.reset_index(drop=True, inplace=True)

# Inspect the dynamic ratings for a specific team (e.g., TeamID 1101)
team_1101 = all_team_games_long[all_team_games_long['TeamID'] == 1101].sort_values(by='DayNum')
print("Dynamic Ratings for Team 1101:")
print(team_1101[['Season', 'DayNum', 'NetRtg', 'DynamicRating']])

# Optionally, you can merge these dynamic ratings back into your wide-format merged_final dataset
# For instance, for winning teams:
w_dynamic = all_team_games_long[all_team_games_long['Role'] == 'W'][['Season', 'TeamID', 'DayNum', 'DynamicRating']].copy()
w_dynamic.rename(columns={'TeamID': 'WTeamID', 'DynamicRating': 'W_DynamicRating'}, inplace=True)

merged_final = pd.merge(merged_final, w_dynamic, on=['Season', 'WTeamID', 'DayNum'], how='left')

# And for losing teams:
l_dynamic = all_team_games_long[all_team_games_long['Role'] == 'L'][['Season', 'TeamID', 'DayNum', 'DynamicRating']].copy()
l_dynamic.rename(columns={'TeamID': 'LTeamID', 'DynamicRating': 'L_DynamicRating'}, inplace=True)

merged_final = pd.merge(merged_final, l_dynamic, on=['Season', 'LTeamID', 'DayNum'], how='left')

# Inspect final merged data sample with dynamic ratings for both winners and losers
print("Merged Final Dataset Sample with Dynamic Ratings:")
print(merged_final[['Season', 'DayNum', 'WTeamID', 'W_NetRtg', 'W_DynamicRating',
                     'LTeamID', 'L_NetRtg', 'L_DynamicRating']].head())

team_1101 = all_team_games_long[all_team_games_long['TeamID'] == 1101].sort_values(by='DayNum')
print(team_1101[['Season', 'DayNum', 'NetRtg', 'DynamicRating']])

print(merged_final.shape)




# # Assume merged_final has already been built and includes columns:
# # 'Season', 'DayNum', 'WTeamID', 'LTeamID', 'W_NetRtg', 'L_NetRtg', ... etc.

# # -----------------------------------------------------
# # Step 1: Reshape the Data into a "Long" Format
# # -----------------------------------------------------
# # For the winning team records
# w_data = merged_final[['Season', 'DayNum', 'WTeamID', 'W_NetRtg']].copy()
# w_data.rename(columns={'WTeamID': 'TeamID', 'W_NetRtg': 'NetRtg'}, inplace=True)
# w_data['Role'] = 'W'

# # For the losing team records
# l_data = merged_final[['Season', 'DayNum', 'LTeamID', 'L_NetRtg']].copy()
# l_data.rename(columns={'LTeamID': 'TeamID', 'L_NetRtg': 'NetRtg'}, inplace=True)
# l_data['Role'] = 'L'

# # Combine into a single DataFrame where each row represents one team's performance in a game
# all_team_games = pd.concat([w_data, l_data], ignore_index=True)

# # Sort by Season, then by TeamID, and then by DayNum so that earlier games come first
# all_team_games.sort_values(by=['Season', 'TeamID', 'DayNum'], inplace=True)

# # -----------------------------------------------------
# # Step 2: Compute the Dynamic Rating for Each Team
# # -----------------------------------------------------
# # For each team in each season, compute a cumulative average of their NetRtg 
# # Instead of using .apply(), use .transform() to ensure index alignment:
# all_team_games['DynamicRating'] = all_team_games.groupby(['Season', 'TeamID'])['NetRtg']\
#     .transform(lambda x: x.shift().expanding().mean())

# # -----------------------------------------------------
# # Step 3: Merge the Dynamic Ratings Back into merged_final
# # -----------------------------------------------------
# # For the winning teams:
# w_dynamic = all_team_games[all_team_games['Role'] == 'W'][['Season', 'TeamID', 'DayNum', 'DynamicRating']].copy()
# w_dynamic.rename(columns={'TeamID': 'WTeamID', 'DynamicRating': 'W_DynamicRating'}, inplace=True)

# # Merge back on Season, WTeamID, and DayNum
# merged_final = pd.merge(merged_final, w_dynamic, on=['Season', 'WTeamID', 'DayNum'], how='left')

# # For the losing teams:
# l_dynamic = all_team_games[all_team_games['Role'] == 'L'][['Season', 'TeamID', 'DayNum', 'DynamicRating']].copy()
# l_dynamic.rename(columns={'TeamID': 'LTeamID', 'DynamicRating': 'L_DynamicRating'}, inplace=True)

# # Merge back on Season, LTeamID, and DayNum
# merged_final = pd.merge(merged_final, l_dynamic, on=['Season', 'LTeamID', 'DayNum'], how='left')

# # -----------------------------------------------------
# # Display a Sample of the Final DataFrame
# # -----------------------------------------------------
# print("Merged Final Dataset with Dynamic Ratings:")
# print(merged_final[['Season', 'DayNum', 'WTeamID', 'W_NetRtg', 'W_DynamicRating',
#                      'LTeamID', 'L_NetRtg', 'L_DynamicRating']].head(10))


# # Optionally, save the final merged dataset to a CSV
# merged_final.to_csv("Merged_Final_Data.csv", index=False)

# Detailed regular
# [117748 rows x 8 columns]

# detailed tourney
# [1382 rows x 8 columns]

# preprocess combined total
# [194314 rows x 18 columns]

# 114450
# 75184