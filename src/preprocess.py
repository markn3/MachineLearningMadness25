import pandas as pd


def load_data():
    data = pd.read_csv("./data/Cities.csv")

    return data


if __name__ == "__main__":
    data = load_data()
    print(data)