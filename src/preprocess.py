import pandas as pd
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

# Display Final Merged Dataset Sample
print("Final Merged Dataset Sample:")
print(all_games.head())
print(all_games['WTeamID'].nunique())

# Save to CSV for Future Use
# all_games.to_csv("Merged_Season_Tourney_Data.csv", index=False)


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

# Display a sample of the final merged dataset
print("Merged Final Dataset Sample:")
print(merged_final)

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