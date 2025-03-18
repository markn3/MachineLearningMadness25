import pandas as pd
from autogluon.tabular import TabularPredictor

# Load your trained model (if not already loaded)

m_predictor = TabularPredictor.load("./data/AutogluonModels/m_pred/")
print(m_predictor)

df = pd.read_csv("./data/m_matchups_1_4.csv")
print(df)
# Get the predicted probabilities for the positive class (Team1 wins)
# predictions = m_predictor.predict_proba(df)

# # Typically, predictions will be a DataFrame with columns for each class.
# # If your target is binary (0 and 1) and you've set up your predictor such that 1 = Team1 wins,
# # then you might extract the column for class 1:
# matchup_features_df["Pred"] = predictions[1]

# # Now, you can create the final submission file with the ID and Pred columns.
# submission = matchup_features_df[["ID", "Pred"]]
# submission.to_csv("submission.csv", index=False)






# # Get the predicted probabilities for the positive class (Team1 wins)
# predictions = m_predictor.predict_proba(matchup_features_df)

# # Typically, predictions will be a DataFrame with columns for each class.
# # If your target is binary (0 and 1) and you've set up your predictor such that 1 = Team1 wins,
# # then you might extract the column for class 1:
# matchup_features_df["Pred"] = predictions[1]

# # Now, you can create the final submission file with the ID and Pred columns.
# submission = matchup_features_df[["ID", "Pred"]]
# submission.to_csv("submission.csv", index=False)