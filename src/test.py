import pandas as pd
import itertools
pd.set_option('display.max_columns', None)

def get_season_matchups(season, csv_path="./data/m_final_raw.csv"):
    """
    Returns a DataFrame of matchups for a given season.
    
    Parameters:
        season (int): The season for which to generate matchups.
        csv_path (str): Path to the CSV file containing the data.
        
    Returns:
        pd.DataFrame: A DataFrame containing matchup details for the specified season.
    """
    # --------------------------
    # 1. Load and filter the data for the specified season
    # --------------------------
    df = pd.read_csv(csv_path)
    # Optionally, if your CSV contains multiple seasons, filter to only the specified season.
    df_season = df[df['Season'] == season].copy()
    
    # --------------------------
    # 2. Get all unique teams for the season
    # --------------------------
    teams = pd.concat([df_season['Team1'], df_season['Team2']]).unique()
    teams = sorted(teams)  # sort to ensure a consistent order

    # --------------------------
    # 3. Prepare team metrics (latest game details per team)
    # --------------------------
    def extract_team_rows(df_input):
        # Extract metrics when a team is Team1
        df1 = df_input[['Season', 'DayNum', 'Team1', 'T1_Seed', 'T1_roll_Off', 'T1_roll_Def', 'T1_win_ratio']].copy()
        df1 = df1.rename(columns={
            'Team1': 'Team',
            'T1_Seed': 'Seed',
            'T1_roll_Off': 'roll_Off',
            'T1_roll_Def': 'roll_Def',
            'T1_win_ratio': 'win_ratio'
        })
        # Extract metrics when a team is Team2
        df2 = df_input[['Season', 'DayNum', 'Team2', 'T2_Seed', 'T2_roll_Off', 'T2_roll_Def', 'T2_win_ratio']].copy()
        df2 = df2.rename(columns={
            'Team2': 'Team',
            'T2_Seed': 'Seed',
            'T2_roll_Off': 'roll_Off',
            'T2_roll_Def': 'roll_Def',
            'T2_win_ratio': 'win_ratio'
        })
        return pd.concat([df1, df2], ignore_index=True)

    team_metrics = extract_team_rows(df_season)
    team_metrics = team_metrics.sort_values('DayNum')  # sorting so that the most recent game is last
    latest_metrics = team_metrics.groupby('Team').last().reset_index()

    # --------------------------
    # 4. Generate all matchups and merge in row details
    # --------------------------
    matchup_dicts = []
    for t1, t2 in itertools.combinations(teams, 2):
        # Determine the lower and higher team IDs for the matchup_id.
        try:
            lower = str(min(int(t1), int(t2)))
            higher = str(max(int(t1), int(t2)))
        except ValueError:
            lower = min(t1, t2)
            higher = max(t1, t2)
            
        matchup_id = f"{season}_{lower}_{higher}"
        
        # Look for games between these two teams in the specified season
        mask = ((df_season['Team1'] == t1) & (df_season['Team2'] == t2)) | ((df_season['Team1'] == t2) & (df_season['Team2'] == t1))
        df_match = df_season[mask]
        
        if not df_match.empty:
            # If there are multiple games, select the one with the highest DayNum (i.e. the most recent)
            row = df_match.loc[df_match['DayNum'].idxmax()]
            # Determine the order so that our stored details remain consistent.
            if row['Team1'] == t1:
                row_details = {
                    'T1_Seed': row['T1_Seed'],
                    'T1_roll_Off': row['T1_roll_Off'],
                    'T1_roll_Def': row['T1_roll_Def'],
                    'T1_win_ratio': row['T1_win_ratio'],
                    'T2_Seed': row['T2_Seed'],
                    'T2_roll_Off': row['T2_roll_Off'],
                    'T2_roll_Def': row['T2_roll_Def'],
                    'T2_win_ratio': row['T2_win_ratio'],
                    'net_diff': row['net_diff'],
                    'HomeCourt_1': row['HomeCourt_1'],
                    'HomeCourt_2': row['HomeCourt_2'],
                }
            else:
                # If t1 appears as Team2 in the record, swap the order.
                row_details = {
                    'T2_Seed': row['T2_Seed'],
                    'T2_roll_Off': row['T2_roll_Off'],
                    'T2_roll_Def': row['T2_roll_Def'],
                    'T2_win_ratio': row['T2_win_ratio'],
                    'T1_Seed': row['T1_Seed'],
                    'T1_roll_Off': row['T1_roll_Off'],
                    'T1_roll_Def': row['T1_roll_Def'],
                    'T1_win_ratio': row['T1_win_ratio'],
                    'net_diff': -row['net_diff'],  # Invert net_diff if the order is swapped.
                    'HomeCourt_2': row['HomeCourt_2'],
                    'HomeCourt_1': row['HomeCourt_1'],
                }
            matchup_season = row['Season']
        else:
            # For matchups that never happened in this season, use each team’s latest metrics.
            if not latest_metrics[latest_metrics['Team'] == t1].empty:
                metricsA = latest_metrics[latest_metrics['Team'] == t1].iloc[0]
            else:
                metricsA = {'Seed': None, 'roll_Off': None, 'roll_Def': None, 'win_ratio': None, 'Season': season}
            if not latest_metrics[latest_metrics['Team'] == t2].empty:
                metricsB = latest_metrics[latest_metrics['Team'] == t2].iloc[0]
            else:
                metricsB = {'Seed': None, 'roll_Off': None, 'roll_Def': None, 'win_ratio': None}
            
            row_details = {
                'T1_Seed': metricsA['Seed'],
                'T1_roll_Off': metricsA['roll_Off'],
                'T1_roll_Def': metricsA['roll_Def'],
                'T1_win_ratio': metricsA['win_ratio'],
                'T2_Seed': metricsB['Seed'],
                'T2_roll_Off': metricsB['roll_Off'],
                'T2_roll_Def': metricsB['roll_Def'],
                'T2_win_ratio': metricsB['win_ratio'],
                'net_diff': (metricsA['roll_Off'] - metricsA['roll_Def']) - (metricsB['roll_Off'] - metricsB['roll_Def']),
                'HomeCourt_1': False,
                'HomeCourt_2': False,
            }
            matchup_season = season
        
        # Build the matchup dictionary.
        matchup_dict = {
            "Season": matchup_season,
            "Team_lower": lower,
            "Team_higher": higher,
            "matchup": matchup_id,
            "TeamA": t1,
            "TeamB": t2
        }
        matchup_dict.update(row_details)
        matchup_dicts.append(matchup_dict)

    # --------------------------
    # 5. Create the final DataFrame
    # --------------------------
    m_matchups_df = pd.DataFrame(matchup_dicts)
    return m_matchups_df

