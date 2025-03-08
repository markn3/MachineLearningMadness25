import pickle

# Later, load the model from the file
with open('trained_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

