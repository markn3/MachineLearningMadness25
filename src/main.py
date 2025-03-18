import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score

from sklearn.model_selection import GridSearchCV

from autogluon.tabular import TabularDataset, TabularPredictor
pd.set_option('display.max_columns', None)


df = pd.read_csv("./data/m_final_df.csv")

# 2. Drop columns you don't want as model features
#    Here, we remove Team1, Team2, and Season, but keep the rest (like T1_Seed, T2_Seed, net_diff, etc.).
X = df.drop(columns=['Team1', 'Team2'])  # drop team IDs if you don't want them as features
y = df['Target']

# 3. Split into training and validation sets
#    - stratify=y ensures class balance in splits
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4. Train a Logistic Regression model
model = LogisticRegression(
    solver='lbfgs',       # or 'liblinear' if you want simpler approach
    max_iter=100,        # increase if you see convergence warnings
    random_state=42
)
model.fit(X_train, y_train)

# 5. Predict probabilities on the validation set
y_pred_proba = model.predict_proba(X_val)[:, 1]

# 6. Evaluate using log loss and AUC
logloss = log_loss(y_val, y_pred_proba)
auc = roc_auc_score(y_val, y_pred_proba)

print(f"Log Loss: {logloss:.4f}")
print(f"AUC: {auc:.4f}")


# Test AutoGlauon
data = TabularDataset("./data/m_final_df.csv")

print(df)

# # Define target column (change 'target' to your actual label column)
# label_column = "Target"

# # Split into train and test sets (80% train, 20% test)
# train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# # Train AutoGluon model
# predictor = TabularPredictor(label=label_column).fit(train_data)

# # Evaluate on test set
# predictions = predictor.predict(test_data)
# performance = predictor.evaluate(test_data)

# print("Model Performance:", performance)


# PICKLE? Or try looking up documentation for models
# # Save the model to a file
# with open('trained_model.pkl', 'wb') as file:
#     pickle.dump(model, file)

# Grid search