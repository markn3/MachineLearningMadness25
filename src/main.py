import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score

df = pd.read_csv("./data/final_df.csv")

# 1. Separate Features (X) and Target (y)
y = df['Target']