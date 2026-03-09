import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def preprocess_data(df):

    df = df.copy()

    # Handle missing numeric values
    for col in df.select_dtypes(include=["int64","float64"]).columns:
        df[col] = df[col].fillna(df[col].mean())

    # Handle missing categorical values
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Encode categorical columns
    label_encoders = {}

    for col in df.select_dtypes(include=["object"]).columns:

        le = LabelEncoder()

        df[col] = le.fit_transform(df[col])

        label_encoders[col] = le

    # Scale numeric features
    scaler = StandardScaler()

    numeric_cols = df.select_dtypes(include=["int64","float64"]).columns

    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    return df