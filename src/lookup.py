import pandas as pd
from autogluon.tabular import TabularPredictor


# Use final csv to find data
matches = pd.read_csv(f"./data/submission_stage2.csv")
teams = pd.read_csv(f"./data/MTeams.csv")

matches[['Season', 'LowerTeam', 'HigherTeam']] = matches['ID'].str.split('_', expand=True)
matches['LowerTeam'] = matches['LowerTeam'].astype(int)
matches['HigherTeam'] = matches['HigherTeam'].astype(int)

def findIDs(team_name):
    id = teams.loc[teams['TeamName'] == team_name, 'TeamID'].iloc[0]
    if id:
        return id
    else:
        return -1


def match_results(team1, team2):
    team1_id = findIDs(team1)
    team2_id = findIDs(team2)

    if team1_id < team2_id:
        lower = team1_id
        higher = team2_id
        lower_team_name = team1
        higher_team_name = team2
    else:
        lower = team2_id
        higher = team1_id
        lower_team_name = team2
        higher_team_name = team1

    # Filter the DataFrame where both conditions are met
    filtered = matches[(matches['LowerTeam'] == lower) & (matches['HigherTeam'] == higher)]

    # Get the 'Pred' value. If you expect only one row, you can use .iloc[0]
    if not filtered.empty:
        pred_value = filtered['Pred'].iloc[0]
        print(f"{lower_team_name} has a {round(pred_value*100, 2)}% of beating {higher_team_name}")
    else:
        print("No matching row found.")

match_results("Louisville", "Creighton")
