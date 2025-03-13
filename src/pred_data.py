import pandas as pd
import itertools


df = pd.read_csv("./data/m_final_raw.csv")  # Load mens dataframe
print(df)

df = df[(2025 > df['Season']) & (df['Season']>=2021)] # get data from season 2021 onwards

# Get all unique teams for the season
teams = pd.concat([df['Team1'], df['Team2']]).unique()
teams = sorted(teams)  # sort to ensure order

# Specify the season (assuming one season, or loop over multiple seasons if needed)
season = 2021

# Generate all possible matchups with the lower team ID always in the middle
# and create a dictionary for each matchup
matchup_dicts = [
    {
        "Season": season,
        "Team_lower": min(t1, t2),
        "Team_higher": max(t1, t2),
        "matchup": f"{season}_{min(t1, t2)}_{max(t1, t2)}"
    }
    for t1, t2 in itertools.combinations(teams, 2)
]

# Create a new DataFrame from the list of dictionaries
m_matchups_df = pd.DataFrame(matchup_dicts)

print(m_matchups_df)

df = pd.read_csv("./data/w_final_raw.csv")

df = df[(2025 > df['Season']) & (df['Season']>=2021)] # get data from season 2021 onwards

# Get all unique teams for the season
teams = pd.concat([df['Team1'], df['Team2']]).unique()
teams = sorted(teams)  # sort to ensure order

# Specify the season (assuming one season, or loop over multiple seasons if needed)
season = 2021

# Generate all possible matchups with the lower team ID always in the middle
# and create a dictionary for each matchup
matchup_dicts = [
    {
        "Season": season,
        "Team_lower": min(t1, t2),
        "Team_higher": max(t1, t2),
        "matchup": f"{season}_{min(t1, t2)}_{max(t1, t2)}"
    }
    for t1, t2 in itertools.combinations(teams, 2)
]

# Create a new DataFrame from the list of dictionaries
matchups_df = pd.DataFrame(matchup_dicts)

print(matchups_df)

all_games = pd.concat([m_matchups_df, matchups_df], ignore_index=True)

print(all_games)

# Get all unique teams for the season
teams = pd.concat([all_games['Team_lower'], all_games['Team_higher']]).nunique()
print(teams)

