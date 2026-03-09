import joblib

def export_model(model, filename="best_model.pkl"):

    joblib.dump(model, filename)

    return filename