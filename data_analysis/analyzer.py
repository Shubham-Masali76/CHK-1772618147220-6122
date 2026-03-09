import pandas as pd

def analyze_dataset(df):

    dataset_shape = df.shape

    missing_values = df.isnull().sum().to_dict()

    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

    numerical_columns = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

    duplicate_rows = df.duplicated().sum()

    return {
        "dataset_shape": dataset_shape,
        "missing_values": missing_values,
        "categorical_columns": categorical_columns,
        "numerical_columns": numerical_columns,
        "duplicate_rows": duplicate_rows
    }
    