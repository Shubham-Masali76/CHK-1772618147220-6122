import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler

def preprocess_data(df, missing_strategy="mean", encoding="label", scaling="standard"):

    df = df.copy()

    num_cols = df.select_dtypes(include=["int64","float64"]).columns
    cat_cols = df.select_dtypes(include=["object"]).columns

    if missing_strategy == "mean":
        for c in num_cols:
            df[c] = df[c].fillna(df[c].mean())

    elif missing_strategy == "median":
        for c in num_cols:
            df[c] = df[c].fillna(df[c].median())

    elif missing_strategy == "mode":
        for c in num_cols:
            df[c] = df[c].fillna(df[c].mode()[0])

    elif missing_strategy == "drop":
        df = df.dropna()

    for c in cat_cols:
        df[c] = df[c].fillna(df[c].mode()[0])

    if encoding == "label":
        for c in cat_cols:
            le = LabelEncoder()
            df[c] = le.fit_transform(df[c])

    elif encoding == "onehot":
        df = pd.get_dummies(df, columns=cat_cols)

    if scaling == "standard":
        scaler = StandardScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])

    elif scaling == "minmax":
        scaler = MinMaxScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])

    return df