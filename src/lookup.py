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

    # Filter the DataFrame where both conditions are met
    filtered = matches[(matches['LowerTeam'] == 1101) & (matches['HigherTeam'] == 1102)]

    # Get the 'Pred' value. If you expect only one row, you can use .iloc[0]
    if not filtered.empty:
        pred_value = filtered['Pred'].iloc[0]
        print(pred_value)
    else:
        print("No matching row found.")

match_results("Auburn", "Alabama St")
