import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler

def preprocess_data(df, missing_strategy="mean", encoding="label", scaling="standard", target_col=None):
    """
    Preprocess data while preserving the target column in its original form.
    
    Args:
        df: Input DataFrame
        missing_strategy: Strategy for handling missing values
        encoding: Encoding strategy for categorical variables
        scaling: Scaling strategy for numerical variables
        target_col: Name of target column to exclude from encoding/scaling
    """
    df = df.copy()

    num_cols = df.select_dtypes(include=["int64","float64"]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object"]).columns.tolist()

    # Handle missing values
    if missing_strategy == "mean":
        for c in num_cols:
            if c != target_col:
                df[c] = df[c].fillna(df[c].mean())

    elif missing_strategy == "median":
        for c in num_cols:
            if c != target_col:
                df[c] = df[c].fillna(df[c].median())

    elif missing_strategy == "mode":
        for c in num_cols:
            if c != target_col:
                df[c] = df[c].fillna(df[c].mode()[0])

    elif missing_strategy == "drop":
        df = df.dropna()

    # Fill missing values in categorical columns
    for c in cat_cols:
        if c != target_col:
            df[c] = df[c].fillna(df[c].mode()[0])

    # Encode categorical variables (excluding target)
    cat_cols_to_encode = [c for c in cat_cols if c != target_col]
    
    if encoding == "label":
        for c in cat_cols_to_encode:
            le = LabelEncoder()
            df[c] = le.fit_transform(df[c].astype(str))

    elif encoding == "onehot":
        df = pd.get_dummies(df, columns=cat_cols_to_encode)

    # Scale numerical variables (excluding target)
    num_cols_to_scale = [c for c in num_cols if c != target_col]
    
    if scaling == "standard":
        scaler = StandardScaler()
        df[num_cols_to_scale] = scaler.fit_transform(df[num_cols_to_scale])

    elif scaling == "minmax":
        scaler = MinMaxScaler()
        df[num_cols_to_scale] = scaler.fit_transform(df[num_cols_to_scale])

    return df