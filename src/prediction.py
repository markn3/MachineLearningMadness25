import pandas as pd
from autogluon.tabular import TabularPredictor

# Load your trained model (if not already loaded)


def get_predictions(gender, season):
    predictor = TabularPredictor.load(f"./data/AutogluonModels/{gender}_pred/")
    matches = pd.read_csv(f"./data/{gender}_matchups_{season}.csv")
    raw_predictions = predictor.predict_proba(matches)

    predictions = matches[['matchup']].copy()
    predictions.rename(columns={"matchup":"ID"}, inplace=True)
    predictions['Pred'] = raw_predictions.iloc[:, 0]

    return predictions

# Men predictions
m_2021 = get_predictions("m", 2021)
m_2022 = get_predictions("m", 2022)
m_2023 = get_predictions("m", 2023)
m_2024 = get_predictions("m", 2024)

# Women predictions
w_2021 = get_predictions("w", 2021)
w_2022 = get_predictions("w", 2022)
w_2023 = get_predictions("w", 2023)
w_2024 = get_predictions("w", 2024)

# Combine them all by year
all_games_21 = pd.concat([m_2021, w_2021], ignore_index=True)
all_games_22 = pd.concat([m_2022, w_2022], ignore_index=True)
all_games_23 = pd.concat([m_2023, w_2023], ignore_index=True)
all_games_24 = pd.concat([m_2024, w_2024], ignore_index=True)
all_games = pd.concat([all_games_21, all_games_22], ignore_index=True)
all_games = pd.concat([all_games, all_games_23], ignore_index=True)
all_games = pd.concat([all_games, all_games_24], ignore_index=True)


print(all_games)
all_games.to_csv(f"./data/submission_stage1.csv", index=False)

