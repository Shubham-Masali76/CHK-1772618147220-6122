import pandas as pd

def get_feature_importance(model, features):

    if hasattr(model, "feature_importances_"):

        return pd.DataFrame({
            "feature": features,
            "importance": model.feature_importances_
        }).sort_values(by="importance", ascending=False)

    return None