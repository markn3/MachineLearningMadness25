import pandas as pd

df = pd.read_csv("./data/SampleSubmissionStage1.csv")  # Load mens dataframe
print(df.head())

df[['Season', 'Team1', 'Team2']] = df['ID'].str.split('_', expand=True)

# Convert to integers for easier comparison
df[['Season', 'Team1', 'Team2']] = df[['Season', 'Team1', 'Team2']].astype(int)

df = df[df['Season'] == 2021]
print(df)

# Get all unique teams for the season
teams = pd.concat([df['Team1'], df['Team2']]).nunique()
print(teams)

# # Create a set of (season, min(team1, team2), max(team1, team2)) for checking reversed matches
# df['Sorted_Tuple'] = list(zip(df['Season'], df[['Team1', 'Team2']].min(axis=1), df[['Team1', 'Team2']].max(axis=1)))

# # Find duplicates where the same matchup appears in reversed order
# duplicate_mask = df.duplicated('Sorted_Tuple', keep=False)

# # Filter the duplicate matchups
# duplicates = df[duplicate_mask]

# # Display results
# print(duplicates)