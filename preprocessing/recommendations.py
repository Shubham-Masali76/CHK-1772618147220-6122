def recommend_preprocessing(df):

    rec = {}

    if df.isnull().sum().sum() > 0:
        rec["missing_values"] = {
            "recommended": "mean",
            "reason": "Some values are missing. Filling them keeps the dataset complete."
        }
    else:
        rec["missing_values"] = {
            "recommended": None,
            "reason": "Great! No missing values were found."
        }

    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

    if cat_cols:
        rec["encoding"] = {
            "recommended": "onehot",
            "reason": "Text values must be converted into numbers."
        }
    else:
        rec["encoding"] = {
            "recommended": None,
            "reason": "All columns are already numeric."
        }

    rec["scaling"] = {
        "recommended": "standard",
        "reason": "Scaling helps ML models perform better."
    }

    return rec