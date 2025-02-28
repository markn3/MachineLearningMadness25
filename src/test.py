import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)

# --- 1. Load Core Data ---



# Teams & Seasons
m_teams = pd.read_csv("./data/MTeams.csv")
m_seasons = pd.read_csv("./data/MSeasons.csv")

# Regular Season Compact Results (all games up to Selection Sunday)
m_reg_compact = pd.read_csv("./data/MRegularSeasonCompactResults.csv")

# Tournament Seed Data
m_ncaa_seeds = pd.read_csv("./data/MNCAATourneySeeds.csv")

# Sample submission file (defines matchups to predict)
sample_submission = pd.read_csv("./data/SampleSubmissionStage1.csv")

# --- 2. Compute Team-Level Aggregated Statistics from Regular Season ---

# Calculate wins: each row in m_reg_compact is a win for WTeamID.
wins = m_reg_compact.groupby(['Season', 'WTeamID']).agg(
    wins=('WTeamID', 'count'),
    avg_win_score=('WScore', 'mean')
).reset_index().rename(columns={'WTeamID': 'TeamID'})

# Calculate losses: each row is also a loss for LTeamID.
losses = m_reg_compact.groupby(['Season', 'LTeamID']).agg(
    losses=('LTeamID', 'count'),
    avg_loss_score=('LScore', 'mean')
).reset_index().rename(columns={'LTeamID': 'TeamID'})

# Merge wins and losses
team_stats = pd.merge(wins, losses, on=['Season', 'TeamID'], how='outer').fillna(0)
team_stats['total_games'] = team_stats['wins'] + team_stats['losses']
team_stats['win_pct'] = team_stats['wins'] / team_stats['total_games']
# Compute a combined average score (weighted by number of games)
team_stats['avg_score'] = (
    team_stats['avg_win_score'] * team_stats['wins'] + team_stats['avg_loss_score'] * team_stats['losses']
) / team_stats['total_games']

# --- 3. Prepare Tournament Seed Data ---

# Some seeds include region letters and possible play-in markers (e.g., "W01" or "W16a").
# Extract the numeric portion as a simple measure (lower number = better seed).
m_ncaa_seeds['SeedNumeric'] = m_ncaa_seeds['Seed'].str.extract('(\d+)').astype(int)

# --- 4. Build the Matchup-Level Dataset Using the Sample Submission ---

# The sample submission file has an "ID" column with format "Season_TeamID1_TeamID2"
matchups = sample_submission.copy()
matchups[['Season', 'Team1ID', 'Team2ID']] = matchups['ID'].str.split('_', expand=True)
matchups['Season'] = matchups['Season'].astype(int)
matchups['Team1ID'] = matchups['Team1ID'].astype(int)
matchups['Team2ID'] = matchups['Team2ID'].astype(int)

# --- 5. Merge in Aggregated Team Stats for Each Team ---

# Merge stats for Team1
matchups = matchups.merge(
    team_stats[['Season', 'TeamID', 'win_pct', 'avg_score']],
    left_on=['Season', 'Team1ID'],
    right_on=['Season', 'TeamID'],
    how='left'
).rename(columns={'win_pct': 'Team1_win_pct', 'avg_score': 'Team1_avg_score'}).drop('TeamID', axis=1)

# Merge stats for Team2
matchups = matchups.merge(
    team_stats[['Season', 'TeamID', 'win_pct', 'avg_score']],
    left_on=['Season', 'Team2ID'],
    right_on=['Season', 'TeamID'],
    how='left'
).rename(columns={'win_pct': 'Team2_win_pct', 'avg_score': 'Team2_avg_score'}).drop('TeamID', axis=1)

# --- 6. Merge in Tournament Seed Data for Each Team ---

# Merge seeds for Team1
matchups = matchups.merge(
    m_ncaa_seeds[['Season', 'TeamID', 'Seed', 'SeedNumeric']],
    left_on=['Season', 'Team1ID'],
    right_on=['Season', 'TeamID'],
    how='left'
).rename(columns={'Seed': 'Team1_seed', 'SeedNumeric': 'Team1_seed_num'}).drop('TeamID', axis=1)

# Merge seeds for Team2
matchups = matchups.merge(
    m_ncaa_seeds[['Season', 'TeamID', 'Seed', 'SeedNumeric']],
    left_on=['Season', 'Team2ID'],
    right_on=['Season', 'TeamID'],
    how='left'
).rename(columns={'Seed': 'Team2_seed', 'SeedNumeric': 'Team2_seed_num'}).drop('TeamID', axis=1)

# --- 7. Compute Differential Features ---

# For example, difference in win percentages, average scores, and seeds.
matchups['win_pct_diff'] = matchups['Team1_win_pct'] - matchups['Team2_win_pct']
matchups['avg_score_diff'] = matchups['Team1_avg_score'] - matchups['Team2_avg_score']
matchups['seed_diff'] = matchups['Team1_seed_num'] - matchups['Team2_seed_num']

# --- 8. (Optional) Add More Features or Outcome Labels ---
# If you have historical tournament results, you could merge them in to create a target variable.
# For demonstration, we leave that out, since the sample submission is used for future predictions.

# --- Final Dataset Preview ---

print(matchups.head())
