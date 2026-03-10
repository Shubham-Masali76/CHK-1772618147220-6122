def preprocessing_advisor(df):

    advice = []

    # Missing values
    missing = df.isnull().sum().sum()

    if missing > 0:

        advice.append({
            "title": "Missing Values",
            "message": "Some values are missing in the dataset.",
            "recommendation": "Fill missing values using mean, median, or most frequent value."
        })

    else:

        advice.append({
            "title": "Missing Values",
            "message": "Great! No missing values were found.",
            "recommendation": "No action needed."
        })


    # Categorical columns
    categorical = df.select_dtypes(include=["object"]).columns.tolist()

    if categorical:

        advice.append({
            "title": "Categorical Data",
            "message": "Some columns contain text values.",
            "recommendation": "Convert text values into numbers so the model can understand them."
        })


    # Numerical scaling
    numeric = df.select_dtypes(include=["int64","float64"]).columns

    if len(numeric) > 0:

        advice.append({
            "title": "Feature Scaling",
            "message": "Numbers in the dataset may have very different ranges.",
            "recommendation": "Scaling will help the model treat all numbers fairly."
        })


    # Highly correlated features
    if len(numeric) > 1:

        advice.append({
            "title": "Feature Similarity",
            "message": "Some features may contain very similar information.",
            "recommendation": "Removing highly similar features can improve model performance."
        })


    return advice