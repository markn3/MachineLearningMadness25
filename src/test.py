import pandas as pd
import itertools
pd.set_option('display.max_columns', None)

import pandas as pd
import itertools

# --------------------------
# 1. Load and filter the data
# --------------------------
df = pd.read_csv("./data/m_final_raw.csv")
# Filter to include seasons from 2021 up to (but not including) 2025
df = df[(df['Season'] < 2025) & (df['Season'] >= 2021)]

# For this example, we'll work with season 2021.
season = 2021

# --------------------------
# 2. Get all unique teams for the season
# --------------------------
teams = pd.concat([df['Team1'], df['Team2']]).unique()
teams = sorted(teams)  # sort to ensure a consistent order

# --------------------------
# 3. Prepare team metrics (latest game details per team)
# --------------------------
def extract_team_rows(df):
    # Extract metrics when a team is Team1
    df1 = df[['Season', 'DayNum', 'Team1', 'T1_Seed', 'T1_roll_Off', 'T1_roll_Def', 'T1_win_ratio']].copy()
    df1 = df1.rename(columns={
        'Team1': 'Team',
        'T1_Seed': 'Seed',
        'T1_roll_Off': 'roll_Off',
        'T1_roll_Def': 'roll_Def',
        'T1_win_ratio': 'win_ratio'
    })
    # Extract metrics when a team is Team2
    df2 = df[['Season', 'DayNum', 'Team2', 'T2_Seed', 'T2_roll_Off', 'T2_roll_Def', 'T2_win_ratio']].copy()
    df2 = df2.rename(columns={
        'Team2': 'Team',
        'T2_Seed': 'Seed',
        'T2_roll_Off': 'roll_Off',
        'T2_roll_Def': 'roll_Def',
        'T2_win_ratio': 'win_ratio'
    })
    return pd.concat([df1, df2], ignore_index=True)

team_metrics = extract_team_rows(df)
team_metrics = team_metrics.sort_values('DayNum')  # sorting so that the most recent game is last
latest_metrics = team_metrics.groupby('Team').last().reset_index()

# --------------------------
# 4. Generate all matchups and merge in row details
# --------------------------
matchup_dicts = []
for t1, t2 in itertools.combinations(teams, 2):
    # Determine the lower and higher team IDs for the matchup_id.
    # If team IDs are numeric strings, we convert them for proper comparison.
    try:
        lower = str(min(int(t1), int(t2)))
        higher = str(max(int(t1), int(t2)))
    except ValueError:
        lower = min(t1, t2)
        higher = max(t1, t2)
        
    matchup_id = f"{season}_{lower}_{higher}"
    
    # Look for games between these two teams in the season
    mask = ((df['Team1'] == t1) & (df['Team2'] == t2)) | ((df['Team1'] == t2) & (df['Team2'] == t1))
    df_match = df[mask]
    
    if not df_match.empty:
        # If there are multiple games, select the one with the highest DayNum (i.e. the most recent)
        row = df_match.loc[df_match['DayNum'].idxmax()]
        # Determine the order so that our stored details remain consistent.
        # We assume that t1 and t2 are the pair in the same order as in the combinations.
        if row['Team1'] == t1:
            row_details = {
                'A_Seed': row['T1_Seed'],
                'A_roll_Off': row['T1_roll_Off'],
                'A_roll_Def': row['T1_roll_Def'],
                'A_win_ratio': row['T1_win_ratio'],
                'B_Seed': row['T2_Seed'],
                'B_roll_Off': row['T2_roll_Off'],
                'B_roll_Def': row['T2_roll_Def'],
                'B_win_ratio': row['T2_win_ratio'],
                'net_diff': row['net_diff'],
                'Target': row['Target'],
                'HomeCourt_A': row['HomeCourt_1'],
                'HomeCourt_B': row['HomeCourt_2'],
                'DayNum': row['DayNum']
            }
        else:
            # If t1 appears as Team2 in the record, swap the order.
            row_details = {
                'A_Seed': row['T2_Seed'],
                'A_roll_Off': row['T2_roll_Off'],
                'A_roll_Def': row['T2_roll_Def'],
                'A_win_ratio': row['T2_win_ratio'],
                'B_Seed': row['T1_Seed'],
                'B_roll_Off': row['T1_roll_Off'],
                'B_roll_Def': row['T1_roll_Def'],
                'B_win_ratio': row['T1_win_ratio'],
                # Optionally, invert these if it makes sense:
                'net_diff': -row['net_diff'],
                'Target': -row['Target'],
                'HomeCourt_A': row['HomeCourt_2'],
                'HomeCourt_B': row['HomeCourt_1'],
                'DayNum': row['DayNum']
            }
        matchup_season = row['Season']
    else:
        # For matchups that never happened, use each team’s latest metrics.
        if not latest_metrics[latest_metrics['Team'] == t1].empty:
            metricsA = latest_metrics[latest_metrics['Team'] == t1].iloc[0]
        else:
            metricsA = {'Seed': None, 'roll_Off': None, 'roll_Def': None, 'win_ratio': None, 'Season': season}
        if not latest_metrics[latest_metrics['Team'] == t2].empty:
            metricsB = latest_metrics[latest_metrics['Team'] == t2].iloc[0]
        else:
            metricsB = {'Seed': None, 'roll_Off': None, 'roll_Def': None, 'win_ratio': None}
        
        row_details = {
            'A_Seed': metricsA['Seed'],
            'A_roll_Off': metricsA['roll_Off'],
            'A_roll_Def': metricsA['roll_Def'],
            'A_win_ratio': metricsA['win_ratio'],
            'B_Seed': metricsB['Seed'],
            'B_roll_Off': metricsB['roll_Off'],
            'B_roll_Def': metricsB['roll_Def'],
            'B_win_ratio': metricsB['win_ratio'],
            'net_diff': None,
            'Target': None,
            'HomeCourt_A': None,
            'HomeCourt_B': None,
            'DayNum': None
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
print(m_matchups_df)
