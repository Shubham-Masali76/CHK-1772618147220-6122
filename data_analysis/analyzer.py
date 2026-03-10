def analyze_dataset(df):

    return {
        "dataset_shape": df.shape,
        "missing_values": df.isnull().sum().to_dict(),
        "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
        "numerical_columns": df.select_dtypes(include=["int64","float64"]).columns.tolist(),
        "duplicate_rows": df.duplicated().sum()
    }