# Example usage:
# [58653
m_matchups_2021 = get_season_matchups(2021)
w_matchups_2021 = get_season_matchups(2021, "./data/w_final_raw.csv")
all_games_2021 = pd.concat([m_matchups_2021, w_matchups_2021], ignore_index=True)

m_matchups_2022 = get_season_matchups(2022)
w_matchups_2022 = get_season_matchups(2022, "./data/w_final_raw.csv")
all_games_2022 = pd.concat([m_matchups_2022, w_matchups_2022], ignore_index=True)

m_matchups_2023 = get_season_matchups(2023)
w_matchups_2023 = get_season_matchups(2023, "./data/w_final_raw.csv")
all_games_2023 = pd.concat([m_matchups_2023, w_matchups_2023], ignore_index=True)

m_matchups_2024 = get_season_matchups(2024)
w_matchups_2024 = get_season_matchups(2024, "./data/w_final_raw.csv")
all_games_2024 = pd.concat([m_matchups_2024, w_matchups_2024], ignore_index=True)

all_games_1_2 = pd.concat([all_games_2021, all_games_2022], ignore_index=True)
all_games_1_3 = pd.concat([all_games_1_2, all_games_2023], ignore_index=True)
all_games_1_4 = pd.concat([all_games_1_3, all_games_2024], ignore_index=True)

all_games_1_4.to_csv("./data/pred_matchups.csv", index=False)

print(all_games_1_4)

