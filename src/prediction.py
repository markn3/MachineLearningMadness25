import pandas as pd
from autogluon.tabular import TabularPredictor

# Load your trained model (if not already loaded)

m_predictor = TabularPredictor.load("./data/AutogluonModels/m_pred/")

m_matches = pd.read_csv("./data/m_matchups_1_4.csv")
# Get the predicted probabilities for the positive class (Team1 wins)
m_matches.rename(columns={"TeamA": "Team1", "TeamB":"Team2"}, inplace=True)
m_predictions = m_predictor.predict_proba(m_matches)


m_pred = m_matches[['matchup']].copy()
m_pred.rename({"matchup": "ID"}, inplace=True)
m_pred['Pred'] = m_predictions.iloc[:, 0]  # Use iloc for column selection
print(m_pred)

# submission.to_csv("submission.csv", index=False)

# # Now, you can create the final submission file with the ID and Pred columns.
# submission = matchup_features_df[["ID", "Pred"]]
# submission.to_csv("submission.csv", index=False)
