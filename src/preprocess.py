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

print(m_reg_compact)

# Merge DayZero into the regular season data:
m_reg_compact = m_reg_compact.merge(
    m_seasons[['Season', 'DayZero']], 
    on='Season', 
    how='left'
)

# Compute the actual game date (if desired)
m_reg_compact['GameDate'] = pd.to_datetime(m_reg_compact['DayZero']) + pd.to_timedelta(m_reg_compact['DayNum'], unit='D')

print(m_reg_compact)


# Merge winning team seed for tournament games:
m_ncaa_compact = m_ncaa_compact.merge(
    m_ncaa_seeds[['Season', 'TeamID', 'Seed']],
    left_on=['Season', 'WTeamID'],
    right_on=['Season', 'TeamID'],
    how='left'
).rename(columns={'Seed': 'WSeed'}).drop('TeamID', axis=1)

# Merge losing team seed:
m_ncaa_compact = m_ncaa_compact.merge(
    m_ncaa_seeds[['Season', 'TeamID', 'Seed']],
    left_on=['Season', 'LTeamID'],
    right_on=['Season', 'TeamID'],
    how='left'
).rename(columns={'Seed': 'LSeed'}).drop('TeamID', axis=1)

# Extract numeric part from seed (example for simple cases)
m_ncaa_compact['WSeedNumeric'] = m_ncaa_compact['WSeed'].str.extract('(\d+)').astype(int)
m_ncaa_compact['LSeedNumeric'] = m_ncaa_compact['LSeed'].str.extract('(\d+)').astype(int)

# Compute seed differential (example: lower seed value indicates stronger team)
m_ncaa_compact['SeedDiff'] = m_ncaa_compact['LSeedNumeric'] - m_ncaa_compact['WSeedNumeric']




print(m_ncaa_compact)