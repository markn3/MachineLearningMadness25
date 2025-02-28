import pandas as pd
# Teams & Seasons
m_teams = pd.read_csv("./data/MTeams.csv")
w_teams = pd.read_csv("./data/WTeams.csv")
m_seasons = pd.read_csv("./data/MSeasons.csv")
w_seasons = pd.read_csv("./data/WSeasons.csv")

# Tournament Seeds
m_ncaa_seeds = pd.read_csv("./data/MNCAATourneySeeds.csv")
w_ncaa_seeds = pd.read_csv("./data/WNCAATourneySeeds.csv")

# Basic Game Results (Regular Season & Tournament)
m_reg_compact = pd.read_csv("./data/MRegularSeasonCompactResults.csv")
w_reg_compact = pd.read_csv("./data/WRegularSeasonCompactResults.csv")
m_ncaa_compact = pd.read_csv("./data/MNCAATourneyCompactResults.csv")
w_ncaa_compact = pd.read_csv("./data/WNCAATourneyCompactResults.csv")

# Sample submission format (to guide matchup construction)
sample_submission = pd.read_csv("./data/SampleSubmissionStage1.csv")


# Data Preprocessing

# Merge winning team names into men's regular season compact results:
m_reg_compact = m_reg_compact.merge(
    m_teams[['TeamID', 'TeamName']], 
    left_on='WTeamID', right_on='TeamID', 
    how='left'
).rename(columns={'TeamName': 'WTeamName'}).drop('TeamID', axis=1)

# Merge losing team names:
m_reg_compact = m_reg_compact.merge(
    m_teams[['TeamID', 'TeamName']], 
    left_on='LTeamID', right_on='TeamID', 
    how='left'
).rename(columns={'TeamName': 'LTeamName'}).drop('TeamID', axis=1)