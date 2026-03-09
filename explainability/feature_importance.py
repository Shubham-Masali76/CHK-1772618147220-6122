import pandas as pd

def get_feature_importance(model, feature_names):

    if hasattr(model, "feature_importances_"):

        importance = model.feature_importances_

        df = pd.DataFrame({
            "feature": feature_names,
            "importance": importance
        })

        return df.sort_values(by="importance", ascending=False)

    return None