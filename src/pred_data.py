import pandas as pd
from itertools import combinations
from autogluon.tabular import TabularPredictor

# 1. Load your current season's team performance data (this should be prepared
# using the same pipeline as your training data). For example:
current_season_features = pd.read_csv("2025_team_features.csv")
# This DataFrame should have columns like: TeamID, T_Seed, roll_Net, roll_Off, roll_Def, etc.

# 2. Get the list of team IDs for the upcoming tournament
team_ids = sorted(current_season_features["TeamID"].unique())

# 3. Generate all possible matchups (Team1 < Team2)
matchups = list(combinations(team_ids, 2))
matchup_df = pd.DataFrame(matchups, columns=["Team1", "Team2"])

# 4. Merge performance data for each team into the matchup DataFrame
# Rename columns for team 1
team_features_team1 = current_season_features.copy().rename(columns={
    "TeamID": "Team1",
    "T_Seed": "T1_Seed",
    "roll_Net": "T1_roll_Net",
    "roll_Off": "T1_roll_Off",
    "roll_Def": "T1_roll_Def"
})
# Merge for Team1
matchup_df = matchup_df.merge(team_features_team1, on="Team1", how="left")

# Rename columns for team 2
team_features_team2 = current_season_features.copy().rename(columns={
    "TeamID": "Team2",
    "T_Seed": "T2_Seed",
    "roll_Net": "T2_roll_Net",
    "roll_Off": "T2_roll_Off",
    "roll_Def": "T2_roll_Def"
})
# Merge for Team2
matchup_df = matchup_df.merge(team_features_team2, on="Team2", how="left")

# 5. Compute differential features
matchup_df["seed_diff"] = matchup_df["T1_Seed"] - matchup_df["T2_Seed"]
matchup_df["roll_net_diff"] = matchup_df["T1_roll_Net"] - matchup_df["T2_roll_Net"]
matchup_df["roll_off_diff"] = matchup_df["T1_roll_Off"] - matchup_df["T2_roll_Off"]
matchup_df["roll_def_diff"] = matchup_df["T1_roll_Def"] - matchup_df["T2_roll_Def"]

# 6. Create the submission ID column in the required format
season = 2025
matchup_df["ID"] = matchup_df.apply(lambda row: f"{season}_{row['Team1']:04d}_{row['Team2']:04d}", axis=1)

# 7. Select the features your model was trained on (e.g., the differential features)
feature_cols = ["seed_diff", "roll_net_diff", "roll_off_diff", "roll_def_diff"]
test_features = matchup_df[feature_cols]

# 8. Load your trained model (e.g., with TabularPredictor)
m_predictor = TabularPredictor.load("trained_model.pkl")

# 9. Get predictions for each matchup
predictions = m_predictor.predict_proba(test_features)
# Extract the probability that the lower-ID team wins (adjust based on how your model outputs probabilities)
matchup_df["Pred"] = predictions[1]  # or predictions[:,1] if using scikit-learn

# 10. Prepare the final submission file with ID and Pred columns
submission = matchup_df[["ID", "Pred"]]
submission.to_csv("submission.csv", index=False)
