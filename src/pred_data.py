import pandas as pd
from itertools import combinations
from autogluon.tabular import TabularPredictor



m_df = pd.read_csv("./data/m_final.csv")  # Contains TeamID and TeamName


