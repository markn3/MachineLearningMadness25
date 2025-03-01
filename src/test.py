import pandas as pd
pd.set_option('display.max_columns', None)
 

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

# sort by Season, Team, and Game Day
m_detailed.sort_values(by=['Season', 'TeamID', 'DayNum'], inplace=True)
m_detailed.reset_index(drop=True, inplace=True)

print(m_detailed)
                       
